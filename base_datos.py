import mysql.connector
from configuracion import CONFIG_BD


class BaseDatos:
    def conectar(self):
        return mysql.connector.connect(**CONFIG_BD)

    def obtener_uno(self, consulta, params=()):
        conn = self.conectar()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(consulta, params)
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def obtener_todos(self, consulta, params=()):
        conn = self.conectar()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(consulta, params)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def ejecutar(self, consulta, params=()):
        conn = self.conectar()
        cur = conn.cursor()
        try:
            cur.execute(consulta, params)
            conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def transaccion(self, sentencias):
        conn = self.conectar()
        cur = conn.cursor()
        try:
            for consulta, params in sentencias:
                cur.execute(consulta, params)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()


bd = BaseDatos()