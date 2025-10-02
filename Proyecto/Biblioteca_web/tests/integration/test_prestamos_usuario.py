import requests
import json

# Probar la API con diferentes usuarios
documentos_prueba = ['1017928936', '5555555555', '1121847200']

for documento in documentos_prueba:
    print(f"\n=== Probando usuario {documento} ===")
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/prestamos_usuario/{documento}')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f'Préstamos activos: {len(data)}')
                for prestamo in data:
                    print(f'  - {prestamo["titulo"]} (ID: {prestamo["id_prestamo"]})')
            else:
                print(f'Respuesta inesperada (no es lista): {data}')
        else:
            print(f'Error HTTP: {response.text}')
            
    except Exception as e:
        print(f'Error de conexión: {e}')