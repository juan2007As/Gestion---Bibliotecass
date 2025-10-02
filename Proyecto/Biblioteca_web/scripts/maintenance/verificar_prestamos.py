import sqlite3

conn = sqlite3.connect('base_datos.db')
cursor = conn.cursor()

print("Estructura tabla Prestamo:")
cursor.execute('PRAGMA table_info(Prestamo)')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} ({row[2]})')

print("\nPrimeros registros de Prestamo:")
cursor.execute('SELECT * FROM Prestamo LIMIT 3')
prestamos = cursor.fetchall()
for i, prestamo in enumerate(prestamos):
    print(f'Registro {i+1}: {prestamo}')

conn.close()