# ===============================
#   IMPORTS Y CONFIGURACIÓN
# ===============================
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from functools import wraps
from models.Proyecto import Libro, Usuario, Prestamo, actualizar_libro, eliminar_libro, crear_tablas, prestar_libro, devolver_libro, actualizar_estructura_base_datos, verificar_consistencia_libros
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialización de la app Flask
app = Flask(__name__, 
           template_folder='../templates',  # Templates están en la carpeta padre
           static_folder='../static')       # Static está en la carpeta padre
app.secret_key = 'tu_clave_secreta'  # Necesaria para mensajes flash

# Crear tablas y actualizar estructura de la base de datos al iniciar la app
crear_tablas()
actualizar_estructura_base_datos()

# Limpiar todas las sesiones al reiniciar la aplicación
print("🧹 Limpiando sesiones previas...")
with app.app_context():
    pass  # Esto forzará la limpieza de cualquier sesión persistente

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
        from models.Proyecto import conectar_base_datos, Usuario
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

if __name__ == "__main__":
    send_daily_reminders()


# ===============================
#   IMPORTS PARA SISTEMA DE EMAIL
# ===============================
try:
    from flask_mail import Mail
    from config.email_config import get_email_config
    from services.email_services import EmailService
    EMAIL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema de email no disponible: {e}")
    EMAIL_AVAILABLE = False
    Mail = None
    get_email_config = None
    EmailService = None

# ===============================
#   CONFIGURACIÓN DEL SISTEMA DE EMAIL
# ===============================
if EMAIL_AVAILABLE:
    try:
        # Obtener configuración de email (desarrollo/producción)
        email_config = get_email_config()
        
        # Configurar Flask-Mail
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
        email_service = EmailService(app, mail)
        
        # Mostrar estado de configuración
        modo = "DESARROLLO (simula emails)" if email_config.MAIL_SUPPRESS_SEND else "PRODUCCIÓN (envía emails reales)"
        print(f"✅ Sistema de email configurado correctamente - Modo: {modo}")
        
    except Exception as e:
        print(f"❌ Error configurando email: {e}")
        email_service = None
else:
    mail = None
    email_service = None


# ===============================
#   AUTENTICACIÓN Y ROLES
# ===============================
def login_required(f):
    """
    Decorador para rutas que requieren login.
    Redirige a login si el usuario no está autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor, inicia sesión para acceder a esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """
    Decorador para rutas que requieren ciertos roles.
    Redirige si el usuario no tiene el rol adecuado.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Por favor, inicia sesión para acceder a esta página.", "warning")
                return redirect(url_for('login'))
            user = Usuario.obtener_por_documento(session['user_documento'])
            if not user:
                flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
                session.clear()
                return redirect(url_for('login'))
            if user.rol not in roles:
                flash("No tienes permiso para acceder a esta página.", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ===============================
#   RUTAS DE AUTENTICACIÓN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Ruta de login. Valida credenciales y redirige según el rol.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password") 
        print(f"DEBUG LOGIN: Intentando login con email: {email}")
        usuario = Usuario.obtener_por_email(email)
        
        if usuario:
            print(f"DEBUG LOGIN: Usuario encontrado: {usuario.nombre} {usuario.apellido}")
            print(f"DEBUG LOGIN: Hash almacenado: {usuario.password}")
            import hashlib
            hash_input = hashlib.sha256(password.encode()).hexdigest()
            print(f"DEBUG LOGIN: Hash de input: {hash_input}")
            print(f"DEBUG LOGIN: Verificación: {usuario.verificar_contraseña(password)}")
        else:
            print(f"DEBUG LOGIN: Usuario NO encontrado para email: {email}")
        
        if usuario and usuario.verificar_contraseña(password):
            session['user_id'] = usuario.id
            session['user_documento'] = usuario.documento
            session['user_rol'] = usuario.rol
            session['user_nombre'] = usuario.nombre
            flash(f"Inicio de sesión exitoso, Bienvenido {usuario.nombre}", "success")
            if usuario.rol in ['admin', 'bibliotecario']:
                return redirect(url_for('index'))
            else:
                return redirect(url_for('dashboard_usuario'))
        else:
            if not usuario:
                flash("Email no encontrado", "error")
            else:
                flash("Contraseña incorrecta", "error")
    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    """
    Cierra la sesión del usuario.
    """
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))


@app.route("/clear_all")
def clear_all():
    """
    Ruta especial para limpiar completamente todas las sesiones
    """
    session.clear()
    print("🧹 Sesión completamente limpiada")
    return redirect(url_for('login'))


# ===============================
#   DASHBOARDS
# ===============================
@app.route("/dashboard")
@login_required
def dashboard():
    """
    Dashboard general que redirige según el rol del usuario.
    """
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    if user.rol in ['admin', 'bibliotecario']:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('dashboard_usuario'))


@app.route("/dashboard/usuario")
@login_required
@role_required(['usuario'])
def dashboard_usuario():
    """
    Dashboard específico para usuarios normales.
    Muestra préstamos y multas del usuario.
    """
    # verificar_consistencia_libros() - REMOVIDO: Se ejecutaba en cada carga causando problemas
    
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    # Usar la función específica que ya incluye toda la información necesaria
    prestamos = Prestamo.obtener_prestamos_activos_por_usuario(user.documento)
    
    # Debug: verificar que los préstamos tienen ID
    print(f"DEBUG: Préstamos encontrados para usuario {user.documento}:")
    for p in prestamos:
        print(f"  - ID: {p.id}, Libro: {getattr(p, 'titulo_libro', 'N/A')}")
        
    multas = [p for p in prestamos if getattr(p, 'multa', 0) > 0]
    total_multas = sum(p.multa for p in multas)
    return render_template('user/dashboard_usuario.html', usuario=user, prestamos=prestamos, total_multas=total_multas)

