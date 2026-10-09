import tkinter as tk
from tkinter import ttk, messagebox
from autenticacion import autenticar
from configuracion import TITULO_APP
from ui.estilos import (COLOR_FONDO, COLOR_TARJETA, COLOR_PRIMARIO,
                        centrar_ventana, _fuente_familia)


class VentanaInicioSesion:
    def __init__(self, root, al_exito):
        self.root = root
        self.al_exito = al_exito

        self.win = tk.Toplevel(root)
        self.win.title(TITULO_APP + " · Iniciar sesión")
        self.win.configure(bg=COLOR_FONDO)
        self.win.resizable(False, False)
        centrar_ventana(self.win, 420, 490)
        self.win.protocol("WM_DELETE_WINDOW", root.destroy)

        familia = _fuente_familia()

        # ----- Cabecera con color primario -----
        cabecera = tk.Frame(self.win, bg=COLOR_PRIMARIO, height=140)
        cabecera.pack(fill="x")
        cabecera.pack_propagate(False)

        tk.Label(cabecera, text="Control de Taller",
                 bg=COLOR_PRIMARIO, fg="#FFFFFF",
                 font=(familia, 20, "bold")).pack(pady=(35, 0))
        tk.Label(cabecera, text="Automotriz",
                 bg=COLOR_PRIMARIO, fg="#BFDBFE",
                 font=(familia, 12)).pack()

        # ----- Tarjeta blanca con el formulario -----
        tarjeta = tk.Frame(self.win, bg=COLOR_TARJETA,
                           highlightbackground="#E5E7EB",
                           highlightthickness=1)
        tarjeta.pack(fill="both", expand=True, padx=28, pady=24)

        contenido = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        contenido.pack(fill="both", expand=True, padx=22, pady=22)

        tk.Label(contenido, text="Inicia sesión",
                 bg=COLOR_TARJETA, fg=COLOR_PRIMARIO,
                 font=(familia, 14, "bold")).pack(anchor="w")
        tk.Label(contenido, text="Ingresa tus credenciales para continuar",
                 bg=COLOR_TARJETA, fg="#6B7280",
                 font=(familia, 9)).pack(anchor="w", pady=(2, 18))

        self.usuario = tk.StringVar()
        self.contrasena = tk.StringVar()

        tk.Label(contenido, text="Usuario",
                 bg=COLOR_TARJETA, fg="#374151",
                 font=(familia, 9, "bold")).pack(anchor="w")
        ttk.Entry(contenido, textvariable=self.usuario).pack(
            fill="x", pady=(4, 14), ipady=3)

        tk.Label(contenido, text="Contraseña",
                 bg=COLOR_TARJETA, fg="#374151",
                 font=(familia, 9, "bold")).pack(anchor="w")
        entrada = ttk.Entry(contenido, textvariable=self.contrasena, show="•")
        entrada.pack(fill="x", pady=(4, 18), ipady=3)

        ttk.Button(contenido, text="Iniciar sesión",
                   command=self.iniciar).pack(fill="x", ipady=6)

        entrada.bind("<Return>", lambda e: self.iniciar())
        self.usuario.set("")
        self.contrasena.set("")

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