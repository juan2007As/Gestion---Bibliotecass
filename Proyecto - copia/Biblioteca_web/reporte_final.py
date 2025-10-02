#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contador final completo de líneas de código
"""

import os

def contar_lineas_archivo(ruta_archivo):
    """Cuenta las líneas de un archivo"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
            return len(lineas)
    except UnicodeDecodeError:
        try:
            with open(ruta_archivo, 'r', encoding='latin-1') as archivo:
                lineas = archivo.readlines()
                return len(lineas)
        except Exception:
            return 0
    except Exception:
        return 0

# Ruta base
base_path = r'c:\Users\Juancho\Desktop\Proyecto\Biblioteca_web'

# Contar archivos principales
archivos_principales = {
    'Proyecto.py': contar_lineas_archivo(os.path.join(base_path, 'Proyecto.py')),
    'app.py': contar_lineas_archivo(os.path.join(base_path, 'app.py')),
    'contador_lineas.py': contar_lineas_archivo(os.path.join(base_path, 'contador_lineas.py'))
}

# Templates
templates_path = os.path.join(base_path, 'templates')
archivos_html = {}
for archivo in os.listdir(templates_path):
    if archivo.endswith('.html'):
        archivos_html[archivo] = contar_lineas_archivo(os.path.join(templates_path, archivo))

# CSS
static_path = os.path.join(base_path, 'static')
archivos_css = {}
for archivo in os.listdir(static_path):
    if archivo.endswith('.css'):
        archivos_css[archivo] = contar_lineas_archivo(os.path.join(static_path, archivo))

# JavaScript
archivos_js = {}
for archivo in os.listdir(static_path):
    if archivo.endswith('.js'):
        archivos_js[archivo] = contar_lineas_archivo(os.path.join(static_path, archivo))

# Mostrar resultados
print("="*90)
print("🏗️  REPORTE FINAL DE LÍNEAS DE CÓDIGO - SISTEMA DE BIBLIOTECA")
print("="*90)

print("\n📄 ARCHIVOS PYTHON (BACKEND):")
print("-"*60)
total_python = 0
for archivo, lineas in archivos_principales.items():
    print(f"  {archivo:<30} {lineas:>8} líneas")
    total_python += lineas

print(f"\n  📄 SUBTOTAL PYTHON:        {total_python:>8} líneas")

print("\n🌐 TEMPLATES HTML (FRONTEND):")
print("-"*60)
total_html = 0
for archivo, lineas in sorted(archivos_html.items()):
    print(f"  {archivo:<30} {lineas:>8} líneas")
    total_html += lineas

print(f"\n  🌐 SUBTOTAL HTML:           {total_html:>8} líneas")

print("\n🎨 ARCHIVOS CSS (ESTILOS):")
print("-"*60)
total_css = 0
for archivo, lineas in sorted(archivos_css.items()):
    print(f"  {archivo:<30} {lineas:>8} líneas")
    total_css += lineas

print(f"\n  🎨 SUBTOTAL CSS:            {total_css:>8} líneas")

print("\n⚡ ARCHIVOS JAVASCRIPT (INTERACTIVIDAD):")
print("-"*60)
total_js = 0
for archivo, lineas in sorted(archivos_js.items()):
    print(f"  {archivo:<30} {lineas:>8} líneas")
    total_js += lineas

print(f"\n  ⚡ SUBTOTAL JAVASCRIPT:     {total_js:>8} líneas")

# Total general
total_general = total_python + total_html + total_css + total_js

print("\n" + "="*90)
print("🚀 RESUMEN FINAL DEL PROYECTO:")
print("="*90)
print(f"  📄 Backend (Python):        {total_python:>8} líneas ({(total_python/total_general)*100:>5.1f}%)")
print(f"  🌐 Frontend (HTML):         {total_html:>8} líneas ({(total_html/total_general)*100:>5.1f}%)")
print(f"  🎨 Estilos (CSS):           {total_css:>8} líneas ({(total_css/total_general)*100:>5.1f}%)")
print(f"  ⚡ Scripts (JavaScript):    {total_js:>8} líneas ({(total_js/total_general)*100:>5.1f}%)")
print("-"*90)
print(f"  🏆 TOTAL SISTEMA:           {total_general:>8} líneas")
print("="*90)

print("\n📈 ANÁLISIS DEL PROYECTO:")
print("-"*60)
print("✅ Sistema completo de gestión de biblioteca")
print("✅ Backend robusto con SQLite y Flask")
print("✅ Frontend interactivo con búsqueda avanzada")
print("✅ Sistema de usuarios con documentos colombianos")
print("✅ Gestión completa de préstamos y devoluciones")
print("✅ Interfaz responsive y estéticamente consistente")
print("✅ Base de datos poblada con 15 usuarios y 25 libros")

print(f"\n🎯 LÍNEAS DE CÓDIGO POR FUNCIONALIDAD:")
print("-"*60)
backend_lineas = archivos_principales['Proyecto.py'] + archivos_principales['app.py']
print(f"  Lógica de negocio y API:    {backend_lineas:>8} líneas")
print(f"  Interfaz de usuario:        {total_html:>8} líneas")
print(f"  Diseño y presentación:      {total_css:>8} líneas")
print(f"  Interactividad y UX:        {total_js:>8} líneas")
print(f"  Scripts de utilidad:        {archivos_principales['contador_lineas.py']:>8} líneas")