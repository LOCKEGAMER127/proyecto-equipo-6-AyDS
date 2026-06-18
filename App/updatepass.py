import customtkinter as ctk
import pymysql as sql
import hashlib
import json


class UpdatePassWindow(ctk.CTk):
    def __init__(self, boleta, **kwargs):
        super().__init__(**kwargs)

        self.boleta = boleta

        self.title("Actualizar Contraseña")
        self.geometry("480x380")
        self.resizable(False, False)

    def conectar_db(self):
        DATABASE = json.loads(
            open(
                'settings.json',
                'r',
                encoding='utf-8'
            ).read()
        )

        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )

    def abrir_login(self):
        self.destroy()

        from App.login import LoginWindow
        LoginWindow().show()

    def verify_password(self):

        password1 = self.entry_password.get().strip()
        password2 = self.entry_confirm.get().strip()

        conn = None
        cur = None
        
        if not password1 or not password2:
            self.label_error.configure(
                text="Por favor completa ambos campos.",
                text_color="orange"
            )
            return

        if len(password1) < 4:
            self.label_error.configure(
                text="La contraseña debe tener al menos 4 caracteres.",
                text_color="orange"
            )
            return

        if password1 != password2:
            self.label_error.configure(
                text="Las contraseñas no coinciden.",
                text_color="orange"
            )
            return

        password_hash = hashlib.sha256(
            password1.encode()
        ).hexdigest()

        try:

            conn = self.conectar_db()
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE usuario
                SET contraseña = %s
                WHERE boleta = %s
                """,
                (
                    password_hash,
                    self.boleta
                )
            )

            conn.commit()
            
            if cur.rowcount == 0:
                self.label_error.configure(
                    text="No se encontró el usuario.",
                    color="red"
                )
                return

            self.label_error.configure(
                text="Contraseña actualizada correctamente",
                text_color="green"
            )

            self.after(
                1500,
                self.abrir_login
            )

        except Exception as e:

            print(e)

            self.label_error.configure(
                text="Error al actualizar la contraseña",
                text_color="red"
            )

        finally:

            if cur:
                cur.close()
            if conn:
                conn.close()

    def show(self):

        self.frame = ctk.CTkFrame(
            self,
            corner_radius=16
        )

        self.frame.pack(
            expand=True,
            fill="both",
            padx=30,
            pady=30
        )

        self.label_titulo = ctk.CTkLabel(
            self.frame,
            text="Actualizar Contraseña",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20,
                weight="bold"
            ),
        )

        self.label_titulo.pack(
            pady=(28, 10)
        )

        self.label_boleta = ctk.CTkLabel(
            self.frame,
            text=f"Boleta: {self.boleta}",
            font=ctk.CTkFont(size=13)
        )

        self.label_boleta.pack(
            pady=(0, 20)
        )

        self.entry_password = ctk.CTkEntry(
            self.frame,
            placeholder_text="Nueva contraseña",
            show="*",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
        )

        self.entry_password.pack(
            pady=(0, 12)
        )

        self.entry_confirm = ctk.CTkEntry(
            self.frame,
            placeholder_text="Confirmar contraseña",
            show="*",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
        )

        self.entry_confirm.pack(
            pady=(0, 12)
        )

        self.entry_confirm.bind(
            "<Return>",
            lambda event: self.verify_password()
        )

        self.label_error = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=240,
        )

        self.label_error.pack(
            pady=(0, 10)
        )

        self.boton_confirmar = ctk.CTkButton(
            self.frame,
            text="Confirmar",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.verify_password,
        )

        self.boton_confirmar.pack(
            pady=(4, 10)
        )

        self.boton_login = ctk.CTkButton(
            self.frame,
            text="Volver al Login",
            width=260,
            height=42,
            corner_radius=10,
            command=self.abrir_login
        )

        self.boton_login.pack(
            pady=(0, 20)
        )

        self.mainloop()


if __name__ == "__main__":
    UpdatePassWindow("2023000000").show()