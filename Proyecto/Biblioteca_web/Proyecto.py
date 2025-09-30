import sqlite3 as sqlite
from datetime import datetime, timedelta
import re
import csv
from fuzzywuzzy import fuzz
import os
import hashlib 

# Usar ruta absoluta para la base de datos
archivo_base_datos = os.path.join(os.path.dirname(__file__), 'base_datos.db')

# =========================================
#   CONFIGURACIÓN Y UTILIDADES GENERALES
# =========================================

# --- Bases de Datos --- #


def conectar_base_datos():
    return sqlite.connect(archivo_base_datos)

def actualizar_estructura_base_datos():
    """Actualiza la estructura de la base de datos existente"""
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna password existe
        cursor.execute("PRAGMA table_info(Usuario)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'password' not in columnas:
            print("Agregando columna 'password' a la tabla Usuario...")
            cursor.execute("ALTER TABLE Usuario ADD COLUMN password TEXT")
            
        if 'email' not in columnas:
            print("Agregando columna 'email' a la tabla Usuario...")
            cursor.execute("ALTER TABLE Usuario ADD COLUMN email TEXT")
            
        # Verificar si la columna rol existe y es correcta
        if 'rol' not in columnas:
            print("Agregando columna 'rol' a la tabla Usuario...")
            cursor.execute("ALTER TABLE Usuario ADD COLUMN rol TEXT DEFAULT 'usuario'")
        
        conn.commit()
        print("Estructura de base de datos actualizada correctamente.")
        
    except Exception as e:
        print(f"Error actualizando estructura: {e}")
    finally:
        conn.close()

def verificar_consistencia_libros():
    """
    Verifica y corrige automáticamente la consistencia entre el estado 'disponible' 
    de los libros y la existencia de préstamos activos.
    """
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    # Obtener todos los libros con sus estados de préstamo
    cursor.execute("""
        SELECT l.id_libro, l.titulo, l.disponible,
               COUNT(CASE WHEN p.fecha_devolucion_real IS NULL THEN 1 END) as prestamos_activos
        FROM Libro l
        LEFT JOIN Prestamo p ON l.id_libro = p.id_libro
        GROUP BY l.id_libro, l.titulo, l.disponible
    """)
    
    libros = cursor.fetchall()
    inconsistencias = []
    
    for libro in libros:
        id_libro, titulo, disponible, prestamos_activos = libro
        
        # Caso 1: Libro marcado como disponible pero tiene préstamos activos
        if disponible and prestamos_activos > 0:
            cursor.execute("UPDATE Libro SET disponible = 0 WHERE id_libro = ?", (id_libro,))
            inconsistencias.append(f"Libro '{titulo}' (ID: {id_libro}) tenía préstamos activos pero estaba marcado como disponible. Corregido.")
        
        # Caso 2: Libro marcado como no disponible pero no tiene préstamos activos
        elif not disponible and prestamos_activos == 0:
            cursor.execute("UPDATE Libro SET disponible = 1 WHERE id_libro = ?", (id_libro,))
            inconsistencias.append(f"Libro '{titulo}' (ID: {id_libro}) no tenía préstamos activos pero estaba marcado como no disponible. Corregido.")
    
    conn.commit()
    conn.close()
    
    return inconsistencias

def crear_tablas():
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Libro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_libro INTEGER, 
            imagen BLOB,
            titulo TEXT,
            autor TEXT,
            editorial TEXT,
            año INTEGER,
            genero TEXT,
            disponible BOOLEAN
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido TEXT,
            documento TEXT UNIQUE,
            telefono TEXT,
            email TEXT UNIQUE,
            password TEXT,
            rol TEXT DEFAULT 'usuario'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Prestamo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_libro INTEGER,
            documento_usuario TEXT,
            fecha_prestamo TEXT,
            fecha_devolucion_esperada TEXT,
            fecha_devolucion_real TEXT,
            multa REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# crear_tablas() # Ya se ejecuta desde app.py

# =========================================
#   CLASES PRINCIPALES: Libro, Usuario, Prestamo
# =========================================

# --- Clases --- #

class Libro:
    def __init__(self, id_libro, titulo, autor, editorial, año, genero, imagen, disponible=True, id=None):
        self.id = id
        self.id_libro = id_libro
        self.imagen = imagen
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.año = año
        self.genero = genero
        self.disponible = disponible
    
    def guardar(self):
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Libro (id_libro, titulo, imagen, autor, editorial, año, genero, disponible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.id_libro, self.titulo, self.imagen, self.autor, self.editorial, self.año, self.genero, self.disponible))
        conn.commit()
        conn.close()
    
    def obtener_imagen_base64(self):
        """Devuelve la imagen en formato base64 para mostrar en HTML"""
        if not self.imagen:
            return None
        
        import base64

        imagen_base64  = base64.b64encode(self.imagen).decode('utf-8')

        if self.imagen.startswith(b'\xFF\xD8\xFF'):
            mime_type = 'image/jpeg'
        elif self.imagen.startswith(b'\x89PNG\x0A'):
            mime_type = 'image/png'
        elif self.imagen.startswith(b'GIF87a') or self.imagen.startswith(b'GIF89a'):
            mime_type = 'image/gif'
        else:
            mime_type = 'image/jpeg'
         
        return f'data:{mime_type};base64,{imagen_base64}'   
    
    @staticmethod
    def obtener_todos():
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Libro')
        filas = cursor.fetchall()
        conn.close()
        return [Libro(id=f[0], id_libro=f[1], titulo=f[2], autor=f[3], editorial=f[4], año=f[5], genero=f[6], disponible=bool(f[7]), imagen=f[8]) for f in filas]
    
    @staticmethod
    def buscar_por_termino(termino):
        """Busca libros por ID, título, autor o género"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        # Intentar convertir el término a número para buscar por ID
        try:
            id_libro = int(termino)
            cursor.execute('''
                SELECT * FROM Libro 
                WHERE id_libro = ? 
                OR titulo LIKE ? 
                OR autor LIKE ? 
                OR genero LIKE ?
            ''', (id_libro, f'%{termino}%', f'%{termino}%', f'%{termino}%'))
        except ValueError:
            # Si no es número, buscar solo por texto
            cursor.execute('''
                SELECT * FROM Libro 
                WHERE titulo LIKE ? 
                OR autor LIKE ? 
                OR genero LIKE ?
            ''', (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
        
        filas = cursor.fetchall()
        conn.close()
        return [Libro(id=f[0], id_libro=f[1], titulo=f[2], autor=f[3], editorial=f[4], año=f[5], genero=f[6], disponible=bool(f[7]), imagen=f[8]) for f in filas]

    @staticmethod
    def obtener_por_id(id_libro):
        """Obtiene un libro específico por su ID"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Libro WHERE id_libro = ?', (id_libro,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Libro(id=fila[0], id_libro=fila[1], titulo=fila[2], imagen=fila[3], autor=fila[4], editorial=fila[5], año=fila[6], genero=fila[7], disponible=bool(fila[8]))
        return None

