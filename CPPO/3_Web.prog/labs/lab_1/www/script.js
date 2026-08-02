let selectedX = null;
let selectedY = null;
let selectedR = null;

function getCurrentR() {
    return selectedR;
}

window.currentR = getCurrentR;
window.addPointFromCanvas = addPointFromCanvas;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация...');

    try {
        initializeForm();
        initializeModal();
        initializeTable();
        loadStoredResults();
        initializeConfirmModal();

        console.log('Инициализация завершена успешно');
    } catch (error) {
        console.error('Ошибка при инициализации:', error);
    }
});

function initializeForm() {
    console.log('Инициализация формы...');

    // X - radio
    const xRadios = document.querySelectorAll('input[name="x"]');
    console.log('Найдено X радио:', xRadios.length);

    xRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                selectedX = parseInt(this.value, 10);
                console.log('Выбран X:', selectedX);
                validateX();
            }
        });
    });

    const yInput = document.getElementById('y-input');
    if (yInput) {
        yInput.addEventListener('keypress', function(e) {
            const char = String.fromCharCode(e.which);
            const value = this.value;

            if (!/[\d.,\-]/.test(char)) {
                e.preventDefault();
                return;
            }

            if (char === '-' && value.length > 0) {
                e.preventDefault();
                return;
            }

            if ((char === '.' || char === ',') && (value.includes('.') || value.includes(','))) {
                e.preventDefault();
                return;
            }
        });

        yInput.addEventListener('input', function() {
            let value = this.value.trim().replace(',', '.');
            if (value.length > 100) {
                value = value.substring(0, 100);
                this.value = value;
            }
            selectedY = value ? value : null;
            console.log('Введен Y (строка):', selectedY);
            validateY();
        });

        yInput.addEventListener('paste', function(e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleanedText = pastedText.replace(',', '.').trim();

            if (/^-?\d*\.?\d*$/.test(cleanedText)) {
                this.value = cleanedText;
                selectedY = cleanedText;
                validateY();
            }
        });
    }

    const rRadios = document.querySelectorAll('input[name="r"]');
    console.log('Найдено R радио:', rRadios.length);

    rRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                selectedR = parseFloat(this.value);
                console.log('Выбран R:', selectedR);

                updateCurrentRDisplay();
                validateR();

                setTimeout(() => {
                    if (window.drawCoordinatePlane) {
                        window.drawCoordinatePlane();
                    }
                }, 50);
            }
        });
    });

    const form = document.getElementById('coordinateForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmit();
        });
    }

    const clearButton = document.getElementById('clear-results');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            showConfirmModal('Очистить все результаты?', 'Это действие нельзя отменить', function() {
                clearResults();
            });
        });
    }
}

function updateCurrentRDisplay() {
    const currentRSpan = document.getElementById('current-r');
    if (currentRSpan) {
        currentRSpan.textContent = selectedR || '-';
    }
}

function validateX() {
    const errorElement = document.getElementById('x-error');
    if (!errorElement) return true;

    if (selectedX === null || isNaN(selectedX)) {
        showError(errorElement, 'Выберите значение X');
        return false;
    }

    const allowedValues = [-4, -3, -2, -1, 0, 1, 2, 3, 4];
    if (!allowedValues.includes(selectedX)) {
        showError(errorElement, 'X должен быть одним из допустимых значений');
        return false;
    }

    hideError(errorElement);
    return true;
}

function validateY() {
    const errorElement = document.getElementById('y-error');
    if (!errorElement) return true;

    if (selectedY === null || selectedY === '') {
        showError(errorElement, 'Введите значение Y');
        return false;
    }

    if (!/^-?\d+\.?\d*$/.test(selectedY)) {
        showError(errorElement, 'Y должен быть числом');
        return false;
    }
    if (selectedY <= -3 || selectedY >= 5) {
        showError(errorElement, 'Y должен быть в диапазоне от -3 до 5');
        return false;
    }

    console.log('validateY: selectedY =', selectedY);
    hideError(errorElement);
    return true;
}

function validateR() {
    const errorElement = document.getElementById('r-error');
    if (!errorElement) return true;

    if (selectedR === null || isNaN(selectedR)) {
        showError(errorElement, 'Выберите значение R');
        return false;
    }

    const allowedValues = [1, 1.5, 2, 2.5, 3];
    if (!allowedValues.includes(selectedR)) {
        showError(errorElement, 'R должен быть одним из допустимых значений');
        return false;
    }

    hideError(errorElement);
    return true;
}

function showError(element, message) {
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        element.closest('.form-group')?.classList.add('error');
    }
}

function hideError(element) {
    if (element) {
        element.textContent = '';
        element.classList.remove('show');
        element.closest('.form-group')?.classList.remove('error');
    }
}

