import pymysql as sql
import json
from datetime import date

import customtkinter as ctk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkOptionMenu as OptionMenu
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame


# ──────────────────────────────────────────────
# BD
# ──────────────────────────────────────────────
def conectar_db():
    cfg = json.loads(open('settings.json', 'r', encoding='utf-8').read())
    return sql.connect(
        host=cfg['host'], user=cfg['user'],
        password=cfg['password'], database=cfg['database']
    )


# ──────────────────────────────────────────────
# CLASE BASE DE VENTANA
# ──────────────────────────────────────────────
class Ventana(Frame):
    def __init__(self, master, gestor, **kwargs):
        super().__init__(master, **kwargs)
        self.gestor = gestor

    def show(self):
        self.pack(expand=True, fill='both')

    def close(self):
        self.pack_forget()


# ──────────────────────────────────────────────
# ENCUESTA BASE  →  quiz_base + materias
# ──────────────────────────────────────────────
class VentanaBase(Ventana):
    """
    Encuesta base que se aplica cada semestre.
    Flujo:
      1. El usuario llena los campos generales.
      2. Al escribir el número de materias y presionar Enter (o el botón
         "Continuar"), se generan dinámicamente los campos de materia/docente.
      3. "Guardar" inserta en quiz_base y en materias.
    """

    OPCIONES_SIT_ACAD = ['Regular', 'Recursador', 'Oyente']
    OPCIONES_TOLERANCIA = ['Baja', 'Media', 'Alta']

    def __init__(self, master, gestor, boleta=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.boleta = boleta
        self._campos_materias = []   # lista de (entry_nombre, entry_docente, cb_estres)

        # ── Título ──────────────────────────────────────────────────────
        Label(self, text='Encuesta Base', font=Font(family='Calibri', size=18, weight='bold')).pack(pady=(12, 4))
        Label(self, text='Completa los datos del semestre actual', font=Font(size=12)).pack(pady=(0, 8))

        # ── Scroll contenedor ───────────────────────────────────────────
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(expand=True, fill='both', padx=16, pady=8)
        inner = self.scroll

        # ── Campos generales ────────────────────────────────────────────
        self._make_label(inner, 'Grupo (ej. 4CM3)')
        self.e_grupo = self._make_entry(inner, 'Grupo')

        self._make_label(inner, 'Situación académica')
        self.cb_sit_acad = OptionMenu(inner, values=self.OPCIONES_SIT_ACAD)
        self.cb_sit_acad.set(self.OPCIONES_SIT_ACAD[0])
        self.cb_sit_acad.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Semestre actual')
        self.e_semestre = self._make_entry(inner, 'Ej. 6')

        self._make_label(inner, 'Tolerancia al estrés (1 = muy alta - 5 = muy baja)')
        self.cb_tolerancia = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_tolerancia.set('3')
        self.cb_tolerancia.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Percepción de carga (1 = muy baja - 5 = muy alta)')
        self.cb_perse_carga = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_perse_carga.set('3')
        self.cb_perse_carga.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Relación con el grupo (1 = excelente - 5 = pobre)')
        self.cb_grupo_relacion = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_grupo_relacion.set('3')
        self.cb_grupo_relacion.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Percepción anímica general (1 = muy alta - 5 = muy baja)')
        self.cb_anim = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_anim.set('3')
        self.cb_anim.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Motivación académica (1 = muy alta - 5 = muy baja)')
        self.cb_motivacion = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_motivacion.set('3')
        self.cb_motivacion.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Percepción carga académica (1 = muy baja - 5 = muy alta)')
        self.cb_percepcion = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_percepcion.set('3')
        self.cb_percepcion.pack(fill='x', padx=8, pady=(0, 8))

        self._make_label(inner, 'Hobbies / actividades fuera horas / por semana (1 = (0-2 horas), 2 = (3-7 horas), 3 = (8-13 horas), 4 = (14-19 horas), 5 = (20+ horas))')
        self.cb_hobbies = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_hobbies.set('3')
        self.cb_hobbies.pack(fill='x', padx=8, pady=(0, 8))

        # ── Número de materias ──────────────────────────────────────────
        self._make_label(inner, '¿Cuántas materias llevas este semestre?')
        frame_nm = Frame(inner)
        frame_nm.pack(fill='x', padx=8, pady=(0, 8))
        self.e_num_materias = Entry(frame_nm, placeholder_text='Ej. 5', width=80)
        self.e_num_materias.pack(side='left', padx=(0, 8))
        Button(frame_nm, text='Continuar →', width=120,
            command=self._generar_campos_materias).pack(side='left')
        self.e_num_materias.bind('<Return>', lambda e: self._generar_campos_materias())

        # ── Zona dinámica de materias ───────────────────────────────────
        self.frame_materias = Frame(inner)
        self.frame_materias.pack(fill='x', padx=8, pady=(0, 8))

        # ── Botón guardar y status ──────────────────────────────────────
        Button(self, text='Guardar encuesta', command=self.guardar,
               font=Font(size=14, weight='bold'), height=40).pack(pady=10, padx=16, fill='x')
        self.status = Label(self, text='')
        self.status.pack(pady=(0, 8))

    # ── Helpers UI ──────────────────────────────────────────────────────
    def _make_label(self, parent, text):
        Label(parent, text=text, font=Font(size=12)).pack(anchor='w', padx=8, pady=(6, 0))

    def _make_entry(self, parent, placeholder):
        e = Entry(parent, placeholder_text=placeholder)
        e.pack(fill='x', padx=8, pady=(0, 8))
        return e

    # ── Generar campos de materias dinámicamente ────────────────────────
    def _generar_campos_materias(self):
        # Limpiar campos anteriores
        for w in self.frame_materias.winfo_children():
            w.destroy()
        self._campos_materias.clear()

        try:
            n = int(self.e_num_materias.get().strip())
            if n <= 0 or n > 20:
                raise ValueError
        except ValueError:
            self.status.configure(text='Ingresa un número de materias válido (1-20)', text_color='orange')
            return

        Label(self.frame_materias, text='Materias del semestre',
              font=Font(size=13, weight='bold')).pack(anchor='w', pady=(8, 4))

        for i in range(n):
            frame_m = Frame(self.frame_materias, fg_color='transparent')
            frame_m.pack(fill='x', pady=4)

            Label(frame_m, text=f'Materia {i+1}', font=Font(size=12, weight='bold')).pack(anchor='w')

            e_nombre = Entry(frame_m, placeholder_text='Nombre de la materia')
            e_nombre.pack(fill='x', pady=(2, 2))

            e_docente = Entry(frame_m, placeholder_text='Nombre del docente')
            e_docente.pack(fill='x', pady=(2, 4))

            Label(frame_m, text='Dificultad/estrés que percibes de esta materia (1 = fácil, 5 = muy difícil)',
                  font=Font(size=11)).pack(anchor='w', pady=(0, 2))
            cb_estres_mat = OptionMenu(frame_m, values=['1', '2', '3', '4', '5'])
            cb_estres_mat.set('3')
            cb_estres_mat.pack(fill='x', pady=(0, 6))

            self._campos_materias.append((e_nombre, e_docente, cb_estres_mat))

        self.status.configure(text=f'{n} materias listas para llenar.', text_color='gray')

    # ── Guardar ─────────────────────────────────────────────────────────
    def guardar(self):
        if not self.boleta:
            self.status.configure(text='Boleta no definida.', text_color='red')
            return

        grupo = self.e_grupo.get().strip()
        sit_acad = self.cb_sit_acad.get()
        semestre_txt = self.e_semestre.get().strip()
        str_tolerancia = int(self.cb_tolerancia.get())
        perse_carga = int(self.cb_perse_carga.get())
        grupo_relacion = int(self.cb_grupo_relacion.get())
        pers_anim = int(self.cb_anim.get())
        motivacion = int(self.cb_motivacion.get())
        percepcion = int(self.cb_percepcion.get())
        hobbies = int(self.cb_hobbies.get())

        if not grupo or not semestre_txt:
            self.status.configure(text='Completa grupo y semestre.', text_color='orange')
            return
        try:
            semestre = int(semestre_txt)
        except ValueError:
            self.status.configure(text='Semestre debe ser un número.', text_color='orange')
            return

        # Validar materias
        if not self._campos_materias:
            self.status.configure(text='Primero indica cuántas materias llevas.', text_color='orange')
            return

        materias_datos = []
        for i, (e_nombre, e_docente, cb_estres_mat) in enumerate(self._campos_materias):
            nombre = e_nombre.get().strip()
            docente = e_docente.get().strip()
            estres_mat = int(cb_estres_mat.get())
            if not nombre or not docente:
                self.status.configure(text=f'Completa nombre y docente de la materia {i+1}.', text_color='orange')
                return
            materias_datos.append((nombre, docente, estres_mat))

        hoy = date.today()

        try:
            conn = conectar_db()
            cur = conn.cursor()

            # ── 1. Insertar quiz_base ────────────────────────────────────
            cur.execute('''
                INSERT INTO quiz_base
                    (usuario_boleta, fecha_quiz, grupo, sit_acad, semestre,
                     str_tolerancia, perse_carga, grupo_relacion,
                     pers_anim_general, motivacion_acad, persepcion_academica, hobbies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (self.boleta, hoy, grupo, sit_acad, semestre,
                  str_tolerancia, perse_carga, grupo_relacion,
                  pers_anim, motivacion, percepcion, hobbies))

            # ── 2. Insertar/actualizar docentes y materias ───────────────
            for nombre_mat, nombre_doc, estres_mat in materias_datos:
                # ¿Existe el docente? Si no, crearlo
                cur.execute('SELECT iddocente FROM docente WHERE nombre = %s AND usuario_boleta = %s',
                            (nombre_doc, self.boleta))
                row = cur.fetchone()
                if row:
                    iddocente = row[0]
                else:
                    cur.execute(
                        'INSERT INTO docente (nombre, inf, usuario_boleta) VALUES (%s, %s, %s)',
                        (nombre_doc, 0, self.boleta)
                    )
                    iddocente = cur.lastrowid

                # Insertar materia con estrés percibido
                cur.execute('''
                    INSERT INTO materias (nombre, estres, docente_iddocente, usuario_boleta)
                    VALUES (%s, %s, %s, %s)
                ''', (nombre_mat, estres_mat, iddocente, self.boleta))

            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='✓ Encuesta guardada correctamente.', text_color='green')

        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar. Revisa los datos.', text_color='red')


# ──────────────────────────────────────────────
# ACTIVIDADES
# ──────────────────────────────────────────────
class VentanaActividades(Ventana):
    """
    Registra actividades en la tabla `actividades`.
    La materia se elige de una lista desplegable cargada desde BD.
    """

    def __init__(self, master, gestor, boleta=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.boleta = boleta
        self._materias_map = {}   # nombre_materia → idmaterias

        Label(self, text='Registrar Actividad',
              font=Font(family='Calibri', size=18, weight='bold')).pack(pady=(12, 4))

        self.scroll = ScrollableFrame(self)
        self.scroll.pack(expand=True, fill='both', padx=16, pady=8)
        inner = self.scroll

        # Materia
        self._lbl(inner, 'Materia')
        self.cb_materia = OptionMenu(inner, values=['— Cargando... —'])
        self.cb_materia.pack(fill='x', padx=8, pady=(0, 8))
        Button(inner, text='↻ Recargar materias', command=self._cargar_materias,
               width=160, height=28).pack(anchor='w', padx=8, pady=(0, 10))

        # Día
        self._lbl(inner, f'Fecha (YYYY-MM-DD)  — hoy: {date.today()}')
        self.e_dia = Entry(inner, placeholder_text=str(date.today()))
        self.e_dia.pack(fill='x', padx=8, pady=(0, 8))

        # Tiempo estimado
        self._lbl(inner, 'Tiempo estimado (ej. "2 horas", "30 min")')
        self.e_tiempo = Entry(inner, placeholder_text='Tiempo estimado')
        self.e_tiempo.pack(fill='x', padx=8, pady=(0, 8))

        # Estrés generado
        self._lbl(inner, 'Estrés que genera (1 = poco, 5 = mucho)')
        self.cb_estres = OptionMenu(inner, values=['1', '2', '3', '4', '5'])
        self.cb_estres.set('3')
        self.cb_estres.pack(fill='x', padx=8, pady=(0, 8))

        # Descripción
        self._lbl(inner, 'Descripción (máx. 45 caracteres)')
        self.e_descripcion = Entry(inner, placeholder_text='Ej. "Estudiar parcial unidad 3"')
        self.e_descripcion.pack(fill='x', padx=8, pady=(0, 8))

        # Botón
        Button(self, text='Registrar actividad', command=self.registrar,
               font=Font(size=14, weight='bold'), height=40).pack(pady=10, padx=16, fill='x')

        # Lista de actividades pendientes
        Label(self, text='Actividades registradas',
              font=Font(size=13, weight='bold')).pack(anchor='w', padx=16, pady=(8, 0))
        self.frame_lista = ScrollableFrame(self, height=160)
        self.frame_lista.pack(fill='x', padx=16, pady=(4, 4))

        self.status = Label(self, text='')
        self.status.pack(pady=(0, 8))

        self._cargar_materias()

    def _lbl(self, parent, text):
        Label(parent, text=text, font=Font(size=12)).pack(anchor='w', padx=8, pady=(6, 0))

    def _cargar_materias(self):
        if not self.boleta:
            return
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT idmaterias, nombre FROM materias WHERE usuario_boleta = %s', (self.boleta,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            if rows:
                self._materias_map = {f'{r[1]} (ID {r[0]})': r[0] for r in rows}
                self.cb_materia.configure(values=list(self._materias_map.keys()))
                self.cb_materia.set(list(self._materias_map.keys())[0])
            else:
                self.cb_materia.configure(values=['Sin materias — llena primero la encuesta base'])
                self.cb_materia.set('Sin materias — llena primero la encuesta base')
        except Exception as e:
            print(e)

    def registrar(self):
        if not self.boleta:
            self.status.configure(text='Boleta no definida.', text_color='red')
            return

        materia_key = self.cb_materia.get()
        id_materia = self._materias_map.get(materia_key)
        if id_materia is None:
            self.status.configure(text='Selecciona una materia válida.', text_color='orange')
            return

        dia_txt = self.e_dia.get().strip() or str(date.today())
        tiempo = self.e_tiempo.get().strip()
        estres = int(self.cb_estres.get())
        descripcion = self.e_descripcion.get().strip()[:45]

        if not tiempo:
            self.status.configure(text='Indica el tiempo estimado.', text_color='orange')
            return
        if not descripcion:
            self.status.configure(text='Agrega una descripción a la actividad.', text_color='orange')
            return

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO actividades
                    (usuario_boleta, materias_idmaterias, dia, tiempo_estimado, estres_generado, estado, descripcion)
                VALUES (%s, %s, %s, %s, %s, 0, %s)
            ''', (self.boleta, id_materia, dia_txt, tiempo, estres, descripcion))
            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='✓ Actividad registrada.', text_color='green')
            self._refrescar_lista()
        except Exception as e:
            print(e)
            self.status.configure(text='Error al registrar actividad.', text_color='red')

    def _refrescar_lista(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()
        if not self.boleta:
            return
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('''
                SELECT a.id_actividad, m.nombre, a.dia, a.tiempo_estimado, a.estres_generado, a.estado, a.descripcion
                FROM actividades a
                LEFT JOIN materias m ON a.materias_idmaterias = m.idmaterias
                WHERE a.usuario_boleta = %s
                ORDER BY a.dia DESC
                LIMIT 10
            ''', (self.boleta,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            if not rows:
                Label(self.frame_lista, text='Sin actividades registradas.').pack(anchor='w', padx=8)
                return

            for r in rows:
                estado_txt = '✓ Completada' if r[5] else '⏳ Pendiente'
                color = 'green' if r[5] else 'gray'
                desc = r[6] or ''
                txt = f'#{r[0]}  [{r[1]}]  {r[2]}  |  {r[3]}  |  Estrés: {r[4]}  |  {estado_txt}'
                row_frame = Frame(self.frame_lista, fg_color='transparent')
                row_frame.pack(fill='x', padx=4, pady=(3, 0))
                Label(row_frame, text=txt, font=Font(size=11), text_color=color).pack(side='left')
                if not r[5]:
                    Button(row_frame, text='Completar', width=90, height=24,
                           command=lambda aid=r[0]: self._completar(aid)).pack(side='right', padx=4)
                if desc:
                    Label(self.frame_lista, text=f'   📝 {desc}',
                          font=Font(size=10), text_color='gray').pack(anchor='w', padx=8, pady=(0, 4))
        except Exception as e:
            print(e)

    def _completar(self, id_actividad):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('UPDATE actividades SET estado = 1 WHERE id_actividad = %s', (id_actividad,))
            conn.commit()
            cur.close()
            conn.close()
            self._refrescar_lista()
        except Exception as e:
            print(e)

    def show(self):
        super().show()
        self._cargar_materias()
        self._refrescar_lista()


# ──────────────────────────────────────────────
# GESTOR DE VENTANAS
# ──────────────────────────────────────────────
class GestorVentanas:
    def __init__(self, master, boleta=None):
        self.master = master
        self.boleta = boleta
        self.ventana_actual = None

        # ── Nav bar ─────────────────────────────────────────────────────
        nav = Frame(master, height=50)
        nav.pack(fill='x', padx=10, pady=6)

        ctk.CTkLabel(nav, text=f'👤 Boleta: {boleta}',
                     font=Font(size=13)).pack(side='left', padx=12)

        Button(nav, text='📋 Encuesta Base',
               command=lambda: self.show('base'), width=150).pack(side='left', padx=4)
        Button(nav, text='📌 Actividades',
               command=lambda: self.show('actividades'), width=140).pack(side='left', padx=4)

        # ── Contenedor ──────────────────────────────────────────────────
        self.container = Frame(master)
        self.container.pack(expand=True, fill='both')

        # ── Crear ventanas ───────────────────────────────────────────────
        self.windows = {
            'base':        VentanaBase(self.container, self, boleta=self.boleta),
            'actividades': VentanaActividades(self.container, self, boleta=self.boleta),
        }

        self.show('base')

    def show(self, name):
        for w in self.windows.values():
            w.pack_forget()
        win = self.windows.get(name)
        if win:
            win.show()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == '__main__':
    from customtkinter import CTk as Tk
    app = Tk()
    app.geometry('820x700')
    app.title('AyDS - Sistema')
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('blue')
    GestorVentanas(app, boleta=None)
    app.mainloop()