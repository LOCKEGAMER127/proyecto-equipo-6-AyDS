import customtkinter as ctk
import pymysql as sql
import json

class ResultadosWindow(ctk.CTkToplevel): 
    def __init__(self, boleta_usuario):
        super().__init__()
        
        self.title("Resultados y Diagnóstico de Estrés")
        self.geometry("500x550")
        self.resizable(False, False)
        
        
        self.attributes('-topmost', True)
        self.grab_set()
        
        self.boleta = boleta_usuario
        
        
        datos_bd = self.obtener_datos_mysql()
        
        if datos_bd:
            self.dificultad = float(datos_bd['dificultad'])
            self.tiempo = float(datos_bd['tiempo'])
            self.estres_percibido = float(datos_bd['estres_percibido'])
            self.construir_interfaz()
        else:
            lbl_vacio = ctk.CTkLabel(self, text="No hay encuestas registradas aún.\n¡Ve a contestar una primero!", font=("Segoe UI", 18))
            lbl_vacio.pack(expand=True, pady=100)

    def conectar_db(self):
        try:
            DATABASE = json.loads(open('settings.json', 'r', encoding='utf-8').read())
        except Exception:
            DATABASE = {"host": "localhost", "user": "root", "password": "", "database": "ayds"}
        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )

    def obtener_datos_mysql(self):
        conexion = None
        cursor = None
        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor(sql.cursors.DictCursor)
            
           
            query = """
                SELECT persepcion_academica as dificultad, 
                       hobbies as tiempo, 
                       perse_carga as estres_percibido 
                FROM quiz_base 
                WHERE usuario_boleta = %s 
                ORDER BY fecha_quiz DESC LIMIT 1
            """
            cursor.execute(query, (self.boleta,))
            return cursor.fetchone()

        except Exception as e:
            print("Error al leer la BD:", e)
            return None
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def calcular_estres_matematico(self):
        calculo = (0.4 * self.dificultad) + (0.3 * self.tiempo) + (0.3 * self.estres_percibido)
        return round(calculo, 2)

    def obtener_diagnostico_y_consejo(self, nivel):
        if nivel >= 4.0:
            return "#ff4a4a", "NIVEL DE RIESGO: ALTO", "Es fundamental aplicar técnicas de autorregulación emocional. Cuando te sientas abrumado por tareas complejas o código que no compila, haz una pausa en seco.\n\nTip Práctico: Aplica una desconexión digital estricta al menos una hora antes de dormir."
        elif nivel >= 3.0:
            return "#f5a742", "NIVEL DE ALERTA: MODERADO", "Estás en el límite y la carga académica empieza a pesar. Evita pasar demasiadas horas seguidas en la misma posición.\n\nTip Práctico: Establece alarmas para hacer rutinas de estiramiento físico cada 2 horas."
        else:
            return "#42f566", "ESTADO EXCELENTE: BAJO", "¡Excelente manejo de tus actividades! Tienes un nivel de estrés bajo y buena adaptación al entorno.\n\nTip Práctico: Sigue manteniendo un equilibrio saludable entre tus entregas académicas y tu tiempo personal."

    def construir_interfaz(self):
        puntaje_final = self.calcular_estres_matematico()
        color_semaforo, texto_estado, texto_consejo = self.obtener_diagnostico_y_consejo(puntaje_final)

        frame_principal = ctk.CTkFrame(self, corner_radius=15)
        frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame_principal, text="Tu Nivel de Estrés Actual", font=("Segoe UI", 20, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(frame_principal, text=f"{puntaje_final}", font=("Segoe UI", 60, "bold"), text_color=color_semaforo).pack(pady=(5, 5))
        ctk.CTkLabel(frame_principal, text=texto_estado, font=("Segoe UI", 16, "bold"), text_color=color_semaforo).pack(pady=(0, 20))
        
        ctk.CTkFrame(frame_principal, height=2, fg_color="gray").pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(frame_principal, text="💡 Recomendación del Sistema:", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=30, pady=(10, 5))
        
        caja_consejo = ctk.CTkTextbox(frame_principal, width=400, height=150, font=("Segoe UI", 14), wrap="word")
        caja_consejo.pack(padx=30, pady=5)
        caja_consejo.insert("0.0", texto_consejo)
        caja_consejo.configure(state="disabled")

        ctk.CTkButton(frame_principal, text="Cerrar Diagnóstico", command=self.destroy).pack(pady=(20, 20))