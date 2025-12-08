/* ============================================================
   🎯 FUNCIONES DE ALERTAS Y CONFIRMACIONES MODALES
   ============================================================ */

/**
 * Mostrar alerta modal con estilo dinámico
 * @param {string} titulo - Título de la alerta
 * @param {string} mensaje - Mensaje de la alerta
 * @param {string} tipo - Tipo: success, error, warning, info
 * @param {function} callback - Función opcional a ejecutar al cerrar
 */
function showAlert(titulo, mensaje, tipo = 'info', callback = null) {
    // Remover modal anterior si existe
    const anterior = document.querySelector('.modal-alert-backdrop');
    if (anterior) anterior.remove();

    // Crear backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-alert-backdrop';

    // Crear modal
    const modal = document.createElement('div');
    modal.className = 'modal-alert';

    // Iconos según tipo
    const iconos = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const colores = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#0dcaf0'
    };

    modal.innerHTML = `
        <div class="modal-alert-container">
            <div class="modal-alert-icon" style="color: ${colores[tipo] || '#0dcaf0'}">
                ${iconos[tipo] || '📢'}
            </div>
            <h5 class="modal-alert-titulo">${titulo}</h5>
            <p class="modal-alert-mensaje">${mensaje}</p>
            <button type="button" class="btn btn-primary modal-alert-btn">
                Aceptar
            </button>
        </div>
    `;

    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    // Event listeners
    function cerrar() {
        backdrop.classList.add('modal-alert-hide');
        setTimeout(() => {
            backdrop.remove();
            if (callback) callback();
        }, 200);
    }

    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) cerrar();
    });

    modal.querySelector('.modal-alert-btn').addEventListener('click', cerrar);

    // Permitir cerrar con Enter
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            document.removeEventListener('keydown', handleKeyPress);
            cerrar();
        }
    };
    document.addEventListener('keydown', handleKeyPress);
}

/**
 * Mostrar confirmación modal con estilo dinámico
 * @param {string} titulo - Título de la confirmación
 * @param {string} mensaje - Mensaje de la confirmación
 * @param {function} onConfirm - Callback si confirma
 * @param {function} onCancel - Callback si cancela
 * @param {object} opciones - Opciones adicionales (textos de botones, etc)
 */
function showConfirm(titulo, mensaje, onConfirm = null, onCancel = null, opciones = {}) {
    // Remover modal anterior si existe
    const anterior = document.querySelector('.modal-confirm-backdrop');
    if (anterior) anterior.remove();

    // Opciones por defecto
    const {
        textConfirm = 'Confirmar',
        textCancel = 'Cancelar',
        colorConfirm = '#dc3545',
        tipoConfirm = 'danger'
    } = opciones;

    // Crear backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-confirm-backdrop';

    // Crear modal
    const modal = document.createElement('div');
    modal.className = 'modal-confirm';

    modal.innerHTML = `
        <div class="modal-confirm-container">
            <div class="modal-confirm-icon">⚠️</div>
            <h5 class="modal-confirm-titulo">${titulo}</h5>
            <p class="modal-confirm-mensaje">${mensaje}</p>
            <div class="modal-confirm-acciones">
                <button type="button" class="btn btn-secondary modal-confirm-cancel">
                    ${textCancel}
                </button>
                <button type="button" class="btn btn-${tipoConfirm} modal-confirm-ok">
                    ${textConfirm}
                </button>
            </div>
        </div>
    `;

    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    // Event listeners
    function cerrar(confirmado = false) {
        backdrop.classList.add('modal-confirm-hide');
        setTimeout(() => {
            backdrop.remove();
            if (confirmado) {
                if (onConfirm) onConfirm();
            } else {
                if (onCancel) onCancel();
            }
        }, 200);
    }

    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) cerrar(false);
    });

    modal.querySelector('.modal-confirm-cancel').addEventListener('click', () => cerrar(false));
    modal.querySelector('.modal-confirm-ok').addEventListener('click', () => cerrar(true));

    // Permitir cerrar con ESC
    const handleKeyPress = (e) => {
        if (e.key === 'Escape') {
            document.removeEventListener('keydown', handleKeyPress);
            cerrar(false);
        }
    };
    document.addEventListener('keydown', handleKeyPress);
}

