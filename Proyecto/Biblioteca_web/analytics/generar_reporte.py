#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Reporte Completo del Sistema de Biblioteca
Genera estadísticas detalladas de líneas de código por archivo y categoría
"""

import os
import glob
from datetime import datetime

def contar_lineas_archivo(archivo):
    """Cuenta las líneas totales y de código de un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total = len(lines)
            empty = sum(1 for line in lines if line.strip() == '')
            return total, total - empty
    except:
        try:
            with open(archivo, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                total = len(lines)
                empty = sum(1 for line in lines if line.strip() == '')
                return total, total - empty
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
            return 0, 0

def get_file_size(archivo):
    """Obtiene el tamaño de un archivo en bytes"""
    try:
        return os.path.getsize(archivo)
    except:
        return 0

def main():
    print('='*80)
    print('📋 REPORTE COMPLETO DEL SISTEMA DE BIBLIOTECA')
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'📅 Fecha: {fecha_actual}')
    print('='*80)

    # Definir categorías de archivos
    categorias = {
        '🐍 BACKEND PYTHON': {
            'patrones': ['*.py'],
            'descripcion': 'Lógica de negocio y servidor Flask',
            'excluir': set(['generar_reporte.py'])  # Excluir este mismo archivo
        },
        '🌐 TEMPLATES HTML': {
            'patrones': ['templates/*.html'],
            'descripcion': 'Interfaz de usuario y vistas',
            'excluir': set()
        },
        '⚡ JAVASCRIPT': {
            'patrones': ['static/*.js'],
            'descripcion': 'Funcionalidad del lado cliente',
            'excluir': set()
        },
        '🎨 ESTILOS CSS': {
            'patrones': ['static/*.css'],
            'descripcion': 'Diseño y presentación visual',
            'excluir': set()
        },
        '📊 ARCHIVOS DE PRUEBA': {
            'patrones': ['test_*.py', 'verificar_*.py'],
            'descripcion': 'Scripts de testing y verificación',
            'excluir': set()
        },
        '⚙️ UTILIDADES': {
            'patrones': ['insertar_*.py', 'ajustar_*.py', 'contador_*.py', 'reporte_*.py'],
            'descripcion': 'Scripts auxiliares y herramientas',
            'excluir': set(['generar_reporte.py'])
        }
    }

    total_archivos = 0
    total_lineas = 0
    total_lineas_codigo = 0
    total_tamaño = 0
    detalle_por_categoria = {}

    for categoria, info in categorias.items():
        archivos_encontrados = []
        for patron in info['patrones']:
            archivos_encontrados.extend(glob.glob(patron))
        
        # Filtrar archivos excluidos
        archivos_encontrados = [f for f in archivos_encontrados 
                               if os.path.basename(f) not in info['excluir']]
        
        if archivos_encontrados:
            print(f'\n{categoria}')
            print(f'📝 {info["descripcion"]}')
            print('-'*70)
            
            subtotal_lineas = 0
            subtotal_codigo = 0
            subtotal_tamaño = 0
            archivos_detalle = []
            
            for archivo in sorted(archivos_encontrados):
                if os.path.isfile(archivo):
                    lineas_total, lineas_codigo = contar_lineas_archivo(archivo)
                    tamaño = get_file_size(archivo)
                    
                    subtotal_lineas += lineas_total
                    subtotal_codigo += lineas_codigo
                    subtotal_tamaño += tamaño
                    
                    tamaño_kb = tamaño / 1024
                    nombre = os.path.basename(archivo)
                    archivos_detalle.append({
                        'nombre': nombre,
                        'lineas': lineas_total,
                        'codigo': lineas_codigo,
                        'tamaño_kb': tamaño_kb
                    })
                    
                    print(f'  📄 {nombre:<35} {lineas_total:>5} líneas ({lineas_codigo:>4} código) {tamaño_kb:>6.1f} KB')
            
            print(f'  📊 SUBTOTAL: {len(archivos_encontrados)} archivos, {subtotal_lineas} líneas, {subtotal_tamaño/1024:.1f} KB')
            
            detalle_por_categoria[categoria] = {
                'archivos': len(archivos_encontrados),
                'lineas': subtotal_lineas,
                'codigo': subtotal_codigo,
                'tamaño_kb': subtotal_tamaño/1024,
                'detalle': archivos_detalle
            }
            
            total_archivos += len(archivos_encontrados)
            total_lineas += subtotal_lineas
            total_lineas_codigo += subtotal_codigo
            total_tamaño += subtotal_tamaño

    print(f'\n{"="*80}')
    print('📈 RESUMEN ESTADÍSTICO FINAL')
    print(f'{"="*80}')
    print(f'📁 Total de archivos analizados:    {total_archivos:>6}')
    print(f'📄 Total de líneas:                 {total_lineas:>6}')
    print(f'💻 Líneas de código (sin vacías):   {total_lineas_codigo:>6}')
    print(f'💾 Tamaño total del proyecto:       {total_tamaño/1024:>6.1f} KB')
    print(f'📊 Promedio líneas por archivo:     {total_lineas/total_archivos if total_archivos > 0 else 0:.1f}')
    print(f'{"="*80}')
    
    # Generar distribución porcentual
    print('\n📊 DISTRIBUCIÓN PORCENTUAL POR CATEGORÍA:')
    print('-'*50)
    for categoria, datos in detalle_por_categoria.items():
        porcentaje = (datos['lineas'] / total_lineas * 100) if total_lineas > 0 else 0
        print(f'{categoria:<25} {datos["lineas"]:>6} líneas ({porcentaje:>5.1f}%)')
    
    # Archivos más grandes
    print('\n📈 TOP 5 ARCHIVOS MÁS GRANDES (por líneas):')
    print('-'*50)
    todos_archivos = []
    for categoria, datos in detalle_por_categoria.items():
        for archivo in datos['detalle']:
            todos_archivos.append((archivo['nombre'], archivo['lineas'], categoria))
    
    todos_archivos.sort(key=lambda x: x[1], reverse=True)
    for i, (nombre, lineas, categoria) in enumerate(todos_archivos[:5], 1):
        print(f'{i}. {nombre:<35} {lineas:>5} líneas ({categoria})')

if __name__ == "__main__":
    main()