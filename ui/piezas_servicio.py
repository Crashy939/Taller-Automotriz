import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import bd
from ui.comun import mostrar_error_db


class VentanaPiezasServicio:
    """Ventana para administrar las piezas usadas en un servicio (folio)."""

    def __init__(self, parent, folio):
        self.w = tk.Toplevel(parent)
        self.w.title(f'Piezas del servicio - Folio {folio}')
        self.w.geometry('700x580')
        self.folio = folio
        self.piezas = []

        # Tabla de piezas usadas en el servicio
        ttk.Label(self.w, text=f'Folio: {folio}',
                  font=('TkDefaultFont', 12, 'bold'),
                  padding=8).pack(anchor='w')

        marco_tabla = ttk.Frame(self.w, padding=(10, 0))
        marco_tabla.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(
            marco_tabla,
            columns=('pieza_id', 'descripcion', 'marca', 'cantidad'),
            show='headings')
        for c, t, w in (('pieza_id', 'ID', 60),
                        ('descripcion', 'Descripción', 300),
                        ('marca', 'Marca', 150),
                        ('cantidad', 'Cantidad', 90)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill='both', expand=True)

        # Formulario para agregar
        form = ttk.LabelFrame(self.w, text='Agregar pieza', padding=10)
        form.pack(fill='x', padx=10, pady=8)

        ttk.Label(form, text='Pieza').grid(row=0, column=0, padx=6, pady=5, sticky='w')
        self.cmb_pieza = ttk.Combobox(form, state='readonly', width=55)
        self.cmb_pieza.grid(row=0, column=1, padx=6, pady=5, sticky='ew')

        ttk.Label(form, text='Cantidad').grid(row=1, column=0, padx=6, pady=5, sticky='w')
        self.var_cantidad = tk.StringVar(value='1')
        ttk.Entry(form, textvariable=self.var_cantidad, width=10).grid(
            row=1, column=1, padx=6, pady=5, sticky='w')

        # Barra de botones
        barra = ttk.Frame(self.w, padding=8)
        barra.pack()
        ttk.Button(barra, text='Agregar', command=self.agregar).pack(side='left', padx=3)
        ttk.Button(barra, text='Quitar seleccionada',
                   command=self.quitar).pack(side='left', padx=3)
        ttk.Button(barra, text='Cerrar', command=self.w.destroy).pack(side='left', padx=3)

        self.cargar_disponibles()
        self.cargar_usadas()

    # ---------- Carga de datos ----------
    def cargar_disponibles(self):
        """Solo piezas con stock > 0."""
        try:
            self.piezas = bd.obtener_todos(
                'SELECT pieza_id, descripcion, marca, stock '
                'FROM pieza WHERE stock > 0')
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        self.cmb_pieza['values'] = [
            f"{p['pieza_id']} - {p['descripcion']} "
            f"({p['marca'] or 'sin marca'}) [stock {p['stock']}]"
            for p in self.piezas]

    def cargar_usadas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            filas = bd.obtener_todos(
                'SELECT d.pieza_id, p.descripcion, p.marca, d.cantidad '
                'FROM detalle_reparacion_pieza d '
                'JOIN pieza p ON p.pieza_id = d.pieza_id '
                'WHERE d.folio = %s', (self.folio,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        for f in filas:
            self.tree.insert('', 'end', values=(
                f['pieza_id'], f['descripcion'],
                f['marca'] or '', f['cantidad']))

    # ---------- Acciones ----------
    def agregar(self):
        sel = self.cmb_pieza.get()
        if not sel:
            return messagebox.showwarning('Atención',
                                          'Seleccione una pieza.', parent=self.w)

        # ---- VALIDACIÓN: el folio debe existir en reparacion ----
        try:
            existe_folio = bd.obtener_uno(
                'SELECT folio FROM reparacion WHERE folio=%s', (self.folio,))
        except Exception as exc:
            return mostrar_error_db(exc, self.w)
        if not existe_folio:
            return messagebox.showwarning(
                'Atención',
                f'El folio {self.folio} todavía no está guardado.\n'
                'Primero guarda el servicio antes de agregar piezas.',
                parent=self.w)
        # --------------------------------------------------------

        pieza_id = sel.split(' - ')[0]

        try:
            cantidad = int(self.var_cantidad.get() or 0)
        except ValueError:
            return messagebox.showwarning('Atención',
                                          'La cantidad debe ser un número entero.',
                                          parent=self.w)
        if cantidad <= 0:
            return messagebox.showwarning('Atención',
                                          'La cantidad debe ser mayor a 0.',
                                          parent=self.w)

        pieza = next((p for p in self.piezas
                      if str(p['pieza_id']) == pieza_id), None)
        if not pieza:
            return
        if cantidad > pieza['stock']:
            return messagebox.showwarning(
                'Atención',
                f"Solo hay {pieza['stock']} unidades disponibles.",
                parent=self.w)

        try:
            existe = bd.obtener_uno(
                'SELECT cantidad FROM detalle_reparacion_pieza '
                'WHERE folio=%s AND pieza_id=%s',
                (self.folio, pieza_id))

            sentencias = []
            if existe:
                sentencias.append((
                    'UPDATE detalle_reparacion_pieza '
                    'SET cantidad = cantidad + %s '
                    'WHERE folio=%s AND pieza_id=%s',
                    (cantidad, self.folio, pieza_id)))
            else:
                sentencias.append((
                    'INSERT INTO detalle_reparacion_pieza '
                    '(folio, pieza_id, cantidad) VALUES (%s, %s, %s)',
                    (self.folio, pieza_id, cantidad)))

            # Descontar stock de la pieza
            sentencias.append((
                'UPDATE pieza SET stock = stock - %s WHERE pieza_id=%s',
                (cantidad, pieza_id)))

            bd.transaccion(sentencias)

            self.var_cantidad.set('1')
            self.cmb_pieza.set('')
            self.cargar_disponibles()   # refresca stock en el combo
            self.cargar_usadas()
        except Exception as exc:
            mostrar_error_db(exc, self.w)

    def quitar(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning('Atención',
                                          'Seleccione una pieza de la lista.',
                                          parent=self.w)
        vals = self.tree.item(sel[0], 'values')
        pieza_id = vals[0]
        cantidad = int(vals[3])

        if not messagebox.askyesno('Confirmar',
                                   '¿Quitar esta pieza del servicio?',
                                   parent=self.w):
            return
        try:
            bd.transaccion([
                ('DELETE FROM detalle_reparacion_pieza '
                 'WHERE folio=%s AND pieza_id=%s',
                 (self.folio, pieza_id)),
                ('UPDATE pieza SET stock = stock + %s WHERE pieza_id=%s',
                 (cantidad, pieza_id)),
            ])
            self.cargar_disponibles()
            self.cargar_usadas()
        except Exception as exc:
            mostrar_error_db(exc, self.w)