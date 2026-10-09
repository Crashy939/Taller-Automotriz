import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from ui.comun import campo, mostrar_error_db, gestionar_botones, SelectorRelacion


class VentanaVehiculo:
    def __init__(self, parent):
        self.w = tk.Toplevel(parent)
        self.w.title('Vehículos')
        self.w.geometry('600x460')

        self.vars = {k: tk.StringVar() for k in (
            'matricula', 'marca', 'modelo', 'anio', 'cliente_id',
            'color', 'kilometraje')}
        self.original = None
        self.modo = 'inicial'
        self.entradas = {}

        top = ttk.Frame(self.w, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Ingrese matrícula a buscar:').pack(side='left')
        ttk.Entry(top, textvariable=self.vars['matricula'], width=14).pack(side='left', padx=5)
        ttk.Button(top, text='Buscar', command=self.buscar).pack(side='left')

        form = ttk.LabelFrame(self.w, text='Datos del vehículo', padding=10)
        form.pack(fill='x', padx=10, pady=5)
        self.entradas['marca'] = campo(form, 'Marca', self.vars['marca'], 0)
        self.entradas['modelo'] = campo(form, 'Modelo', self.vars['modelo'], 1)
        self.entradas['anio'] = campo(form, 'Año', self.vars['anio'], 2)
        self.entradas['color'] = campo(form, 'Color', self.vars['color'], 3)
        self.entradas['kilometraje'] = campo(form, 'Kilometraje', self.vars['kilometraje'], 4)

        self.selector_cliente = SelectorRelacion(
            form, 'Cliente', self.vars['cliente_id'],
            'SELECT cliente_id AS id, nombre FROM cliente', 5)

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
        self.selector_cliente.set_habilitado(editable)

    def buscar(self):
        mat = self.vars['matricula'].get().strip()
        if not mat:
            return messagebox.showwarning('Atención', 'Ingrese una matrícula.', parent=self.w)
        try:
            fila = bd.obtener_uno('SELECT * FROM vehiculo WHERE matricula=%s', (mat,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not fila:
            messagebox.showinfo('Vehículos', 'La matrícula no existe.', parent=self.w)
            return self.set_modo('inicial')

        self.vars['marca'].set(fila.get('marca') or '')
        self.vars['modelo'].set(fila.get('modelo') or '')
        self.vars['anio'].set(str(fila.get('anio') or ''))
        self.vars['color'].set(fila.get('color') or '')
        self.vars['kilometraje'].set(str(fila.get('kilometraje') or ''))
        self.vars['cliente_id'].set(str(fila.get('cliente_id') or ''))
        self.original = {k: v.get() for k, v in self.vars.items()}
        self.set_modo('encontrado')

    def nuevo(self):
        self.limpiar()
        self.set_modo('nuevo')

    def guardar(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not v['matricula'] or not v['marca'] or not v['modelo']:
            return messagebox.showwarning('Atención',
                                          'Matrícula, marca y modelo son obligatorios.',
                                          parent=self.w)
        try:
            if self.modo == 'editar':
                bd.ejecutar(
                    'UPDATE vehiculo SET marca=%s, modelo=%s, anio=%s, cliente_id=%s, '
                    'color=%s, kilometraje=%s WHERE matricula=%s',
                    (v['marca'], v['modelo'], v['anio'] or None,
                     v['cliente_id'] or None, v['color'], v['kilometraje'] or None,
                     v['matricula']))
            else:
                bd.ejecutar(
                    'INSERT INTO vehiculo (matricula, marca, modelo, anio, cliente_id, '
                    'color, kilometraje) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (v['matricula'], v['marca'], v['modelo'], v['anio'] or None,
                     v['cliente_id'] or None, v['color'], v['kilometraje'] or None))
            messagebox.showinfo('Vehículos', 'Guardado correctamente.', parent=self.w)
            self.set_modo('guardado')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def cancelar(self):
        self.limpiar()
        self.set_modo('inicial')

    def editar(self):
        self.set_modo('editar')

    def remover(self):
        mat = self.vars['matricula'].get().strip()
        if not mat:
            return
        if not messagebox.askyesno('Confirmar', '¿Eliminar este vehículo?', parent=self.w):
            return
        try:
            bd.ejecutar('DELETE FROM vehiculo WHERE matricula=%s', (mat,))
            messagebox.showinfo('Vehículos', 'Vehículo eliminado.', parent=self.w)
            self.limpiar()
            self.set_modo('inicial')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def limpiar(self):
        for var in self.vars.values():
            var.set('')