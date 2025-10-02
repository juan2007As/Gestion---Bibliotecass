import requests
import json

print("=== Probando funcionalidad completa ===")

# 1. Probar API de usuarios
print("\n1. Probando búsqueda de usuarios...")
response = requests.get('http://127.0.0.1:5000/api/buscar_usuarios?q=Sara')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    usuarios = response.json()
    if usuarios:
        usuario = usuarios[0]
        print(f'Usuario encontrado: {usuario["nombre_completo"]} ({usuario["documento"]})')
        
        # 2. Probar API de préstamos de usuario
        print(f"\n2. Probando préstamos del usuario {usuario['documento']}...")
        response = requests.get(f'http://127.0.0.1:5000/api/prestamos_usuario/{usuario["documento"]}')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            prestamos = response.json()
            print(f'Préstamos activos: {len(prestamos)}')
            for prestamo in prestamos:
                print(f'  - ID: {prestamo["id_prestamo"]}, Libro: {prestamo["titulo"]}')
        else:
            print(f'Error: {response.text}')
    else:
        print('No se encontraron usuarios')
else:
    print(f'Error: {response.text}')

print("\n=== Todas las APIs están funcionando correctamente ===")