@app.route("/perfil/editar", methods=["GET", "POST"])
@login_required
@role_required(['usuario'])
def editar_perfil_usuario():
    """
    Permite a un usuario editar su perfil.
    """
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == "POST":
        try:
            email = request.form.get("email")
            telefono = request.form.get("telefono")
            
            if not all([email, telefono]):
                flash("Email y teléfono son obligatorios.", "error")
                return redirect(url_for("dashboard_usuario"))

            if "@" not in email or "." not in email:
                flash("El email no es válido.", "error")
                return redirect(url_for("dashboard_usuario"))
            
            usuario_email_existente = Usuario.obtener_por_email(email)
            if usuario_email_existente and usuario_email_existente.documento != user.documento:
                flash("Ya existe un usuario con ese email.", "error")
                return redirect(url_for("dashboard_usuario"))
            
            from models.Proyecto import actualizar_usuario_por_documento
            exito, mensaje = actualizar_usuario_por_documento(user.documento, email=email, telefono=telefono)
            
            if exito:
                flash("Perfil actualizado correctamente.", "success")
            else:
                flash(mensaje, "error")
        except Exception as e:
            flash(f"Error al actualizar el perfil: {str(e)}", "error")
        return redirect(url_for("dashboard_usuario"))
    


# ===============================
#   GESTIÓN DE MULTAS (USUARIO)
# ===============================
@app.route("/pagar_multas", methods=["POST"])
@login_required
@role_required(['usuario'])
def pagar_multas():
    """
    Permite a un usuario pagar multas seleccionadas.
    """
    ids = request.form.getlist("ids_prestamos")
    if not ids:
        flash("No se seleccionaron multas para pagar.", "error")
        return redirect(url_for('dashboard_usuario'))
    for id_prestamo in ids:
        Prestamo.pagar_multas_por_usuario(id_prestamo)
    flash("Multas seleccionandas pagadas correctamente.", "success")
    return redirect(url_for('dashboard_usuario'))

@app.route("/pagar_multas_todas", methods=["POST"])
@login_required
@role_required(['usuario'])
def pagar_multas_todas():
    """
    Permite a un usuario pagar todas sus multas.
    """
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    Prestamo.pagar_multas_por_usuario(user.documento)
    flash("Todas las multas han sido pagadas.", "success")
    return redirect(url_for('dashboard_usuario'))


# ===============================
#   MENÚ PRINCIPAL (ADMIN/BIBLIOTECARIO)
# ===============================
@app.route("/")
def index():
    """
    Ruta principal: redirige al login si no está autenticado, 
    o al dashboard correspondiente según el rol.
    """
    # Si no hay sesión activa, ir al login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    # Redirigir según el rol
    if user.rol in ['admin', 'bibliotecario']:
        return render_template("admin/index.html")
    else:
        return redirect(url_for('dashboard_usuario')) 


# ===============================
#   CRUD DE LIBROS
# ===============================
@app.route("/libros")
@login_required
@role_required(['admin', 'bibliotecario'])
def listar_libros():
    """
    Lista todos los libros.
    """
    libros = Libro.obtener_todos()
    return render_template("admin/libros.html", libros=libros)


@app.route("/agregar_libro", methods=["GET", "POST"])
def agregar_libro_web():
    """
    Agrega un libro nuevo a la base de datos.
    """
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            titulo = request.form.get("titulo")
            autor = request.form.get("autor")
            editorial = request.form.get("editorial")
            año = request.form.get("año")
            genero = request.form.get("genero")
            imagen_file = request.files.get("imagen")
            imagen_bytes = None
            if imagen_file and imagen_file.filename:
                imagen_bytes = imagen_file.read()
            # Validar que todos los campos estén presentes
            if not all([titulo, autor, editorial, año, genero]):
                flash("Todos los campos son obligatorios.", "error")
                return render_template("admin/libros.html", libros=Libro.obtener_todos())
            # Convertir año a entero y validar
            try:
                año = int(año)
                if año < 0 or año > 2025:
                    flash("El año debe estar entre 0 y 2025.", "error")
                    return render_template("admin/libros.html", libros=Libro.obtener_todos())
            except (ValueError, TypeError):
                flash("El año debe ser un número válido.", "error")
                return render_template("admin/libros.html", libros=Libro.obtener_todos())
            # Generar nuevo ID
            libros = Libro.obtener_todos()
            nuevo_id = max([l.id_libro for l in libros], default=0) + 1
            # Crear y guardar el libro
            libro = Libro(id_libro=nuevo_id, titulo=titulo, autor=autor, editorial=editorial, año=año, genero=genero, imagen=imagen_bytes)
            libro.guardar()
            flash("Libro agregado correctamente.", "success")
            return redirect(url_for("listar_libros"))
        except Exception as e:
            flash(f"Error al agregar el libro: {str(e)}", "error")
            return render_template("admin/libros.html", libros=Libro.obtener_todos())
    # Para GET, mostrar el formulario (en la misma página libros.html)
    return render_template("admin/libros.html", libros=Libro.obtener_todos())

