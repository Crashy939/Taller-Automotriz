import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from ui.comun import campo, mostrar_error_db, gestionar_botones


class VentanaPieza:
    def __init__(self, parent):
        self.w = tk.Toplevel(parent)
        self.w.title('Piezas')
        self.w.geometry('540x360')

        self.vars = {k: tk.StringVar() for k in (
            'pieza_id', 'descripcion', 'marca', 'stock')}
        self.original = None
        self.modo = 'inicial'
        self.entradas = {}

        top = ttk.Frame(self.w, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Ingrese ID a buscar:').pack(side='left')
        ttk.Entry(top, textvariable=self.vars['pieza_id'], width=12).pack(side='left', padx=5)
        ttk.Button(top, text='Buscar', command=self.buscar).pack(side='left')

        form = ttk.LabelFrame(self.w, text='Datos de la pieza', padding=10)
        form.pack(fill='x', padx=10, pady=5)
        self.entradas['descripcion'] = campo(form, 'Descripción', self.vars['descripcion'], 0)
        self.entradas['marca'] = campo(form, 'Marca', self.vars['marca'], 1)
        self.entradas['stock'] = campo(form, 'Stock', self.vars['stock'], 2)

        barra = ttk.Frame(self.w, padding=10)
        barra.pack()
        self.botones = {}
        for texto, cmd in [('Nuevo', self.nuevo), ('Guardar', self.guardar),
                           ('Cancelar', self.cancelar), ('Editar', self.editar),
                           ('Remover', self.remover)]:
            b = ttk.Button(barra, text=texto, command=cmd)
            b.pack(side='left', padx=3)
            self.botones[texto] = b

        self.set_modo('inicial')

    def set_modo(self, modo):
        self.modo = modo
        gestionar_botones(self.botones, modo)
        editable = modo in ('nuevo', 'editar')
        for widget in self.entradas.values():
            widget.config(state='normal' if editable else 'readonly')

    def buscar(self):
        pid = self.vars['pieza_id'].get().strip()
        if not pid:
            return messagebox.showwarning('Atención', 'Ingrese un ID para buscar.', parent=self.w)
        try:
            fila = bd.obtener_uno('SELECT * FROM pieza WHERE pieza_id=%s', (pid,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not fila:
            messagebox.showinfo('Piezas', 'No existe esa pieza.', parent=self.w)
            return self.set_modo('inicial')

        self.vars['descripcion'].set(fila.get('descripcion') or '')
        self.vars['marca'].set(fila.get('marca') or '')
        self.vars['stock'].set(str(fila.get('stock') or ''))
        self.original = {k: v.get() for k, v in self.vars.items()}
        self.set_modo('encontrado')

    def nuevo(self):
        self.limpiar()
        self.set_modo('nuevo')

    def guardar(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not v['descripcion'] or not v['stock'].isdigit():
            return messagebox.showwarning('Atención',
                                          'Descripción y stock (entero) son obligatorios.',
                                          parent=self.w)
        try:
            if self.modo == 'editar':
                bd.ejecutar('UPDATE pieza SET descripcion=%s, marca=%s, stock=%s '
                            'WHERE pieza_id=%s',
                            (v['descripcion'], v['marca'], v['stock'], v['pieza_id']))
            else:
                bd.ejecutar('INSERT INTO pieza (descripcion, marca, stock) '
                            'VALUES (%s,%s,%s)',
                            (v['descripcion'], v['marca'], v['stock']))
            messagebox.showinfo('Piezas', 'Guardado correctamente.', parent=self.w)
            self.set_modo('guardado')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def cancelar(self):
        self.limpiar()
        self.set_modo('inicial')

    def editar(self):
        self.set_modo('editar')

    def remover(self):
        pid = self.vars['pieza_id'].get().strip()
        if not pid:
            return
        if not messagebox.askyesno('Confirmar', '¿Eliminar esta pieza?', parent=self.w):
            return
        try:
            bd.ejecutar('DELETE FROM pieza WHERE pieza_id=%s', (pid,))
            messagebox.showinfo('Piezas', 'Pieza eliminada.', parent=self.w)
            self.limpiar()
            self.set_modo('inicial')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def limpiar(self):
        for var in self.vars.values():
            var.set('')