import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from base_datos import bd


def campo(parent, label, var, row, col=0, width=22):
    ttk.Label(parent, text=label).grid(row=row, column=col, padx=6, pady=5, sticky='w')
    e = ttk.Entry(parent, textvariable=var, width=width)
    e.grid(row=row, column=col + 1, padx=6, pady=5, sticky='ew')
    return e


def fecha_valida(valor):
    try:
        datetime.strptime(valor, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def mostrar_error_db(exc, parent):
    messagebox.showerror('Base de datos', str(exc), parent=parent)


# Tabla de estados de botones según el modo de la ventana
ESTADOS_BOTONES = {
    'inicial':    {'Nuevo': True,  'Guardar': False, 'Cancelar': False, 'Editar': False, 'Remover': False},
    'encontrado': {'Nuevo': True,  'Guardar': False, 'Cancelar': False, 'Editar': True,  'Remover': True},
    'nuevo':      {'Nuevo': False, 'Guardar': True,  'Cancelar': True,  'Editar': False, 'Remover': False},
    'editar':     {'Nuevo': False, 'Guardar': True,  'Cancelar': False, 'Editar': False, 'Remover': False},
    'guardado':   {'Nuevo': True,  'Guardar': True,  'Cancelar': True,  'Editar': True,  'Remover': True},
}


def gestionar_botones(botones, modo):
    est = ESTADOS_BOTONES.get(modo, ESTADOS_BOTONES['inicial'])
    for nombre, boton in botones.items():
        if nombre in est:
            boton.config(state='normal' if est[nombre] else 'disabled')


class SelectorRelacion:
    """Botón que abre una lista de opciones (FK). Muestra sólo el nombre en
    la lista y, a un lado del botón, el ID del registro elegido."""

    def __init__(self, parent, label, var_id, query, row, col=0):
        self.parent = parent
        self.var_id = var_id
        self.query = query
        ttk.Label(parent, text=label).grid(row=row, column=col, padx=6, pady=5, sticky='w')
        contenedor = ttk.Frame(parent)
        contenedor.grid(row=row, column=col + 1, padx=6, pady=5, sticky='ew')
        self.btn = ttk.Button(contenedor, text='Seleccionar...', command=self.abrir_lista)
        self.btn.pack(side='left')
        self.ent_id = ttk.Entry(contenedor, textvariable=var_id, width=10, state='readonly')
        self.ent_id.pack(side='left', padx=5)

    def set_habilitado(self, estado):
        self.btn.config(state='normal' if estado else 'disabled')

    def abrir_lista(self):
        try:
            filas = bd.obtener_todos(self.query)
        except Exception as exc:
            return mostrar_error_db(exc, self.parent)
        if not filas:
            return messagebox.showinfo('Sin registros', 'No hay opciones disponibles.', parent=self.parent)

        v = tk.Toplevel(self.parent)
        v.title('Seleccionar')
        v.geometry('340x340')
        v.transient(self.parent)
        v.grab_set()

        ttk.Label(v, text='Seleccione un registro:', padding=8).pack(anchor='w')
        marco = ttk.Frame(v, padding=8)
        marco.pack(fill='both', expand=True)
        barra = ttk.Scrollbar(marco, orient='vertical')
        lista = tk.Listbox(marco, yscrollcommand=barra.set)
        barra.config(command=lista.yview)
        barra.pack(side='right', fill='y')
        lista.pack(side='left', fill='both', expand=True)

        for f in filas:
            lista.insert('end', f['nombre'])

        def elegir(event=None):
            sel = lista.curselection()
            if not sel:
                return
            self.var_id.set(str(filas[sel[0]]['id']))
            v.destroy()

        lista.bind('<Double-Button-1>', elegir)
        ttk.Button(v, text='Seleccionar', command=elegir).pack(pady=8)
        lista.focus_set()