@app.route("/libros/eliminar", methods=["POST"])
def eliminar_libros_web():
    try:
        id_libro = request.form.get("id_libro")
        if not id_libro:
            flash("El ID del libro es obligatorio.", "error")
            return render_template("admin/libros.html", libros=Libro.obtener_todos())

        id_libro = int(id_libro)
        resultado = eliminar_libro(id_libro)
        
        if resultado and resultado.get("success"):
            flash(resultado["message"], "success")
        else:
            mensaje = resultado["message"] if resultado else "Error desconocido al eliminar el libro."
            flash(mensaje, "error")
            
        return redirect(url_for("listar_libros"))
    except ValueError:
        flash("El ID del libro debe ser un número válido.", "error")
        return render_template("admin/libros.html", libros=Libro.obtener_todos())
    except Exception as e:
        flash(f"Error al eliminar el libro: {str(e)}", "error")
        return render_template("admin/libros.html", libros=Libro.obtener_todos())

@app.route("/libros/actualizar", methods=["POST"])
def actualizar_libros_web():
    try:
        id_libro = request.form.get("id_libro")
        kwargs = {}
        
        if request.form.get("titulo"):
            kwargs['titulo'] = request.form.get("titulo")
        if request.form.get("autor"):
            kwargs['autor'] = request.form.get("autor")
        if request.form.get("editorial"):
            kwargs['editorial'] = request.form.get("editorial")
        if request.form.get("año"):
            try:
                año = int(request.form.get("año"))
                if año < 0 or año > 2025:
                    flash("El año debe estar entre 0 y 2025.", "error")
                    return render_template("admin/libros.html", libros=Libro.obtener_todos())
                kwargs['año'] = año
            except (ValueError, TypeError):
                flash("El año debe ser un número válido.", "error")
                return render_template("admin/libros.html", libros=Libro.obtener_todos())
        if request.form.get("genero"):
            kwargs['genero'] = request.form.get("genero")
        if request.form.get("disponible"):
            kwargs['disponible'] = request.form.get("disponible") == "si"
            
        if not id_libro:
            flash("El ID del libro es obligatorio.", "error")
            return render_template("admin/libros.html", libros=Libro.obtener_todos())

        id_libro = int(id_libro)
        actualizar_libro(id_libro, **kwargs)
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("listar_libros"))
        
    except ValueError:
        flash("El ID del libro debe ser un número válido.", "error")
        return render_template("admin/libros.html", libros=Libro.obtener_todos())
    except Exception as e:
        flash(f"Error al actualizar el libro: {str(e)}", "error")
        return render_template("admin/libros.html", libros=Libro.obtener_todos())

@app.route("/usuarios")
def listar_usuarios():
    usuarios = Usuario.obtener_todos()
    return render_template("admin/usuarios.html", usuarios=usuarios)   

@app.route("/libro/<int:id_libro>/imagen")
def obtener_imagen_libro(id_libro):
    libro = Libro.obtener_por_id(id_libro)

    # Si no hay libro o imagen, usar imagen predeterminada
    if not libro or not libro.imagen:
        try:
            print(f"[DEBUG] Sirviendo imagen predeterminada para libro id={id_libro}")
            with open('../static/images/ImagenLibro.png', 'rb') as f:
                imagen = f.read()
            mime_type = 'image/png'
            return Response(imagen, mimetype=mime_type)
        except Exception as e:
            print(f"[ERROR] No se pudo servir la imagen predeterminada para libro id={id_libro}: {e}")
            return "Sin imagen", 404

    # Si la imagen es string, intenta convertir a bytes (caso raro)
    imagen = libro.imagen
    if isinstance(imagen, str):
        try:
            print(f"[DEBUG] Convirtiendo imagen string a bytes para libro id={id_libro}")
            imagen = imagen.encode('latin1')  # o 'utf-8' según cómo se guardó
        except Exception as e:
            print(f"[ERROR] Imagen corrupta para libro id={id_libro}: {e}")
            # Si no se puede convertir, usar imagen predeterminada
            try:
                with open('../static/images/ImagenLibro.png', 'rb') as f:
                    imagen = f.read()
                mime_type = 'image/png'
                print(f"[DEBUG] Fallback a imagen predeterminada para libro id={id_libro}")
                return Response(imagen, mimetype=mime_type)
            except Exception as e2:
                print(f"[ERROR] Fallback fallido para libro id={id_libro}: {e2}")
                return "Sin imagen", 404

    # Solo si es bytes, detecta el tipo
    if isinstance(imagen, bytes):
        # Validar cabecera de imagen
        if imagen.startswith(b'\xFF\xD8\xFF'):
            mime_type = 'image/jpeg'
        elif imagen.startswith(b'\x89PNG'):
            mime_type = 'image/png'
        else:
            # Si no es JPEG ni PNG, usar imagen predeterminada
            print(f"[WARN] Imagen no válida para libro id={id_libro}, usando predeterminada")
            try:
                with open('../static/images/ImagenLibro.png', 'rb') as f:
                    imagen = f.read()
                mime_type = 'image/png'
                print(f"[DEBUG] Fallback a imagen predeterminada para libro id={id_libro}")
                return Response(imagen, mimetype=mime_type)
            except Exception as e2:
                print(f"[ERROR] Fallback fallido para libro id={id_libro}: {e2}")
                return "Sin imagen", 404
        print(f"[DEBUG] Sirviendo imagen de libro id={id_libro} con mime_type={mime_type}")
        return Response(imagen, mimetype=mime_type)
    else:
        print(f"[ERROR] Formato de imagen no soportado para libro id={id_libro}, usando predeterminada")
        try:
            with open('../static/images/ImagenLibro.png', 'rb') as f:
                imagen = f.read()
            mime_type = 'image/png'
            print(f"[DEBUG] Fallback a imagen predeterminada para libro id={id_libro}")
            return Response(imagen, mimetype=mime_type)
        except Exception as e2:
            print(f"[ERROR] Fallback fallido para libro id={id_libro}: {e2}")
            return "Sin imagen", 404

