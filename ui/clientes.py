import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from ui.comun import campo, mostrar_error_db, gestionar_botones
from ui.estilos import VentanaModal

class VentanaCliente:
    def __init__(self, parent, usuario):
        self.w = VentanaModal(parent, 'Clientes', 625, 400)
        self.usuario = usuario

        self.vars = {k: tk.StringVar() for k in (
            'cliente_id', 'rfc', 'nombre', 'telefono', 'email')}
        self.original = None
        self.modo = 'inicial'
        self.entradas = {}

        # Búsqueda
        top = ttk.Frame(self.w, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Ingrese ID a buscar:').pack(side='left')
        ttk.Entry(top, textvariable=self.vars['cliente_id'], width=12).pack(side='left', padx=5)
        ttk.Button(top, text='Buscar', command=self.buscar).pack(side='left')

        # Formulario
        form = ttk.LabelFrame(self.w, text='Datos del cliente', padding=10)
        form.pack(fill='x', padx=10, pady=5)
        self.entradas['rfc'] = campo(form, 'RFC', self.vars['rfc'], 0)
        self.entradas['nombre'] = campo(form, 'Nombre', self.vars['nombre'], 1)
        self.entradas['telefono'] = campo(form, 'Teléfono', self.vars['telefono'], 2)
        self.entradas['email'] = campo(form, 'Email', self.vars['email'], 3)

        # Usuario (solo lectura - es el usuario logueado)
        ttk.Label(form, text='Usuario').grid(row=4, column=0, padx=6, pady=5, sticky='w')
        ttk.Label(form,
                  text=f"{usuario['nombre']} (ID {usuario['usuario_id']})",
                  foreground='#555555').grid(row=4, column=1, padx=6, pady=5, sticky='w')

        # Botones
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
        cid = self.vars['cliente_id'].get().strip()
        if not cid:
            return messagebox.showwarning('Atención', 'Ingrese un ID para buscar.', parent=self.w)
        try:
            fila = bd.obtener_uno('SELECT * FROM cliente WHERE cliente_id=%s', (cid,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not fila:
            messagebox.showinfo('Clientes', 'El cliente no existe. Verifique el ID.', parent=self.w)
            return self.set_modo('inicial')

        self.vars['rfc'].set(fila.get('rfc') or '')
        self.vars['nombre'].set(fila.get('nombre') or '')
        self.vars['telefono'].set(fila.get('telefono') or '')
        self.vars['email'].set(fila.get('email') or '')
        self.original = {k: v.get() for k, v in self.vars.items()}
        self.set_modo('encontrado')

    def nuevo(self):
        self.limpiar()
        self.set_modo('nuevo')

    def guardar(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not v['nombre']:
            return messagebox.showwarning('Atención', 'El nombre es obligatorio.', parent=self.w)
        try:
            uid = self.usuario['usuario_id']
            if self.modo == 'editar':
                bd.ejecutar(
                    'UPDATE cliente SET rfc=%s, nombre=%s, telefono=%s, email=%s, '
                    'usuario_id=%s WHERE cliente_id=%s',
                    (v['rfc'], v['nombre'], v['telefono'], v['email'],
                     uid, v['cliente_id']))
            else:
                if not v['cliente_id']:
                    return messagebox.showwarning('Atención',
                                                  'El ID del cliente es obligatorio.',
                                                  parent=self.w)
                bd.ejecutar(
                    'INSERT INTO cliente (cliente_id, rfc, nombre, telefono, email, '
                    'usuario_id) VALUES (%s,%s,%s,%s,%s,%s)',
                    (v['cliente_id'], v['rfc'], v['nombre'], v['telefono'],
                     v['email'], uid))
            messagebox.showinfo('Clientes', 'Guardado correctamente.', parent=self.w)
            self.set_modo('guardado')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def cancelar(self):
        self.limpiar()
        self.set_modo('inicial')

    def editar(self):
        self.set_modo('editar')

    def remover(self):
        cid = self.vars['cliente_id'].get().strip()
        if not cid:
            return
        if not messagebox.askyesno('Confirmar', '¿Eliminar este cliente?', parent=self.w):
            return
        try:
            bd.ejecutar('DELETE FROM cliente WHERE cliente_id=%s', (cid,))
            messagebox.showinfo('Clientes', 'Cliente eliminado.', parent=self.w)
            self.limpiar()
            self.set_modo('inicial')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def limpiar(self):
        for var in self.vars.values():
            var.set('')