class Usuario:
    def __init__(self, nombre, apellido, documento, telefono, email, rol="usuario", password=None, id=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.documento = documento
        self.telefono = telefono
        self.email = email
        self.rol = rol 
        self.password = password

    def _hash_password(self, password):
        """Hashea la contraseña para almacenarla de forma segura"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def set_password(self, password):
       """Establece la contraseña hasheada"""
       self.password = self._hash_password(password)
    
    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return self.password == self._hash_password(password)

    def guardar(self):
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Usuario (nombre, apellido, documento, telefono, email, password, rol)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.nombre, self.apellido, self.documento, self.telefono, self.email, self.password, self.rol))
        conn.commit()
        conn.close()

    def verificar_contraseña(self, password):
        """Alias para check_password (compatibilidad)"""
        return self.check_password(password)
    
    @staticmethod
    def obtener_por_email(email):
        """Obtiene un usuario específico por su email"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE email = ?', (email,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Usuario(id=fila[0], nombre=fila[1], apellido=fila[2], documento=fila[3], telefono=fila[4], email=fila[5], rol=fila[6], password=fila[7] if len(fila) > 7 else None)
        return None

    @staticmethod
    def obtener_todos():
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario')
        filas = cursor.fetchall()
        conn.close()
        usuarios = []
        for f in filas:
            usuario = Usuario(
                id=f[0], nombre=f[1], apellido=f[2], documento=f[3],
                telefono=f[4], email=f[5] if len(f) > 5 else None,
                rol=f[6] if len(f) > 6 else "usuario",
                password=f[7] if len(f) > 7 else None
            )
            usuarios.append(usuario)
        return usuarios
    
    @staticmethod
    def buscar_por_documento_o_nombre(termino):
        """Busca usuarios por documento o nombre (nombre + apellido)"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Usuario 
            WHERE documento LIKE ? 
            OR (nombre || ' ' || apellido) LIKE ?
            OR nombre LIKE ?
            OR apellido LIKE ?
        ''', (f'%{termino}%', f'%{termino}%', f'%{termino}%', f'%{termino}%'))
        filas = cursor.fetchall()
        conn.close()
        usuarios = []
        for f in filas:
            usuario = Usuario(
                id=f[0], nombre=f[1], apellido=f[2], documento=f[3],
                telefono=f[4], email=f[5] if len(f) > 5 else None,
                rol=f[6] if len(f) > 6 else "usuario",
                password=f[7] if len(f) > 7 else None
            )
            usuarios.append(usuario)
        return usuarios
    
    @staticmethod
    def obtener_por_documento(documento):
        """Obtiene un usuario específico por su documento"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE documento = ?', (documento,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Usuario(
                id=fila[0], nombre=fila[1], apellido=fila[2], documento=fila[3],
                telefono=fila[4], email=fila[5] if len(fila) > 5 else None,
                rol=fila[6] if len(fila) > 6 else "usuario",
                password=fila[7] if len(fila) > 7 else None
            )
        return None

