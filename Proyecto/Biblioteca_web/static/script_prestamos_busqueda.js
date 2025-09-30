// ========================================
// SISTEMA DE BÚSQUEDA AVANZADA - BIBLIOTECA
// Archivo: script_prestamos_busqueda.js
// Funcionalidad: Búsqueda en tiempo real y autocompletado
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ===========================================
    // VARIABLES GLOBALES
    // ===========================================
    let usuarioSeleccionado = null;
    let libroSeleccionado = null;
    let prestamoSeleccionado = null;
    let prestamosSeleccionados = []; // Nueva variable para múltiples préstamos
    
    // ===========================================
    // BÚSQUEDA DE USUARIOS PARA PRÉSTAMOS
    // ===========================================
    const busquedaUsuario = document.getElementById('busqueda_usuario');
    const resultadosUsuario = document.getElementById('resultados_usuario');
    const documentoUsuarioHidden = document.getElementById('documento_usuario');
    
    if (busquedaUsuario) {
        let timeoutUsuario;
        busquedaUsuario.addEventListener('input', function() {
            clearTimeout(timeoutUsuario);
            const termino = this.value.trim();
            if (termino.length < 2) {
                ocultarResultados(resultadosUsuario);
                return;
            }
            timeoutUsuario = setTimeout(() => {
                buscarUsuarios(termino, resultadosUsuario, (usuario) => {
                    busquedaUsuario.value = `${usuario.nombre_completo} (${usuario.documento})`;
                    documentoUsuarioHidden.value = usuario.documento;
                    usuarioSeleccionado = usuario;
                    ocultarResultados(resultadosUsuario);
                });
            }, 300);
        });
        // Limpiar selección si el usuario modifica el campo
        busquedaUsuario.addEventListener('keydown', function() {
            if (usuarioSeleccionado) {
                documentoUsuarioHidden.value = '';
                usuarioSeleccionado = null;
            }
        });
        // Ocultar resultados al cerrar el modal
        const modal = document.getElementById('modalPrestarLibro');
        if (modal) {
            modal.addEventListener('transitionend', function() {
                if (this.style.display === 'none') ocultarResultados(resultadosUsuario);
            });
        }
    }
    
    // ===========================================
    // BÚSQUEDA DE LIBROS PARA PRÉSTAMOS
    // ===========================================
    const busquedaLibro = document.getElementById('busqueda_libro');
    const resultadosLibro = document.getElementById('resultados_libro');
    const idLibroHidden = document.getElementById('id_libro');
    
    if (busquedaLibro) {
        let timeoutLibro;
        busquedaLibro.addEventListener('input', function() {
            clearTimeout(timeoutLibro);
            const termino = this.value.trim();
            if (termino.length < 1) {
                ocultarResultados(resultadosLibro);
                return;
            }
            timeoutLibro = setTimeout(() => {
                buscarLibros(termino, resultadosLibro, (libro) => {
                    busquedaLibro.value = `${libro.titulo} (ID: ${libro.id_libro})`;
                    idLibroHidden.value = libro.id_libro;
                    libroSeleccionado = libro;
                    ocultarResultados(resultadosLibro);
                });
            }, 300);
        });
        // Limpiar selección si el usuario modifica el campo
        busquedaLibro.addEventListener('keydown', function() {
            if (libroSeleccionado) {
                idLibroHidden.value = '';
                libroSeleccionado = null;
            }
        });
        // Ocultar resultados al cerrar el modal
        const modal = document.getElementById('modalPrestarLibro');
        if (modal) {
            modal.addEventListener('transitionend', function() {
                if (this.style.display === 'none') ocultarResultados(resultadosLibro);
            });
        }
    }
    
    // ===========================================
    // SISTEMA DE DEVOLUCIÓN POR PASOS
    // ===========================================
    const busquedaUsuarioDevolver = document.getElementById('busqueda_usuario_devolver');
    const resultadosUsuarioDevolver = document.getElementById('resultados_usuario_devolver');
    const pasoSeleccionarLibro = document.getElementById('paso_seleccionar_libro');
    const librosPrespadosContainer = document.getElementById('libros_prestados');
    const formDevolver = document.getElementById('form_devolver');
    
    if (busquedaUsuarioDevolver) {
        let timeoutUsuarioDevolver;
        busquedaUsuarioDevolver.addEventListener('input', function() {
            clearTimeout(timeoutUsuarioDevolver);
            const termino = this.value.trim();
            if (termino.length < 2) {
                ocultarResultados(resultadosUsuarioDevolver);
                return;
            }
            timeoutUsuarioDevolver = setTimeout(() => {
                buscarUsuarios(termino, resultadosUsuarioDevolver, (usuario) => {
                    busquedaUsuarioDevolver.value = `${usuario.nombre_completo} (${usuario.documento})`;
                    ocultarResultados(resultadosUsuarioDevolver);
                    mostrarLibrosPrestados(usuario);
                });
            }, 300);
        });
        // Ocultar resultados al cerrar el modal
        const modal = document.getElementById('modalDevolverLibro');
        if (modal) {
            modal.addEventListener('transitionend', function() {
                if (this.style.display === 'none') ocultarResultados(resultadosUsuarioDevolver);
            });
        }
    }
    
    // ===========================================
    // FUNCIONES DE BÚSQUEDA Y UTILIDADES
    // ===========================================
    
    async function buscarUsuarios(termino, contenedorResultados, onSelect) {
        try {
            const response = await fetch(`/api/buscar_usuarios?q=${encodeURIComponent(termino)}`);
            const usuarios = await response.json();
            
            if (usuarios.length === 0) {
                mostrarMensajeVacio(contenedorResultados, 'No se encontraron usuarios');
                return;
            }
            
            mostrarResultadosUsuarios(usuarios, contenedorResultados, onSelect);
        } catch (error) {
            mostrarError(contenedorResultados, 'Error al buscar usuarios');
            console.error('Error:', error);
        }
    }
    
    async function buscarLibros(termino, contenedorResultados, onSelect) {
        try {
            const response = await fetch(`/api/buscar_libros?q=${encodeURIComponent(termino)}`);
            const libros = await response.json();
            
            if (libros.length === 0) {
                mostrarMensajeVacio(contenedorResultados, 'No se encontraron libros disponibles');
                return;
            }
            
            mostrarResultadosLibros(libros, contenedorResultados, onSelect);
        } catch (error) {
            mostrarError(contenedorResultados, 'Error al buscar libros');
            console.error('Error:', error);
        }
    }
    
    async function mostrarLibrosPrestados(usuario) {
        try {
            const response = await fetch(`/api/prestamos_usuario/${usuario.documento}`);
            const prestamos = await response.json();
            
            if (prestamos.length === 0) {
                librosPrespadosContainer.innerHTML = '<p>Este usuario no tiene libros prestados.</p>';
                pasoSeleccionarLibro.style.display = 'block';
                return;
            }
            
            let html = '';
            prestamos.forEach(prestamo => {
                const fechaLimite = new Date(prestamo.fecha_devolucion_esperada);
                const hoy = new Date();
                const esVencido = fechaLimite < hoy;
                
                html += `
                    <div class="libro-prestado-checkbox" data-prestamo-id="${prestamo.id_prestamo}">
                        <div class="checkbox-container">
                            <input type="checkbox" id="prestamo_${prestamo.id_prestamo}" 
                                   class="prestamo-checkbox" data-prestamo-id="${prestamo.id_prestamo}">
                            <label for="prestamo_${prestamo.id_prestamo}" class="checkbox-label"></label>
                        </div>
                        <div class="libro-info">
                            <div class="titulo">${prestamo.titulo}</div>
                            <div class="detalles">Autor: ${prestamo.autor} • Prestado: ${prestamo.fecha_prestamo}</div>
                        </div>
                        <div class="libro-estado">
                            <div class="${esVencido ? 'fecha-limite' : 'fecha-normal'}">
                                Vence: ${prestamo.fecha_devolucion_esperada}
                            </div>
                            ${esVencido ? '<div style="color: #e74c3c; font-weight: bold;">¡VENCIDO!</div>' : ''}
                        </div>
                    </div>
                `;
            });
            
            librosPrespadosContainer.innerHTML = html;
            pasoSeleccionarLibro.style.display = 'block';
            
            // Inicializar controles de selección múltiple
            inicializarControlesiMultiples(prestamos, usuario);
            
            // Agregar eventos de cambio a los checkboxes
            document.querySelectorAll('.prestamo-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    actualizarSeleccionMultiple();
                });
            });
            
        } catch (error) {
            librosPrespadosContainer.innerHTML = '<p>Error al cargar los préstamos.</p>';
            console.error('Error:', error);
        }
    }
    
    // ===========================================
    // FUNCIONES PARA SELECCIÓN MÚLTIPLE
    // ===========================================
    
    /**
     * Inicializa los controles de selección múltiple de préstamos.
     * Permite seleccionar/deseleccionar todos y guarda referencias globales.
     */
    function inicializarControlesMultiples(prestamos, usuario) {
        // Botón seleccionar todos
        const btnSeleccionarTodos = document.getElementById('btn_seleccionar_todos');
        const btnDeseleccionarTodos = document.getElementById('btn_deseleccionar_todos');
        
        if (btnSeleccionarTodos) {
            btnSeleccionarTodos.addEventListener('click', function() {
                // Marca todos los checkboxes de préstamos como seleccionados
                document.querySelectorAll('.prestamo-checkbox').forEach(checkbox => {
                    checkbox.checked = true;
                });
                actualizarSeleccionMultiple();
            });
        }
        
        if (btnDeseleccionarTodos) {
            btnDeseleccionarTodos.addEventListener('click', function() {
                // Desmarca todos los checkboxes de préstamos
                document.querySelectorAll('.prestamo-checkbox').forEach(checkbox => {
                    checkbox.checked = false;
                });
                actualizarSeleccionMultiple();
            });
        }
        // Guardar referencia de prestamos para uso posterior
        window.prestamosDisponibles = prestamos;
        window.usuarioActual = usuario;
    }
    
    /**
     * Actualiza la selección múltiple de préstamos y el contador visual.
     * Muestra u oculta el formulario de devolución múltiple según la selección.
     */
    function actualizarSeleccionMultiple() {
        const checkboxesSeleccionados = document.querySelectorAll('.prestamo-checkbox:checked');
        const contador = document.getElementById('contador_seleccionados');
        const cantidad = checkboxesSeleccionados.length;
        // Actualizar contador visual
        if (contador) {
            contador.textContent = `${cantidad} libro${cantidad !== 1 ? 's' : ''} seleccionado${cantidad !== 1 ? 's' : ''}`;
        }
        // Actualizar array de préstamos seleccionados
        prestamosSeleccionados = [];
        checkboxesSeleccionados.forEach(checkbox => {
            const prestamoId = parseInt(checkbox.dataset.prestamoId);
            const prestamo = window.prestamosDisponibles?.find(p => p.id_prestamo === prestamoId);
            if (prestamo) {
                prestamosSeleccionados.push(prestamo);
            }
        });
        // Mostrar/ocultar formulario de devolución múltiple
        if (cantidad > 0) {
            mostrarFormularioDevolucionMultiple(prestamosSeleccionados, window.usuarioActual);
        } else {
            ocultarFormularioDevolucionMultiple();
        }
    }
    
    /**
     * Muestra el formulario de confirmación para devolución múltiple de libros.
     * @param {Array} prestamos - Préstamos seleccionados
     * @param {Object} usuario - Usuario actual
     */
    function mostrarFormularioDevolucionMultiple(prestamos, usuario) {
        const resumenDiv = document.getElementById('resumen_devolucion_multiple');
        const idsPrestamoInput = document.getElementById('ids_prestamos_devolver');
        const formDevolver = document.getElementById('form_devolver_multiple');
        if (!resumenDiv || !idsPrestamoInput || !formDevolver) return; // Validación de existencia
        let html = `
            <h4>Confirmar Devolución de ${prestamos.length} Libro${prestamos.length !== 1 ? 's' : ''}</h4>
            <p><strong>Usuario:</strong> ${usuario.nombre_completo} (${usuario.documento})</p>
            <div class="libros-a-devolver">
                <h5>Libros seleccionados:</h5>
                <ul>
        `;
        const idsPrestamosList = [];
        prestamos.forEach(prestamo => {
            const fechaLimite = new Date(prestamo.fecha_devolucion_esperada);
            const hoy = new Date();
            const esVencido = fechaLimite < hoy;
            html += `
                <li class="${esVencido ? 'libro-vencido' : ''}">
                    <strong>${prestamo.titulo}</strong> - ${prestamo.autor}
                    <br><small>Prestado: ${prestamo.fecha_prestamo} | Vence: ${prestamo.fecha_devolucion_esperada}</small>
                    ${esVencido ? '<span style="color: #e74c3c; font-weight: bold;"> ¡VENCIDO!</span>' : ''}
                </li>
            `;
            idsPrestamosList.push(prestamo.id_prestamo);
        });
        html += `
                </ul>
            </div>
        `;
        resumenDiv.innerHTML = html;
        idsPrestamoInput.value = idsPrestamosList.join(',');
        formDevolver.style.display = 'block';
        // Mostrar botones de confirmación si existen
        const btnConfirmar = document.getElementById('btn_confirmar_devolucion_multiple');
        const btnCancelar = document.getElementById('btn_cancelar_devolucion');
        if (btnConfirmar) btnConfirmar.style.display = 'inline-block';
        if (btnCancelar) btnCancelar.style.display = 'inline-block';
    }
    
    /**
     * Oculta el formulario de devolución múltiple y los botones de confirmación.
     */
    function ocultarFormularioDevolucionMultiple() {
        const formDevolver = document.getElementById('form_devolver_multiple');
        if (formDevolver) {
            formDevolver.style.display = 'none';
        }
        // Ocultar botones de confirmación si existen
        const btnConfirmar = document.getElementById('btn_confirmar_devolucion_multiple');
        const btnCancelar = document.getElementById('btn_cancelar_devolucion');
        if (btnConfirmar) btnConfirmar.style.display = 'none';
        if (btnCancelar) btnCancelar.style.display = 'none';
    }
    

    
    /**
     * Muestra los resultados de usuarios en el contenedor y agrega eventos de selección.
     */
    function mostrarResultadosUsuarios(usuarios, contenedor, onSelect) {
        let html = '';
        usuarios.forEach(usuario => {
            html += `
                <div class="resultado-item" data-documento="${usuario.documento}">
                    <div class="titulo">${usuario.nombre_completo}</div>
                    <div class="detalles">Documento: ${usuario.documento} • ${usuario.rol}</div>
                </div>
            `;
        });
        contenedor.innerHTML = html;
        contenedor.style.display = 'block';
        // Agregar eventos de clic a cada resultado
        contenedor.querySelectorAll('.resultado-item').forEach(item => {
            item.addEventListener('click', function() {
                const documento = this.dataset.documento;
                const usuario = usuarios.find(u => u.documento === documento);
                if (usuario && onSelect) {
                    onSelect(usuario);
                }
            });
        });
    }
    
    /**
     * Muestra los resultados de libros en el contenedor y agrega eventos de selección.
     */
    function mostrarResultadosLibros(libros, contenedor, onSelect) {
        let html = '';
        libros.forEach(libro => {
            html += `
                <div class="resultado-item" data-id-libro="${libro.id_libro}">
                    <div class="titulo">${libro.titulo}</div>
                    <div class="detalles">ID: ${libro.id_libro} • ${libro.autor} • ${libro.genero} (${libro.año})</div>
                </div>
            `;
        });
        contenedor.innerHTML = html;
        contenedor.style.display = 'block';
        // Agregar eventos de clic a cada resultado
        contenedor.querySelectorAll('.resultado-item').forEach(item => {
            item.addEventListener('click', function() {
                const idLibro = parseInt(this.dataset.idLibro);
                const libro = libros.find(l => l.id_libro === idLibro);
                if (libro && onSelect) {
                    onSelect(libro);
                }
            });
        });
    }
    
    function mostrarMensajeVacio(contenedor, mensaje) {
        contenedor.innerHTML = `<div class="resultado-item">${mensaje}</div>`;
        contenedor.style.display = 'block';
    }
    
    function mostrarError(contenedor, mensaje) {
        contenedor.innerHTML = `<div class="resultado-item" style="color: #e74c3c;">${mensaje}</div>`;
        contenedor.style.display = 'block';
    }
    
    function ocultarResultados(contenedor) {
        contenedor.style.display = 'none';
        contenedor.innerHTML = '';
    }
    
    // ===========================================
    // FUNCIONES GLOBALES
    // ===========================================
    
    window.reiniciarDevolucion = function() {
        // Limpiar formulario de devolución múltiple
        document.getElementById('busqueda_usuario_devolver').value = '';
        document.getElementById('paso_seleccionar_libro').style.display = 'none';
        document.getElementById('form_devolver_multiple').style.display = 'none';
        document.getElementById('btn_confirmar_devolucion_multiple').style.display = 'none';
        document.getElementById('btn_cancelar_devolucion').style.display = 'none';
        // Limpiar variables globales
        prestamosSeleccionados = [];
        window.prestamosDisponibles = [];
        window.usuarioActual = null;
        ocultarResultados(resultadosUsuarioDevolver);
        // Cierra el modal si está abierto
        if (typeof ocultarMenuDevolver === 'function') ocultarMenuDevolver();
    };
    
    window.confirmarDevolucionMultiple = function() {
        if (prestamosSeleccionados.length === 0) {
            alert('Por favor selecciona al menos un libro para devolver.');
            return;
        }
        
        // Mostrar confirmación con detalles
        const cantidad = prestamosSeleccionados.length;
        const libros = prestamosSeleccionados.map(p => p.titulo).join(', ');
        const mensaje = `¿Confirmas la devolución de ${cantidad} libro${cantidad !== 1 ? 's' : ''}?\n\n${libros}`;
        
        if (confirm(mensaje)) {
            // Enviar el formulario de devolución múltiple
            const form = document.getElementById('form_devolver_multiple');
            if (form) {
                // Crear y enviar el formulario
                const formData = new FormData(form);
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    if (response.ok) {
                        // Mostrar mensaje de éxito
                        alert(`✅ Se devolvieron ${cantidad} libro${cantidad !== 1 ? 's' : ''} correctamente.`);
                        // Redirigir al menú principal
                        window.location.href = response.url || '/prestamos';
                    } else {
                        alert('❌ Error al procesar las devoluciones');
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    alert('❌ Error al procesar las devoluciones');
                });
            }
        }
    };
    
    // Ocultar resultados al hacer clic fuera
    document.addEventListener('click', function(e) {
        // Si el click es fuera de cualquier modal y fuera de los campos de búsqueda, oculta los resultados
        if (!e.target.closest('.campo-busqueda') && !e.target.closest('.modal-content')) {
            document.querySelectorAll('.resultados-busqueda').forEach(contenedor => {
                ocultarResultados(contenedor);
            });
        }
    });
});