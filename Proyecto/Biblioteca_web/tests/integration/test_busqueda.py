import requests
import json

# Probar búsqueda sin término
print("=== Búsqueda sin término ===")
response = requests.get('http://127.0.0.1:5000/api/buscar_libros_admin')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Total libros: {len(data)}')
else:
    print(f'Error: {response.text}')

# Probar búsqueda con término
print("\n=== Búsqueda con término 'Cien' ===")
response = requests.get('http://127.0.0.1:5000/api/buscar_libros_admin', params={'termino': 'Cien'})
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Resultados encontrados: {len(data)}')
    if data:
        print('Primer resultado:')
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
else:
    print(f'Error: {response.text}')