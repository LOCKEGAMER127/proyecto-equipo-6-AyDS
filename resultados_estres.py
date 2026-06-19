import customtkinter as ctk
import pymysql as sql
import json

class ResultadosWindow(ctk.CTkToplevel):
    def __init__(self, boleta_usuario):
        super().__init__()
        self.title("Diagnóstico de Estrés Completo")
        self.geometry("500x620")
        self.resizable(False, False)
        
       
        self.attributes('-topmost', True)
        self.grab_set()
        
        self.boleta = boleta_usuario
        self.datos = self.obtener_datos_completos()
        
        self.construir_interfaz()

    def conectar_db(self):
        try:
            db_config = json.loads(open('settings.json', 'r', encoding='utf-8').read())
            return sql.connect(
                host=db_config['host'], user=db_config['user'],
                password=db_config['password'], database=db_config['database']
            )
        except Exception:
            return sql.connect(host="localhost", user="root", password="", database="AyDS")

    def obtener_datos_completos(self):
        conexion = self.conectar_db()
        cursor = conexion.cursor(sql.cursors.DictCursor)
        try:
            
            cursor.execute("""
                SELECT str_tolerancia, perse_carga, persepcion_academica 
                FROM quiz_base 
                WHERE usuario_boleta = %s 
                ORDER BY fecha_quiz DESC LIMIT 1
            """, (self.boleta,))
            encuesta = cursor.fetchone()
            
            
            cursor.execute("""
                SELECT AVG(estres_generado) as prom_estres 
                FROM actividades 
                WHERE usuario_boleta = %s AND estado = 0
            """, (self.boleta,))
            actividades = cursor.fetchone()
            
            return {"encuesta": encuesta, "actividades": actividades}
        except Exception as e:
            print("Error al consultar datos:", e)
            return {"encuesta": None, "actividades": None}
        finally:
            cursor.close()
            conexion.close()

    def calcular_estres(self):
        encuesta = self.datos.get('encuesta')
        actividades = self.datos.get('actividades')
        
        # Promedio puro de actividades (si no hay ninguna, se queda en 0.0)
        prom_act = float(actividades['prom_estres']) if actividades and actividades['prom_estres'] is not None else 0.0
        
        # Promedio de la encuesta base (perfil inicial)
        if encuesta:
            estres_base = (float(encuesta['str_tolerancia']) + float(encuesta['perse_carga']) + float(encuesta['persepcion_academica'])) / 3
        else:
            estres_base = 0.0

        
        estres_solo_actividades = round(prom_act, 2)
        
        
        if prom_act > 0:
            estres_general = (estres_base * 0.4) + (prom_act * 0.6)
        else:
            
            estres_general = estres_base
            
        return round(estres_general, 2), estres_solo_actividades

    def obtener_color_y_texto(self, nivel):
        if nivel == 0:
            return "gray", "SIN REGISTROS"
        elif nivel >= 4.0:
            return "#ff4a4a", "NIVEL ALTO (RIESGO)"
        elif nivel >= 2.5:
            return "#f5a742", "NIVEL MODERADO"
        else:
            return "#42f566", "NIVEL BAJO (SALUDABLE)"

    def construir_interfaz(self):
        estres_general, estres_solo_actividades = self.calcular_estres()
        
        color_gen, txt_gen = self.obtener_color_y_texto(estres_general)
        color_act, txt_act = self.obtener_color_y_texto(estres_solo_actividades)

        frame_principal = ctk.CTkFrame(self, corner_radius=15)
        frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame_principal, text="📊 Diagnóstico del Sistema", font=("Segoe UI", 20, "bold")).pack(pady=(15, 15))

        #BLOQUE 1: ESTRÉS GENERAL
        frame_gen = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_gen.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(frame_gen, text="1. Estrés General (Encuesta + Actividades)", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(frame_gen, text="Ponderación de tu estado psicológico con tu carga real.", font=("Segoe UI", 11), text_color="gray").pack(anchor="w")
        
        lbl_num_gen = ctk.CTkLabel(frame_gen, text=f"{estres_general if estres_general > 0 else 'N/A'}", font=("Segoe UI", 46, "bold"), text_color=color_gen)
        lbl_num_gen.pack(pady=2)
        ctk.CTkLabel(frame_gen, text=txt_gen, font=("Segoe UI", 12, "bold"), text_color=color_gen).pack()

        
        ctk.CTkFrame(frame_principal, height=2, fg_color="gray").pack(fill="x", padx=40, pady=15)

        #  BLOQUE 2: ESTRÉS SOLO ACTIVIDADES 
        frame_act = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_act.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(frame_act, text="2. Estrés Únicamente por Actividades", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(frame_act, text="Promedio del nivel de impacto de tus tareas entregadas.", font=("Segoe UI", 11), text_color="gray").pack(anchor="w")
        
        lbl_num_act = ctk.CTkLabel(frame_act, text=f"{estres_solo_actividades if estres_solo_actividades > 0 else '0.0'}", font=("Segoe UI", 46, "bold"), text_color=color_act)
        lbl_num_act.pack(pady=2)
        ctk.CTkLabel(frame_act, text=txt_act, font=("Segoe UI", 12, "bold"), text_color=color_act).pack()

        
        ctk.CTkButton(frame_principal, text="Entendido", command=self.destroy, font=("Segoe UI", 13, "bold")).pack(pady=(25, 10))