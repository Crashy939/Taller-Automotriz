import tkinter as tk
from tkinter import ttk, messagebox
from configuracion import TITULO_APP
from ui.estilos import (COLOR_FONDO, COLOR_TARJETA, COLOR_PRIMARIO,
                        COLOR_TEXTO_SUAVE, _fuente_familia)
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
        self.root.geometry("880x600")
        self.root.configure(bg=COLOR_FONDO)
        self.root.protocol("WM_DELETE_WINDOW", self.salir)

        familia = _fuente_familia()

        # ----- Barra superior -----
        barra = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=64)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra, text=TITULO_APP,
                 bg=COLOR_PRIMARIO, fg="#FFFFFF",
                 font=(familia, 14, "bold")).pack(side="left", padx=20)

        self.opciones = ttk.Menubutton(barra, text="Opciones ▾")
        self.menu = tk.Menu(self.opciones, tearoff=False)
        self.opciones["menu"] = self.menu

        # ----- Menú (mismo orden que antes) -----
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
        self.menu.add_separator()
        self.menu.add_command(label="Salir", command=self.salir)

        self.opciones.pack(side="right", padx=20, pady=14)

        # ----- Contenido central -----
        contenido = tk.Frame(self.root, bg=COLOR_FONDO)
        contenido.pack(fill="both", expand=True, padx=40, pady=40)

        # Tarjeta de bienvenida
        tarjeta = tk.Frame(contenido, bg=COLOR_TARJETA,
                           highlightbackground="#E5E7EB",
                           highlightthickness=1)
        tarjeta.pack(fill="x", pady=(0, 24))

        interior = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        interior.pack(fill="both", expand=True, padx=32, pady=28)

        perfil_nombre = {1: 'Administrador', 2: 'Auxiliar', 3: 'Mecánico'}.get(
            self.usuario['perfil'], 'Usuario')

        tk.Label(interior, text=f"Bienvenido, {self.usuario['nombre']}",
                 bg=COLOR_TARJETA, fg=COLOR_PRIMARIO,
                 font=(familia, 20, "bold")).pack(anchor="w")
        tk.Label(interior, text=f"Perfil: {perfil_nombre}",
                 bg=COLOR_TARJETA, fg=COLOR_TEXTO_SUAVE,
                 font=(familia, 11)).pack(anchor="w", pady=(4, 0))

        # ----- Grid de accesos rápidos -----
        tk.Label(contenido, text="Accesos rápidos",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE,
                 font=(familia, 11, "bold")).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(contenido, bg=COLOR_FONDO)
        grid.pack(fill="both", expand=True)

        accesos = []
        if self.usuario["perfil"] == 1:
            accesos.append(("👤", "Usuarios",
                            lambda: VentanaUsuario(self.root)))
        accesos += [
            ("🧑", "Clientes",   lambda: VentanaCliente(self.root, self.usuario)),
            ("🚗", "Vehículos",  lambda: VentanaVehiculo(self.root)),
            ("🔧", "Servicios",  lambda: VentanaServicio(self.root, self.usuario)),
        ]
        if self.usuario["perfil"] == 1:
            accesos.append(("📊", "Reportes",
                            lambda: VentanaReportes(self.root)))
        accesos.append(("📦", "Piezas", lambda: VentanaPieza(self.root)))

        columnas = 3
        for i, (icono, titulo, cmd) in enumerate(accesos):
            fila, col = divmod(i, columnas)
            self._crear_tarjeta(grid, fila, col, icono, titulo, cmd, familia)

        for c in range(columnas):
            grid.columnconfigure(c, weight=1, uniform="col")

    def _crear_tarjeta(self, parent, fila, col, icono, titulo, comando, familia):
        tarjeta = tk.Frame(parent, bg=COLOR_TARJETA,
                           highlightbackground="#E5E7EB",
                           highlightthickness=1, cursor="hand2")
        tarjeta.grid(row=fila, column=col, sticky="nsew", padx=8, pady=8)

        interior = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        interior.pack(fill="both", expand=True, padx=20, pady=22)

        lbl_icono = tk.Label(interior, text=icono,
                             bg=COLOR_TARJETA, fg=COLOR_PRIMARIO,
                             font=(familia, 26))
        lbl_icono.pack()

        lbl_titulo = tk.Label(interior, text=titulo,
                              bg=COLOR_TARJETA, fg=COLOR_PRIMARIO,
                              font=(familia, 12, "bold"))
        lbl_titulo.pack(pady=(6, 0))

        def _click(_e=None):
            comando()

        def _hover_in(_e=None):
            tarjeta.configure(highlightbackground=COLOR_PRIMARIO,
                              highlightthickness=2)

        def _hover_out(_e=None):
            tarjeta.configure(highlightbackground="#E5E7EB",
                              highlightthickness=1)

        for w in (tarjeta, interior, lbl_icono, lbl_titulo):
            w.bind("<Button-1>", _click)
            w.bind("<Enter>", _hover_in)
            w.bind("<Leave>", _hover_out)

    def salir(self):
        if messagebox.askyesno("Salir", "¿Deseas cerrar la sesión?", parent=self.root):
            for hijo in self.root.winfo_children():
                hijo.destroy()
            self.cerrar_sesion()