@app.route("/usuarios/agregar", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def agregar_usuario_web():
    if request.method == "POST":
        try:
            documento = request.form.get("documento")
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            telefono = request.form.get("telefono")
            email = request.form.get("email")
            password = request.form.get("password")
            rol = request.form.get("rol", "usuario")
            contrasena = request.form['password']
            
            hash_contra = generate_password_hash(contrasena)

            if not all([documento, nombre, apellido, telefono, email, hash_contra]):
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for("listar_usuarios"))

            # Verificar que el documento no exista ya
            usuario_existente = Usuario.obtener_por_documento(documento)
            if usuario_existente:
                flash("Ya existe un usuario con ese documento.", "error")
                return redirect(url_for("listar_usuarios"))

            # Verificar que el email no exista ya
            usuario_email = Usuario.obtener_por_email(email)
            if usuario_email:
                flash("Ya existe un usuario con ese email.", "error")
                return redirect(url_for("listar_usuarios"))

            usuario = Usuario(nombre=nombre, apellido=apellido, telefono=telefono, email=email, rol=rol, documento=documento)
            usuario.set_password(password)  # Establecer contraseña hasheada
            usuario.guardar()

            flash("Usuario agregado correctamente.", "success")
            return redirect(url_for("listar_usuarios"))
        except Exception as e:
            flash(f"Error al agregar el usuario: {str(e)}", "error")
            return redirect(url_for("listar_usuarios"))

    return render_template("admin/usuarios.html", usuarios=Usuario.obtener_todos())

@app.route("/usuarios/eliminar", methods=["POST"])
def eliminar_usuarios_web():
    try:
        documento = request.form.get("documento")
        if not documento:
            flash("El documento del usuario es obligatorio.", "error")
            return redirect(url_for("listar_usuarios"))

        from models.Proyecto import eliminar_usuario_por_documento
        exito, mensaje = eliminar_usuario_por_documento(documento)
        if exito:
            flash("Usuario eliminado correctamente.", "success")
        else:
            flash(mensaje, "error")
        return redirect(url_for("listar_usuarios"))
    except Exception as e:
        flash(f"Error al eliminar el usuario: {str(e)}", "error")
        return render_template("admin/usuarios.html", usuarios=Usuario.obtener_todos())

@app.route("/usuarios/actualizar", methods=["POST"])
def actualizar_usuarios_web():
    try:
        documento = request.form.get("documento")
        kwargs = {}
        
        if request.form.get("nombre"):
            kwargs['nombre'] = request.form.get("nombre")
        if request.form.get("apellido"):
            kwargs['apellido'] = request.form.get("apellido")
        if request.form.get("telefono"):
            kwargs['telefono'] = request.form.get("telefono")
        if request.form.get("email"):
            kwargs['email'] = request.form.get("email")
        if request.form.get("rol"):
            kwargs['rol'] = request.form.get("rol")
            
        if not documento:
            flash("El documento del usuario es obligatorio.", "error")
            return redirect(url_for("listar_usuarios"))

        from models.Proyecto import actualizar_usuario_por_documento
        exito, mensaje = actualizar_usuario_por_documento(documento, **kwargs)
        if exito:
            flash("Usuario actualizado correctamente.", "success")
        else:
            flash(mensaje, "error")
        return redirect(url_for("listar_usuarios"))
        
    except Exception as e:
        flash(f"Error al actualizar el usuario: {str(e)}", "error")
        return redirect(url_for("listar_usuarios"))

@app.route("/prestamos/menu")
def menu_prestamos():
    prestamos = Prestamo.obtener_todos()
    usuarios = Usuario.obtener_todos()
    libros = Libro.obtener_todos()
    generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
    return render_template(
        "admin/prestamos.html",
        prestamos=Prestamo.obtener_todos(),
        usuarios=Usuario.obtener_todos(),
        libros=Libro.obtener_todos(),
        generos=generos,
        total_generos=total_generos
    )

@app.route("/prestamos")
@login_required  
@role_required(['admin', 'bibliotecario'])
def listar_prestamos():
    prestamos = Prestamo.obtener_todos()
    usuarios = Usuario.obtener_todos()
    libros = Libro.obtener_disponibles()
    todos_los_libros = Libro.obtener_todos()  # Para calcular estadísticas
    generos, total_generos = calcular_estadisticas_generos(prestamos, todos_los_libros)
    return render_template(
        "admin/prestamos_lista.html",
        prestamos=prestamos,
        usuarios=usuarios,
        libros=libros,
        todos_los_libros=todos_los_libros,
        generos=generos,
        total_generos=total_generos
    )

