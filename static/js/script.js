// ============== FUNCIONES AUXILIARES ==============

// Cerrar alertas automáticamente
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Confirmación para acciones peligrosas
function confirmDelete(message = '¿Estás seguro de que deseas eliminar esto?') {
    return confirm(message);
}

// Validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    let isValid = true;
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#e74c3c';
            isValid = false;
        } else {
            input.style.borderColor = '#e0e0e0';
        }
    });
    
    return isValid;
}

// Mostrar loading
function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.textContent = 'Cargando...';
    }
}

// Formatear fecha
function formatDate(dateString) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}

// Copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('¡Copiado al portapapeles!');
    }).catch(() => {
        alert('Error al copiar');
    });
}

// Mostrar/ocultar contraseña
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

// Modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Validar email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Descargar archivo
function downloadFile(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Detectar cambios en formulario
function trackFormChanges(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const originalData = new FormData(form);
    let hasChanges = false;
    
    form.addEventListener('change', function() {
        hasChanges = true;
    });
    
    window.addEventListener('beforeunload', function(e) {
        if (hasChanges && !form.querySelector('button[type="submit"]:disabled')) {
            e.preventDefault();
            e.returnValue = '¿Deseas salir sin guardar los cambios?';
        }
    });
}

// Animar elementos al hacer scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.stat-card, .task-card, .material-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.5s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => observer.observe(el));
}

document.addEventListener('DOMContentLoaded', animateOnScroll);

document.addEventListener('DOMContentLoaded', function() {
    const bellButton = document.getElementById('navBellButton');
    const bellDropdown = document.getElementById('navBellDropdown');
    const bellSoundToggle = document.getElementById('bellSoundToggle');

    if (!bellButton || !bellDropdown) return;

    let markedAsRead = false;

    const badge = bellButton.querySelector('.bell-badge');
    const currentUnread = badge ? Number.parseInt(badge.textContent || '0', 10) || 0 : 0;
    let soundEnabled = (document.body?.dataset?.notificationSoundEnabled || '1') === '1';
    const bellStorageKey = 'nav_unread_count_last';
    const previousUnread = Number.parseInt(localStorage.getItem(bellStorageKey) || '0', 10) || 0;

    function playBellTone() {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const audioContext = new AudioCtx();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(920, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.0001, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.035, audioContext.currentTime + 0.02);
            gainNode.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.25);

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.26);
        } catch (error) {
            console.warn('No se pudo reproducir el tono de notificación');
        }
    }

    if (currentUnread > 0) {
        bellButton.classList.add('bell-pulse');
    }
    if (soundEnabled && currentUnread > previousUnread) {
        playBellTone();
    }
    localStorage.setItem(bellStorageKey, String(currentUnread));

    if (bellSoundToggle) {
        bellSoundToggle.checked = soundEnabled;
        bellSoundToggle.addEventListener('change', async function() {
            const enabled = !!bellSoundToggle.checked;
            soundEnabled = enabled;
            if (document.body && document.body.dataset) {
                document.body.dataset.notificationSoundEnabled = enabled ? '1' : '0';
            }

            try {
                await fetch('/notifications/sound-preference', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled })
                });
            } catch (error) {
                console.warn('No se pudo guardar preferencia de sonido');
            }
        });
    }

    bellButton.addEventListener('click', async function(event) {
        event.preventDefault();
        event.stopPropagation();
        const willOpen = !bellDropdown.classList.contains('open');
        bellDropdown.classList.toggle('open');

        if (willOpen && !markedAsRead) {
            markedAsRead = true;
            try {
                await fetch('/notifications/mark-read', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                bellButton.classList.remove('has-unread');
                bellButton.classList.remove('bell-pulse');
                const unreadBadge = bellButton.querySelector('.bell-badge');
                if (unreadBadge) unreadBadge.remove();
                localStorage.setItem(bellStorageKey, '0');
            } catch (error) {
                console.warn('No se pudieron marcar notificaciones como leídas');
            }
        }
    });

    document.addEventListener('click', function(event) {
        if (!bellDropdown.contains(event.target) && event.target !== bellButton) {
            bellDropdown.classList.remove('open');
        }
    });
});

// Buscar en tablas
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Exportar datos a CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => {
            csvRow.push('"' + col.textContent.trim() + '"');
        });
        csv.push(csvRow.join(','));
    });
    
    const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv.join('\n'));
    downloadFile(csvContent, filename);
}

// Crear notificación
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.style.display='none';" class="close-btn">&times;</button>
    `;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
        
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
}

// Validar contraseña fuerte
function validatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    return strength;
}

// Mostrar indicador de fortaleza de contraseña
function showPasswordStrength(inputId, strengthId) {
    const input = document.getElementById(inputId);
    const strengthDisplay = document.getElementById(strengthId);
    
    if (!input || !strengthDisplay) return;
    
    input.addEventListener('input', function() {
        const strength = validatePasswordStrength(this.value);
        const strengthTexts = ['Muy débil', 'Débil', 'Medio', 'Fuerte', 'Muy fuerte'];
        const strengthColors = ['#e74c3c', '#e67e22', '#f39c12', '#2ecc71', '#27ae60'];
        
        strengthDisplay.textContent = strengthTexts[strength];
        strengthDisplay.style.color = strengthColors[strength];
    });
}

// Log de eventos para debugging
function logEvent(eventName, details = {}) {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log(`[App Event] ${eventName}`, details);
    }
}
