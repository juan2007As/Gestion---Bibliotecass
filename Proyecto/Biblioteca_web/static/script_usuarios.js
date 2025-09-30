// ========================================
// SISTEMA DE GESTIÓN DE USUARIOS - DASHBOARD ESTÁNDAR (LIBROS)
// Comentarios y validaciones mejorados - 2025
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // ===================== BÚSQUEDA =====================
    const searchInput = document.getElementById('input__Busqueda');
    const tableBody = document.getElementById('tableBody');
    if (searchInput && tableBody) {
        const rows = tableBody.getElementsByTagName('tr');
        searchInput.addEventListener('input', function() {
            const searchTerm = searchInput.value.toLowerCase();
            for (let i = 0; i < rows.length; i++) {
                const text = rows[i].textContent.toLowerCase();
                rows[i].style.display = text.includes(searchTerm) ? '' : 'none';
            }
        });
    }

    // ===================== MODALES (ESTÁNDAR DASHBOARD) =====================
    /**
     * Abre un modal por ID, con animación.
     */
    function abrirModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('active'), 10);
        }
    }
    /**
     * Cierra un modal por ID, con animación.
     */
    function cerrarModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => { modal.style.display = 'none'; }, 200);
        }
    }
    // Overlay y botón cerrar
    document.querySelectorAll('.modal').forEach(function(modal) {
        const overlay = modal.querySelector('.modal-overlay');
        if (overlay) overlay.onclick = function() { cerrarModal(modal.id); };
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) closeBtn.onclick = function() { cerrarModal(modal.id); };
    });
    // Botones barra administración
    const btnAgregar = document.getElementById('Boton_Agregar');
    if (btnAgregar) btnAgregar.onclick = function() { abrirModal('modalAgregarUsuario'); };
    const btnEliminar = document.getElementById('Boton_Eliminar');
    if (btnEliminar) btnEliminar.onclick = function() { abrirModal('modalEliminarUsuario'); };

    // ===================== ACTUALIZAR USUARIO =====================
    // Botón actualizar y eliminar de la tabla
    if (tableBody) {
        tableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-actualizar')) {
                const fila = e.target.closest('tr');
                if (fila) {
                    const celdas = fila.getElementsByTagName('td');
                    document.getElementById('documento_usuario_actualizar').value = celdas[0].textContent;
                    document.getElementById('nombre_actualizar').value = celdas[1].textContent;
                    document.getElementById('apellido_actualizar').value = celdas[2].textContent;
                    document.getElementById('telefono_actualizar').value = celdas[3].textContent;
                    document.getElementById('email_actualizar').value = celdas[4].textContent;
                    // Rol
                    const rolSelect = document.getElementById('rol_actualizar');
                    if (rolSelect) {
                        rolSelect.value = celdas[5].textContent.trim();
                    }
                    abrirModal('modalActualizarUsuario');
                }
            }
            // Botón eliminar de la tabla (enlace)
            if (e.target.classList.contains('btn-eliminar')) {
                const fila = e.target.closest('tr');
                if (fila) {
                    const doc = fila.cells[0].textContent;
                    const input = document.querySelector('#modalEliminarUsuario input[name="documento"]');
                    if (input) input.value = doc;
                    abrirModal('modalEliminarUsuario');
                    e.preventDefault(); // Evita navegación
                }
            }
        });
    }

    // ===================== VALIDACIONES =====================
    // Agregar usuario
    const addForm = document.querySelector('#modalAgregarUsuario form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const email = addForm.querySelector('input[name="email"]')?.value;
            const telefono = addForm.querySelector('input[name="telefono"]')?.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Por favor, ingrese un email válido.');
                return;
            }
            if (!/^\d+$/.test(telefono)) {
                e.preventDefault();
                alert('El teléfono debe contener solo números.');
                return;
            }
        });
    }
    // Actualizar usuario
    const updateForm = document.querySelector('#modalActualizarUsuario form');
    if (updateForm) {
        updateForm.addEventListener('submit', function(e) {
            const email = updateForm.querySelector('input[name="email"]')?.value;
            const telefono = updateForm.querySelector('input[name="telefono"]')?.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Por favor, ingrese un email válido.');
                return;
            }
            if (!/^\d+$/.test(telefono)) {
                e.preventDefault();
                alert('El teléfono debe contener solo números.');
                return;
            }
        });
    }
    // Limpiar formularios al cerrar modales
    window.ocultarMenuAgregar = function() {
        cerrarModal('modalAgregarUsuario');
        if (addForm) addForm.reset();
    };
    window.ocultarMenuActualizar = function() {
        cerrarModal('modalActualizarUsuario');
        if (updateForm) updateForm.reset();
    };
    window.ocultarMenuEliminar = function() {
        cerrarModal('modalEliminarUsuario');
        const delForm = document.querySelector('#modalEliminarUsuario form');
        if (delForm) delForm.reset();
    };
});