def calcular_estadisticas_generos(prestamos, libros):
    """Helper function para calcular estadísticas de géneros para prestamos.html"""
    generos = {}
    libros_sin_genero = 0
    
    print(f"[DEBUG] Calculando estadísticas de géneros para {len(prestamos)} préstamos y {len(libros)} libros")
    
    # Procesar TODOS los libros
    for libro in libros:
        genero = getattr(libro, "genero", None)
        print(f"[DEBUG] Libro ID {libro.id_libro} tiene género: '{genero}'")
        
        # Manejar libros sin género
        if not genero or genero.strip() == "":
            genero = "Sin género"
            libros_sin_genero += 1
        else:
            # Normalizar género
            genero = genero.strip().title()
            
        # Contar el género
        generos[genero] = generos.get(genero, 0) + 1
    
    # Mostrar resumen final (FUERA del bucle)
    print(f"[DEBUG] Libros sin género: {libros_sin_genero}")
    print(f"[DEBUG] Conteo final de géneros: {generos}")
    print(f"[DEBUG] Total de géneros únicos: {len(generos)}")
    
    total_generos = len(generos)
    return generos, total_generos

@app.route("/prestamos/prestar", methods=["GET", "POST"])
def prestar_libro_web():
    print(f"DEBUG: Entrando a prestar_libro_web, método: {request.method}")
    if request.method == "POST":
        print("DEBUG: Procesando POST para prestar libro")
        try:
            documento_usuario = request.form.get("documento_usuario")
            id_libro = request.form.get("id_libro")
            dias = request.form.get("dias")
            
            print(f"DEBUG: Datos recibidos - documento_usuario: {documento_usuario}, id_libro: {id_libro}, dias: {dias}")
            
            # WORKAROUND TEMPORAL: Si documento_usuario es None/vacío, usar el de la sesión
            if not documento_usuario or documento_usuario == 'None':
                documento_usuario = session.get('user_documento')
                print(f"DEBUG: Documento vacío/None, usando de sesión: {documento_usuario}")
            elif documento_usuario == 'AUTO':
                documento_usuario = session.get('user_documento')
                print(f"DEBUG: Documento AUTO convertido a: {documento_usuario}")
            
            # WORKAROUND TEMPORAL: Si dias viene como string inválido, usar 7
            if not dias or not dias.isdigit():
                dias = '7'
                print(f"DEBUG: Días inválidos, usando por defecto: {dias}")
                
            if not documento_usuario:
                print("DEBUG: ERROR - No se pudo obtener el documento del usuario de la sesión")
                flash("Error: No se pudo obtener el documento del usuario.", "error")
                return redirect(url_for("dashboard_usuario"))

            print(f"DEBUG: Validando campos - documento_usuario: {bool(documento_usuario)}, id_libro: {bool(id_libro)}, dias: {bool(dias)}")
            if not all([documento_usuario, id_libro, dias]):
                print("DEBUG: ERROR - Campos faltantes")
                flash("Todos los campos son obligatorios.", "error")
                prestamos = Prestamo.obtener_todos()
                usuarios = Usuario.obtener_todos()
                libros = Libro.obtener_todos()
                generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
                return render_template("admin/prestamos.html", prestamos=prestamos, usuarios=usuarios, libros=libros, generos=generos, total_generos=total_generos)

            id_libro = int(id_libro)
            dias = int(dias)
            
            print(f"DEBUG: Intentando prestar libro ID: {id_libro} a usuario: {documento_usuario} por {dias} días")

            # Verificar que el libro esté realmente disponible
            libro = Libro.obtener_por_id(int(id_libro))
            if not libro or not libro.disponible:
                flash('El libro seleccionado no está disponible para préstamo', 'error')
                return redirect(url_for('listar_prestamos'))

            resultado = prestar_libro(id_libro, documento_usuario, dias)
            print(f"DEBUG: Resultado del préstamo: {resultado}")
            
            if resultado.get("success", True):
                flash("Préstamo registrado correctamente.", "success")
                
                # Redirigir según el rol del usuario
                user_role = session.get('user_rol')  # CORREGIDO: era 'user_role', ahora 'user_rol'
                print(f"DEBUG: Rol del usuario para redirección: '{user_role}'")
                if user_role == 'usuario':
                    print("DEBUG: Redirigiendo a dashboard_usuario")
                    return redirect(url_for("dashboard_usuario"))
                else:
                    print(f"DEBUG: Rol no es 'usuario', redirigiendo a menu_prestamos")
                    return redirect(url_for("menu_prestamos"))
            else:
                flash(resultado.get("message", "Error al registrar el préstamo."), "error")
                prestamos = Prestamo.obtener_todos()
                usuarios = Usuario.obtener_todos()
                libros = Libro.obtener_todos()
                generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
                return render_template("admin/prestamos.html", prestamos=prestamos, usuarios=usuarios, libros=libros, generos=generos, total_generos=total_generos)
        except ValueError as ve:
            print(f"DEBUG: ValueError en prestar libro: {ve}")
            flash("Los campos ID de libro y días deben ser números válidos.", "error")
            prestamos = Prestamo.obtener_todos()
            usuarios = Usuario.obtener_todos()
            libros = Libro.obtener_todos()
            generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
            return render_template("admin/prestamos.html", prestamos=prestamos, usuarios=usuarios, libros=libros, generos=generos, total_generos=total_generos)
        except Exception as e:
            print(f"DEBUG: Exception general en prestar libro: {e}")
            flash(f"Error al registrar el préstamo: {str(e)}", "error")
            prestamos = Prestamo.obtener_todos()
            usuarios = Usuario.obtener_todos()
            libros = Libro.obtener_todos()
            generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
            return render_template("admin/prestamos.html", prestamos=prestamos, usuarios=usuarios, libros=libros, generos=generos, total_generos=total_generos)

    # Si es GET, redirigir según el rol del usuario
    print("DEBUG: Método GET en prestar_libro_web - redirigiendo según rol")
    user_role = session.get('user_rol')  # CORREGIDO: era 'user_role', ahora 'user_rol'
    if user_role == 'usuario':
        print("DEBUG: Usuario normal, redirigiendo a dashboard")
        return redirect(url_for("dashboard_usuario"))
    else:
        print("DEBUG: Admin/bibliotecario, mostrando página de préstamos")
        prestamos = Prestamo.obtener_todos()
        usuarios = Usuario.obtener_todos()
        libros = Libro.obtener_todos()
        generos, total_generos = calcular_estadisticas_generos(prestamos, libros)
        return render_template("admin/prestamos.html", prestamos=prestamos, usuarios=usuarios, libros=libros, generos=generos, total_generos=total_generos)

