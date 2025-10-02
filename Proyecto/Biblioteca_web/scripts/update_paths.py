#!/usr/bin/env python3
"""
Script para actualizar todas las rutas de archivos en el código 
después de la reorganización del proyecto
"""

import os
import re

def update_file_paths():
    """
    Actualiza todas las rutas de archivos en los archivos de código
    """
    
    # Diccionario de reemplazos
    replacements = {
        # Rutas de imágenes
        "Biblioteca_web/static/imagenes/": "../static/images/",
        
        # Imports de Proyecto
        "from Proyecto import": "from models.Proyecto import",
        
        # Imports de servicios
        "from notifications.email_services import": "from services.email_services import",
        
        # Imports de config  
        "from config.": "from config.",
        
    }
    
    # Archivos a actualizar
    files_to_update = [
        "c:/Users/Juancho/Downloads/Gestion---Biblioteca-main/Gestion---Biblioteca-main/Proyecto/src/app.py"
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            print(f"📝 Actualizando {file_path}...")
            
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Aplicar reemplazos
            original_content = content
            for old_path, new_path in replacements.items():
                content = content.replace(old_path, new_path)
            
            # Guardar si hay cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Actualizado")
            else:
                print(f"  ➡️ Sin cambios necesarios")
        else:
            print(f"  ❌ Archivo no encontrado: {file_path}")

def create_readme():
    """
    Crea un README.md con la nueva estructura del proyecto
    """
    readme_content = """# 📚 Sistema de Gestión de Biblioteca

## 🏗️ Estructura del Proyecto

```
Proyecto_Biblioteca/
├── 📊 database/                  # Base de datos
│   ├── base_datos.db
│   └── migrations/
│
├── 🚀 src/                       # Código fuente principal
│   ├── app.py                    # Aplicación Flask principal
│   ├── models/                   # Modelos de datos
│   │   └── Proyecto.py
│   ├── routes/                   # Rutas organizadas
│   ├── services/                 # Servicios (email, notificaciones)
│   ├── config/                   # Configuraciones
│   └── utils/                    # Utilidades
│
├── 🎨 static/                    # Archivos estáticos
│   ├── css/                     # Estilos CSS
│   ├── js/                      # JavaScript
│   └── images/                  # Imágenes
│
├── 📄 templates/                 # Plantillas HTML
│   ├── auth/                    # Autenticación
│   ├── admin/                   # Panel administrativo
│   └── user/                    # Dashboard de usuario
│
├── 🧪 tests/                     # Pruebas
│   ├── unit/                    # Pruebas unitarias
│   ├── integration/             # Pruebas de integración
│   └── fixtures/                # Datos de prueba
│
├── 📝 scripts/                   # Scripts utilitarios
│   └── maintenance/             # Mantenimiento
│
├── 📋 docs/                      # Documentación
├── 📊 analytics/                 # Análisis y reportes
└── ⚙️ config_files/             # Archivos de configuración
```

## 🚀 Instalación y Uso

1. **Instalar dependencias:**
   ```bash
   pip install flask flask-mail werkzeug
   ```

2. **Ejecutar la aplicación:**
   ```bash
   cd src
   python app.py
   ```

3. **Acceder al sistema:**
   - URL: http://localhost:5000
   - Admin: admin@biblioteca.com / admin123

## 📧 Configuración de Emails

- Panel de administración: `/admin/email_config`
- Recordatorios manuales disponibles
- Notificaciones de préstamos y devoluciones

## 🔧 Funcionalidades

- ✅ Gestión de libros, usuarios y préstamos
- ✅ Sistema de autenticación por roles
- ✅ Notificaciones por email
- ✅ Recordatorios automáticos
- ✅ Dashboard de usuario
- ✅ Panel administrativo

## 📞 Soporte

Para soporte técnico, consulta la documentación en `/docs/`
"""
    
    readme_path = "c:/Users/Juancho/Downloads/Gestion---Biblioteca-main/Gestion---Biblioteca-main/Proyecto/README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📖 README.md creado en: {readme_path}")

if __name__ == "__main__":
    print("🔧 ACTUALIZANDO RUTAS DEL PROYECTO...")
    print("=" * 50)
    
    update_file_paths()
    create_readme()
    
    print("\n✅ ACTUALIZACIÓN COMPLETADA")
    print("📋 Resumen de cambios:")
    print("  - Rutas de imágenes actualizadas")
    print("  - Imports de módulos actualizados") 
    print("  - README.md creado")
    print("\n💡 Próximos pasos:")
    print("  1. Probar que la aplicación funcione: cd src && python app.py")
    print("  2. Verificar que los emails funcionen")
    print("  3. Revisar que todas las rutas estén correctas")