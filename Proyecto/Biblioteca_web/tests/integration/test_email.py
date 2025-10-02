# ===============================
#   PRUEBA DEL SISTEMA DE EMAIL
# ===============================

from app import app, email_service
from Proyecto import Usuario

def create_test_user():
    """
    Crea un usuario de prueba con el email especificado
    """
    target_email = "juan6722634@gmail.com"
    
    # Verificar si ya existe
    existing_user = Usuario.obtener_por_email(target_email)
    if existing_user:
        print(f"✅ Usuario ya existe: {existing_user.nombre} {existing_user.apellido}")
        return existing_user
    
    # Crear nuevo usuario
    try:
        nuevo_usuario = Usuario(
            nombre="Juan Carlos",
            apellido="Test User", 
            documento="123456789",
            telefono="3001234567",
            email=target_email,
            rol="usuario"
        )
        nuevo_usuario.set_password("test123")
        nuevo_usuario.guardar()
        
        print(f"✅ Usuario creado exitosamente:")
        print(f"   - Nombre: Juan Carlos Test User")
        print(f"   - Email: {target_email}")
        print(f"   - Documento: 123456789")
        print(f"   - Rol: usuario")
        
        return nuevo_usuario
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return None

def test_email_system():
    with app.app_context():
        print("🔍 Probando sistema de emails...")
        
        # Crear o obtener usuario de prueba
        print("\n📝 Creando/verificando usuario de prueba...")
        test_user = create_test_user()
        
        if not test_user:
            print("❌ No se pudo crear/obtener el usuario de prueba")
            return
        
        print(f"\n👤 Probando con usuario: {test_user.nombre} {test_user.apellido} ({test_user.email})")
        
        print("\n📧 Enviando email de confirmación de préstamo...")
        
        # Enviar email de prueba
        success = email_service.send_loan_confirmation(
            user_email=test_user.email,
            user_name=f"{test_user.nombre} {test_user.apellido}",
            book_title="📚 El Principito - Antoine de Saint-Exupéry",
            due_date="2025-10-15"
        )
        
        if success:
            print("✅ ¡Email enviado exitosamente!")
            print(f"📬 Revisa tu bandeja de entrada en: {test_user.email}")
            print("📱 También revisa la carpeta de spam/promociones si no lo ves")
            print("\n🎯 ¡Sistema de notificaciones funcionando perfectamente!")
        else:
            print("❌ Error enviando el email")

def test_reminder_email():
    """
    Prueba adicional: enviar recordatorio de devolución
    """
    with app.app_context():
        print("\n🔄 Probando email de recordatorio...")
        
        test_user = Usuario.obtener_por_email("juan6722634@gmail.com")
        if test_user:
            success = email_service.send_return_reminder(
                user_email=test_user.email,
                user_name=f"{test_user.nombre} {test_user.apellido}",
                book_title="📚 El Principito - Antoine de Saint-Exupéry",
                days_left=1
            )
            
            if success:
                print("✅ ¡Email de recordatorio enviado!")
            else:
                print("❌ Error enviando recordatorio")

if __name__ == "__main__":
    print("🚀 PRUEBA RÁPIDA DEL SISTEMA DE EMAILS")
    print("=" * 50)
    print("💡 Para control completo, usa: /admin/email_config en la web")
    print("=" * 50)
    
    # Prueba principal
    test_email_system()
    
    print("\n" + "=" * 50)
    print("🎉 PRUEBA COMPLETADA")
    print("💡 Usa la interfaz web para más opciones!")