@app.route("/prestamos/devolver/", methods=["POST"])
def devolver_libro_web():
    try:
        id_prestamo = request.form.get("id_prestamo")
        redirect_to = request.form.get("redirect_to")
        
        print(f"DEBUG: Intentando devolver préstamo ID: {id_prestamo}")
        print(f"DEBUG: Redirect to: {redirect_to}")
        
        resultado = devolver_libro(id_prestamo)
        print(f"DEBUG: Resultado devolución: {resultado}")
        
        if resultado and resultado.get("success", False):
            flash("Libro devuelto correctamente.", "success")
        else:
            flash(f"Error: {resultado.get('message', 'Error desconocido')}", "error")
        
        # Decidir dónde redirigir basado en el parámetro
        if redirect_to == "dashboard_usuario":
            return redirect(url_for("dashboard_usuario"))
        else:
            return redirect(url_for("menu_prestamos"))
            
    except Exception as e:
        flash(f"Error al devolver el libro: {str(e)}", "error")
        
        # También manejar el error según dónde se solicitó la devolución
        redirect_to = request.form.get("redirect_to")
        if redirect_to == "dashboard_usuario":
            return redirect(url_for("dashboard_usuario"))
        else:
            return redirect(url_for("menu_prestamos"))

@app.route("/prestamos/devolver_multiples/", methods=["POST"])
def devolver_libros_multiples():
    try:
        # Obtener la lista de IDs de préstamos como string separado por comas
        ids_prestamos_str = request.form.get("ids_prestamos")
        
        if not ids_prestamos_str:
            flash("No se seleccionaron libros para devolver.", "error")
            return redirect(url_for("menu_prestamos"))
        
        # Convertir string a lista de enteros
        try:
            ids_prestamos = [int(id_str.strip()) for id_str in ids_prestamos_str.split(',') if id_str.strip()]
        except (ValueError, TypeError):
            flash("Error en los datos de los préstamos seleccionados.", "error")
            return redirect(url_for("menu_prestamos"))
        
        if not ids_prestamos:
            flash("No se seleccionaron libros válidos para devolver.", "error")
            return redirect(url_for("menu_prestamos"))
        
        # Importar la nueva función de devolución múltiple
        from models.Proyecto import devolver_libros_multiples as devolver_multiples_func
        
        # Procesar devoluciones múltiples
        resultados = devolver_multiples_func(ids_prestamos)
        
        # Analizar resultados
        exitosos = len([r for r in resultados if r['exito']])
        fallidos = len(resultados) - exitosos
        
        if exitosos > 0:
            flash(f"✅ Se devolvieron {exitosos} libro{'s' if exitosos != 1 else ''} correctamente.", "success")
        
        if fallidos > 0:
            errores = [r['error'] for r in resultados if not r['exito']]
            flash(f"❌ {fallidos} devolución{'es' if fallidos != 1 else ''} fallida{'s' if fallidos != 1 else ''}: {'; '.join(errores)}", "error")
        
        return redirect(url_for("menu_prestamos"))
        
    except Exception as e:
        flash(f"Error al procesar las devoluciones múltiples: {str(e)}", "error")
        return redirect(url_for("menu_prestamos"))


# ===============================
#   (Resto de rutas CRUD, APIs, usuarios, préstamos...)
#   ...existing code...

# ===============================
#   FIN DE ARCHIVO
# ===============================

@app.route("/libros/eliminar/<int:id_libro>")
def eliminar_libro_web(id_libro):
    try:
        eliminar_libro(id_libro)
        flash("Libro eliminado correctamente.", "success")
        return redirect(url_for("listar_libros"))
    except Exception as e:
        flash(f"Error al eliminar el libro: {str(e)}", "error")
        return redirect(url_for("listar_libros"))

