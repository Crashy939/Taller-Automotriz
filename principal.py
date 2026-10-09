import tkinter as tk
from ui.inicio_sesion import VentanaInicioSesion
from ui.ventana_principal import VentanaPrincipal


class Aplicacion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.mostrar_login()

    def mostrar_login(self):
        VentanaInicioSesion(self.root, self.al_iniciar_sesion)

    def al_iniciar_sesion(self, usuario):
        VentanaPrincipal(self.root, usuario, self.cerrar_sesion)

    def cerrar_sesion(self):
        for hijo in self.root.winfo_children():
            hijo.destroy()
        self.root.withdraw()
        self.mostrar_login()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    Aplicacion().run()