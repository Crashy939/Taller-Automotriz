import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# ---------- Paleta ----------
COLOR_PRIMARIO      = "#1E3A8A"   # azul profundo
COLOR_PRIMARIO_HOVER= "#1D4ED8"   # azul hover
COLOR_PRIMARIO_ACT  = "#1E40AF"   # azul pressed
COLOR_ACENTO        = "#0EA5E9"   # azul claro (focus)
COLOR_FONDO         = "#F3F4F6"   # gris muy claro
COLOR_TARJETA       = "#FFFFFF"   # blanco
COLOR_TEXTO         = "#111827"   # gris muy oscuro
COLOR_TEXTO_SUAVE   = "#6B7280"   # gris medio
COLOR_PELIGRO       = "#DC2626"   # rojo (Remover)
COLOR_EXITO         = "#059669"   # verde (Guardar)
COLOR_BORDE         = "#D1D5DB"   # gris borde


def _fuente_familia():
    """Devuelve 'Segoe UI' si existe, si no Helvetica."""
    try:
        familias = set(tkfont.families())
    except Exception:
        return "Helvetica"
    for f in ("Segoe UI", "Inter", "Roboto", "Helvetica Neue", "Helvetica"):
        if f in familias:
            return f
    return "Helvetica"


def aplicar_tema(root):
    """Aplica tema, colores y tipografías a toda la app."""
    familia = _fuente_familia()

    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=COLOR_FONDO)
    root.option_add("*Font", (familia, 10))

    # ----- Frames -----
    estilo.configure("TFrame", background=COLOR_FONDO)
    estilo.configure("Tarjeta.TFrame", background=COLOR_TARJETA)
    estilo.configure("Cabecera.TFrame", background=COLOR_PRIMARIO)

    # ----- Labels -----
    estilo.configure("TLabel",
                     background=COLOR_FONDO,
                     foreground=COLOR_TEXTO,
                     font=(familia, 10))
    estilo.configure("Tarjeta.TLabel",
                     background=COLOR_TARJETA,
                     foreground=COLOR_TEXTO,
                     font=(familia, 10))
    estilo.configure("Suave.TLabel",
                     background=COLOR_TARJETA,
                     foreground=COLOR_TEXTO_SUAVE,
                     font=(familia, 9))
    estilo.configure("Titulo.TLabel",
                     background=COLOR_FONDO,
                     foreground=COLOR_PRIMARIO,
                     font=(familia, 18, "bold"))
    estilo.configure("Subtitulo.TLabel",
                     background=COLOR_FONDO,
                     foreground=COLOR_TEXTO_SUAVE,
                     font=(familia, 11))
    estilo.configure("CabeceraTitulo.TLabel",
                     background=COLOR_PRIMARIO,
                     foreground="#FFFFFF",
                     font=(familia, 14, "bold"))

    # ----- LabelFrame -----
    estilo.configure("TLabelframe",
                     background=COLOR_TARJETA,
                     bordercolor=COLOR_BORDE,
                     relief="solid",
                     borderwidth=1)
    estilo.configure("TLabelframe.Label",
                     background=COLOR_TARJETA,
                     foreground=COLOR_PRIMARIO,
                     font=(familia, 10, "bold"))

    # ----- Entry -----
    estilo.configure("TEntry",
                     fieldbackground="#FFFFFF",
                     bordercolor=COLOR_BORDE,
                     lightcolor=COLOR_ACENTO,
                     darkcolor=COLOR_BORDE,
                     padding=6)
    estilo.map("TEntry",
               bordercolor=[("focus", COLOR_ACENTO)],
               lightcolor=[("focus", COLOR_ACENTO)])

    # ----- Combobox -----
    estilo.configure("TCombobox",
                     fieldbackground="#FFFFFF",
                     bordercolor=COLOR_BORDE,
                     padding=5)
    estilo.map("TCombobox",
               fieldbackground=[("readonly", "#FFFFFF")],
               bordercolor=[("focus", COLOR_ACENTO)])

    # ----- Botones (por defecto) -----
    estilo.configure("TButton",
                     background=COLOR_PRIMARIO,
                     foreground="#FFFFFF",
                     focuscolor=COLOR_PRIMARIO,
                     borderwidth=0,
                     padding=(14, 8),
                     font=(familia, 10, "bold"))
    estilo.map("TButton",
               background=[("disabled", "#9CA3AF"),
                           ("pressed",  COLOR_PRIMARIO_ACT),
                           ("active",   COLOR_PRIMARIO_HOVER)],
               foreground=[("disabled", "#F3F4F6")])

    # ----- Botones con variantes de color -----
    estilo.configure("Exito.TButton",
                     background=COLOR_EXITO, foreground="#FFFFFF")
    estilo.map("Exito.TButton",
               background=[("disabled", "#9CA3AF"),
                           ("pressed", "#047857"),
                           ("active",  "#10B981")])

    estilo.configure("Peligro.TButton",
                     background=COLOR_PELIGRO, foreground="#FFFFFF")
    estilo.map("Peligro.TButton",
               background=[("disabled", "#9CA3AF"),
                           ("pressed", "#B91C1C"),
                           ("active",  "#EF4444")])

    estilo.configure("Secundario.TButton",
                     background="#E5E7EB", foreground=COLOR_TEXTO)
    estilo.map("Secundario.TButton",
               background=[("disabled", "#F3F4F6"),
                           ("pressed", "#D1D5DB"),
                           ("active",  "#E5E7EB")])

    # ----- Treeview -----
    estilo.configure("Treeview",
                     background="#FFFFFF",
                     fieldbackground="#FFFFFF",
                     foreground=COLOR_TEXTO,
                     rowheight=26,
                     bordercolor=COLOR_BORDE,
                     borderwidth=1)
    estilo.configure("Treeview.Heading",
                     background=COLOR_PRIMARIO,
                     foreground="#FFFFFF",
                     font=(familia, 10, "bold"),
                     relief="flat",
                     padding=(6, 6))
    estilo.map("Treeview.Heading", background=[("active", COLOR_PRIMARIO_HOVER)])
    estilo.map("Treeview",
               background=[("selected", COLOR_PRIMARIO)],
               foreground=[("selected", "#FFFFFF")])

    # ----- Menú (MenuButton y Menu) -----
    estilo.configure("TMenubutton",
                     background=COLOR_PRIMARIO,
                     foreground="#FFFFFF",
                     font=(familia, 10, "bold"),
                     padding=(16, 10),
                     borderwidth=0)
    estilo.map("TMenubutton",
               background=[("active", COLOR_PRIMARIO_HOVER)])

    root.option_add("*Menu.background", "#FFFFFF")
    root.option_add("*Menu.foreground", COLOR_TEXTO)
    root.option_add("*Menu.activeBackground", COLOR_PRIMARIO)
    root.option_add("*Menu.activeForeground", "#FFFFFF")
    root.option_add("*Menu.font", (familia, 10))
    root.option_add("*Menu.relief", "flat")
    root.option_add("*Menu.borderWidth", 0)


def centrar_ventana(ventana, ancho, alto):
    """Centra una ventana Toplevel en la pantalla."""
    ventana.update_idletasks()
    pantalla_w = ventana.winfo_screenwidth()
    pantalla_h = ventana.winfo_screenheight()
    x = (pantalla_w - ancho) // 2
    y = (pantalla_h - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


class VentanaModal(tk.Toplevel):
    """Toplevel con estilo base (fondo, título, tamaño centrado)."""
    def __init__(self, parent, titulo, ancho, alto, modal=True):
        super().__init__(parent)
        self.title(titulo)
        self.configure(bg=COLOR_FONDO)
        centrar_ventana(self, ancho, alto)
        self.minsize(ancho, alto)
        if modal:
            self.transient(parent)
            self.grab_set()