@app.route("/usuarios/editar/<documento>", methods=["GET", "POST"])
def editar_usuario(documento):
    usuario = Usuario.obtener_por_documento(documento)
    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("listar_usuarios"))

    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            telefono = request.form.get("telefono")
            email = request.form.get("email")
            rol = request.form.get("rol", "normal")

            if not all([nombre, apellido, telefono, email]):
                flash("Todos los campos son obligatorios.", "error")
                return redirect(url_for("listar_usuarios"))

            # Usar la función de actualización por documento
            from models.Proyecto import actualizar_usuario_por_documento
            exito, mensaje = actualizar_usuario_por_documento(documento, 
                                                            nombre=nombre, 
                                                            apellido=apellido, 
                                                            telefono=telefono, 
                                                            email=email, 
                                                            rol=rol)
            if exito:
                flash("Usuario editado correctamente.", "success")
            else:
                flash(mensaje, "error")
            return redirect(url_for("listar_usuarios"))
        except Exception as e:
            flash(f"Error al editar el usuario: {str(e)}", "error")
            return redirect(url_for("listar_usuarios"))

    return redirect(url_for("listar_usuarios"))

@app.route("/usuarios/eliminar/<documento>")
def eliminar_usuario_web(documento):
    try:
        from models.Proyecto import eliminar_usuario_por_documento
        exito, mensaje = eliminar_usuario_por_documento(documento)
        if exito:
            flash("Usuario eliminado correctamente.", "success")
        else:
            flash(mensaje, "error")
        return redirect(url_for("listar_usuarios"))
    except Exception as e:
        flash(f"Error al eliminar el usuario: {str(e)}", "error")
        return redirect(url_for("listar_usuarios"))

@app.route("/verificar_consistencia")
def verificar_consistencia_web():
    """Verifica y corrige inconsistencias en la base de datos"""
    try:
        from models.Proyecto import verificar_consistencia_libros
        inconsistencias = verificar_consistencia_libros()
        
        if inconsistencias:
            for inconsistencia in inconsistencias:
                flash(inconsistencia, "warning")
            flash(f"Se corrigieron {len(inconsistencias)} inconsistencias.", "success")
        else:
            flash("No se encontraron inconsistencias en la base de datos.", "info")
            
        return redirect(url_for("menu_principal"))
    except Exception as e:
        flash(f"Error al verificar consistencia: {str(e)}", "error")
        return redirect(url_for("menu_principal"))

# =================================================================
# RUTA TEMPORAL PARA CREAR USUARIOS DE PRUEBA
# =================================================================

@app.route("/crear_usuarios_prueba")
def crear_usuarios_prueba_web():
    """Ruta temporal para crear usuarios de prueba"""
    try:
        from models.Proyecto import crear_usuarios_prueba
        crear_usuarios_prueba()
        flash("Usuarios de prueba creados correctamente", "success")
        return """
        <h2>Usuarios creados:</h2>
        <ul>
            <li><strong>Admin:</strong> admin@biblioteca.com / admin123</li>
            <li><strong>Bibliotecario:</strong> bibliotecario@biblioteca.com / biblio123</li>
            <li><strong>Usuario:</strong> usuario@biblioteca.com / user123</li>
        </ul>
        <a href="/login">Ir al Login</a>
        """
    except Exception as e:
        return f"Error: {e}"

# =================================================================
# RUTAS DE API PARA BÚSQUEDA EN TIEMPO REAL
# =================================================================

