import os

class EmailConfig:
    """Clase para manejar la configuración de correo electrónico."""
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    MAIL_USERNAME = 'bibliotecanotificacion@gmail.com'
    MAIL_PASSWORD = 'pawv rfma bqlv gviq'
    MAIL_DEFAULT_SENDER = ('Biblioteca', 'bibliotecanotificacion@gmail.com')
    
    # CONFIGURACIÓN PARA PRODUCCIÓN
    # True = Solo simula emails (desarrollo/testing)
    # False = Envía emails reales (producción)
    MAIL_SUPPRESS_SEND = True  # Cambiar a False cuando quieras emails reales
    
# Configuración para producción (emails reales)
class ProductionEmailConfig(EmailConfig):
    MAIL_SUPPRESS_SEND = False  # Envía emails reales

# Configuración para desarrollo (solo simula)
class DevelopmentEmailConfig(EmailConfig):
    MAIL_SUPPRESS_SEND = True   # Solo simula emails

# Configuración por defecto (puedes cambiar fácilmente)
# Cambia a ProductionEmailConfig() para emails reales
def get_email_config():
    """
    Función para obtener la configuración de email.
    Cambia entre DevelopmentEmailConfig() y ProductionEmailConfig()
    """
    return ProductionEmailConfig()  # Cambiar por DevelopmentEmailConfig() para simular emails