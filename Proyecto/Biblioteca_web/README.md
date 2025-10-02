# 📚 Sistema de Gestión de Biblioteca

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
