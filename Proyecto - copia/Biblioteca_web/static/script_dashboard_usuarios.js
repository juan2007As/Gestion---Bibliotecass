// =================================================================
// JAVASCRIPT PARA DASHBOARD DE USUARIO CON PAGINACIÓN
// =================================================================

let librosCatalogo = [];
let paginaActual = 1;
const librosPorPagina = 8;
let totalPaginas = 1;
let ultimoTerminoBusqueda = '';

function activarEdicion() {
    // Ocultar los spans y mostrar los inputs
    document.getElementById('email-display').style.display = 'none';
    document.getElementById('email-input').style.display = 'inline-block';
    
    document.getElementById('telefono-display').style.display = 'none';
    document.getElementById('telefono-input').style.display = 'inline-block';
    
    // Cambiar botones
    document.getElementById('btn-editar').style.display = 'none';
    document.getElementById('botones-guardar').style.display = 'flex';
    
    // Enfocar el primer campo
    document.getElementById('email-input').focus();
}

function cancelarEdicion() {
    // Mostrar los spans y ocultar los inputs
    document.getElementById('email-display').style.display = 'inline-block';
    document.getElementById('email-input').style.display = 'none';
    
    document.getElementById('telefono-display').style.display = 'inline-block';
    document.getElementById('telefono-input').style.display = 'none';
    
    // Cambiar botones
    document.getElementById('btn-editar').style.display = 'inline-block';
    document.getElementById('botones-guardar').style.display = 'none';
    
    // Restaurar valores originales
    document.getElementById('email-input').value = "{{ usuario.email }}";
    document.getElementById('telefono-input').value = "{{ usuario.telefono }}";
}

function renderizarCatalogoLibros(data, pagina = 1) {
    const resultsDiv = document.getElementById('booksResults');
    if (!data || data.length === 0) {
        resultsDiv.innerHTML = '<p>No se encontraron libros disponibles</p>';
        document.getElementById('paginacionLibros')?.remove();
        return;
    }
    totalPaginas = Math.ceil(data.length / librosPorPagina);
    if (pagina < 1) pagina = 1;
    if (pagina > totalPaginas) pagina = totalPaginas;
    paginaActual = pagina;
    const inicio = (pagina - 1) * librosPorPagina;
    const fin = inicio + librosPorPagina;
    const librosPagina = data.slice(inicio, fin);
    let html = '';
    librosPagina.forEach(libro => {
        html += `
            <div class="book-card" onclick="abrirMenuLibro(${libro.id_libro})">
                <img src="${libro.imagen_url}" alt="Portada de ${libro.titulo}" class="book-img" />
                <div class="book-info">
                    <h4>${libro.titulo}</h4>
                    <p><strong>Autor:</strong> ${libro.autor}</p>
                    <p><strong>Género:</strong> ${libro.genero}</p>
                    <p><strong>Año:</strong> ${libro.año}</p>
                </div>
            </div>
        `;
    });
    resultsDiv.innerHTML = html;
    renderizarPaginacion();
}

function renderizarPaginacion() {
    let paginacionDiv = document.getElementById('paginacionLibros');
    if (!paginacionDiv) {
        paginacionDiv = document.createElement('div');
        paginacionDiv.id = 'paginacionLibros';
        paginacionDiv.style.display = 'flex';
        paginacionDiv.style.justifyContent = 'center';
        paginacionDiv.style.margin = '18px 0 0 0';
        document.getElementById('booksResults').parentNode.appendChild(paginacionDiv);
    }
    if (totalPaginas <= 1) {
        paginacionDiv.innerHTML = '';
        return;
    }
    let html = '';
    html += `<button class="paginacion-btn" onclick="cambiarPagina(1)" ${paginaActual === 1 ? 'disabled' : ''}>«</button>`;
    html += `<button class="paginacion-btn" onclick="cambiarPagina(${paginaActual - 1})" ${paginaActual === 1 ? 'disabled' : ''}>Anterior</button>`;
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === paginaActual) {
            html += `<button class="paginacion-btn pagina-activa" disabled>${i}</button>`;
        } else if (i === 1 || i === totalPaginas || Math.abs(i - paginaActual) <= 1) {
            html += `<button class="paginacion-btn" onclick="cambiarPagina(${i})">${i}</button>`;
        } else if (i === paginaActual - 2 || i === paginaActual + 2) {
            html += '<span style="margin:0 6px;">...</span>';
        }
    }
    html += `<button class="paginacion-btn" onclick="cambiarPagina(${paginaActual + 1})" ${paginaActual === totalPaginas ? 'disabled' : ''}>Siguiente</button>`;
    html += `<button class="paginacion-btn" onclick="cambiarPagina(${totalPaginas})" ${paginaActual === totalPaginas ? 'disabled' : ''}>»</button>`;
    paginacionDiv.innerHTML = html;
}

