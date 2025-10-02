import sqlite3
import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def analizar_y_ajustar_db(ruta_db):
    print(f'\nAnalizando: {ruta_db}')
    if not os.path.exists(ruta_db):
        print('  - Archivo no encontrado.')
        return
    conn = sqlite3.connect(ruta_db)
    c = conn.cursor()
    # Buscar tabla de usuarios (ahora solo 'Usuario')
    tabla = None
    for t in ['Usuario']:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
        if c.fetchone():
            tabla = t
            break
    if not tabla:
        print('  - No se encontró tabla de usuarios.')
        conn.close()
        return
    # Buscar campo de contraseña
    c.execute(f"PRAGMA table_info({tabla})")
    columnas = [col[1] for col in c.fetchall()]
    campo_pwd = None
    for pwd in ['contraseña', 'contrasena', 'password']:
        if pwd in columnas:
            campo_pwd = pwd
            break
    if not campo_pwd:
        print(f'  - La tabla {tabla} no tiene campo de contraseña. Puedes agregarlo con:')
        print(f'    ALTER TABLE {tabla} ADD COLUMN contraseña TEXT;')
        conn.close()
        return
    # Actualizar usuarios sin contraseña
    c.execute(f"SELECT documento, {campo_pwd} FROM {tabla}")
    usuarios = c.fetchall()
    actualizados = 0
    for doc, pwd in usuarios:
        if not pwd or pwd.strip() == '':
            hash_123 = hash_password('123')
            c.execute(f"UPDATE {tabla} SET {campo_pwd}=? WHERE documento=?", (hash_123, doc))
            actualizados += 1
    conn.commit()
    print(f'  - Usuarios actualizados con contraseña por defecto (123): {actualizados}')
    conn.close()

# Analizar ambas bases de datos
analizar_y_ajustar_db('base_datos.db')
analizar_y_ajustar_db('Biblioteca_web/base_datos.db')

print('\nListo. Si alguna tabla no tenía campo de contraseña, revisa el mensaje y ejecuta el ALTER TABLE sugerido.')