@app.route("/api/buscar_usuarios")
def buscar_usuarios_api():
    """API para buscar usuarios por documento o nombre"""
    termino = request.args.get('q', '')
    if len(termino) < 2:
        return jsonify([])
    
    try:
        from models.Proyecto import Usuario
        usuarios = Usuario.buscar_por_documento_o_nombre(termino)
        resultado = []
        for usuario in usuarios[:10]:  # Limitar a 10 resultados
            resultado.append({
                'documento': usuario.documento,
                'nombre_completo': f"{usuario.nombre} {usuario.apellido}",
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'rol': usuario.rol
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/buscar_libros")
def buscar_libros_api():
    """API para dashboard de usuario - Solo libros disponibles"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            # Si no hay query, devolver solo libros disponibles
            libros = Libro.obtener_disponibles()
        else:
            libros = Libro.buscar_disponibles_por_termino(query)
        
        # Convertir a formato JSON usando el método to_dict()
        libros_json = []
        for libro in libros:
            try:
                libro_dict = libro.to_dict()
                libros_json.append(libro_dict)
            except Exception as e:
                # Si hay error con un libro específico, saltarlo
                print(f"Error procesando libro {libro.id_libro}: {e}")
                continue
        
        return jsonify(libros_json)
    except Exception as e:
        print(f"Error en buscar_libros_api: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/buscar_libros_admin")
def buscar_libros_admin_api():
    """API para administradores - Todos los libros con información completa"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            # Si no hay query, devolver todos los libros
            libros = Libro.obtener_todos()
        else:
            libros = Libro.buscar_por_termino(query)
        
        # Convertir a formato JSON usando el método to_dict()
        libros_json = []
        for libro in libros:
            try:
                libro_dict = libro.to_dict()
                libros_json.append(libro_dict)
            except Exception as e:
                # Si hay error con un libro específico, saltarlo
                print(f"Error procesando libro {libro.id_libro}: {e}")
                continue
        
        return jsonify(libros_json)
    except Exception as e:
        print(f"Error en buscar_libros_admin_api: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/prestamos_usuario/<documento>")
def prestamos_usuario_api(documento):
    """API para obtener los préstamos activos de un usuario"""
    try:
        from models.Proyecto import Prestamo
        prestamos = Prestamo.obtener_prestamos_activos_por_usuario(documento)
        resultado = []
        for prestamo in prestamos:
            resultado.append({
                'id_prestamo': prestamo.id,
                'id_libro': prestamo.id_libro,
                'titulo': prestamo.titulo_libro,
                'autor': prestamo.autor_libro,
                'fecha_prestamo': prestamo.fecha_prestamo,
                'fecha_devolucion_esperada': prestamo.fecha_devolucion_esperada,
                'nombre_usuario': prestamo.nombre_usuario,
                'apellido_usuario': prestamo.apellido_usuario
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =================================================================
# RUTAS DE ADMINISTRACIÓN DE EMAILS
# =================================================================

@app.route("/admin/email_config")
@login_required
@role_required(['admin'])
def email_config_admin():
    """
    Panel de administración para configurar emails
    """
    global email_service
    
    # Estado actual del sistema
    if email_service and hasattr(email_service, 'mail'):
        suppress_send = app.config.get('MAIL_SUPPRESS_SEND', True)
        email_username = app.config.get('MAIL_USERNAME', 'No configurado')
        status = "activo"
    else:
        suppress_send = True
        email_username = "No disponible"
        status = "inactivo"
    
    config_info = {
        'status': status,
        'modo': 'Desarrollo (simula)' if suppress_send else 'Producción (envía reales)',
        'email_username': email_username,
        'suppress_send': suppress_send
    }
    
    return f"""
    <h1>🔧 Configuración de Emails</h1>
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Estado Actual:</h2>
        <ul>
            <li><strong>Estado:</strong> {config_info['status']}</li>
            <li><strong>Modo:</strong> {config_info['modo']}</li>
            <li><strong>Email configurado:</strong> {config_info['email_username']}</li>
        </ul>
        
        <h2>Acciones:</h2>
        <div style="margin: 10px 0;">
            <a href="/admin/email_toggle" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                {'🔇 Activar Emails Reales' if suppress_send else '🔕 Desactivar Emails (Modo Testing)'}
            </a>
        </div>
        
        <div style="margin: 10px 0;">
            <a href="/admin/test_email" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                📧 Enviar Email de Prueba
            </a>
        </div>
        
        <div style="margin: 10px 0;">
            <a href="/admin/enviar_recordatorios" style="background: #ff6b35; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                🔔 Enviar Recordatorios Ahora
            </a>
        </div>
        
        <div style="margin: 10px 0;">
            <a href="/" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                ⬅️ Volver al Menu Principal
            </a>
        </div>
        
        <h3>⚠️ Importante:</h3>
        <p><strong>Modo Desarrollo:</strong> Los emails se simulan (no se envían realmente)</p>
        <p><strong>Modo Producción:</strong> Los emails se envían realmente a los usuarios</p>
    </div>
    """

@app.route("/admin/email_toggle")
@login_required  
@role_required(['admin'])
def email_toggle():
    """
    Alterna entre modo desarrollo y producción para emails
    """
    current_suppress = app.config.get('MAIL_SUPPRESS_SEND', True)
    new_suppress = not current_suppress
    
    # Actualizar configuración
    app.config['MAIL_SUPPRESS_SEND'] = new_suppress
    
    modo = "Desarrollo (simula emails)" if new_suppress else "Producción (envía emails reales)"
    flash(f"Configuración de email cambiada a: {modo}", "success")
    
    return redirect(url_for('email_config_admin'))

@app.route("/admin/test_email")
@login_required
@role_required(['admin'])  
def test_email_admin():
    """
    Envía un email de prueba al administrador
    """
    if not email_service:
        flash("Sistema de email no disponible", "error")
        return redirect(url_for('email_config_admin'))
    
    user = Usuario.obtener_por_documento(session['user_documento'])
    if not user:
        flash("Usuario no encontrado. Por favor, inicia sesión nuevamente.", "error")
        session.clear()
        return redirect(url_for('login'))
    
    if not user.email:
        flash("El administrador no tiene email configurado", "warning")
        return redirect(url_for('email_config_admin'))
    
    # Enviar email de prueba
    success = email_service.send_loan_confirmation(
        user_email=user.email,
        user_name=f"{user.nombre} {user.apellido}",
        book_title="📧 Email de Prueba del Sistema",
        due_date="2025-12-31"
    )
    
    if success:
        modo = "simulado" if app.config.get('MAIL_SUPPRESS_SEND', True) else "enviado realmente"
        flash(f"Email de prueba {modo} exitosamente a {user.email}", "success")
    else:
        flash("Error enviando email de prueba", "error")
        
    return redirect(url_for('email_config_admin'))

@app.route("/admin/enviar_recordatorios")
@login_required
@role_required(['admin'])
def enviar_recordatorios_manual():
    """
    Ejecuta manualmente el envío de recordatorios desde la web
    """
    if not email_service:
        flash("Sistema de email no disponible", "error")
        return redirect(url_for('email_config_admin'))
    
    try:
        # Importar función desde send_reminders.py
        from tasks.send_reminders import send_reminders_standalone
        
        # Ejecutar recordatorios
        sent_count = send_reminders_standalone()
        
        if sent_count == 0:
            flash("✅ No hay préstamos próximos a vencer hoy", "info")
        else:
            modo = "simulados" if app.config.get('MAIL_SUPPRESS_SEND', True) else "enviados realmente"
            flash(f"✅ Recordatorios {modo}: {sent_count} emails procesados correctamente", "success")
        
    except Exception as e:
        flash(f"❌ Error enviando recordatorios: {str(e)}", "error")
        
    return redirect(url_for('email_config_admin'))

if __name__ == "__main__":
    app.run(debug=True)