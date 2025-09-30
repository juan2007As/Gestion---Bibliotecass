// =================================================================
// JAVASCRIPT PARA DASHBOARD DE USUARIO CON PAGINACIÓN
// =================================================================

let librosCatalogo = [];
let paginaActual = 1;
const librosPorPagina = 8;
let totalPaginas = 1;
let ultimoTerminoBusqueda = '';

function toggleEditProfile() {
    // Función para mostrar/ocultar formulario de edición de perfil
    alert('Función de editar perfil - Por implementar');
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

function devolverLibro(idPrestamo) {
    idPrestamo = parseInt(idPrestamo);
    if (confirm('¿Estás seguro de que quieres devolver este libro?')) {
        // Crear formulario dinámico para enviar POST
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/prestamos/devolver/';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'id_prestamo';
        input.value = idPrestamo;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
}


function buscarLibros() {
    const searchTerm = document.getElementById('searchBooks').value.trim();
    ultimoTerminoBusqueda = searchTerm;
    if (searchTerm.length < 1) {
        // Si no hay término, recargar todos los libros desde el backend
        fetch('/api/buscar_libros?q=')
            .then(response => response.json())
            .then(data => {
                librosCatalogo = data;
                renderizarCatalogoLibros(librosCatalogo, 1);
            })
            .catch(error => {
                document.getElementById('booksResults').innerHTML = `<p>Error al cargar libros: ${error}</p>`;
                document.getElementById('paginacionLibros')?.remove();
            });
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
    const dias = prompt('¿Por cuántos días quieres el libro? (máximo 30)');
    
    if (dias === null) return; // Usuario canceló
    
    const diasNum = parseInt(dias);
    if (isNaN(diasNum) || diasNum < 1 || diasNum > 30) {
        alert('Por favor ingresa un número válido entre 1 y 30 días');
        return;
    }
    
    if (confirm(`¿Confirmas que quieres prestar este libro por ${diasNum} días?`)) {
        // Crear formulario dinámico para enviar POST
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/prestamos/prestar';
        
        // Campo para documento (se obtiene de la sesión en el servidor)
        const inputDoc = document.createElement('input');
        inputDoc.type = 'hidden';
        inputDoc.name = 'documento_usuario';
        inputDoc.value = 'AUTO'; // El servidor usará el documento de la sesión
        
        const inputLibro = document.createElement('input');
        inputLibro.type = 'hidden';
        inputLibro.name = 'id_libro';
        inputLibro.value = idLibro;
        
        const inputDias = document.createElement('input');
        inputDias.type = 'hidden';
        inputDias.name = 'dias';
        inputDias.value = diasNum;
        
        form.appendChild(inputDoc);
        form.appendChild(inputLibro);
        form.appendChild(inputDias);
        document.body.appendChild(form);
        form.submit();
    }
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
});