#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis complementario del sistema de biblioteca
"""

import os
import sqlite3
from datetime import datetime

def analizar_base_datos():
    try:
        conn = sqlite3.connect('base_datos.db')
        cursor = conn.cursor()
        
        # Obtener estadísticas de la base de datos
        cursor.execute('SELECT COUNT(*) FROM Usuario')
        usuarios = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM Libro')
        libros = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM Prestamo')
        prestamos_total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM Prestamo WHERE fecha_devolucion_real IS NULL')
        prestamos_activos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM Libro WHERE disponible = 1')
        libros_disponibles = cursor.fetchone()[0]
        
        # Obtener información del tamaño de la base de datos
        tamaño_db = os.path.getsize('base_datos.db') / 1024  # KB
        
        conn.close()
        
        return {
            'usuarios': usuarios,
            'libros': libros,
            'libros_disponibles': libros_disponibles,
            'prestamos_total': prestamos_total,
            'prestamos_activos': prestamos_activos,
            'tamaño_kb': tamaño_db
        }
    except Exception as e:
        return {'error': str(e)}

def get_project_structure():
    estructura = {}
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in root or '.git' in root:
            continue
        
        folder_name = os.path.basename(root) or 'ROOT'
        
        if folder_name not in estructura:
            estructura[folder_name] = {'dirs': [], 'files': []}
        
        for file in files:
            if not file.endswith('.pyc') and not file.startswith('.'):
                ext = os.path.splitext(file)[1] or 'sin_ext'
                estructura[folder_name]['files'].append((file, ext))
        
        for dir in dirs:
            if not dir.startswith('__') and not dir.startswith('.'):
                estructura[folder_name]['dirs'].append(dir)
    
    return estructura

def main():
    print('='*80)
    print('📊 ANÁLISIS COMPLEMENTARIO DEL SISTEMA')
    print('='*80)

    # Análisis de la base de datos
    print('\n🗄️ ESTADO DE LA BASE DE DATOS:')
    print('-'*50)
    db_stats = analizar_base_datos()
    if 'error' not in db_stats:
        print('👥 Usuarios registrados:        {:>6}'.format(db_stats['usuarios']))
        print('📚 Libros en catálogo:         {:>6}'.format(db_stats['libros']))  
        print('✅ Libros disponibles:         {:>6}'.format(db_stats['libros_disponibles']))
        print('📋 Préstamos históricos:       {:>6}'.format(db_stats['prestamos_total']))
        print('🔄 Préstamos activos:          {:>6}'.format(db_stats['prestamos_activos']))
        print('💾 Tamaño base de datos:       {:>6.1f} KB'.format(db_stats['tamaño_kb']))
        
        if db_stats['libros'] > 0:
            tasa = db_stats['libros_disponibles']/db_stats['libros']*100
        else:
            tasa = 0
        print('📊 Tasa de disponibilidad:     {:>5.1f}%'.format(tasa))
    else:
        print('❌ Error accediendo a BD: {}'.format(db_stats['error']))

    # Análisis de estructura de archivos
    print('\n📁 ESTRUCTURA DEL PROYECTO:')
    print('-'*50)
    estructura = get_project_structure()

    # Contar archivos por extensión
    extensiones = {}
    total_archivos = 0

    for folder, data in estructura.items():
        for archivo, ext in data['files']:
            extensiones[ext] = extensiones.get(ext, 0) + 1
            total_archivos += 1

    print('Archivos por tipo:')
    for ext, count in sorted(extensiones.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / total_archivos * 100) if total_archivos > 0 else 0
        tipo_desc = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.css': 'CSS',
            '.html': 'HTML',
            '.db': 'Base de Datos',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.workspace': 'VS Code Config',
            'sin_ext': 'Sin extensión'
        }.get(ext, ext.upper())
        print('  {:<15} {:>3} archivos ({:>5.1f}%)'.format(tipo_desc, count, porcentaje))

    print('\nTotal de archivos: {}'.format(total_archivos))

    # Información de directorios
    print('\n📂 DIRECTORIOS PRINCIPALES:')
    print('-'*50)
    for folder, data in estructura.items():
        if data['dirs']:
            print('{}/ - {} subdirectorios'.format(folder, len(data['dirs'])))
            for subdir in data['dirs']:
                print('  ├── {}/'.format(subdir))

    print('\n⚙️ CONFIGURACIÓN TÉCNICA:')
    print('-'*50)
    print('Backend Framework:     Flask (Python)')
    print('Base de Datos:         SQLite')
    print('Frontend:              HTML5 + CSS3 + JavaScript')
    print('Template Engine:       Jinja2')
    print('Autenticación:         Session-based')
    print('Arquitectura:          MVC Pattern')
    print('Deployment:            Standalone Python Server')
    
    print('\n🔧 TECNOLOGÍAS DETECTADAS:')
    print('-'*50)
    tecnologias = {
        'Backend': ['Flask', 'SQLite', 'Python 3.x'],
        'Frontend': ['HTML5', 'CSS3', 'JavaScript ES6+'],
        'Tools': ['Jinja2', 'AJAX', 'JSON']
    }
    
    for categoria, techs in tecnologias.items():
        print('{}: {}'.format(categoria, ', '.join(techs)))

if __name__ == "__main__":
    main()