window.showModal = function(msg, onOk) {
    let modal = document.getElementById('modal');
    let modalMsg = document.getElementById('modalMsg');
    let modalBtn = document.getElementById('modalBtn');
    let modalCancelBtn = document.getElementById('modalCancelBtn');

    modalMsg.textContent = msg;
    modal.classList.remove('hidden');

    // Снимаем все старые обработчики:
    let okClone = modalBtn.cloneNode(true);
    modalBtn.parentNode.replaceChild(okClone, modalBtn);
    let cancelClone = modalCancelBtn.cloneNode(true);
    modalCancelBtn.parentNode.replaceChild(cancelClone, modalCancelBtn);

    okClone.onclick = function() {
        modal.classList.add('hidden');
        if (onOk) onOk();
    };

    cancelClone.onclick = function() {
        modal.classList.add('hidden');
    };

    okClone.focus();
};

function filterDecimalInput(evt) {
    let v = evt.target.value;
    v = v.replace(/[^0-9.,-]/g, '');
    v = v.replace(/(?!^)-/g, '');

    let firstDot = v.indexOf('.');
    let firstComma = v.indexOf(',');

    if (firstComma !== -1 && (firstDot === -1 || firstComma < firstDot)) {
        v = v.replace(',', '.');
        v = v.replace(/[\.,]/g, (match, offset) => offset === v.indexOf('.') ? '.' : '');
    } else {
        v = v.replace(/[\.,]/g, (match, offset) => offset === v.indexOf('.') ? '.' : '');
    }

    evt.target.value = v;
}

function validateInput() {
    let y = document.getElementById('y').value.trim();
    let r = document.getElementById('r').value.trim();
    let yNum = parseFloat(y);
    let rNum = parseFloat(r);

    let xChecked = document.querySelector('[name="x"]:checked');
    if(!xChecked){
        window.showModal('Выберите X!');
        return false;
    }

    let x = parseFloat(xChecked.value);
    if(isNaN(x) || x < -2 || x > 2){
        window.showModal('Координата X вне допустимых значений!');
        return false;
    }

    if(isNaN(yNum) || yNum <= -3 || yNum >= 5) {
        window.showModal('Y должен быть числом от -3 (не включая) до 5 (не включая)!');
        return false;
    }

    if(isNaN(rNum) || rNum < 1 || rNum > 4) {
        window.showModal('R должен быть числом от 1 до 4!');
        return false;
    }

    return true;
}

document.addEventListener('DOMContentLoaded', function() {
    // Обработка формы проверки
    const form = document.getElementById('checkForm');
    if (form) {
        form.onsubmit = function(e) {
            if (!validateInput()) {
                e.preventDefault();
            }
        };
    }

    // Фильтрация ввода для Y и R
    let y = document.getElementById('y');
    let r = document.getElementById('r');
    if (y) y.addEventListener('input', filterDecimalInput);
    if (r) r.addEventListener('input', filterDecimalInput);

    // Обработка кнопки очистки
    const clearBtn = document.getElementById('clearResultsBtn');
    if (clearBtn) {
        clearBtn.onclick = function() {
            window.showModal('Вы действительно хотите удалить всю историю?', function() {
                document.getElementById('clearForm').submit();
            });
        };
    }

    // Обработка кнопки выхода (удаление JWT cookie)
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.onclick = function() {
            window.showModal('Вы действительно хотите выйти?', function() {
                // Удаляем JWT cookie
                document.cookie = "jwt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.location.reload();
            });
        };
    }
});