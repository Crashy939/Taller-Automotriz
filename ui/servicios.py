import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from ui.comun import campo, fecha_valida, mostrar_error_db, gestionar_botones, SelectorRelacion
from ui.piezas_servicio import VentanaPiezasServicio
from ui.estilos import VentanaModal

class VentanaServicio:
    def __init__(self, parent, usuario):
        self.w = VentanaModal(parent, 'Servicios', 625, 650)
        self.usuario = usuario

        self.vars = {k: tk.StringVar() for k in (
            'folio', 'fecha_entrada', 'fecha_salida', 'hora_entrada',
            'hora_salida', 'matricula', 'tipo_servicio',
            'total_pagar', 'falla')}
        self.original = None
        self.modo = 'inicial'
        self.entradas = {}

        # Búsqueda
        top = ttk.Frame(self.w, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='Ingrese folio a buscar:').pack(side='left')
        ttk.Entry(top, textvariable=self.vars['folio'], width=12).pack(side='left', padx=5)
        ttk.Button(top, text='Buscar', command=self.buscar).pack(side='left')

        # Formulario
        form = ttk.LabelFrame(self.w, text='Datos del servicio', padding=10)
        form.pack(fill='x', padx=10, pady=5)

        self.entradas['fecha_entrada'] = campo(
            form, 'Fecha entrada (AAAA-MM-DD)', self.vars['fecha_entrada'], 0)
        self.entradas['fecha_salida'] = campo(
            form, 'Fecha salida (AAAA-MM-DD)', self.vars['fecha_salida'], 1)
        self.entradas['hora_entrada'] = campo(
            form, 'Hora entrada (HH:MM)', self.vars['hora_entrada'], 2)
        self.entradas['hora_salida'] = campo(
            form, 'Hora salida (HH:MM)', self.vars['hora_salida'], 3)
        self.entradas['tipo_servicio'] = campo(
            form, 'Tipo servicio', self.vars['tipo_servicio'], 4)
        self.entradas['total_pagar'] = campo(
            form, 'Total a pagar', self.vars['total_pagar'], 5)
        self.entradas['falla'] = campo(
            form, 'Falla', self.vars['falla'], 6)

        # Vehículo (sigue siendo seleccionable)
        self.selector_vehiculo = SelectorRelacion(
            form, 'Matrícula', self.vars['matricula'],
            'SELECT matricula AS id, matricula AS nombre FROM vehiculo', 7)

        # Usuario (solo lectura - es el logueado)
        ttk.Label(form, text='Usuario').grid(row=8, column=0, padx=6, pady=5, sticky='w')
        ttk.Label(form,
                  text=f"{usuario['nombre']} (ID {usuario['usuario_id']})",
                  foreground='#555555').grid(row=8, column=1, padx=6, pady=5, sticky='w')

        # Botón Piezas a usar
        frame_piezas = ttk.Frame(self.w, padding=(10, 5))
        frame_piezas.pack(fill='x')
        ttk.Button(frame_piezas, text='Piezas a usar',
                   command=self.abrir_piezas).pack(side='left')

        # Barra de botones
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
        self.selector_vehiculo.set_habilitado(editable)

    # ---------- Abrir ventana de piezas ----------
    def abrir_piezas(self):
        folio = self.vars['folio'].get().strip()
        if not folio:
            return messagebox.showwarning(
                'Atención',
                'Primero debe indicar un folio (búsquelo o escríbalo).',
                parent=self.w)
        VentanaPiezasServicio(self.w, folio)

    # ---------- Acciones ----------
    def buscar(self):
        folio = self.vars['folio'].get().strip()
        if not folio:
            return messagebox.showwarning('Atención', 'Ingrese un folio.', parent=self.w)
        try:
            fila = bd.obtener_uno('SELECT * FROM reparacion WHERE folio=%s', (folio,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not fila:
            messagebox.showinfo('Servicios', 'El folio no existe.', parent=self.w)
            return self.set_modo('inicial')

        self.vars['fecha_entrada'].set(str(fila.get('fecha_entrada') or ''))
        self.vars['fecha_salida'].set(str(fila.get('fecha_salida') or ''))
        self.vars['hora_entrada'].set(str(fila.get('hora_entrada') or ''))
        self.vars['hora_salida'].set(str(fila.get('hora_salida') or ''))
        self.vars['matricula'].set(str(fila.get('matricula') or ''))
        self.vars['tipo_servicio'].set(str(fila.get('tipo_servicio') or ''))
        self.vars['total_pagar'].set(str(fila.get('total_pagar') or ''))
        self.vars['falla'].set(str(fila.get('falla') or ''))
        self.original = {k: v.get() for k, v in self.vars.items()}
        self.set_modo('encontrado')

    def nuevo(self):
        self.limpiar()
        self.set_modo('nuevo')

    def guardar(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        if not v['folio'] or not v['matricula'] or not fecha_valida(v['fecha_entrada']):
            return messagebox.showwarning(
                'Atención',
                'Folio, matrícula y fecha de entrada válida son obligatorios.',
                parent=self.w)
        if v['fecha_salida'] and not fecha_valida(v['fecha_salida']):
            return messagebox.showwarning('Atención',
                                          'Fecha de salida inválida (AAAA-MM-DD).',
                                          parent=self.w)
        if v['fecha_salida'] and v['fecha_salida'] < v['fecha_entrada']:
            return messagebox.showwarning('Atención',
                                          'La fecha de salida no puede ser anterior a la entrada.',
                                          parent=self.w)
        try:
            # Usuario SIEMPRE es el logueado
            uid = self.usuario['usuario_id']
            if self.modo == 'editar':
                bd.ejecutar(
                    'UPDATE reparacion SET fecha_entrada=%s, fecha_salida=%s, '
                    'hora_entrada=%s, hora_salida=%s, matricula=%s, usuario_id=%s, '
                    'tipo_servicio=%s, total_pagar=%s, falla=%s WHERE folio=%s',
                    (v['fecha_entrada'], v['fecha_salida'] or None,
                     v['hora_entrada'] or None, v['hora_salida'] or None,
                     v['matricula'], uid,
                     v['tipo_servicio'], v['total_pagar'] or 0,
                     v['falla'], v['folio']))
            else:
                bd.ejecutar(
                    'INSERT INTO reparacion (folio, fecha_entrada, fecha_salida, '
                    'hora_entrada, hora_salida, matricula, usuario_id, tipo_servicio, '
                    'total_pagar, falla) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (v['folio'], v['fecha_entrada'], v['fecha_salida'] or None,
                     v['hora_entrada'] or None, v['hora_salida'] or None,
                     v['matricula'], uid,
                     v['tipo_servicio'], v['total_pagar'] or 0, v['falla']))
            messagebox.showinfo('Servicios', 'Guardado correctamente.', parent=self.w)
            self.set_modo('guardado')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def cancelar(self):
        self.limpiar()
        self.set_modo('inicial')

    def editar(self):
        self.set_modo('editar')

    def remover(self):
        folio = self.vars['folio'].get().strip()
        if not folio:
            return
        if not messagebox.askyesno(
                'Confirmar',
                '¿Eliminar este servicio? También se eliminarán sus piezas asociadas.',
                parent=self.w):
            return
        try:
            # Borrar primero los detalles (por si no hay ON DELETE CASCADE)
            bd.ejecutar('DELETE FROM detalle_reparacion_pieza WHERE folio=%s', (folio,))
            bd.ejecutar('DELETE FROM reparacion WHERE folio=%s', (folio,))
            messagebox.showinfo('Servicios', 'Servicio eliminado.', parent=self.w)
            self.limpiar()
            self.set_modo('inicial')
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def limpiar(self):
        for var in self.vars.values():
            var.set('')