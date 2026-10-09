import getpass
from autenticacion import hash_contrasena
from base_datos import bd


def crear(usuario, nombre, perfil):
    contrasena = getpass.getpass(f'Contraseña para {usuario}: ')
    bd.ejecutar(
        'INSERT INTO usuario (perfil, password, nombre, nombre_usuario, activo) '
        'VALUES (%s, %s, %s, %s, 1)',
        (perfil, hash_contrasena(contrasena), nombre, usuario))
    print(f'Usuario {usuario} creado.')


if __name__ == '__main__':
    crear(input('Usuario administrador [admin]: ') or 'admin',
          input('Nombre [Administrador]: ') or 'Administrador', 1)
    crear(input('Usuario normal [usuario]: ') or 'usuario',
          input('Nombre [Usuario normal]: ') or 'Usuario normal', 2)