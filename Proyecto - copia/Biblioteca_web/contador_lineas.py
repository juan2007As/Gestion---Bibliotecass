#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para contar todas las líneas de código del proyecto de biblioteca
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
        except Exception as e:
            print(f"Error leyendo {ruta_archivo}: {str(e)}")
            return 0
    except Exception as e:
        print(f"Error leyendo {ruta_archivo}: {str(e)}")
        return 0

def main():
    # Ruta base del proyecto
    base_path = r'c:\Users\Juancho\Desktop\Proyecto\Biblioteca_web'
    
    # Archivos Python
    archivos_python = [
        'Proyecto.py',
        'app.py'
    ]
    
    # Templates HTML
    archivos_html = [
        'templates/index.html',
        'templates/usuarios.html', 
        'templates/libros.html',
        'templates/prestamos.html',
        'templates/prestamos_lista.html'
    ]
    
    # Archivos CSS
    archivos_css = [
        'static/estilos_menu_principal.css',
        'static/estilos_menu_usuarios.css',
        'static/estilos_menu_libros.css',
        'static/estilos_menu_prestamos.css'
    ]
    
    # Archivos JavaScript
    archivos_js = [
        'static/script_usuarios.js',
        'static/script_libros.js',
        'static/script_prestamos.js',
        'static/script_prestamos_menu.js',
        'static/script_prestamos_busqueda.js'
    ]
    
    # Contadores
    total_lineas = 0
    total_python = 0
    total_html = 0
    total_css = 0
    total_js = 0
    
    print("="*80)
    print("CONTADOR DE LÍNEAS DE CÓDIGO - SISTEMA DE BIBLIOTECA")
    print("="*80)
    
    # Contar archivos Python
    print("\n📄 ARCHIVOS PYTHON:")
    print("-" * 40)
    for archivo in archivos_python:
        ruta_completa = os.path.join(base_path, archivo)
        if os.path.exists(ruta_completa):
            lineas = contar_lineas_archivo(ruta_completa)
            total_python += lineas
            print(f"  {archivo:<25} {lineas:>6} líneas")
        else:
            print(f"  {archivo:<25} NO ENCONTRADO")
    
    # Contar templates HTML
    print("\n🌐 TEMPLATES HTML:")
    print("-" * 40)
    for archivo in archivos_html:
        ruta_completa = os.path.join(base_path, archivo)
        if os.path.exists(ruta_completa):
            lineas = contar_lineas_archivo(ruta_completa)
            total_html += lineas
            print(f"  {archivo:<25} {lineas:>6} líneas")
        else:
            print(f"  {archivo:<25} NO ENCONTRADO")
    
    # Contar archivos CSS
    print("\n🎨 ARCHIVOS CSS:")
    print("-" * 40)
    for archivo in archivos_css:
        ruta_completa = os.path.join(base_path, archivo)
        if os.path.exists(ruta_completa):
            lineas = contar_lineas_archivo(ruta_completa)
            total_css += lineas
            print(f"  {archivo:<35} {lineas:>6} líneas")
        else:
            print(f"  {archivo:<35} NO ENCONTRADO")
    
    # Contar archivos JavaScript
    print("\n⚡ ARCHIVOS JAVASCRIPT:")
    print("-" * 40)
    for archivo in archivos_js:
        ruta_completa = os.path.join(base_path, archivo)
        if os.path.exists(ruta_completa):
            lineas = contar_lineas_archivo(ruta_completa)
            total_js += lineas
            print(f"  {archivo:<35} {lineas:>6} líneas")
        else:
            print(f"  {archivo:<35} NO ENCONTRADO")
    
    # Calcular totales
    total_lineas = total_python + total_html + total_css + total_js
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("📊 RESUMEN TOTAL:")
    print("="*80)
    print(f"  📄 Python (backend):      {total_python:>6} líneas")
    print(f"  🌐 HTML (templates):      {total_html:>6} líneas") 
    print(f"  🎨 CSS (estilos):         {total_css:>6} líneas")
    print(f"  ⚡ JavaScript (frontend): {total_js:>6} líneas")
    print("-" * 80)
    print(f"  🚀 TOTAL PROYECTO:        {total_lineas:>6} líneas")
    print("="*80)
    
    # Estadísticas adicionales
    print("\n📈 ESTADÍSTICAS:")
    print("-" * 40)
    if total_lineas > 0:
        print(f"  Backend (Python):     {(total_python/total_lineas)*100:>5.1f}%")
        print(f"  Frontend (HTML):      {(total_html/total_lineas)*100:>5.1f}%")
        print(f"  Estilos (CSS):        {(total_css/total_lineas)*100:>5.1f}%")
        print(f"  Scripts (JavaScript): {(total_js/total_lineas)*100:>5.1f}%")
    
    # Archivos de utilidad también
    print("\n🔧 ARCHIVOS DE UTILIDAD:")
    print("-" * 40)
    archivos_utilidad = [
        'llenar_base_datos.py',
        'verificar_db.py',
        'debug_funciones.py',
        'debug_rutas.py',
        'verificar_db_completo.py'
    ]
    
    total_utilidad = 0
    for archivo in archivos_utilidad:
        ruta_completa = os.path.join(base_path, archivo)
        if os.path.exists(ruta_completa):
            lineas = contar_lineas_archivo(ruta_completa)
            total_utilidad += lineas
            print(f"  {archivo:<25} {lineas:>6} líneas")
    
    if total_utilidad > 0:
        print(f"\n  Total utilidades:         {total_utilidad:>6} líneas")
        print(f"  GRAN TOTAL:               {total_lineas + total_utilidad:>6} líneas")

if __name__ == "__main__":
    main()