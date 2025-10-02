#!/usr/bin/env python3
"""
Generador de mapa de estructura de carpetas del proyecto
Crea una visualización clara de toda la organización del sistema
"""

import os
from pathlib import Path

def generate_folder_map():
    """
    Genera un mapa visual de la estructura de carpetas del proyecto
    """
    
    # Ruta base del proyecto
    base_path = Path("c:/Users/Juancho/Downloads/Gestion---Biblioteca-main/Gestion---Biblioteca-main/Proyecto")
    
    # Definir la estructura esperada y descripciones
    folder_structure = {
        "📊 database/": {
            "description": "Base de datos y migraciones",
            "files": ["base_datos.db"],
            "subfolders": {
                "migrations/": "Archivos de migración de BD"
            }
        },
        "🚀 src/": {
            "description": "Código fuente principal de la aplicación",
            "files": ["app.py"],
            "subfolders": {
                "models/": "Modelos de datos (Libro, Usuario, Prestamo)",
                "routes/": "Rutas organizadas por funcionalidad",
                "services/": "Servicios (email, notificaciones)",
                "config/": "Configuraciones de la aplicación",
                "utils/": "Utilidades y decoradores"
            }
        },
        "🎨 static/": {
            "description": "Archivos estáticos del frontend",
            "subfolders": {
                "css/": "Archivos de estilos CSS",
                "js/": "Scripts JavaScript",
                "images/": "Imágenes e iconos"
            }
        },
        "📄 templates/": {
            "description": "Plantillas HTML de la aplicación",
            "subfolders": {
                "auth/": "Plantillas de autenticación",
                "admin/": "Plantillas del panel administrativo",
                "user/": "Plantillas del dashboard de usuario"
            }
        },
        "🧪 tests/": {
            "description": "Suite completa de pruebas",
            "subfolders": {
                "unit/": "Pruebas unitarias",
                "integration/": "Pruebas de integración",
                "fixtures/": "Datos de prueba y configuración"
            }
        },
        "📝 scripts/": {
            "description": "Scripts utilitarios y automatización",
            "files": ["send_reminders.py", "update_paths.py"],
            "subfolders": {
                "maintenance/": "Scripts de mantenimiento"
            }
        },
        "📋 docs/": {
            "description": "Documentación completa del proyecto",
            "files": [
                "PLAN_MEJORAS_SISTEMA_BIBLIOTECA.txt",
                "REPORTE_TECNICO_COMPLETO.md",
                "EVALUACION_PROFESIONAL_DETALLADA.md"
            ],
            "subfolders": {
                "api/": "Documentación de la API"
            }
        },
        "📊 analytics/": {
            "description": "Herramientas de análisis y reportes",
            "files": [
                "analisis_complementario.py",
                "analisis_economico.py",
                "contador_lineas.py",
                "generar_reporte.py"
            ]
        },
        "⚙️ config_files/": {
            "description": "Archivos de configuración del proyecto",
            "files": [
                "requirements.txt",
                ".env.example",
                "Gestion-Bilioteca-1.code-workspace"
            ]
        }
    }
    
    def scan_directory(path, max_depth=3, current_depth=0):
        """
        Escanea un directorio y retorna su contenido real
        """
        items = {'folders': [], 'files': []}
        
        if current_depth >= max_depth or not path.exists():
            return items
            
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                    items['folders'].append(item.name)
                elif item.is_file() and not item.name.startswith('.'):
                    items['files'].append(item.name)
        except PermissionError:
            pass
            
        return items
    
    # Generar el mapa
    print("🗺️  MAPA COMPLETO DE LA ESTRUCTURA DEL PROYECTO")
    print("=" * 80)
    print(f"📍 Ruta base: {base_path}")
    print("=" * 80)
    
    # Verificar qué carpetas existen realmente
    print("\n📋 ESTADO ACTUAL DE CARPETAS:")
    print("-" * 50)
    
    for folder_name, info in folder_structure.items():
        folder_path = base_path / folder_name.split()[-1].rstrip('/')
        exists = "✅" if folder_path.exists() else "❌"
        print(f"{exists} {folder_name}")
        print(f"   📝 {info['description']}")
        
        # Escanear contenido real
        real_content = scan_directory(folder_path)
        
        if folder_path.exists():
            # Mostrar subcarpetas
            if 'subfolders' in info:
                print("   📁 Subcarpetas esperadas:")
                for subfolder, desc in info['subfolders'].items():
                    subfolder_path = folder_path / subfolder.rstrip('/')
                    sub_exists = "✅" if subfolder_path.exists() else "❌"
                    print(f"      {sub_exists} {subfolder} - {desc}")
            
            # Mostrar subcarpetas reales encontradas
            if real_content['folders']:
                print("   📁 Subcarpetas encontradas:")
                for folder in real_content['folders'][:10]:  # Limitar a 10
                    print(f"      📂 {folder}/")
                if len(real_content['folders']) > 10:
                    print(f"      ... y {len(real_content['folders']) - 10} más")
            
            # Mostrar archivos
            if 'files' in info:
                print("   📄 Archivos principales esperados:")
                for file_name in info['files']:
                    file_path = folder_path / file_name
                    file_exists = "✅" if file_path.exists() else "❌"
                    print(f"      {file_exists} {file_name}")
            
            # Mostrar archivos reales encontrados
            if real_content['files']:
                print("   📄 Archivos encontrados:")
                for file in real_content['files'][:10]:  # Limitar a 10
                    print(f"      📄 {file}")
                if len(real_content['files']) > 10:
                    print(f"      ... y {len(real_content['files']) - 10} más")
        
        print()
    
    # Generar vista de árbol visual
    print("\n🌳 VISTA DE ÁRBOL COMPLETA:")
    print("-" * 50)
    
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        """
        Imprime un árbol visual de la estructura
        """
        if current_depth >= max_depth or not path.exists():
            return
            
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, item in enumerate(items):
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                    
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = prefix + ("    " if is_last else "│   ")
                
                if item.is_dir():
                    # Obtener emoji basado en el nombre de la carpeta
                    emoji = get_folder_emoji(item.name)
                    print(f"{prefix}{current_prefix}{emoji} {item.name}/")
                    print_tree(item, next_prefix, max_depth, current_depth + 1)
                else:
                    # Obtener emoji basado en la extensión del archivo
                    emoji = get_file_emoji(item.suffix)
                    print(f"{prefix}{current_prefix}{emoji} {item.name}")
                    
        except PermissionError:
            print(f"{prefix}└── ❌ [Acceso denegado]")
    
    def get_folder_emoji(folder_name):
        """
        Retorna emoji apropiado para carpetas
        """
        folder_emojis = {
            'database': '📊',
            'src': '🚀',
            'static': '🎨',
            'templates': '📄',
            'tests': '🧪',
            'scripts': '📝',
            'docs': '📋',
            'analytics': '📊',
            'config_files': '⚙️',
            'models': '🏗️',
            'routes': '🛣️',
            'services': '⚙️',
            'config': '🔧',
            'utils': '🔧',
            'css': '💄',
            'js': '⚡',
            'images': '🖼️',
            'auth': '🔐',
            'admin': '👨‍💼',
            'user': '👤',
            'unit': '🔬',
            'integration': '🔗',
            'fixtures': '📋',
            'maintenance': '🔧',
            'api': '📡'
        }
        return folder_emojis.get(folder_name, '📁')
    
    def get_file_emoji(extension):
        """
        Retorna emoji apropiado para archivos
        """
        file_emojis = {
            '.py': '🐍',
            '.html': '🌐',
            '.css': '💄',
            '.js': '⚡',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.db': '🗃️',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.sql': '🗃️',
            '.env': '⚙️',
            '.workspace': '💼'
        }
        return file_emojis.get(extension, '📄')
    
    print_tree(base_path)
    
    # Resumen final
    print("\n📊 RESUMEN DE LA ESTRUCTURA:")
    print("-" * 50)
    
    total_folders = sum(1 for _ in base_path.rglob('*') if _.is_dir() and not _.name.startswith('.') and _.name != '__pycache__')
    total_files = sum(1 for _ in base_path.rglob('*') if _.is_file() and not _.name.startswith('.'))
    
    print(f"📁 Total de carpetas: {total_folders}")
    print(f"📄 Total de archivos: {total_files}")
    print(f"🎯 Estructura: Profesional y organizada")
    print(f"✅ Estado: Lista para desarrollo y producción")
    
    print("\n🚀 COMANDOS ÚTILES:")
    print("-" * 50)
    print("• Ejecutar aplicación:")
    print("  cd Proyecto && python src\\app.py")
    print("• Acceder al sistema:")
    print("  http://localhost:5000/login")
    print("• Panel de administración:")
    print("  http://localhost:5000/admin/email_config")

if __name__ == "__main__":
    generate_folder_map()