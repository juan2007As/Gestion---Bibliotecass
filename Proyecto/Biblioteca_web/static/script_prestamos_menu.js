// ========================================
// Lógica de apertura/cierre de modales dashboard préstamos
// (El resto de la lógica de búsqueda y devolución está en script_prestamos_busqueda.js)
// Comentarios y robustez mejorados - 2025
// ========================================

// Funciones globales para mostrar/ocultar modales (por compatibilidad)
function mostrarMenuPrestar() { mostrarModal('modalPrestarLibro'); }
function ocultarMenuPrestar() { ocultarModal('modalPrestarLibro'); }
function mostrarMenuDevolver() { mostrarModal('modalDevolverLibro'); }
function ocultarMenuDevolver() { ocultarModal('modalDevolverLibro'); }

/**
 * Muestra un modal por ID con animación.
 */
function mostrarModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    }
}
/**
 * Oculta un modal por ID con animación.
 */
function ocultarModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => { modal.style.display = 'none'; }, 200);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const btnPrestar = document.getElementById('Boton_Prestamo');
    const btnDevolver = document.getElementById('Boton_Devolver');
    if (btnPrestar) btnPrestar.onclick = mostrarMenuPrestar;
    if (btnDevolver) btnDevolver.onclick = mostrarMenuDevolver;
    document.querySelectorAll('.modal').forEach(function(modal) {
        const overlay = modal.querySelector('.modal-overlay');
        if (overlay) overlay.onclick = function() { ocultarModal(modal.id); };
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) closeBtn.onclick = function() { ocultarModal(modal.id); };
    });
});