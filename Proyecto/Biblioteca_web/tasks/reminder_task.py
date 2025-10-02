# ===============================
#   RECORDATORIOS AUTOMÁTICOS
# ===============================

import sys
import os
from datetime import datetime, timedelta

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_daily_reminders():
    """
    Función que envía recordatorios diarios de libros próximos a vencer
    """
    try:
        from Proyecto import conectar_base_datos, Usuario
        from app import email_service
        
        if not email_service:
            print("❌ Servicio de email no disponible")
            return 0
        
        conn = conectar_base_datos()
        cursor = conn.cursor()
        
        # Fechas para recordatorios
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        in_3_days = today + timedelta(days=3)
        
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
            
            print(f"📧 Enviando recordatorio a {nombre} {apellido} ({email}) - '{titulo}' - {days_left} días")
            
            # Enviar recordatorio
            success = email_service.send_return_reminder(
                user_email=email,
                user_name=f"{nombre} {apellido}",
                book_title=titulo,
                days_left=days_left
            )
            
            if success:
                sent_count += 1
        
        conn.close()
        print(f"✅ Recordatorios enviados: {sent_count}/{len(loans)}")
        return sent_count
        
    except Exception as e:
        print(f"❌ Error en recordatorios automáticos: {e}")
        return 0

def test_reminders():
    """
    Función de prueba para ver qué recordatorios se enviarían
    """
    print("🧪 MODO PRUEBA - Recordatorios que se enviarían:")
    return send_daily_reminders()

if __name__ == "__main__":
    # Ejecutar en modo prueba
    test_reminders()