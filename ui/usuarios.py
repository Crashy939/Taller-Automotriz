import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from autenticacion import hash_contrasena
from ui.comun import campo, mostrar_error_db, gestionar_botones

PERFILES = {'Administrador': 1, 'Auxiliar': 2, 'Mecanico': 3}
PERFILES_INV = {v: k for k, v in PERFILES.items()}


class VentanaUsuario:
    def __init__(self, parent):
        self.w = tk.Toplevel(parent)
        self.w.title('Usuarios')
        self.w.geometry('540x520')

        self.vars = {k: tk.StringVar() for k in (
            'usuario_id', 'nombre', 'telefono', 'email',
            'nombre_usuario', 'password', 'perfil')}
        self.original = None
        self.modo = 'inicial'
        self.entradas = {}

        # Búsqueda
        top = ttk.Frame(self.w, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Ingrese ID a buscar:').pack(side='left')
        ttk.Entry(top, textvariable=self.vars['usuario_id'], width=12).pack(side='left', padx=5)
        ttk.Button(top, text='Buscar', command=self.buscar).pack(side='left')

        # Formulario
        form = ttk.LabelFrame(self.w, text='Datos del usuario', padding=10)
        form.pack(fill='x', padx=10, pady=5)
        self.entradas['nombre'] = campo(form, 'Nombre', self.vars['nombre'], 0)
        self.entradas['telefono'] = campo(form, 'Teléfono', self.vars['telefono'], 1)
        self.entradas['email'] = campo(form, 'Email', self.vars['email'], 2)
        self.entradas['nombre_usuario'] = campo(form, 'Nombre de usuario', self.vars['nombre_usuario'], 3)

        ttk.Label(form, text='Contraseña').grid(row=4, column=0, padx=6, pady=5, sticky='w')
        self.entradas['password'] = ttk.Entry(form, textvariable=self.vars['password'],
                                              show='•', width=22)
        self.entradas['password'].grid(row=4, column=1, padx=6, pady=5, sticky='ew')

        ttk.Label(form, text='Perfil').grid(row=5, column=0, padx=6, pady=5, sticky='w')
        self.cmb_perfil = ttk.Combobox(form, textvariable=self.vars['perfil'],
                                       values=list(PERFILES.keys()),
                                       state='readonly', width=20)
        self.cmb_perfil.grid(row=5, column=1, padx=6, pady=5, sticky='ew')

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

    # ---------- Modos ----------
    def set_modo(self, modo):
        self.modo = modo
        gestionar_botones(self.botones, modo)
        editable = modo in ('nuevo', 'editar')
        for nombre, widget in self.entradas.items():
            widget.config(state='normal' if editable else 'readonly')
        self.cmb_perfil.config(state='readonly' if editable else 'disabled')

    # ---------- Acciones ----------
    def buscar(self):
        uid = self.vars['usuario_id'].get().strip()
        if not uid:
            return messagebox.showwarning('Atención', 'Ingrese un ID para buscar.', parent=self.w)
        try:
            fila = bd.obtener_uno('SELECT * FROM usuario WHERE usuario_id=%s', (uid,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not fila:
            messagebox.showinfo('Usuarios', 'El usuario no existe. Verifique el ID.', parent=self.w)
            return self.set_modo('inicial')

        self.vars['nombre'].set(fila.get('nombre') or '')
        self.vars['telefono'].set(fila.get('telefono') or '')
        self.vars['email'].set(fila.get('email') or '')
        self.vars['nombre_usuario'].set(fila.get('nombre_usuario') or '')
        self.vars['password'].set('')  # no mostramos el hash
        self.vars['perfil'].set(PERFILES_INV.get(fila.get('perfil'), 'Auxiliar'))
        self.original = {k: v.get() for k, v in self.vars.items()}
        self.set_modo('encontrado')

    def nuevo(self):
        self.limpiar()
        self.vars['perfil'].set('Auxiliar')
        self.set_modo('nuevo')

    def guardar(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not v['nombre'] or not v['nombre_usuario']:
            return messagebox.showwarning('Atención',
                                          'Nombre y nombre de usuario son obligatorios.',
                                          parent=self.w)
        try:
            perfil = PERFILES.get(v['perfil'], 2)
            if self.modo == 'editar':
                bd.ejecutar(
                    'UPDATE usuario SET nombre=%s, telefono=%s, email=%s, '
                    'nombre_usuario=%s, perfil=%s WHERE usuario_id=%s',
                    (v['nombre'], v['telefono'] or None, v['email'] or None,
                     v['nombre_usuario'], perfil, v['usuario_id']))
                if v['password']:
                    bd.ejecutar('UPDATE usuario SET password=%s WHERE usuario_id=%s',
                                (hash_contrasena(v['password']), v['usuario_id']))
            else:
                if not v['password']:
                    return messagebox.showwarning('Atención',
                                                  'La contraseña es obligatoria.',
                                                  parent=self.w)
                bd.ejecutar(
                    'INSERT INTO usuario (nombre, telefono, email, nombre_usuario, '
                    'password, perfil, activo) VALUES (%s,%s,%s,%s,%s,%s,1)',
                    (v['nombre'], v['telefono'] or None, v['email'] or None,
                     v['nombre_usuario'], hash_contrasena(v['password']), perfil))
            messagebox.showinfo('Usuarios', 'Guardado correctamente.', parent=self.w)
            self.set_modo('guardado')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def cancelar(self):
        self.limpiar()
        self.set_modo('inicial')

    def editar(self):
        self.set_modo('editar')

    def remover(self):
        uid = self.vars['usuario_id'].get().strip()
        if not uid:
            return
        if not messagebox.askyesno('Confirmar', '¿Eliminar este usuario?', parent=self.w):
            return
        try:
            bd.ejecutar('DELETE FROM usuario WHERE usuario_id=%s', (uid,))
            messagebox.showinfo('Usuarios', 'Usuario eliminado.', parent=self.w)
            self.limpiar()
            self.set_modo('inicial')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def limpiar(self):
        for var in self.vars.values():
            var.set('')