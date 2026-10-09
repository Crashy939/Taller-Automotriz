import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from base_datos import bd
from ui.comun import fecha_valida


class VentanaReportes:
    def __init__(self, parent):
        self.w = tk.Toplevel(parent)
        self.w.title('Reportes')
        self.w.geometry('900x500')

        f = ttk.Frame(self.w, padding=8)
        f.pack(fill='x')
        self.cid = tk.StringVar()
        self.fd = tk.StringVar()

        ttk.Label(f, text='Cliente ID').pack(side='left')
        ttk.Entry(f, textvariable=self.cid, width=10).pack(side='left')
        ttk.Button(f, text='Buscar cliente', command=self.por_cliente).pack(side='left', padx=4)

        ttk.Label(f, text='Desde (AAAA-MM-DD)').pack(side='left')
        ttk.Entry(f, textvariable=self.fd, width=14).pack(side='left')
        ttk.Button(f, text='Buscar fecha', command=self.por_fecha).pack(side='left', padx=4)

        self.tree = ttk.Treeview(
            self.w,
            columns=('folio', 'cliente', 'matricula', 'fecha', 'tipo', 'total'),
            show='headings')
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)

        encabezados = {'folio': 'Folio', 'cliente': 'Cliente',
                       'matricula': 'Matrícula', 'fecha': 'Fecha',
                       'tipo': 'Tipo', 'total': 'Total'}
        for c in self.tree['columns']:
            self.tree.heading(c, text=encabezados[c])
            self.tree.column(c, width=130)

    def cargar(self, filas):
        for x in self.tree.get_children():
            self.tree.delete(x)
        for r in filas:
            self.tree.insert('', 'end', values=tuple(
                r.get(k, '') for k in ('folio', 'cliente_id', 'matricula',
                                       'fecha_entrada', 'tipo_servicio', 'total_pagar')))

    def por_cliente(self):
        cid = self.cid.get().strip()
        if not cid:
            return messagebox.showwarning('Atención', 'Ingrese un Cliente ID.', parent=self.w)
        try:
            filas = bd.obtener_todos(
                'SELECT r.*, v.cliente_id FROM reparacion r '
                'JOIN vehiculo v ON v.matricula=r.matricula WHERE v.cliente_id=%s',
                (cid,))
        except Exception as exc:
            return messagebox.showerror('Base de datos', str(exc), parent=self.w)
        self.cargar(filas)
        if filas:
            archivo = self.generar_archivo(filas, f'cliente_{cid}')
            messagebox.showinfo('Reporte generado',
                                f'Se guardó el archivo:\n{archivo}',
                                parent=self.w)
        else:
            messagebox.showinfo('Reportes', 'No se encontraron registros.', parent=self.w)

    def por_fecha(self):
        fd = self.fd.get().strip()
        if not fecha_valida(fd):
            return messagebox.showwarning('Atención',
                                          'Ingrese una fecha válida (AAAA-MM-DD).',
                                          parent=self.w)
        try:
            filas = bd.obtener_todos(
                'SELECT r.*, v.cliente_id FROM reparacion r '
                'JOIN vehiculo v ON v.matricula=r.matricula WHERE r.fecha_entrada >= %s',
                (fd,))
        except Exception as exc:
            return messagebox.showerror('Base de datos', str(exc), parent=self.w)
        self.cargar(filas)
        if filas:
            archivo = self.generar_archivo(filas, f'desde_{fd}')
            messagebox.showinfo('Reporte generado',
                                f'Se guardó el archivo:\n{archivo}',
                                parent=self.w)
        else:
            messagebox.showinfo('Reportes', 'No se encontraron registros.', parent=self.w)

    def generar_archivo(self, filas, etiqueta):
        carpeta = 'reportes'
        os.makedirs(carpeta, exist_ok=True)
        nombre = f"reporte_{etiqueta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        ruta = os.path.join(carpeta, nombre)

        with open(ruta, 'w', encoding='utf-8') as f:
            f.write('=' * 90 + '\n')
            f.write('REPORTE DE SERVICIOS\n')
            f.write(f'Criterio: {etiqueta}\n')
            f.write(f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('=' * 90 + '\n\n')
            encabezados = ['Folio', 'ClienteID', 'Matrícula', 'Fecha Entrada',
                           'Tipo Servicio', 'Total']
            f.write('{:<10} {:<12} {:<15} {:<15} {:<20} {:<10}\n'.format(*encabezados))
            f.write('-' * 90 + '\n')
            for r in filas:
                f.write('{:<10} {:<12} {:<15} {:<15} {:<20} {:<10}\n'.format(
                    str(r.get('folio', '') or ''),
                    str(r.get('cliente_id', '') or ''),
                    str(r.get('matricula', '') or ''),
                    str(r.get('fecha_entrada', '') or ''),
                    str(r.get('tipo_servicio', '') or ''),
                    str(r.get('total_pagar', '') or '')))
            f.write('\n' + '-' * 90 + '\n')
            f.write(f'Total de registros: {len(filas)}\n')
        return ruta