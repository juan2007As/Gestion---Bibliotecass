// ========================================
// SISTEMA MEJORADO DE NOTIFICACIONES TOAST
// Archivo: toast_notifications.js
// Auto-dismiss, botón de cierre, barra de progreso
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    initializeToastNotifications();
});

function initializeToastNotifications() {
    // Configurar las notificaciones existentes
    const toastAlerts = document.querySelectorAll('.toast-alert:not(.toast-initialized)');
    
    toastAlerts.forEach(function(toast, index) {
        toast.classList.add('toast-initialized');
        
        // Agregar botón de cierre
        const closeBtn = document.createElement('button');
        closeBtn.className = 'toast-close-btn';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Cerrar notificación');
        closeBtn.setAttribute('title', 'Cerrar notificación');
        toast.appendChild(closeBtn);
        
        // Agregar barra de progreso
        const progressContainer = document.createElement('div');
        progressContainer.className = 'toast-progress';
        const progressBar = document.createElement('div');
        progressBar.className = 'toast-progress-bar';
        progressContainer.appendChild(progressBar);
        toast.appendChild(progressContainer);
        
        // Configurar auto-dismiss (4 segundos)
        const duration = 4000;
        let startTime = Date.now();
        let intervalId;
        let isPaused = false;
        
        // Función para actualizar la barra de progreso
        function updateProgress() {
            if (isPaused) return;
            
            const elapsed = Date.now() - startTime;
            const remaining = Math.max(0, duration - elapsed);
            const progress = ((duration - remaining) / duration) * 100;
            
            progressBar.style.width = progress + '%';
            
            if (remaining <= 0) {
                clearInterval(intervalId);
                dismissToast(toast);
            }
        }
        
        // Iniciar barra de progreso con delay escalonado
        setTimeout(function() {
            if (toast.parentNode) {
                startTime = Date.now();
                intervalId = setInterval(updateProgress, 50);
            }
        }, index * 150); // Delay escalonado para múltiples notificaciones
        
        // Pausar en hover
        toast.addEventListener('mouseenter', function() {
            isPaused = true;
        });
        
        // Reanudar al salir del hover
        toast.addEventListener('mouseleave', function() {
            isPaused = false;
            startTime = Date.now() - (duration * (parseFloat(progressBar.style.width) || 0) / 100);
        });
        
        // Cerrar al hacer clic en el botón
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            clearInterval(intervalId);
            dismissToast(toast);
        });
        
        // Cerrar al hacer clic en la notificación
        toast.addEventListener('click', function() {
            clearInterval(intervalId);
            dismissToast(toast);
        });
    });
}

// Función para cerrar notificación con animación
function dismissToast(toast) {
    if (toast.classList.contains('toast-closing')) return;
    
    toast.classList.add('toast-closing');
    
    setTimeout(function() {
        if (toast.parentNode) {
            toast.remove();
            
            // Si no quedan notificaciones, remover el contenedor
            const toastContainer = document.querySelector('.toast-alerts');
            if (toastContainer && toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }
    }, 300); // Duración de la animación de salida
}

// Función para crear notificaciones dinámicamente (opcional)
function showToast(message, type = 'info', duration = 4000) {
    let toastContainer = document.querySelector('.toast-alerts');
    
    // Crear contenedor si no existe
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-alerts';
        document.body.appendChild(toastContainer);
    }
    
    // Crear notificación
    const toast = document.createElement('div');
    toast.className = `toast-alert toast-${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Inicializar la notificación
    setTimeout(() => {
        initializeToastNotifications();
    }, 10);
}