function handleFormSubmit() {
    console.log('Отправка формы:', { x: selectedX, y: selectedY, r: selectedR });

    if (!validateX() || !validateY() || !validateR()) {
        showModal('Ошибка в форме');
        return;
    }

    sendDataToServer(selectedX, selectedY, selectedR);
}

function sendDataToServer(x, y, r, fromCanvas = false) {
    console.log('Отправка на сервер:', { x, y, r });

    if (!fromCanvas) {
        showLoading(true);
    }

    const data = {
        x: x,
        y: String(y),
        r: r
    };

    console.log('JSON для отправки:', JSON.stringify(data));

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Ответ сервера:', data);
            handleServerResponse(data);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            handleServerError(error);
        })
        .finally(() => {
            if (!fromCanvas) {
                showLoading(false);
            }
        });
}

function handleServerResponse(data) {
    if (data.error) {
        showModal('Ошибка сервера: ' + data.error);
        return;
    }

    console.log('Обработка ответа:', data);

    addResultToTable(data);
    saveResultToStorage(data);

    if (window.addPointToCanvas) {
        window.addPointToCanvas(parseFloat(data.x), parseFloat(data.y), data.hit, parseFloat(data.r));
    }

    hideEmptyState();
    clearForm();
}

function handleServerError(error) {
    let errorMessage = 'Ошибка при отправке запроса на сервер';

    if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Не удается подключиться к серверу. Проверьте, что FastCGI сервер запущен';
    } else if (error.message.includes('500')) {
        errorMessage = 'Внутренняя ошибка сервера';
    } else if (error.message.includes('400')) {
        errorMessage = 'Некорректные данные';
    } else if (error.message.includes('404')) {
        errorMessage = 'Endpoint не найден. Проверьте URL запроса';
    } else if (error.message.includes('405')) {
        errorMessage = 'Недопустимый метод запроса';
    }

    showModal(errorMessage);
}

function truncateNumber(value, maxLength = 20) {
    const str = String(value);
    if (str.length <= maxLength) {
        return str;
    }
    return str.substring(0, maxLength) + '...';
}

function createCellWithTooltip(value) {
    const truncated = truncateNumber(value);
    const fullValue = String(value);

    if (truncated === fullValue) {
        return truncated;
    }

    return `<span class="truncated-value" data-full-value="${fullValue}">${truncated}</span>`;
}

function addResultToTable(data) {
    const tableBody = document.getElementById('results-body');
    if (!tableBody) return;

    const row = document.createElement('tr');
    row.className = data.hit ? 'hit' : 'miss';

    const resultText = data.hit ? 'Попадание' : 'Промах';
    const resultClass = data.hit ? 'result-hit' : 'result-miss';

    row.innerHTML = `
        <td>${createCellWithTooltip(data.x)}</td>
        <td>${createCellWithTooltip(data.y)}</td>
        <td>${createCellWithTooltip(data.r)}</td>
        <td class="${resultClass}">${resultText}</td>
        <td>${formatTime(data.currentTime)}</td>
        <td>${data.scriptTimeMs} мс</td>
    `;

    tableBody.insertBefore(row, tableBody.firstChild);

    initializeTooltips(row);

    hideEmptyState();
}

function initializeTooltips(container = document) {
    const truncatedElements = container.querySelectorAll('.truncated-value');

    truncatedElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.currentTarget;
    const fullValue = element.getAttribute('data-full-value');

    hideTooltip();

    const tooltip = document.createElement('div');
    tooltip.className = 'value-tooltip';
    tooltip.id = 'active-tooltip';

    tooltip.innerHTML = `
        <div class="tooltip-header">
            <span class="tooltip-label">ПОЛНОЕ ЗНАЧЕНИЕ</span>
            <button class="tooltip-close" onclick="window.hideTooltip()">×</button>
        </div>
        <span class="tooltip-number">${fullValue}</span>
        <div class="tooltip-arrow"></div>
    `;

    document.body.appendChild(tooltip);

    const closeBtn = tooltip.querySelector('.tooltip-close');
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hideTooltip();
    });

    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 12;

    const padding = 10;
    if (left < padding) left = padding;
    if (left + tooltipRect.width > window.innerWidth - padding) {
        left = window.innerWidth - tooltipRect.width - padding;
    }

    if (top < padding) {
        top = rect.bottom + 12;
        tooltip.classList.add('below');
    }

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + window.scrollY + 'px';

    requestAnimationFrame(() => {
        tooltip.classList.add('visible');
    });
}

window.hideTooltip = hideTooltip;

function hideTooltip() {
    const existingTooltip = document.getElementById('active-tooltip');
    if (existingTooltip) {
        existingTooltip.classList.remove('visible');
        setTimeout(() => existingTooltip.remove(), 200);
    }
}