class Prestamo:
    def __init__(self, id_libro, documento_usuario, fecha_prestamo, fecha_devolucion_esperada, fecha_devolucion_real=None, multa=0, id=None):
        self.id = id
        self.id_libro = id_libro
        self.documento_usuario = documento_usuario
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion_esperada = fecha_devolucion_esperada
        self.fecha_devolucion_real = fecha_devolucion_real
        self.multa = multa
    
    def guardar(self):
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Prestamo (id_libro, documento_usuario, fecha_prestamo, fecha_devolucion_esperada, fecha_devolucion_real, multa)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.id_libro, self.documento_usuario, self.fecha_prestamo, self.fecha_devolucion_esperada, self.fecha_devolucion_real, self.multa))
        conn.commit()
        conn.close()
    
    @staticmethod
    def pagar_multas_por_usuario(documento):
        """Marca todas las multas de un usuario como pagadas (establece multa a 0)"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Prestamo
            SET multa = 0
            WHERE documento_usuario = ? AND multa > 0
        ''', (documento,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def pagar_multas_por_id(id_prestamo):
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('Update Prestamo SET multa = 0 WHERE id = ?', (id_prestamo,))
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_todos():
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Prestamo')
        filas = cursor.fetchall()
        conn.close()
        return [Prestamo(id=f[0], id_libro=f[1], documento_usuario=f[2], fecha_prestamo=f[3], fecha_devolucion_esperada=f[4], fecha_devolucion_real=f[5], multa=f[6]) for f in filas]
    
    @staticmethod
    def obtener_prestamos_activos_por_usuario(documento):
        """Obtiene todos los préstamos activos de un usuario específico"""
        conn = conectar_base_datos()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, l.titulo, l.autor, u.nombre, u.apellido
            FROM Prestamo p
            JOIN Libro l ON p.id_libro = l.id_libro
            JOIN Usuario u ON p.documento_usuario = u.documento
            WHERE p.documento_usuario = ? AND p.fecha_devolucion_real IS NULL
        ''', (documento,))
        filas = cursor.fetchall()
        conn.close()
        
        prestamos = []
        for f in filas:
            prestamo = Prestamo(id=f[0], id_libro=f[1], documento_usuario=f[2], 
                              fecha_prestamo=f[3], fecha_devolucion_esperada=f[4], 
                              fecha_devolucion_real=f[5], multa=f[6])
            prestamo.titulo_libro = f[7]
            prestamo.autor_libro = f[8]
            prestamo.nombre_usuario = f[9]
            prestamo.apellido_usuario = f[10]
            prestamos.append(prestamo)
        return prestamos

# =========================================
#   CRUD DE LIBROS
# =========================================

# --- CRUD Libros --- #
def agregar_libro():
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id_libro) FROM Libro")
    max_id = cursor.fetchone()[0]
    nuevo_id = (max_id or 0) + 1
    
    titulo = input("Ingrese el titulo del libro: ").strip()
    if not titulo:
        print("El titulo no puede estar vacio.")
        conn.close()
        return
    
    imagen = input("Ingrese la ruta de la imagen del libro (o deje en blanco para omitir): ").strip()
    
    imagen_bytes = None
    if imagen and os.path.isfile(imagen):
        try:
            with open(imagen , 'rb') as archivo_imagen:
                imagen_bytes = archivo_imagen.read() 
                print("Imagen cargada correctamente.")
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
    elif imagen:
        print("La ruta de la imagen no es valida. Continuando sin imagen.")
    
    autor = input("Ingrese el nombre del autor: ")
    
    while True:
        editorial = input("Ingrese la editorial del libro: ").strip()
        if editorial:
            break
        else:
            print("La editorial no puede estar vacia")
                
    
    while True:
        try:
            año = int(input("Ingrese el año del libro: "))
            año_actual = datetime.now().year
            if 0 <= año <= año_actual:
                break
            else:
                print(f"Por favor ingrese un año entre 0 y el {año_actual}")
        except ValueError:
            print("Por favor ingrese un numero valido paras el año.")
    
    genero_valido = ["Ficción", "No ficción", "Misterio", "Ciencia ficción", "Fantasía",
    "Romance", "Terror", "Aventura", "Histórica", "Biografía",
    "Autoayuda", "Poesía", "Clásicos", "Thriller", "Juvenil",
    "Infantil", "Ensayo", "Crimen", "Distopía", "Realismo mágico"]
    
    while True:
            genero = input("Ingrese el genero del libro: ").strip()
            if genero in genero_valido:
                break
            else:
                (f"Genero invalido. Opciones validas {','.join(genero_valido)}")
                
    libro = Libro(id_libro=nuevo_id, titulo=titulo, autor=autor, editorial=editorial, año=año, genero=genero, imagen=imagen_bytes, disponible=True)
    libro.guardar()
    print(f"Libro '{titulo}' agregado con ID {nuevo_id}.")

def eliminar_libro(id_libro):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, disponible FROM Libro WHERE id_libro=?", (id_libro,))
    fila = cursor.fetchone()
    
    if not fila:
        print("Libro no encontrado.")
        return {"success": False, "message": "Libro no encontrado."}
    
    # Verificar si hay préstamos activos reales
    cursor.execute("SELECT COUNT(*) FROM Prestamo WHERE id_libro=? AND fecha_devolucion_real IS NULL", (id_libro,))
    prestamos_activos = cursor.fetchone()[0]
    
    if prestamos_activos > 0:
        cursor.execute("""
            SELECT u.nombre, u.apellido, p.fecha_prestamo 
            FROM Prestamo p 
            JOIN Usuario u ON p.id_usuario = u.id_persona 
            WHERE p.id_libro=? AND p.fecha_devolucion_real IS NULL
        """, (id_libro,))
        prestamo_info = cursor.fetchone()
        mensaje = f"No se puede eliminar. El libro está prestado a {prestamo_info[0]} {prestamo_info[1]} desde {prestamo_info[2]}."
        conn.close()
        return {"success": False, "message": mensaje}
    
    # Si no hay préstamos activos pero está marcado como no disponible, corregir el estado
    if not fila[2]:  # disponible = False
        cursor.execute("UPDATE Libro SET disponible = 1 WHERE id_libro=?", (id_libro,))
        print(f"Corrigiendo estado de disponibilidad para libro ID {id_libro}")
    
    cursor.execute("DELETE FROM Libro WHERE id_libro=?", (id_libro,))
    conn.commit()
    conn.close()
    print(f"Libro con ID {id_libro} eliminado.")
    return {"success": True, "message": f"Libro con ID {id_libro} eliminado correctamente."}

def buscar_libro(criterio,valor,solo_disponibles=True):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    query = f"SELECT * FROM Libro WHERE {criterio} LIKE ?"
    params = (f"%{valor}%",)
    
    if solo_disponibles:
        query += " AND disponible=1"
    
    cursor.execute(query, params)
    filas = cursor.fetchall()
    conn.close()

    resultados = [Libro(id=f[0], id_libro=f[1], titulo=f[2], imagen=[3], autor=f[4], editorial=f[5], año=f[6], genero=f[7], disponible=bool(f[8])) for f in filas]

    if resultados:
        print("Resultados de búsqueda:")
        for i in resultados:
            estado = "Disponible" if i.disponible else "Prestado"
            print(f"- Titulo: {i.titulo} (Autor: {i.autor}, Editorial: {i.editorial}, Año: {i.año}, Estado: {estado})")
    else:
        print("No se encontraron libros con ese criterio.")

def busqueda_rapida_libro(termino):
    libros = Libro.obtener_todos()
    resultados = []
    for libro in libros:
        similitud = fuzz.ratio(termino.lower(), libro.titulo.lower())
        if similitud >= 80:  # Umbral de similitud
            resultados.append((libro, similitud))
    resultados.sort(key=lambda x: x[1], reverse=True)
    for libro, score in resultados:
        print(f"{libro.titulo} ({score}% coincidencia)")

def actualizar_libro(id_libro, **kwargs):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Libro WHERE id_libro=?", (id_libro,))
    fila = cursor.fetchone()
    if not fila:
        print("Libro no encontrado")
        conn.close()
        return
    
    campos = []
    valores = []
    for campo, valor in kwargs.items():
        campos.append(f"{campo}=?")
        valores.append(valor)
    if campos:
        query = f"UPDATE Libro SET {', '.join(campos)} WHERE id_libro=?"
        valores.append(id_libro)
        cursor.execute(query, tuple(valores))
        conn.commit()
        print(f"Libro con ID {id_libro} actualizado")
    else:
        print("No se proporcionaron datos para actualizar el libro.")
    conn.close()

# =========================================
#   CRUD DE USUARIOS
# =========================================

# --- CRUD Usuarios --- #
def agregar_usuario():
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id_persona) FROM Usuario")
    max_id = cursor.fetchone()[0]
    nuevo_id = (max_id or 0) + 1
    
    nombre = input("Ingrese el nombre del usuario: ").strip()
    if not nombre:
        print("El nombre no puede estar vacio.")
        conn.close()
        return
    
    apellido = input("Ingrese el apellido del usuario: ").strip()
    if not apellido:
        print("El apellido no puede estar vacio.")
        conn.close()
        return
    
    while True:
        telefono = input("Ingrese el telefono del usuario: ").strip()
        if telefono.isdigit() and 7 <= len(telefono) <= 15:
            break
        else:
            print("Telefono invalido.Debe tener digitos numericos minimo 7 max 15.")
    
    while True:
        email = input("Ingrese el email del usuario: ").strip()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            break
        else:
            print("Correo invalido, intente nuevamente.")
    
    while True:
        rol_input = input("Selecciones el rol(1: Admin, 2:Normal): ").strip()
        if rol_input == "1":
            rol = "admin"
            break
        elif rol_input == "2":
            rol = "normal"
            break
        else:
            print("Opcion invalida.")
        
    usuario = Usuario(nombre=nombre, apellido=apellido, id_persona=nuevo_id, telefono=telefono, email=email, rol=rol)
    usuario.guardar()
    print(f"Usuario '{nombre} {apellido} {rol}' agregado con ID {nuevo_id}.")

def eliminar_usuario(id_persona):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Usuario WHERE id_persona=?", (id_persona,))
    fila = cursor.fetchone()
    
    if not fila:
        print("Usuario no encontrado.")
        conn.close()
        return
    
    cursor.execute("SELECT COUNT(*) FROM Prestamo WHERE id_usuario=? AND fecha_devolucion_real IS NULL", (id_persona,))
    prestamos_activos = cursor.fetchone()[0]
    if prestamos_activos > 0:
        print("No se puede eliminar un usuario con prestamos activos.")
        conn.close()
        return
    
    cursor.execute("DELETE FROM Usuario WHERE id_persona=?", (id_persona,))
    conn.commit()
    conn.close()
    print(f"Usuario con ID {id_persona} eliminado.")

def eliminar_usuario_por_documento(documento):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Usuario WHERE documento=?", (documento,))
    fila = cursor.fetchone()
    
    if not fila:
        print("Usuario no encontrado.")
        conn.close()
        return False, "Usuario no encontrado."
    
    cursor.execute("SELECT COUNT(*) FROM Prestamo WHERE documento_usuario=? AND fecha_devolucion_real IS NULL", (documento,))
    prestamos_activos = cursor.fetchone()[0]
    if prestamos_activos > 0:
        print("No se puede eliminar un usuario con prestamos activos.")
        conn.close()
        return False, "No se puede eliminar un usuario con prestamos activos."
    
    cursor.execute("DELETE FROM Usuario WHERE documento=?", (documento,))
    conn.commit()
    conn.close()
    print(f"Usuario con documento {documento} eliminado.")
    return True, f"Usuario con documento {documento} eliminado."

def buscar_usuario(criterio, valor):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    # Validar que el criterio sea seguro
    criterios_validos = ["nombre", "apellido", "telefono", "email", "id_persona"]
    if criterio not in criterios_validos:
        print("Criterio de búsqueda inválido.")
        return
    
    try:
        # Primero obtenemos los nombres de las columnas de la tabla Usuario
        cursor.execute("PRAGMA table_info(Usuario)")
        columnas_info = cursor.fetchall()
        columnas = [col[1] for col in columnas_info]  # col[1] es el nombre de la columna

        # Verificar si la columna 'rol' existe
        rol_existe = "rol" in columnas

        # Construir SELECT dinámico según si existe 'rol'
        select_cols = "id, nombre, apellido, id_persona, telefono, email"
        if rol_existe:
            select_cols += ", rol"

        query = f"SELECT {select_cols} FROM Usuario WHERE {criterio} LIKE ?"
        params = (f"%{valor}%",)
        cursor.execute(query, params)
        filas = cursor.fetchall()

    except Exception as e:
        print(f"Error al buscar usuarios: {e}")
        return
    finally:
        conn.close()
    
    # Crear objetos Usuario
    resultados = []
    for f in filas:
        if rol_existe:
            usuario = Usuario(
                nombre=f[1],
                apellido=f[2],
                id_persona=f[3],
                telefono=f[4],
                email=f[5],
                rol=f[6],
                id=f[0]
            )
        else:
            usuario = Usuario(
                nombre=f[1],
                apellido=f[2],
                id_persona=f[3],
                telefono=f[4],
                email=f[5],
                rol="normal",
                id=f[0]
            )
        resultados.append(usuario)
    
    # Mostrar resultados
    if resultados:
        print("Resultados de búsqueda:")
        for u in resultados:
            print(f"- {u.nombre} {u.apellido} ({u.rol}) - ID: {u.id_persona}, Tel: {u.telefono}, Email: {u.email}")
    else:
        print("No se encontraron usuarios con ese criterio.")


def busqueda_rapida_usuario(termino):
    usuario = Usuario.obtener_todos()
    resultados = []
    for usuario in usuario:
        similitud = fuzz.ratio(termino.lower(), usuario.nombre.lower())
        if similitud >= 80:  # Umbral de similitud
            resultados.append((usuario, similitud))
    resultados.sort(key=lambda x: x[1], reverse=True)
    for usuario, score in resultados:
        print(f"{usuario.nombre} ({score}% coincidencia)")

def actualizar_usuario(id_persona, **kwargs):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuario WHERE id_persona=?", (id_persona,))
    fila = cursor.fetchone()
    if not fila:
        print("Usuario no encontrado.")
        conn.close()
        return
    
    campos = []
    valores = []
    for campo, valor in kwargs.items():
        campos.append(f"{campo}=?")
        valores.append(valor)
    if campos:
        query = f"UPDATE Usuario SET {', '.join(campos)} WHERE id_persona=?"
        valores.append(id_persona)
        cursor.execute(query, tuple(valores))
        conn.commit()
        print(f"Usuario con ID {id_persona} actualizado.")
    else:
        print("No se proporcionaron datos para actualizar el usuario.")
    conn.close()

def actualizar_usuario_por_documento(documento, **kwargs):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuario WHERE documento=?", (documento,))
    fila = cursor.fetchone()
    if not fila:
        print("Usuario no encontrado.")
        conn.close()
        return False, "Usuario no encontrado."
    
    campos = []
    valores = []
    for campo, valor in kwargs.items():
        if campo != 'documento':  # No permitir cambiar el documento
            campos.append(f"{campo}=?")
            valores.append(valor)
    
    if campos:
        query = f"UPDATE Usuario SET {', '.join(campos)} WHERE documento=?"
        valores.append(documento)
        cursor.execute(query, tuple(valores))
        conn.commit()
        print(f"Usuario con documento {documento} actualizado.")
        conn.close()
        return True, f"Usuario con documento {documento} actualizado."
    else:
        print("No se proporcionaron datos para actualizar el usuario.")
        conn.close()
        return False, "No se proporcionaron datos para actualizar el usuario."

# =========================================
#   LÓGICA DE PRÉSTAMOS
# =========================================

# --- Lógica de préstamos --- #
def prestar_libro(id_libro, documento_usuario, dias_prestamo):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    # Verificar que el libro existe y obtener información completa
    cursor.execute("SELECT id, titulo, autor, disponible FROM Libro WHERE id_libro=?", (id_libro,))
    libro = cursor.fetchone()
    if not libro:
        conn.close()
        return {"success": False, "message": "Libro no encontrado."}
    
    # Verificar si realmente hay préstamos activos (doble verificación)
    cursor.execute("SELECT COUNT(*) FROM Prestamo WHERE id_libro=? AND fecha_devolucion_real IS NULL", (id_libro,))
    prestamos_activos = cursor.fetchone()[0]
    
    if prestamos_activos > 0:
        # Si hay préstamos activos, obtener información del prestamista actual
        cursor.execute("""
            SELECT u.nombre, u.apellido, p.fecha_devolucion_esperada 
            FROM Prestamo p 
            JOIN Usuario u ON p.documento_usuario = u.documento 
            WHERE p.id_libro=? AND p.fecha_devolucion_real IS NULL
        """, (id_libro,))
        prestamo_info = cursor.fetchone()
        mensaje = f"El libro '{libro[1]}' ya está prestado a {prestamo_info[0]} {prestamo_info[1]} hasta {prestamo_info[2]}."
        conn.close()
        return {"success": False, "message": mensaje}
    
    # Si el libro está marcado como no disponible pero no tiene préstamos, corregir el estado
    if not libro[3]:
        cursor.execute("UPDATE Libro SET disponible = 1 WHERE id_libro=?", (id_libro,))
        print(f"Corrigiendo estado de disponibilidad para libro '{libro[1]}' (ID: {id_libro})")
    
    # Verificar que el usuario existe
    cursor.execute("SELECT id, nombre, apellido FROM Usuario WHERE documento=?", (documento_usuario,))
    usuario = cursor.fetchone()
    if not usuario:
        conn.close()
        return {"success": False, "message": "Usuario no encontrado."}
    
    fecha_prestamo = datetime.now()
    fecha_devolucion_esperada = fecha_prestamo + timedelta(days=dias_prestamo)
    
    prestamo = Prestamo(
        id_libro=id_libro,
        documento_usuario=documento_usuario,
        fecha_prestamo=fecha_prestamo.strftime("%Y-%m-%d"),
        fecha_devolucion_esperada=fecha_devolucion_esperada.strftime("%Y-%m-%d")
    )
    prestamo.guardar()
    
    # Marcar el libro como no disponible
    cursor.execute("UPDATE Libro SET disponible=0 WHERE id_libro=?", (id_libro,))
    conn.commit()
    conn.close()
    
    mensaje = f"Libro '{libro[1]}' prestado a {usuario[1]} {usuario[2]} hasta {fecha_devolucion_esperada.strftime('%Y-%m-%d')}."
    print(mensaje)
    return {"success": True, "message": mensaje}

def devolver_libro(id_prestamo):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    
    # Obtener información completa del préstamo
    cursor.execute("""
        SELECT p.id_libro, p.fecha_devolucion_esperada, p.documento_usuario,
               l.titulo, u.nombre, u.apellido
        FROM Prestamo p
        JOIN Libro l ON p.id_libro = l.id_libro
        JOIN Usuario u ON p.documento_usuario = u.documento
        WHERE p.id=? AND p.fecha_devolucion_real IS NULL
    """, (id_prestamo,))
    fila = cursor.fetchone()
    
    if not fila:
        conn.close()
        return {"success": False, "message": "Préstamo no encontrado o ya devuelto."}
    
    id_libro, fecha_devolucion_esperada, documento_usuario, titulo, nombre, apellido = fila
    fecha_real = datetime.now()
    
    # Calcular multa por retraso
    multa = 0
    fecha_esperada = datetime.strptime(fecha_devolucion_esperada, "%Y-%m-%d")
    if fecha_real > fecha_esperada:
        dias_retraso = (fecha_real - fecha_esperada).days
        multa = dias_retraso * 1
    
    # Actualizar el préstamo como devuelto
    cursor.execute("UPDATE Prestamo SET fecha_devolucion_real=?, multa=? WHERE id=?", 
                   (fecha_real.strftime("%Y-%m-%d"), multa, id_prestamo))
    
    # Marcar el libro como disponible nuevamente
    cursor.execute("UPDATE Libro SET disponible=1 WHERE id_libro=?", (id_libro,))
    
    conn.commit()
    conn.close()
    
    mensaje_multa = f" Multa: ${multa}." if multa > 0 else " Sin multa."
    mensaje = f"Libro '{titulo}' devuelto por {nombre} {apellido}.{mensaje_multa}"
    print(mensaje)
    return {"success": True, "message": mensaje, "multa": multa}

# =========================================
#   CONSULTAS DE PRÉSTAMOS DE USUARIO
# =========================================

# --- Consultar préstamos de un usuario --- #
def obtener_prestamos_usuario(id_usuario):
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Prestamo WHERE id_usuario=?", (id_usuario,))
    filas = cursor.fetchall()
    conn.close()
    
    prestamos = [Prestamo(id=f[0], id_libro=f[1], id_usuario=f[2], fecha_prestamo=f[3], fecha_devolucion_esperada=f[4], fecha_devolucion_real=f[5], multa=f[6]) for f in filas]
    
    if prestamos:
        print(f"Préstamos del usuario {id_usuario}:")
        for p in prestamos:
            estado = "Devuelto" if p.fecha_devolucion_real else "Pendiente"
            print(f"- Libro {p.id_libro}, Prestado el {p.fecha_prestamo}, Esperado {p.fecha_devolucion_esperada}, Estado: {estado}, Multa: ${p.multa}")
    else:
        print("El usuario no tiene préstamos registrados.")
    
    print("Estadisticas por genero: ")
    reporte_estadisticas_por_genero()
# =========================================
#   FUNCIONES DE REPORTES
# =========================================

# ------------------ FUNCIONES DE REPORTES ------------------ #
def reporte_total_prestados():
    """
    Retorna (imprime) número total de préstamos y número total de préstamos activos.
    """
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT (*) FROM Prestamo")
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT (*) FROM Prestamo WHERE fecha_devolucion_real IS NULL")
    activos = cursor.fetchone()[0] or 0

    conn.close()
    print(f"Total de prestamos es: {total}")
    print(f"Prestamos actualmente activos: {activos}")

def reporte_usuarios_con_multas():
    """
    Muestra usuarios que deben multas (sumadas), ordenado por mayor deuda.
    """
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id_persona, u.nombre, u.apellido, SUM(p.multa) as total_multa
        FROM Prestamo p
        JOIN Usuario u ON p.id_usuario = u.id_persona
        WHERE p.multa > 0
        GROUP BY p.id_usuario
        ORDER BY total_multa DESC
    ''')

    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print("No hay usuarios con multas registradas")
        return

    print("Usuarios con multas registradas: ")
    for f in filas:
        id_persona, nombre, apellido, total_multa = f
        print(f"- {nombre} {apellido} (ID{id_persona}) -> Multa total: ${total_multa:.2f}")

def reporte_estadisticas_por_genero():
    """
    Muestra el número total de libros por género y cuántos de ellos están prestados ahora. 
    """
    conn = conectar_base_datos()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            l.genero,
            COUNT (*) as total_libros,
            SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) as prestados_activos
        FROM Libro l
        LEFT JOIN(
            SELECT id, id_libro FROM Prestamo WHERE fecha_devolucion_real IS NULL
        ) p ON l.id_libro = p.id_libro
        GROUP BY l.genero
    ''')
    
    filas = cursor.fetchall()
    conn.close()
    
    if not filas:
        print("No hay datos de libros para mostrar estadisticas.")
        return
    
    print("Estadisticas por genero: ")
    for genero, total_libros, prestados_activos in filas:
        genero_str = genero if genero else "Sin género"
        prestados_activos = prestados_activos or 0
        print(f"- {genero_str}: {total_libros} libros, {prestados_activos} prestados actualmente")

def exportar_csv():
    libros = Libro.obtener_todos()
    with open("bilbioteca.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["ID", "Titulo", "Autor", "Editoria", "Año", "Genero", "Disponible"])
        for libro in libros:
            escritor.writerow([
                libro.id, libro.titulo, libro.autor, libro.editorial, libro.año, libro.genero, "Sí" if libro.disponible else "No" 
            ])
    print("Archivo biblioteca.csv generado correctamente")

# =========================================
#   FUNCIONES DE LOGS
# =========================================

# ------------------ FUNCIONES DE LOGS ------------------ #
def registrar_log(tipo_operacion, detalles):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open ("biblioteca.log", "a", encoding = "utf-8") as log:
        log.write(f"[{fecha}] [{tipo_operacion}]: {detalles}\n")

def mostrar_log():
    try:
        with open("biblioteca.log", "r", encoding ="utf-8") as log:
            print(log.read())
    except FileNotFoundError:
        print("No hay registro aun")

# =========================================
#   MENÚS DE CONSOLA (LEGADO)
# =========================================

# --- Menu Principal ---#

def Menu_principal():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Gestión de Libros")
        print("2. Gestión de Usuarios")
        print("3. Gestión de Préstamos")
        print("4. Reportes")
        print("5. Salir")
        opcion = input("Seleccione una opcion: ")
        
        if opcion =="1":
            Menu_Libros()
        elif opcion =="2":
            Menu_Usuarios()
        elif opcion == "3":
            Menu_Prestamos()
        elif opcion == "4":
            print("Saliendo...Hasta Luego")
            break
        else:
            print("Opcion no valida.")    

def Menu_Libros(): 
    while True:
        print("\n--- Gestion de Libros ---")
        print("1. Agregar Libros.")
        print("2. Actualizar Libros.")
        print("3. Eliminar Libros.")
        print("4. Buscar Libros.") 
        print("5. Busqueda rapida.")
        print("6. Lista de todos los Libros.")
        print("7. Volver al menu principal.")
        opcion = input("selecione una opcion: ").strip()
        
        if opcion == "1":
            agregar_libro()
        elif opcion == "2":
            try:
                id_libro = int(input("ID (id_libro) del libro a actualizar: ").strip())
            except ValueError:
                print("El ID no es valido.")
                continue
            #Pedir campos opcionales, si estan vacios ignoramos
            
            kwargs = {}
            nuevo_titulo = input("Nuevo titulo(enter para saltar): ").strip()
            if nuevo_titulo:
                kwargs ["titulo"] = nuevo_titulo
            
            nuevo_autor = input("Nuevo autor(enter para saltar): ").strip()
            if nuevo_autor:
                kwargs["autor"] = nuevo_autor
                
            nueva_editorial = input("Nueva editorial(enter para saltar): ").strip()
            if nueva_editorial:
                kwargs["editorial"] = nueva_editorial
                
            nuevo_año = input("Nuevo año(enter para saltar): ").strip()
            if nuevo_año:
                kwargs["año"] = nuevo_año
            
            nuevo_genero = input("Nuevo genero(enter para saltar): ").strip()
            if nuevo_genero:
                kwargs["genero"] = nuevo_genero
            
            disponible_input = input("Disponible? (s/n, enter para no cambiar): ").strip().lower()
            if disponible_input == "s":
                kwargs["disponible"] = 1
            elif disponible_input == "n":
                kwargs["disponible"] = 0
                
            if kwargs:
                actualizar_libro(id_libro, **kwargs)
            else:
                print("No se proporcionaron cambios:")
        
        elif opcion == "3":
            try:
                id_libro = int(input("ID (id_libro) del libro a eliminar.")).strip()
            except ValueError:
                print("ID invalido.")
                continue
            confirmar = input(f"Confirmar eliminar {id_libro}? (s/n): ").strip().lower()
            if confirmar == "s":
                eliminar_libro(id_libro)
            
        
        elif opcion == "4":
            criterio = input("Buscar por (titulo/autor/genero): ").strip()
            valor = input("Texto de busqueda: ").strip()
            solo_disp = input ("Solo disponibles? (s/n): ").strip().lower() == "s"
            buscar_libro(criterio, valor, solo_disponibles = solo_disp)
            
        elif opcion == "5":
            
            termino = input("Ingrese la palabra clave con la que quiere buscar:")
            busqueda_rapida_libro(termino)    
            
        elif opcion == "6":
            libros = Libro.obtener_todos()
            if not libros:
                print("No hay Libros registrados.")
            else:
                for l in libros:
                    estado = "Disponible" if l.disponible else "Prestado"
                    año_str = f"{l.año}" if l.año is not None else "N/A"
                    print(f"[{l.id_libro}] {l.titulo} - {l.autor} - {l.editorial} - {año_str} - {l.genero} - {estado}")
                    
        elif opcion == "7":
            break
        
        else:
            print("Opcion no valida.")

def Menu_Usuarios():
    while True:
        print("\n--- Gestión de Usuarios ---")
        print("1. Agregar usuario")
        print("2. Actualizar usuario")
        print("3. Eliminar usuario")
        print("4. Buscar usuario")
        print("5. Busqueda rapida.")
        print("6. Ver préstamos de un usuario")
        print("7. Volver")
        op = input("Seleccione: ").strip()
        
        if op == "1":
            agregar_usuario()
        elif op == "2":
            try:
                id_persona = int(input("ID (id_persona) del usuario a actualizar: ").strip())
            except ValueError:
                ("ID invalido.")
                continue
            
            kwargs = {}
            
            nuevo_nombre = input("Nuevo nombre(enter para saltar): ").strip()
            if nuevo_nombre:
                kwargs["nombre"] = nuevo_nombre
                
            nuevo_apellido = input("Nuevo apellido(enter para saltar): ").strip()
            if nuevo_apellido:
                kwargs["apellido"] = nuevo_apellido
            
            nuevo_tel = input("Nuevo telefono(enter para saltar): ").strip()
            if nuevo_tel:
                kwargs["telefono"] = nuevo_tel
            
            nuevo_mail = input("Nuevo email(enter para saltar): ").strip()
            if nuevo_mail:
                kwargs["email"] = nuevo_mail
            
            nuevo_rol = input("Nuevo rol(enter para saltar): ").strip()
            if nuevo_rol:
                kwargs["rol"] = nuevo_rol
            
            if kwargs:
                actualizar_usuario(id_persona, **kwargs)
            else:
                print("No se proporcionarion cambios.")
                
        elif op =="3":
            try:
                id_persona = int(input("ID (id_persona) a eliminar: ").strip())
            except ValueError:
                print("ID invalido.")
                continue
            
            confirmar = input(f"Confirma eliminar usuario {id_persona}? (s/n): ").strip().lower()
            if confirmar == "s":
                eliminar_usuario(id_persona)
        elif op == "4":
            criterio = input("Buscar por (nombre/apellido/email/telefono/id_persona): ").strip()
            valor = input("Valor de busqueda: ").strip()
            buscar_usuario(criterio,valor)
        
        elif op == "5":
            
            termino = input("Ingrese la palabra clave con la que quiere buscar:")
            busqueda_rapida_usuario(termino)
            
        elif op == "6":
            try:
                id_persona = int(input("ID (id_persona) del usuario: ").strip())
            except ValueError:
                print("ID invalido.")
                continue
            obtener_prestamos_usuario(id_persona) 
        elif op == "7":
            break
        
        else:
            print("Opcion invalida.")    

def Menu_Prestamos():
    while True:
        print("\n--- Gestión de Préstamos ---")
        print("1. Prestar libro")
        print("2. Devolver libro")
        print("3. Ver todos los préstamos")
        print("4. Ver préstamos de un usuario")
        print("5. Volver")
        op = input("Seleccione: ").strip()
        
        if op == "1":
            try:
                id_usuario = int(input("ID del usuario (id_persona): ").strip())
                id_libro = int(input("ID del libro (id_libro): ").strip())
                
                while True:
                    dias = int(input("Duracion (dias): ").strip())
                    if dias > 0:
                        break
                    else:
                        print("Los dias deben ser positivos.")
            except ValueError:
                print("Entrada invalida.")
                continue
            prestar_libro(id_libro,id_usuario,dias)
            
        elif op == "2":
            try:
                id_prestamo = int(input("ID del prestamo a devolver: ").strip())
            except ValueError:
                print("Entrada invalida.")
                continue
            
            devolver_libro(id_prestamo)
            
        elif op == "3":
            prestamos = Prestamo.obtener_todos()
            if prestamos:
                for p in prestamos:
                    estado = "Devuelto" if p.fecha_devolucion_real else "Pendiente"
                    print(f"[{p.id}] Libro {p.id_libro} - Usuario{p.id_usuario} - {p.fecha_prestamo} -> {p.fecha_devolucion_esperada} - {estado}")
            else:
                print("No hay prestamos registrados.")
        
        elif op == "4":
            try:
                id_usuario = int(input("ID del usuario: ").strip())
            except ValueError:
                print("ID invalido.")
                continue
            obtener_prestamos_usuario(id_usuario)
        
        elif op == "5":
            break
        
        else:
            print("Opcion invalida.")

# =========================================
#   DEVOLUCIÓN MÚLTIPLE DE LIBROS
# =========================================

# --- Devolución Múltiple de Libros --- #
def devolver_libros_multiples(ids_prestamos):
    """
    Devuelve múltiples libros en una sola transacción.
    
    Args:
        ids_prestamos (list): Lista de IDs de préstamos a devolver
    
    Returns:
        list: Lista de diccionarios con resultados de cada devolución
              [{'id_prestamo': int, 'exito': bool, 'mensaje': str, 'error': str}]
    """
    if not ids_prestamos:
        return []
    
    conn = conectar_base_datos()
    cursor = conn.cursor()
    resultados = []
    
    try:
        # Procesar cada préstamo individualmente dentro de la transacción
        for id_prestamo in ids_prestamos:
            resultado = {
                'id_prestamo': id_prestamo,
                'exito': False,
                'mensaje': '',
                'error': ''
            }
            
            try:
                # Obtener información completa del préstamo
                cursor.execute("""
                    SELECT p.id_libro, p.fecha_devolucion_esperada, p.documento_usuario,
                           l.titulo, u.nombre, u.apellido
                    FROM Prestamo p
                    JOIN Libro l ON p.id_libro = l.id_libro
                    JOIN Usuario u ON p.documento_usuario = u.documento
                    WHERE p.id=? AND p.fecha_devolucion_real IS NULL
                """, (id_prestamo,))
                fila = cursor.fetchone()
                
                if not fila:
                    resultado['error'] = f"Préstamo {id_prestamo} no encontrado o ya devuelto"
                    resultados.append(resultado)
                    continue
                
                id_libro, fecha_devolucion_esperada, documento_usuario, titulo, nombre, apellido = fila
                fecha_real = datetime.now()
                
                # Calcular multa por retraso
                multa = 0
                fecha_esperada = datetime.strptime(fecha_devolucion_esperada, "%Y-%m-%d")
                if fecha_real > fecha_esperada:
                    dias_retraso = (fecha_real - fecha_esperada).days
                    multa = dias_retraso * 1
                
                # Actualizar el préstamo como devuelto
                cursor.execute("UPDATE Prestamo SET fecha_devolucion_real=?, multa=? WHERE id=?", 
                               (fecha_real.strftime("%Y-%m-%d"), multa, id_prestamo))
                
                # Marcar el libro como disponible nuevamente
                cursor.execute("UPDATE Libro SET disponible=1 WHERE id_libro=?", (id_libro,))
                
                # Marcar como exitoso
                resultado['exito'] = True
                multa_texto = f" (Multa: ${multa})" if multa > 0 else ""
                resultado['mensaje'] = f"'{titulo}' devuelto por {nombre} {apellido}{multa_texto}"
                
            except Exception as e:
                resultado['error'] = f"Error al devolver préstamo {id_prestamo}: {str(e)}"
            
            resultados.append(resultado)
        
        # Confirmar todas las transacciones si no hubo errores críticos
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        # Marcar todos los resultados como fallidos si hay error general
        for resultado in resultados:
            if resultado['exito']:
                resultado['exito'] = False
                resultado['error'] = f"Error general en transacción: {str(e)}"
    
    finally:
        conn.close()
    
    return resultados

# =========================================
#   UTILIDAD: CREAR USUARIOS DE PRUEBA
# =========================================

def crear_usuarios_prueba():
    """Función temporal para crear usuarios de prueba"""
    try:
        # Crear admin
        admin = Usuario(
            nombre="Admin", 
            apellido="Sistema", 
            documento="12345678", 
            telefono="123456789", 
            email="admin@biblioteca.com", 
            rol="admin"
        )
        admin.set_password("admin123")
        admin.guardar()
        
        # Crear bibliotecario
        biblio = Usuario(
            nombre="Juan", 
            apellido="Bibliotecario", 
            documento="87654321", 
            telefono="987654321", 
            email="bibliotecario@biblioteca.com", 
            rol="bibliotecario"
        )
        biblio.set_password("biblio123")
        biblio.guardar()
        
        # Crear usuario normal
        user = Usuario(
            nombre="María", 
            apellido="Usuario", 
            documento="11223344", 
            telefono="555666777", 
            email="usuario@biblioteca.com", 
            rol="usuario"
        )
        user.set_password("user123")
        user.guardar()
        
        print("Usuarios de prueba creados exitosamente:")
        print("Admin: admin@biblioteca.com / admin123")
        print("Bibliotecario: bibliotecario@biblioteca.com / biblio123") 
        print("Usuario: usuario@biblioteca.com / user123")
        
    except Exception as e:
        print(f"Error al crear usuarios: {e}")            


# =========================================
#   EJECUCIÓN PRINCIPAL (SOLO CONSOLA)
# =========================================

if __name__ == "__main__":
    Menu_principal()
    crear_usuarios_prueba()  # Crear usuarios de prueba al iniciar el programa
