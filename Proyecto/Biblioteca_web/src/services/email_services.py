# ===============================
#   SERVICIO DE EMAIL
# ===============================

from flask_mail import Mail, Message
from datetime import datetime
import os

class EmailService:
    def __init__(self, app=None, mail=None):
        self.app = app
        self.mail = mail
    
    def send_email(self, to_email, subject, html_body, text_body=None):
        """
        Envía un email básico
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body,
                body=text_body or "Ver versión HTML del mensaje"
            )
            
            self.mail.send(msg)
            print(f"✅ Email enviado a {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email a {to_email}: {str(e)}")
            return False
    
    def send_loan_confirmation(self, user_email, user_name, book_title, due_date):
        """
        Envía confirmación de préstamo
        """
        subject = f"✅ Préstamo confirmado: {book_title}"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">📚 ¡Préstamo Confirmado!</h2>
            
            <p>Hola <strong>{user_name}</strong>,</p>
            
            <p>Te confirmamos que has tomado prestado el siguiente libro:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0;">
                <h3 style="margin: 0; color: #28a745;">📖 {book_title}</h3>
                <p style="margin: 10px 0 0 0;"><strong>Fecha de devolución:</strong> {due_date}</p>
            </div>
            
            <p><strong>⚠️ Importante:</strong> Recuerda devolver el libro a tiempo para evitar multas.</p>
            
            <hr style="margin: 30px 0;">
            <p style="color: #6c757d; font-size: 12px;">
                Este mensaje fue enviado automáticamente por el Sistema de Biblioteca.<br>
                No responder a este correo.
            </p>
        </div>
        """
        
        text_body = f"""
        ¡Préstamo Confirmado!
        
        Hola {user_name},
        
        Libro prestado: {book_title}
        Fecha de devolución: {due_date}
        
        Recuerda devolver a tiempo.
        
        Sistema de Biblioteca
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_return_reminder(self, user_email, user_name, book_title, days_left):
        """
        Envía recordatorio de devolución
        """
        if days_left <= 0:
            urgency_icon = "🔴"
            urgency_text = "VENCIDO"
            color = "#dc3545"
        elif days_left == 1:
            urgency_icon = "⚠️"
            urgency_text = "URGENTE"
            color = "#fd7e14"
        else:
            urgency_icon = "📅"
            urgency_text = "Recordatorio"
            color = "#17a2b8"
        
        subject = f"{urgency_icon} {urgency_text}: Devolver '{book_title}'"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: {color};">{urgency_icon} {urgency_text}</h2>
            
            <p>Hola <strong>{user_name}</strong>,</p>
            
            <p>Te recordamos que debes devolver el siguiente libro:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-left: 4px solid {color}; margin: 20px 0;">
                <h3 style="margin: 0; color: {color};">📖 {book_title}</h3>
                <p style="margin: 10px 0 0 0; font-size: 18px;">
                    <strong>Días restantes: {days_left}</strong>
                </p>
            </div>
            
            {f'<div style="background: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px; margin: 20px 0;"><strong>⚠️ ¡Devuélvelo hoy para evitar multas!</strong></div>' if days_left <= 1 else ''}
            
            <p>Gracias por usar nuestro sistema de biblioteca.</p>
            
            <hr style="margin: 30px 0;">
            <p style="color: #6c757d; font-size: 12px;">
                Este mensaje fue enviado automáticamente por el Sistema de Biblioteca.<br>
                No responder a este correo.
            </p>
        </div>
        """
        
        return self.send_email(user_email, subject, html_body)