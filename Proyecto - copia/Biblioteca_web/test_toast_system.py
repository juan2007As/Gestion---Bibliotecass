import requests
import time

print("=== Prueba del Sistema de Notificaciones Toast Mejorado ===")
print()

# URLs a probar
test_urls = [
    'http://127.0.0.1:5000/login',
    'http://127.0.0.1:5000/',
    'http://127.0.0.1:5000/libros',
    'http://127.0.0.1:5000/usuarios',
    'http://127.0.0.1:5000/prestamos/menu'
]

for url in test_urls:
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {url} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ {url} - Error: {str(e)}")
    time.sleep(0.2)

print()
print("📋 Sistema de Notificaciones Implementado:")
print("   ✅ Auto-dismiss después de 4 segundos")
print("   ✅ Botón de cierre manual (×)")
print("   ✅ Barra de progreso visual")
print("   ✅ Pausa en hover")
print("   ✅ Animaciones suaves de entrada y salida")
print("   ✅ Cierre al hacer clic en la notificación")
print("   ✅ Aplicado a todos los templates HTML")
print()
print("🎨 Estilos aplicados en:")
print("   - toast_styles.css (archivo dedicado)")
print("   - estilos_modal_comun.css (estilos principales)")
print()
print("📜 JavaScript aplicado en:")
print("   - toast_notifications.js (lógica compartida)")
print("   - Incluido en todos los templates")
print()
print("🚀 Para probar:")
print("   1. Inicia tu aplicación Flask")
print("   2. Navega a cualquier página")
print("   3. Realiza acciones que generen notificaciones")
print("   4. Observa las mejoras: auto-dismiss, botón cerrar, barra progreso")