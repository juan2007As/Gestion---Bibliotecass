
# ===============================
#   IMPORTS Y CONFIGURACIÓN
# ===============================
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from functools import wraps
from Proyecto import Libro, Usuario, Prestamo, actualizar_libro, eliminar_libro, crear_tablas, prestar_libro, devolver_libro, actualizar_estructura_base_datos
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialización de la app Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesaria para mensajes flash

# Crear tablas y actualizar estructura de la base de datos al iniciar la app
crear_tablas()
actualizar_estructura_base_datos()

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
        usuario = Usuario.obtener_por_email(email)
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
    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Cierra la sesión del usuario.
    """
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
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
    user = Usuario.obtener_por_documento(session['user_documento'])
    prestamos = [p for p in Prestamo.obtener_todos() if p.documento_usuario == user.documento]
    multas = [p for p in prestamos if getattr(p, 'multa', 0) > 0]
    total_multas = sum(p.multa for p in multas)
    return render_template('dashboard_usuario.html', usuario=user, prestamos=prestamos, total_multas=total_multas)


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
    Prestamo.pagar_multas_por_usuario(user.documento)
    flash("Todas las multas han sido pagadas.", "success")
    return redirect(url_for('dashboard_usuario'))


# ===============================
#   MENÚ PRINCIPAL (ADMIN/BIBLIOTECARIO)
# ===============================
@app.route("/")
@login_required
def index():
    """
    Menú principal para admin y bibliotecario.
    """
    user = Usuario.obtener_por_documento(session['user_documento'])
    if user.rol not in ['admin', 'bibliotecario']:
        return redirect(url_for('dashboard_usuario'))
    return render_template("index.html") 


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
    return render_template("libros.html", libros=libros)


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
                return render_template("libros.html", libros=Libro.obtener_todos())
            # Convertir año a entero y validar
            try:
                año = int(año)
                if año < 0 or año > 2025:
                    flash("El año debe estar entre 0 y 2025.", "error")
                    return render_template("libros.html", libros=Libro.obtener_todos())
            except (ValueError, TypeError):
                flash("El año debe ser un número válido.", "error")
                return render_template("libros.html", libros=Libro.obtener_todos())
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
            return render_template("libros.html", libros=Libro.obtener_todos())
    # Para GET, mostrar el formulario (en la misma página libros.html)
    return render_template("libros.html", libros=Libro.obtener_todos())

@app.route("/libros/eliminar", methods=["POST"])
def eliminar_libros_web():
    try:
        id_libro = request.form.get("id_libro")
        if not id_libro:
            flash("El ID del libro es obligatorio.", "error")
            return render_template("libros.html", libros=Libro.obtener_todos())

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
        return render_template("libros.html", libros=Libro.obtener_todos())
    except Exception as e:
        flash(f"Error al eliminar el libro: {str(e)}", "error")
        return render_template("libros.html", libros=Libro.obtener_todos())

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
                    return render_template("libros.html", libros=Libro.obtener_todos())
                kwargs['año'] = año
            except (ValueError, TypeError):
                flash("El año debe ser un número válido.", "error")
                return render_template("libros.html", libros=Libro.obtener_todos())
        if request.form.get("genero"):
            kwargs['genero'] = request.form.get("genero")
        if request.form.get("disponible"):
            kwargs['disponible'] = request.form.get("disponible") == "si"
            
        if not id_libro:
            flash("El ID del libro es obligatorio.", "error")
            return render_template("libros.html", libros=Libro.obtener_todos())

        id_libro = int(id_libro)
        actualizar_libro(id_libro, **kwargs)
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("listar_libros"))
        
    except ValueError:
        flash("El ID del libro debe ser un número válido.", "error")
        return render_template("libros.html", libros=Libro.obtener_todos())
    except Exception as e:
        flash(f"Error al actualizar el libro: {str(e)}", "error")
        return render_template("libros.html", libros=Libro.obtener_todos())

@app.route("/usuarios")
def listar_usuarios():
    usuarios = Usuario.obtener_todos()
    return render_template("usuarios.html", usuarios=usuarios)   

@app.route("/libro/<int:id_libro>/imagen")
def obtener_imagen_libro(id_libro):
    libro = Libro.obtener_por_id(id_libro)

    # Si no hay libro o imagen, usar imagen predeterminada
    if not libro or not libro.imagen:
        try:
            print(f"[DEBUG] Sirviendo imagen predeterminada para libro id={id_libro}")
            with open('Biblioteca_web/static/imagenes/ImagenLibro.png', 'rb') as f:
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
                with open('Biblioteca_web/static/imagenes/ImagenLibro.png', 'rb') as f:
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
                with open('Biblioteca_web/static/imagenes/ImagenLibro.png', 'rb') as f:
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
            with open('Biblioteca_web/static/imagenes/ImagenLibro.png', 'rb') as f:
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

    return render_template("agregar_usuarios.html")

@app.route("/usuarios/eliminar", methods=["POST"])
def eliminar_usuarios_web():
    try:
        documento = request.form.get("documento")
        if not documento:
            flash("El documento del usuario es obligatorio.", "error")
            return redirect(url_for("listar_usuarios"))

        from Proyecto import eliminar_usuario_por_documento
        exito, mensaje = eliminar_usuario_por_documento(documento)
        if exito:
            flash("Usuario eliminado correctamente.", "success")
        else:
            flash(mensaje, "error")
        return redirect(url_for("listar_usuarios"))
    except Exception as e:
        flash(f"Error al eliminar el usuario: {str(e)}", "error")
        return render_template("usuarios.html", usuarios=Usuario.obtener_todos())

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

        from Proyecto import actualizar_usuario_por_documento
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
    # Calcular estadística de géneros
    generos = {}
    for prestamo in prestamos:
        genero = getattr(prestamo, "genero_libro", None)
        if genero is None and hasattr(prestamo, "id_libro"):
            libro = next((l for l in libros if getattr(l, "id_libro", None) == getattr(prestamo, "id_libro", None)), None)
            genero = getattr(libro, "genero", None) if libro else None
        if genero:
            generos[genero] = generos.get(genero, 0) + 1
    total_generos = len(generos)
    return render_template(
        "prestamos.html",
        prestamos=prestamos,
        usuarios=usuarios,
        libros=libros,
        generos=generos,
        total_generos=total_generos
    )

@app.route("/prestamos")
@login_required  
@role_required(['admin', 'bibliotecario'])
def listar_prestamos():
    prestamos = Prestamo.obtener_todos()
    usuarios = Usuario.obtener_todos()
    libros = Libro.obtener_todos()
    # Calcular estadística de géneros
    generos = {}
    for prestamo in prestamos:
        genero = getattr(prestamo, "genero_libro", None)
        if genero is None and hasattr(prestamo, "id_libro"):
            libro = next((l for l in libros if getattr(l, "id_libro", None) == getattr(prestamo, "id_libro", None)), None)
            genero = getattr(libro, "genero", None) if libro else None
        if genero:
            generos[genero] = generos.get(genero, 0) + 1
    total_generos = len(generos)
    return render_template(
        "prestamos_lista.html",
        prestamos=prestamos,
        usuarios=usuarios,
        libros=libros,
        generos=generos,
        total_generos=total_generos
    )

@app.route("/prestamos/prestar", methods=["GET", "POST"])
def prestar_libro_web():
    if request.method == "POST":
        try:
            documento_usuario = request.form.get("documento_usuario")
            id_libro = request.form.get("id_libro")
            dias = request.form.get("dias")

            if not all([documento_usuario, id_libro, dias]):
                flash("Todos los campos son obligatorios.", "error")
                return render_template("prestamos.html", usuarios=Usuario.obtener_todos(), libros=Libro.obtener_todos())

            id_libro = int(id_libro)
            dias = int(dias)

            resultado = prestar_libro(id_libro, documento_usuario, dias)
            if resultado.get("success", True):
                flash("Préstamo registrado correctamente.", "success")
                return redirect(url_for("listar_prestamos"))
            else:
                flash(resultado.get("message", "Error al registrar el préstamo."), "error")
                return render_template("prestamos.html", usuarios=Usuario.obtener_todos(), libros=Libro.obtener_todos())
        except ValueError:
            flash("Los campos ID de libro y días deben ser números válidos.", "error")
            return render_template("prestamos.html", usuarios=Usuario.obtener_todos(), libros=Libro.obtener_todos())
        except Exception as e:
            flash(f"Error al registrar el préstamo: {str(e)}", "error")
            return render_template("prestamos.html", usuarios=Usuario.obtener_todos(), libros=Libro.obtener_todos())

    usuarios = Usuario.obtener_todos()
    libros = Libro.obtener_todos()
    return render_template("prestamos.html", usuarios=usuarios, libros=libros)

@app.route("/prestamos/devolver/", methods=["POST"])
def devolver_libro_web():
    try:
        id_prestamo = request.form.get("id_prestamo")
        devolver_libro(id_prestamo)
        flash("Libro devuelto correctamente.", "success")
        return redirect(url_for("menu_prestamos"))
    except Exception as e:
        flash(f"Error al devolver el libro: {str(e)}", "error")
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
        from Proyecto import devolver_libros_multiples as devolver_multiples_func
        
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
                return render_template("editar_usuario.html", usuario=usuario)

            # Usar la función de actualización por documento
            from Proyecto import actualizar_usuario_por_documento
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
            return render_template("editar_usuario.html", usuario=usuario)

    return render_template("editar_usuario.html", usuario=usuario)

@app.route("/usuarios/eliminar/<documento>")
def eliminar_usuario_web(documento):
    try:
        from Proyecto import eliminar_usuario_por_documento
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
        from Proyecto import verificar_consistencia_libros
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
        from Proyecto import crear_usuarios_prueba
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
        from Proyecto import Usuario
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
    """API para buscar libros por ID, título o género"""
    termino = request.args.get('q', '').strip()
    try:
        from Proyecto import Libro
        if not termino:
            libros = Libro.obtener_todos()
        else:
            libros = Libro.buscar_por_termino(termino)
        # Filtrar solo los disponibles
        resultado = []
        for libro in libros:
            if getattr(libro, 'disponible', True):
                resultado.append({
                    'id_libro': libro.id_libro,
                    'titulo': libro.titulo,
                    'autor': libro.autor,
                    'genero': libro.genero,
                    'año': libro.año,
                    'disponible': libro.disponible,
                    'imagen_url': url_for('obtener_imagen_libro', id_libro=libro.id_libro)
                })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/prestamos_usuario/<documento>")
def prestamos_usuario_api(documento):
    """API para obtener los préstamos activos de un usuario"""
    try:
        from Proyecto import Prestamo
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

if __name__ == "__main__":
    app.run(debug=True)