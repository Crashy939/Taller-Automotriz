import os

CONFIG_BD = {
    "host": os.getenv("TALLER_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("TALLER_DB_PORT", "3306")),
    "user": os.getenv("TALLER_DB_USER", "root"),
    "password": os.getenv("TALLER_DB_PASSWORD", ""),
    "database": os.getenv("TALLER_DB_NAME", "taller_automotriz"),
}

TITULO_APP = "Control de Taller Automotriz"