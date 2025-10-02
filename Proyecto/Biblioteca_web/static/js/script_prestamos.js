// ========================================
// SISTEMA DE PRÉSTAMOS - JS UNIFICADO DASHBOARD
// Archivo: script_prestamos.js
// Incluye: modales, búsqueda, tabla, UX
// ========================================
// SISTEMA DE PRÉSTAMOS - JS UNIFICADO DASHBOARD
// Comentarios y validaciones mejorados - 2025
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // =====================
    // MODALES DASHBOARD
    // =====================
    function mostrarModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('active'), 10);
        }
    }
    function ocultarModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => { modal.style.display = 'none'; }, 200);
        }
    }
    window.mostrarMenuPrestar = () => mostrarModal('modalPrestarLibro');
    window.ocultarMenuPrestar = () => ocultarModal('modalPrestarLibro');
    window.mostrarMenuDevolver = () => mostrarModal('modalDevolverLibro');
    window.ocultarMenuDevolver = () => ocultarModal('modalDevolverLibro');
    // Overlay y close
    document.querySelectorAll('.modal').forEach(modal => {
        const overlay = modal.querySelector('.modal-overlay');
        if (overlay) overlay.onclick = () => ocultarModal(modal.id);
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) closeBtn.onclick = () => ocultarModal(modal.id);
    });

    // =====================
    // TABLA Y FILTRO DE LISTA
    // =====================
    const searchInput = document.getElementById('input__Busqueda');
    const tableBody = document.getElementById('tableBody');
    if (searchInput && tableBody) {
        const rows = tableBody.getElementsByTagName('tr');
        searchInput.addEventListener('input', function() {
            const searchTerm = searchInput.value.toLowerCase();
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                if (row.querySelector('.no-prestamos')) continue;
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            }
            // Eliminar actualización del título con resultados
            // Siempre dejar el título fijo
            const title = document.querySelector('.Administracion__title');
            if (title) {
                title.textContent = 'Gestión de préstamos:';
            }
        });
        // Al cargar, también dejar el título fijo
        const title = document.querySelector('.Administracion__title');
        if (title) {
            title.textContent = 'Gestión de préstamos:';
        }
    }
});