import tkinter as tk
from tkinter import ttk, messagebox
from configuracion import TITULO_APP
from ui.usuarios import VentanaUsuario
from ui.clientes import VentanaCliente
from ui.vehiculos import VentanaVehiculo
from ui.servicios import VentanaServicio
from ui.reportes import VentanaReportes
from ui.piezas import VentanaPieza


class VentanaPrincipal:
    def __init__(self, root, usuario, cerrar_sesion):
        self.root = root
        self.usuario = usuario
        self.cerrar_sesion = cerrar_sesion

        self.root.title(TITULO_APP)
        self.root.geometry("720x460")
        self.root.protocol("WM_DELETE_WINDOW", self.salir)

        self.opciones = ttk.Menubutton(self.root, text="Opciones")
        self.menu = tk.Menu(self.opciones, tearoff=False)
        self.opciones["menu"] = self.menu
        self.opciones.pack(anchor="nw", padx=12, pady=12)

        # Primer botón: Usuarios (solo Administrador)
        if self.usuario["perfil"] == 1:
            self.menu.add_command(label="Usuarios",
                                  command=lambda: VentanaUsuario(self.root))

        self.menu.add_command(label="Clientes",
                              command=lambda: VentanaCliente(self.root, self.usuario))
        self.menu.add_command(label="Vehículos",
                              command=lambda: VentanaVehiculo(self.root))
        self.menu.add_command(label="Servicios",
                              command=lambda: VentanaServicio(self.root, self.usuario))
        if self.usuario["perfil"] == 1:
            self.menu.add_command(label="Reportes",
                                  command=lambda: VentanaReportes(self.root))
        self.menu.add_command(label="Piezas",
                              command=lambda: VentanaPieza(self.root))

        # Salir al final
        self.menu.add_separator()
        self.menu.add_command(label="Salir", command=self.salir)

        perfil = {1: 'Administrador', 2: 'Auxiliar', 3: 'Mecánico'}.get(
            self.usuario['perfil'], 'Usuario')
        ttk.Label(self.root,
                  text=f"Bienvenido, {self.usuario['nombre']}\nPerfil: {perfil}",
                  font=("TkDefaultFont", 18)).pack(pady=100)

    def salir(self):
        if messagebox.askyesno("Salir", "¿Deseas cerrar la sesión?", parent=self.root):
            for hijo in self.root.winfo_children():
                hijo.destroy()
            self.cerrar_sesion()