function formatTime(timeString) {
    try {
        const date = new Date(timeString);
        return date.toLocaleString('ru-RU');
    } catch (e) {
        return timeString;
    }
}

function clearForm() {
    selectedX = null;
    selectedY = null;

    // Снимаем выделение с radio-кнопок X
    document.querySelectorAll('input[name="x"]').forEach(radio => radio.checked = false);

    const yInput = document.getElementById('y-input');
    if (yInput) yInput.value = '';

    ['x-error', 'y-error'].forEach(id => {
        const errorElement = document.getElementById(id);
        if (errorElement) {
            hideError(errorElement);
        }
    });
}

function clearResults() {
    const tableBody = document.getElementById('results-body');
    if (tableBody) {
        tableBody.innerHTML = '';
    }

    localStorage.removeItem('checkResults');

    if (window.clearCanvasPoints) {
        window.clearCanvasPoints();
    }

    showEmptyState();
}

function hideEmptyState() {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
}

function showEmptyState() {
    const emptyState = document.getElementById('empty-state');
    const tableBody = document.getElementById('results-body');
    if (emptyState && tableBody && tableBody.children.length === 0) {
        emptyState.style.display = 'block';
    }
}

function saveResultToStorage(data) {
    try {
        let results = JSON.parse(localStorage.getItem('checkResults') || '[]');
        results.unshift(data);
        if (results.length > 100) {
            results = results.slice(0, 100);
        }
        localStorage.setItem('checkResults', JSON.stringify(results));
    } catch (e) {
        console.error('Ошибка сохранения в localStorage:', e);
    }
}

function loadStoredResults() {
    try {
        const results = JSON.parse(localStorage.getItem('checkResults') || '[]');
        if (results.length === 0) {
            showEmptyState();
            return;
        }

        results.forEach(data => {
            addResultToTable(data);
            if (window.addPointToCanvas) {
                window.addPointToCanvas(parseFloat(data.x), parseFloat(data.y), data.hit, parseFloat(data.r));
            }
        });

        hideEmptyState();
    } catch (e) {
        console.error('Ошибка загрузки из localStorage:', e);
        showEmptyState();
    }
}

function initializeModal() {
    const modal = document.getElementById('error-modal');
    if (!modal) return;

    const closeBtn = modal.querySelector('.close-btn');
    const backdrop = modal.querySelector('.modal-backdrop');

    if (closeBtn) {
        closeBtn.addEventListener('click', () => hideModal());
    }

    if (backdrop) {
        backdrop.addEventListener('click', () => hideModal());
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            hideModal();
        }
    });
}

function showModal(message) {
    const modal = document.getElementById('error-modal');
    const errorText = document.getElementById('error-text');

    if (modal && errorText) {
        errorText.textContent = message;
        modal.style.display = 'flex';
    }
}

function hideModal() {
    const modal = document.getElementById('error-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'flex' : 'none';
    }
}

function initializeTable() {
    initializeTooltips();
}

let confirmCallback = null;

function initializeConfirmModal() {
    const confirmModal = document.getElementById('confirm-modal');
    if (!confirmModal) {
        createConfirmModal();
    }
}

function createConfirmModal() {
    const modalHTML = `
        <div id="confirm-modal" class="modal">
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title" id="confirm-title">Подтверждение</h3>
                    <button class="close-btn" type="button" onclick="hideConfirmModal()">×</button>
                </div>
                <div class="modal-body">
                    <p id="confirm-text"></p>
                </div>
                <div class="modal-actions">
                    <button class="modal-btn modal-btn-secondary" onclick="hideConfirmModal()">Отмена</button>
                    <button class="modal-btn modal-btn-primary" onclick="confirmAction()">Подтвердить</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function showConfirmModal(title, message, callback) {
    let confirmModal = document.getElementById('confirm-modal');
    if (!confirmModal) {
        createConfirmModal();
        confirmModal = document.getElementById('confirm-modal');
    }

    const confirmTitle = document.getElementById('confirm-title');
    const confirmText = document.getElementById('confirm-text');

    if (confirmTitle) confirmTitle.textContent = title;
    if (confirmText) confirmText.textContent = message;

    confirmCallback = callback;

    if (confirmModal) {
        confirmModal.style.display = 'flex';
    }
}

window.hideConfirmModal = function() {
    const confirmModal = document.getElementById('confirm-modal');
    if (confirmModal) {
        confirmModal.style.display = 'none';
    }
    confirmCallback = null;
};

window.confirmAction = function() {
    if (confirmCallback) {
        confirmCallback();
    }
    window.hideConfirmModal();
};

function addPointFromCanvas(mathX, mathY) {
    const r = getCurrentR();
    if (!r || r <= 0) {
        showModal('Выберите значение R перед добавлением точки');
        return;
    }
    sendDataToServer(mathX, mathY, r, true);
}