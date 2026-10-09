import tkinter as tk
from tkinter import ttk, messagebox
from autenticacion import autenticar
from configuracion import TITULO_APP


class VentanaInicioSesion:
    def __init__(self, root, al_exito):
        self.root = root
        self.al_exito = al_exito
        self.win = tk.Toplevel(root)
        self.win.title(TITULO_APP + " - Iniciar sesión")
        self.win.geometry("360x220")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", root.destroy)

        marco = ttk.Frame(self.win, padding=25)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="Acceso al sistema",
                  font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 18))

        self.usuario = tk.StringVar()
        self.contrasena = tk.StringVar()

        ttk.Label(marco, text="Usuario").pack(anchor="w")
        ttk.Entry(marco, textvariable=self.usuario).pack(fill="x", pady=(0, 8))

        ttk.Label(marco, text="Contraseña").pack(anchor="w")
        entrada = ttk.Entry(marco, textvariable=self.contrasena, show="•")
        entrada.pack(fill="x")

        ttk.Button(marco, text="Iniciar sesión", command=self.iniciar).pack(pady=5, ipady=8)
        entrada.bind("<Return>", lambda e: self.iniciar())

    def iniciar(self):
        if not self.usuario.get().strip() or not self.contrasena.get():
            return messagebox.showwarning("Datos requeridos",
                                          "Captura usuario y contraseña.",
                                          parent=self.win)
        try:
            fila = autenticar(self.usuario.get().strip(), self.contrasena.get())
        except Exception as exc:
            return messagebox.showerror("Conexión",
                                        f"No se pudo conectar con MySQL:\n{exc}",
                                        parent=self.win)
        if not fila:
            return messagebox.showerror("Acceso denegado",
                                        "Usuario o contraseña incorrectos.",
                                        parent=self.win)
        self.win.destroy()
        self.root.deiconify()
        self.al_exito(fila)