import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

usuarios = [
    ('12345678', 'Admin', 'Sistema', '123456789', 'admin@biblioteca.com', 'admin', hash_password('123')),
    ('87654321', 'Juan', 'Bibliotecario', '987654321', 'bibliotecario@biblioteca.com', 'bibliotecario', hash_password('123')),
    ('11223344', 'María', 'Usuario', '555666777', 'usuario@biblioteca.com', 'usuario', hash_password('123'))
]

conn = sqlite3.connect('base_datos.db')
c = conn.cursor()

# Buscar tabla 'Usuario'
tabla = 'Usuario'
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
if not c.fetchone():
    raise Exception('No se encontró la tabla Usuario en la base de datos.')

# Detecta si existe campo contraseña
c.execute(f"PRAGMA table_info({tabla})")
columnas = [col[1] for col in c.fetchall()]
if 'contraseña' not in columnas and 'contrasena' not in columnas and 'password' not in columnas:
    raise Exception('La tabla no tiene un campo para contraseña (contraseña, contrasena o password).')

campo_pwd = 'contraseña' if 'contraseña' in columnas else ('contrasena' if 'contrasena' in columnas else 'password')

# Inserta los usuarios
for u in usuarios:
    c.execute(f"""
        INSERT OR IGNORE INTO {tabla} (documento, nombre, apellido, telefono, email, rol, {campo_pwd})
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, u)

conn.commit()
conn.close()

print('Usuarios de prueba insertados con contraseña 123:')
for u in usuarios:
    print(f"{u[1]} ({u[4]}) - Rol: {u[5]} - Documento: {u[0]}")
print('\nCredenciales de acceso:')
print('Admin: admin@biblioteca.com / 123')
print('Bibliotecario: bibliotecario@biblioteca.com / 123')
print('Usuario: usuario@biblioteca.com / 123')
