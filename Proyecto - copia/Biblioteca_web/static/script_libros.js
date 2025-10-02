// ========================================
// SISTEMA DE GESTIÓN DE LIBROS - BIBLIOTECA
// ========================================

// ===========================================
// SISTEMA DE GESTIÓN DE LIBROS - BIBLIOTECA
// Comentarios y validaciones mejorados - 2025
// ===========================================

document.addEventListener('DOMContentLoaded', function() {
    // ===========================================
    // DECLARACIÓN DE ELEMENTOS DEL DOM
    // ===========================================
    const searchInput = document.getElementById('input__Busqueda');
    const tableBody = document.getElementById('tableBody');
    let rows = [];
    if (tableBody) {
        rows = tableBody.getElementsByTagName('tr');
    }
    // Botones principales
    const addBookButton = document.getElementById('Boton_Agregar');
    const deleteBookButton = document.getElementById('Boton_Eliminar');
    // Formularios
    const addForm = document.querySelector('#Agregar_libro_menu form');

    // ===========================================
    // FUNCIONALIDAD DE BÚSQUEDA
    // ===========================================
    if (searchInput && rows.length) {
        searchInput.addEventListener('input', function() {
            const searchTerm = searchInput.value.toLowerCase();
            for (let i = 0; i < rows.length; i++) {
                const text = rows[i].textContent.toLowerCase();
                rows[i].style.display = text.includes(searchTerm) ? '' : 'none';
            }
        });
    }

    // ===========================================
    // VALIDACIONES DE FORMULARIOS
    // ===========================================
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const anio = document.querySelector('#Agregar_libro_menu input[name="año"]')?.value;
            if (!anio || isNaN(anio) || anio < 0 || anio > 2025) {
                e.preventDefault();
                alert('El año debe ser un número válido entre 0 y 2025.');
            }
        });
    }
});

// (Eliminado: funciones antiguas de panel de actualizar libro)

// MODAL AGREGAR LIBRO - DASHBOARD STYLE
function abrirModalAgregarLibro() {
    document.getElementById('modalAgregarLibro').style.display = 'flex';
    document.body.classList.add('modal-open');
}
function cerrarModalAgregarLibro() {
    document.getElementById('modalAgregarLibro').style.display = 'none';
    document.body.classList.remove('modal-open');
}
// Cerrar modal al hacer clic en overlay
window.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalAgregarLibro');
    if (modal) {
        modal.querySelector('.modal-overlay').addEventListener('click', cerrarModalAgregarLibro);
        // Cerrar con Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display !== 'none') {
                cerrarModalAgregarLibro();
            }
        });
    }
});

// Cambiar el botón para abrir el modal
const btnAgregar = document.getElementById('Boton_Agregar');
if (btnAgregar) {
    btnAgregar.onclick = abrirModalAgregarLibro;
}

// MODAL ELIMINAR LIBRO - DASHBOARD STYLE
function abrirModalEliminarLibro() {
    document.getElementById('modalEliminarLibro').style.display = 'flex';
    document.body.classList.add('modal-open');
}
function cerrarModalEliminarLibro() {
    document.getElementById('modalEliminarLibro').style.display = 'none';
    document.body.classList.remove('modal-open');
}
// Cerrar modal al hacer clic en overlay
window.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalEliminarLibro');
    if (modal) {
        modal.querySelector('.modal-overlay').addEventListener('click', cerrarModalEliminarLibro);
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display !== 'none') {
                cerrarModalEliminarLibro();
            }
        });
    }
});

// Cambiar el botón para abrir el modal
const btnEliminar = document.getElementById('Boton_Eliminar');
if (btnEliminar) {
    btnEliminar.onclick = abrirModalEliminarLibro;
}

// MODAL ACTUALIZAR LIBRO - DASHBOARD STYLE
function abrirModalActualizarLibro(libroData) {
    document.getElementById('modalActualizarLibro').style.display = 'flex';
    document.body.classList.add('modal-open');
    // Rellenar campos
    document.getElementById('id_libro_actualizar').value = libroData.id_libro;
    document.getElementById('titulo_actualizar').value = libroData.titulo;
    document.getElementById('autor_actualizar').value = libroData.autor;
    document.getElementById('editorial_actualizar').value = libroData.editorial;
    document.getElementById('año_actualizar').value = libroData.año;
    document.getElementById('genero_actualizar').value = libroData.genero;
    document.getElementById('disponible_actualizar').value = libroData.disponible ? 'si' : 'no';
}
function cerrarModalActualizarLibro() {
    document.getElementById('modalActualizarLibro').style.display = 'none';
    document.body.classList.remove('modal-open');
}
// Cerrar modal al hacer clic en overlay
window.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalActualizarLibro');
    if (modal) {
        modal.querySelector('.modal-overlay').addEventListener('click', cerrarModalActualizarLibro);
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display !== 'none') {
                cerrarModalActualizarLibro();
            }
        });
    }
});

// Conectar los botones de actualizar de la tabla
function obtenerDatosLibroDeFila(btn) {
    const fila = btn.closest('tr');
    return {
        id_libro: fila.children[1].textContent.trim(),
        titulo: fila.children[2].textContent.trim(),
        autor: fila.children[3].textContent.trim(),
        editorial: fila.children[4].textContent.trim(),
        año: fila.children[5].textContent.trim(),
        genero: fila.children[6].textContent.trim(),
        disponible: fila.children[7].textContent.trim() === 'Sí'
    };
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-actualizar').forEach(function(btn) {
        btn.onclick = function() {
            const datos = obtenerDatosLibroDeFila(btn);
            abrirModalActualizarLibro(datos);
        };
    });
});