/**
 * Función auxiliar para ajustar colores
 */
function ajustarColor(color, percent) {
    const num = parseInt(color.replace("#",""), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.max(0, (num >> 16) + amt);
    const G = Math.max(0, (num >> 8 & 0x00FF) + amt);
    const B = Math.max(0, (num & 0x0000FF) + amt);
    return "#" + (0x1000000 + (R<255?R<1?0:R:255)*0x10000 +
      (G<255?G<1?0:G:255)*0x100 +
      (B<255?B<1?0:B:255))
      .toString(16).slice(1);
}

/**
 * Mostrar confirmación modal estilo reserva con información estructurada
 * @param {string} titulo - Título con icono
 * @param {object} info - Objeto con información (claves: nombre, descripción, etc)
 * @param {function} onConfirm - Callback si confirma
 * @param {function} onCancel - Callback si cancela
 * @param {object} opciones - Opciones adicionales
 */
function showConfirmWithInfo(titulo, info = {}, onConfirm = null, onCancel = null, opciones = {}) {
    // Remover modal anterior si existe
    const anterior = document.querySelector('.modal-confirm-info-backdrop');
    if (anterior) anterior.remove();

    // Opciones por defecto
    const {
        textConfirm = 'Confirmar',
        textCancel = 'Cancelar',
        colorFondo = '#5B68E8',
        tipoConfirm = 'primary'
    } = opciones;

    // Crear backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-confirm-info-backdrop';

    // Crear modal
    const modal = document.createElement('div');
    modal.className = 'modal-confirm-info';

    // Construir filas de información
    let infoHtml = '';
    Object.entries(info).forEach(([clave, valor]) => {
        if (valor) {
            const iconos = {
                fecha: '📅',
                fechaInicio: '📅',
                fechaFin: '📅',
                huespedes: '👥',
                monto: '💰',
                valor: '💰',
                habitacion: '🏨',
                hotel: '🏨',
                reserva: '📋',
                pago: '💳',
                factura: '📄',
                estado: '📊'
            };
            const icon = iconos[clave] || '•';
            infoHtml += `<div class="modal-info-row"><span class="modal-info-icon">${icon}</span> <span class="modal-info-label">${clave}:</span> <span class="modal-info-value">${valor}</span></div>`;
        }
    });

    modal.innerHTML = `
        <div class="modal-confirm-info-header" style="background: linear-gradient(135deg, ${colorFondo}, ${ajustarColor(colorFondo, -20)})">
            <div class="modal-confirm-info-title">
                <span class="modal-confirm-info-icon">❓</span>
                <span>${titulo}</span>
            </div>
            <button type="button" class="btn-close btn-close-white modal-confirm-info-close" aria-label="Close"></button>
        </div>
        <div class="modal-confirm-info-body">
            <div class="modal-confirm-info-pregunta">¿Deseas confirmar esta acción?</div>
            <div class="modal-confirm-info-items">
                ${infoHtml}
            </div>
        </div>
        <div class="modal-confirm-info-footer">
            <button type="button" class="btn btn-outline-secondary modal-confirm-info-cancel">
                ${textCancel}
            </button>
            <button type="button" class="btn btn-${tipoConfirm} modal-confirm-info-ok">
                <i class="bi bi-check-circle"></i> ${textConfirm}
            </button>
        </div>
    `;

    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    // Event listeners
    function cerrar(confirmado = false) {
        backdrop.classList.add('modal-confirm-info-hide');
        setTimeout(() => {
            backdrop.remove();
            if (confirmado) {
                if (onConfirm) onConfirm();
            } else {
                if (onCancel) onCancel();
            }
        }, 200);
    }

    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) cerrar(false);
    });

    modal.querySelector('.modal-confirm-info-close')?.addEventListener('click', () => cerrar(false));
    modal.querySelector('.modal-confirm-info-cancel').addEventListener('click', () => cerrar(false));
    modal.querySelector('.modal-confirm-info-ok').addEventListener('click', () => cerrar(true));

    // Permitir cerrar con ESC
    const handleKeyPress = (e) => {
        if (e.key === 'Escape') {
            document.removeEventListener('keydown', handleKeyPress);
            cerrar(false);
        }
    };
    document.addEventListener('keydown', handleKeyPress);
}