function cambiarPagina(nuevaPagina) {
    if (nuevaPagina < 1 || nuevaPagina > totalPaginas) return;
    renderizarCatalogoLibros(librosCatalogo, nuevaPagina);
}

function abrirMenuLibro(idLibro) {
    // Usamos la misma API de búsqueda para obtener el libro por ID
    fetch(`/api/buscar_libros?q=${idLibro}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const libro = data[0];
                let html = `
                    <button class="close" onclick="cerrarModalLibro()" aria-label="Cerrar">&times;</button>
                    <img src="${libro.imagen_url}" alt="Portada" class="modal-book-img"/>
                    <h2>${libro.titulo}</h2>
                    <p><strong>Autor:</strong> ${libro.autor}</p>
                    <p><strong>Género:</strong> ${libro.genero}</p>
                    <p><strong>Año:</strong> ${libro.año}</p>
                    <form method="POST" action="/prestamos/prestar">
                        <input type="hidden" name="id_libro" value="${libro.id_libro}">
                        <label for="dias">Días de préstamo:</label>
                        <input type="number" name="dias" min="1" max="30" required>
                        <button type="submit">Prestar</button>
                    </form>
                `;
                document.getElementById('modalLibroContent').innerHTML = html;
                document.getElementById('modalLibro').style.display = 'block';
                document.body.classList.add('modal-open');
                setTimeout(() => {
                    document.getElementById('modalLibroContent').focus();
                }, 100);
            }
        });
}

function cerrarModalLibro() {
    document.getElementById('modalLibro').style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Cerrar modal al hacer clic fuera del contenido
window.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalLibro');
    if (modal) {
        modal.addEventListener('mousedown', function(e) {
            if (e.target.classList.contains('modal-overlay')) {
                cerrarModalLibro();
            }
        });
        // Cerrar con Escape
        document.addEventListener('keydown', function(e) {
            if (modal.style.display === 'block' && e.key === 'Escape') {
                cerrarModalLibro();
            }
        });
    }
});

let prestamoParaDevolver = null;

// Nueva función que lee el ID desde el atributo data
function devolverLibroNuevo(boton) {
    const idPrestamo = boton.getAttribute('data-prestamo-id');
    console.log('devolverLibroNuevo() leyó ID:', idPrestamo, 'tipo:', typeof idPrestamo);
    
    if (!idPrestamo || idPrestamo === 'None' || idPrestamo === '') {
        console.error('ID de préstamo no válido:', idPrestamo);
        alert('Error: No se pudo obtener el ID del préstamo');
        return;
    }
    
    const idNumerico = parseInt(idPrestamo);
    console.log('ID numérico:', idNumerico);
    
    // Asignar a la variable global ANTES de abrir el modal
    prestamoParaDevolver = idNumerico;
    console.log('Variable global prestamoParaDevolver asignada a:', prestamoParaDevolver);
    
    // Continuar con el resto del proceso
    devolverLibroInterno(idNumerico);
}

function devolverLibro(idPrestamo) {
    console.log('devolverLibro() recibió:', idPrestamo, 'tipo:', typeof idPrestamo);
    idPrestamo = parseInt(idPrestamo);
    console.log('Después de parseInt:', idPrestamo, 'tipo:', typeof idPrestamo);
    prestamoParaDevolver = idPrestamo;
    devolverLibroInterno(idPrestamo);
}

function devolverLibroInterno(idPrestamo) {
    
    // Buscar información del libro para mostrar en el modal
    const infoLibro = obtenerInfoLibroPrestamo(idPrestamo);
    
    // Actualizar contenido del modal con los IDs correctos
    document.getElementById('tituloLibroDevolucion').textContent = infoLibro.titulo;
    document.getElementById('autorLibroDevolucion').textContent = infoLibro.autor;
    document.getElementById('fechaPrestamoDevolucion').textContent = infoLibro.fechaPrestamo;
    document.getElementById('fechaLimiteDevolucion').textContent = infoLibro.fechaLimite;
    
    // Mostrar modal
    document.getElementById('modalConfirmacion').style.display = 'flex';
}

function obtenerInfoLibroPrestamo(idPrestamo) {
    // Buscar el botón de devolver específico por ID del préstamo
    const botonDevolver = document.querySelector(`button[onclick*="devolverLibro('${idPrestamo}')"]`);
    
    if (botonDevolver) {
        // Encontrar el contenedor loan-item más cercano
        const prestamoElement = botonDevolver.closest('.loan-item');
        
        if (prestamoElement) {
            // Extraer información del libro
            const titulo = prestamoElement.querySelector('h3')?.textContent?.trim() || 'Título no disponible';
            
            // Buscar el autor en los párrafos
            const parrafos = prestamoElement.querySelectorAll('p');
            let autor = 'Autor no disponible';
            let fechaPrestamo = 'Fecha no disponible';
            let fechaLimite = 'Fecha no disponible';
            
            parrafos.forEach(p => {
                const texto = p.textContent.trim();
                if (texto.includes('Autor:')) {
                    autor = texto.replace('Autor:', '').trim();
                } else if (texto.includes('Fecha de préstamo:')) {
                    fechaPrestamo = texto.replace('Fecha de préstamo:', '').trim();
                } else if (texto.includes('Fecha de devolución:')) {
                    fechaLimite = texto.replace('Fecha de devolución:', '').trim();
                }
            });
            
            return {
                titulo: titulo,
                autor: autor,
                fechaPrestamo: fechaPrestamo,
                fechaLimite: fechaLimite
            };
        }
    }
    
    return {
        titulo: 'Información no disponible',
        autor: 'Información no disponible',
        fechaPrestamo: 'Información no disponible',
        fechaLimite: 'Información no disponible'
    };
}

function confirmarDevolucion() {
    if (prestamoParaDevolver) {
        // Debug: verificar el ID del préstamo
        console.log('ID del préstamo a devolver:', prestamoParaDevolver);
        console.log('Tipo de prestamoParaDevolver:', typeof prestamoParaDevolver);
        
        // GUARDAR el ID antes de cerrar el modal (que lo resetea a null)
        const idParaDevolver = prestamoParaDevolver;
        
        // Verificar que tenemos un ID válido
        if (!idParaDevolver || idParaDevolver === null || isNaN(idParaDevolver)) {
            console.error('ID de préstamo no válido en confirmarDevolucion:', idParaDevolver);
            alert('Error: ID de préstamo no válido');
            return;
        }
        
        console.log('ID guardado para devolución:', idParaDevolver);
        
        // Cerrar el modal (esto resetea prestamoParaDevolver a null)
        cerrarModalConfirmacion();
        
        // Crear FormData para envío AJAX
        const formData = new FormData();
        formData.append('id_prestamo', String(idParaDevolver)); // Usar el ID guardado
        formData.append('redirect_to', 'dashboard_usuario');
        
        // Enviar petición AJAX
        fetch('/prestamos/devolver/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                // Múltiples formas de encontrar el elemento para mayor robustez
                let prestamoElement = null;
                
                // Método 1: Por atributo data-prestamo-id
                const botonDevolver = document.querySelector(`button[data-prestamo-id="${idParaDevolver}"]`);
                if (botonDevolver) {
                    prestamoElement = botonDevolver.closest('.loan-item');
                }
                
                // Método 2: Si no funciona el anterior, buscar por atributo data
                if (!prestamoElement) {
                    const todosLosBotonnes = document.querySelectorAll('.btn-return');
                    todosLosBotonnes.forEach(boton => {
                        if (boton.getAttribute('data-prestamo-id') === String(idParaDevolver)) {
                            prestamoElement = boton.closest('.loan-item');
                        }
                    });
                }
                
                // Método 3: Si no se puede eliminar visualmente, recargar catálogo y página
                if (!prestamoElement) {
                    console.log('No se pudo encontrar el elemento del préstamo, recargando catálogo y página...');
                    recargarCatalogo(); // Recargar catálogo antes de recargar página
                    setTimeout(() => window.location.reload(), 500); // Dar tiempo para la recarga del catálogo
                    return;
                }
                
                // Animación de salida
                prestamoElement.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                prestamoElement.style.opacity = '0';
                prestamoElement.style.transform = 'translateX(-20px)';
                
                // Eliminar después de la animación
                        setTimeout(() => {
                            prestamoElement.remove();
                            
                            // Verificar si quedan préstamos
                            const listaPrestamosPanels = document.querySelectorAll('.loans-panel .loan-item');
                            if (listaPrestamosPanels.length === 0) {
                                const loansPanel = document.querySelector('.loans-panel');
                                if (loansPanel) {
                                    const loansList = loansPanel.querySelector('.loans-list');
                                    if (loansList) {
                                        loansList.innerHTML = '<p class="no-loans">No tienes préstamos activos</p>';
                                    }
                                }
                            }
                            
                            // ¡RECARGAR EL CATÁLOGO AUTOMÁTICAMENTE!
                            recargarCatalogo();
                        }, 300);                // Libro devuelto exitosamente (sin alertas)
            } else {
                // Error en la devolución - recargar catálogo y página
                console.error('Error al devolver el libro');
                recargarCatalogo(); // Intentar recargar catálogo por si acaso se devolvió
                setTimeout(() => window.location.reload(), 500);
            }
        })
        .catch(error => {
            // Error de conexión - recargar catálogo y página
            console.error('Error de conexión:', error);
            recargarCatalogo(); // Intentar recargar catálogo por si acaso se devolvió
            setTimeout(() => window.location.reload(), 500);
        });
        
        // La variable ya se limpió en cerrarModalConfirmacion()
    }
}

function cerrarModalConfirmacion() {
    document.getElementById('modalConfirmacion').style.display = 'none';
    prestamoParaDevolver = null;
}


// Función específica para recargar el catálogo completo
function recargarCatalogo() {
    fetch('/api/buscar_libros?q=')
        .then(response => response.json())
        .then(data => {
            librosCatalogo = data;
            renderizarCatalogoLibros(librosCatalogo, 1);
            console.log('Catálogo recargado después de devolución');
        })
        .catch(error => {
            console.error('Error al recargar catálogo:', error);
            document.getElementById('booksResults').innerHTML = `<p>Error al cargar libros: ${error}</p>`;
            document.getElementById('paginacionLibros')?.remove();
        });
}

function buscarLibros() {
    const searchTerm = document.getElementById('searchBooks').value.trim();
    ultimoTerminoBusqueda = searchTerm;
    if (searchTerm.length < 1) {
        // Si no hay término, usar la función de recarga
        recargarCatalogo();
        return;
    }
    fetch(`/api/buscar_libros?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('booksResults').innerHTML = `<p>Error: ${data.error}</p>`;
                document.getElementById('paginacionLibros')?.remove();
                return;
            }
            librosCatalogo = data;
            renderizarCatalogoLibros(librosCatalogo, 1);
        })
        .catch(error => {
            document.getElementById('booksResults').innerHTML = `<p>Error al buscar libros: ${error}</p>`;
            document.getElementById('paginacionLibros')?.remove();
        });
}

