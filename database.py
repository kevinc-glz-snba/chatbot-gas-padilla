import sqlite3
from datetime import datetime 

#Variables globales para no tener que cambiar valor en cada consulta
t20 = 28
t30 = 56

#coneccion o creacion de db
def get_connection():
    return sqlite3.connect("gaspadilla.db")

#Creacion de tablas
def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    #Tabla precio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precio (
            id INTEGER PRIMARY KEY,
            cantidad TEXT,
            valor REAL
        )
    """)

    #Tabla pedidos 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            direccion TEXT,
            cantidad REAL,
            telefono TEXT,
            fecha DATE
        )
    """)
    
    #Tabla tanques 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tanques (
            id INTEGER PRIMARY KEY,
            tanque REAL,
            litros REAL,
            precio REAL
        )
    """)

    #Tabla para historial de mensajes 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY,
            telefono TEXT,
            role TEXT,
            mensaje TEXT,
            fecha DATE
        )
    """)
    conn.commit()
    conn.close()

#Incertamos los datos base de los tanques
def insertar_tanques_iniciales():
    conn = get_connection()
    cursor = conn.cursor()

    #Verificar que no existan para evitar duplicados
    cursor.execute("SELECT COUNT(*) FROM tanques")
    if cursor.fetchone()[0] == 0:
        cursor.execute(f"""
            INSERT INTO tanques (id, tanque, litros, precio) VALUES (1,20,{t20},0)
        """)
        cursor.execute(f"""
            INSERT INTO tanques (id, tanque, litros, precio) VALUES (2,30,{t30},0);
        """)
    conn.commit()
    conn.close()

#FUNCIONES GET 
#Funcion para obtener historial
def obtener_historial(telefono):
    conn = get_connection()
    cursor = conn.cursor()
    sql_get = """SELECT * FROM conversaciones WHERE telefono = ?"""

    try:
        cursor.execute(sql_get, (telefono,))
        mensajes = cursor.fetchall()
        return mensajes
    except sqlite3.Error as e:
        print(f"Error al obtener el historial de mensajes: {e}")
    finally:
        conn.close()

def obtener_precios():
    conn = get_connection()
    cursor = conn.cursor()
    resultado = "Precios no disponibles"
    
    try:
        cursor.execute("""SELECT * FROM precio""")
        precios = cursor.fetchall()
        
        cursor.execute("""SELECT * FROM tanques""")
        tanques = cursor.fetchall()

        #Se retornan listas de tuplas
        lineas = []
        if precios:
            lineas.append(f"Precio por litro: ${precios[0][2]}")
        
        for tanque in tanques:
            lineas.append(f"Tanque {tanque[1]}kg ({tanque[2]} litros): ${tanque[3]}")
        
        resultado = "\n".join(lineas)
    except sqlite3.Error as e:
        print (f"Error obteniendo los precios: {e}")
    finally:
        conn.close()
    
    return resultado


#FUNCIONES INSERT O POST 
#Funcion para guardar mensajes en la bd
def guardar_mensajes(telefono, role, mensaje):
    conn = get_connection()
    cursor = conn.cursor()
    fecha_actual = datetime.now()
    sql_insert = """INSERT INTO conversaciones (telefono, role, mensaje, fecha) VALUES (?, ?, ?, ?)"""

    try:
        cursor.execute(sql_insert, (telefono,role, mensaje, fecha_actual))
        conn.commit()
        print("El registro del mensaje a sido un exito")
    except sqlite3.Error as e:
        print(f"Ërror al insertar datos: {e}")
    finally:
        conn.close()

#Funcion para registrar pedidos
def registrar_pedido(nombre, direccion,cantidad,telefono):
    conn = get_connection()
    cursor = conn.cursor()
    fecha = datetime.now()
    sql_insert = "INSERT INTO pedidos (nombre, direccion, cantidad, telefono, fecha ) VALUES (?, ?, ?, ?, ?)"

    try:
        cursor.execute(sql_insert, (nombre, direccion, cantidad, telefono, fecha))
        conn.commit()
        print("Se hizo el registro del pedido en la BD cone exito")
    except sqlite3.Error as e:
        print(f"Error al registrar el pedido en la BD: {e}")
    finally:
        conn.close()

#FUNCIONES PARA ACTUALIZAR VALORES

#Actualizar precios
def actualizar_precio(valor: float):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM precio")
    if cursor.fetchone()[0] == 0:
        sql_insert = f"INSERT INTO precio (cantidad, valor) VALUES ('litro' , ?)"
        cursor.execute(sql_insert, (valor,))
    else:
        cursor.execute(f"UPDATE precio SET  valor = ? WHERE id = 1", (valor,))
    
    cursor.execute(f"UPDATE tanques SET precio = ? WHERE tanque = 20 ", (t20 * valor,))
    cursor.execute(f"UPDATE tanques SET precio = ? WHERE tanque = 30 ", (t30 * valor,))
    
    conn.commit()
    conn.close()
