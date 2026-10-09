import bcrypt
from base_datos import bd


def autenticar(usuario, contrasena):
    fila = bd.obtener_uno(
        "SELECT * FROM usuario WHERE nombre_usuario=%s AND activo=1", (usuario,)
    )
    if fila and bcrypt.checkpw(contrasena.encode(), fila["password"].encode()):
        return fila
    return None


def hash_contrasena(contrasena):
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()