function prestarLibro(idLibro) {
    // Por defecto 7 días, sin prompt molesto
    const diasNum = 7;
    
    console.log(`Prestando libro ID: ${idLibro} por ${diasNum} días`);
    
    // Usar URLSearchParams para mejor compatibilidad
    const params = new URLSearchParams();
    params.append('documento_usuario', 'AUTO');
    params.append('id_libro', idLibro);
    params.append('dias', diasNum);
    
    console.log('Enviando petición POST para prestar libro...');
    console.log('Datos a enviar:');
    console.log('- documento_usuario:', 'AUTO');
    console.log('- id_libro:', idLibro);
    console.log('- dias:', diasNum);
    
    fetch('/prestamos/prestar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params
    })
    .then(response => {
        if (response.ok) {
            console.log('Préstamo exitoso, recargando página...');
            window.location.reload(); // Recargar para mostrar el libro prestado
        } else {
            console.error('Error en el préstamo');
            window.location.reload(); // Recargar de todos modos para ver si hubo cambios
        }
    })
    .catch(error => {
        console.error('Error de conexión:', error);
        window.location.reload(); // Recargar de todos modos
    });
}

// Inicializar catálogo al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/buscar_libros?q=')
        .then(response => response.json())
        .then(data => {
            librosCatalogo = data;
            renderizarCatalogoLibros(librosCatalogo, 1);
        })
        .catch(error => {
            document.getElementById('booksResults').innerHTML = `<p>Error al cargar libros: ${error}</p>`;
        });

    // Soporte para buscar al presionar Enter
    document.getElementById('searchBooks').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            buscarLibros();
        }
    });

    // Búsqueda en vivo al escribir (con debounce)
    let debounceTimeout = null;
    document.getElementById('searchBooks').addEventListener('input', function(e) {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            buscarLibros();
        }, 350); // 350ms para evitar demasiadas peticiones
    });

    // Configurar modal de confirmación - clic en overlay para cerrar
    const modalOverlay = document.getElementById('modalConfirmacion');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            // Solo cerrar si se hace clic en el overlay, no en el contenido del modal
            if (e.target === modalOverlay) {
                cerrarModalConfirmacion();
            }
        });
    }

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modalConfirmacion');
            if (modal && modal.style.display === 'flex') {
                cerrarModalConfirmacion();
            }
        }
    });
});