#!/usr/bin/env python3
"""
Script para enviar recordatorios de libros próximos a vencer
Ejecutar con: python send_reminders.py
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_reminders_standalone():
    """
    Función independiente para enviar recordatorios de libros próximos a vencer
    """
    try:
        # Imports necesarios
        from flask import Flask
        from flask_mail import Mail
        from src.config.email_config import get_email_config
        from src.services.email_services import EmailService
        from src.models.Proyecto import conectar_base_datos, crear_tablas
        
        # Crear aplicación Flask temporal
        app = Flask(__name__)
        app.secret_key = 'temp_key_for_reminders'
        
        # Configurar email
        email_config = get_email_config()
        app.config.update(
            MAIL_SERVER=email_config.MAIL_SERVER,
            MAIL_PORT=email_config.MAIL_PORT,
            MAIL_USE_TLS=email_config.MAIL_USE_TLS,
            MAIL_USERNAME=email_config.MAIL_USERNAME,
            MAIL_PASSWORD=email_config.MAIL_PASSWORD,
            MAIL_DEFAULT_SENDER=email_config.MAIL_DEFAULT_SENDER,
            MAIL_SUPPRESS_SEND=email_config.MAIL_SUPPRESS_SEND
        )
        
        mail = Mail(app)
        
        # Ejecutar dentro del contexto de la aplicación
        with app.app_context():
            email_service = EmailService(app, mail)
            
            # Conectar a la base de datos
            conn = conectar_base_datos()
            cursor = conn.cursor()
            
            # Fechas para recordatorios
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            in_3_days = today + timedelta(days=3)
            
            print(f"📅 Hoy: {today}")
            print(f"🔍 Buscando préstamos que vencen el {tomorrow} o {in_3_days}")
            
            # Buscar préstamos que vencen en 1 y 3 días
            cursor.execute("""
                SELECT p.id, p.documento_usuario, p.fecha_devolucion_esperada,
                       l.titulo, u.nombre, u.apellido, u.email
                FROM Prestamo p
                JOIN Libro l ON p.id_libro = l.id_libro  
                JOIN Usuario u ON p.documento_usuario = u.documento
                WHERE p.fecha_devolucion_real IS NULL 
                AND (p.fecha_devolucion_esperada = ? OR p.fecha_devolucion_esperada = ?)
                AND u.email IS NOT NULL
                AND u.email != ''
            """, (tomorrow.strftime('%Y-%m-%d'), in_3_days.strftime('%Y-%m-%d')))
            
            loans = cursor.fetchall()
            sent_count = 0
            
            print(f"📋 Encontrados {len(loans)} préstamos próximos a vencer")
            
            for loan in loans:
                loan_id, doc_usuario, fecha_vence, titulo, nombre, apellido, email = loan
                
                # Calcular días restantes
                due_date = datetime.strptime(fecha_vence, '%Y-%m-%d').date()
                days_left = (due_date - today).days
                
                print(f"📧 Enviando recordatorio a {nombre} {apellido} ({email})")
                print(f"   Libro: '{titulo}' - Vence en {days_left} días ({fecha_vence})")
                
                # Enviar recordatorio
                success = email_service.send_return_reminder(
                    user_email=email,
                    user_name=f"{nombre} {apellido}",
                    book_title=titulo,
                    days_left=days_left
                )
                
                if success:
                    sent_count += 1
                    print(f"   ✅ Email enviado exitosamente")
                else:
                    print(f"   ❌ Error enviando email")
            
            conn.close()
            
            # Resumen final
            print(f"\n🎯 RESUMEN:")
            print(f"   Préstamos encontrados: {len(loans)}")
            print(f"   Emails enviados: {sent_count}")
            print(f"   Emails fallidos: {len(loans) - sent_count}")
            
            return sent_count
            
    except Exception as e:
        print(f"❌ Error en recordatorios automáticos: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    print("🚀 Iniciando sistema de recordatorios...")
    result = send_reminders_standalone()
    print(f"\n✅ Proceso completado. Recordatorios enviados: {result}")