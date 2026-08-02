let canvas = null;
let ctx = null;

const CONFIG = {
    size: 400,
    center: 200,
    scale: 30
};

function clearCanvas() {
    if (!ctx) {
        console.warn("clearCanvas: Нет контекста для canvas!");
        return;
    }
    ctx.clearRect(0, 0, CONFIG.size, CONFIG.size);
    console.log("clearCanvas: Очищен canvas");
}

function drawArea(r = 2) {
    console.log("drawArea: старт, r =", r);
    clearCanvas();
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(0, 0, CONFIG.size, CONFIG.size, 20);
    ctx.fillStyle = "rgb(106,105,105)";
    ctx.fill();
    ctx.closePath();
    ctx.restore();
    ctx.save();
    ctx.translate(CONFIG.center, CONFIG.center);

    // Четверть круга
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, CONFIG.scale * r, 0, Math.PI * 0.5, false);
    ctx.closePath();
    ctx.fillStyle = "rgb(225,160,39)";
    ctx.fill();

    // Прямоугольник
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(CONFIG.scale * r, 0);
    ctx.lineTo(CONFIG.scale * r, -CONFIG.scale * (r / 2));
    ctx.lineTo(0, -CONFIG.scale * (r / 2));
    ctx.closePath();
    ctx.fillStyle = "rgb(113,225,39)";
    ctx.fill();

    // Треугольник
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-CONFIG.scale * (r/2) , 0);
    ctx.lineTo(0, -CONFIG.scale * r/2);
    ctx.closePath();
    ctx.fillStyle = "rgb(233,248,0)";
    ctx.fill();
    ctx.restore();

    drawAxes();
    drawHitsForCurrentR(r);

    console.log("drawArea: завершено");
}

function drawAxes() {
    ctx.save();
    ctx.translate(CONFIG.center, CONFIG.center);
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    let half = CONFIG.scale * 5.5;
    ctx.beginPath();
    ctx.moveTo(-half, 0);
    ctx.lineTo(half, 0);
    ctx.moveTo(0, half);
    ctx.lineTo(0, -half);
    ctx.stroke();

    // Стрелка X
    ctx.beginPath();
    ctx.moveTo(half, 0);
    ctx.lineTo(half - 12, 7);
    ctx.lineTo(half - 12, -7);
    ctx.closePath();
    ctx.fillStyle = "black";
    ctx.fill();

    // Стрелка Y
    ctx.beginPath();
    ctx.moveTo(0, -half);
    ctx.lineTo(7, -half + 12);
    ctx.lineTo(-7, -half + 12);
    ctx.closePath();
    ctx.fillStyle = "black";
    ctx.fill();

    ctx.font = "bold 15px Arial";
    ctx.fillStyle = "black";
    ctx.fillText("X", half, -10);
    ctx.fillText("Y", 10, -half);
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    for (let v = -5; v <= 5; v++) {
        if (v !== 0) {
            let pos = CONFIG.scale * v;
            ctx.beginPath();
            ctx.moveTo(pos, 5);
            ctx.lineTo(pos, -5);
            ctx.stroke();
            ctx.fillText(v, pos, 20);
            ctx.beginPath();
            ctx.moveTo(-5, -pos);
            ctx.lineTo(5, -pos);
            ctx.stroke();
            ctx.fillText(v, -20, -pos + 5);
        }
    }
    ctx.restore();
    console.log("drawAxes: координатные оси нарисованы");
}

function plotPoint(x, y, hit, r) {
    ctx.save();
    ctx.translate(CONFIG.center, CONFIG.center);
    let px = CONFIG.scale * x;
    let py = -CONFIG.scale * y;
    ctx.beginPath();
    ctx.arc(px, py, 4, 0, 2 * Math.PI);
    ctx.fillStyle = hit ? "green" : "red";
    ctx.fill();
    ctx.strokeStyle = "black";
    ctx.stroke();
    ctx.restore();
    console.log(`plotPoint: нарисована точка x=${x} y=${y} hit=${hit} r=${r}`);
}

function getR() {
    const rInput = document.getElementById('checkForm:r');
    let rVal = 2;
    if (rInput) {
        let v = rInput.value.replace(',', '.');
        let parsed = parseFloat(v);
        if (!isNaN(parsed)) rVal = parsed;
        console.log("getR: r прочитан как", rVal, "(сырой =", v, ")");
    } else {
        console.log("getR: поле r не найдено, используется r = 2");
    }
    return rVal;
}

function getHitHistoryFromTable() {
    const table = document.getElementById('resultsTable');
    if (!table) {
        console.warn("getHitHistoryFromTable: таблица не найдена!");
        return [];
    }

    const rows = table.getElementsByTagName('tr');
    const hits = [];

    // Пропускаем header-строку (начиная с rows[1])
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        // Колонки: X | Y | R | Hit ...
        if (cells.length >= 4) {
            let x = parseFloat(cells[0].textContent.trim());
            let y = parseFloat(cells[1].textContent.trim());
            let r = parseFloat(cells[2].textContent.trim());
            let hit = cells[3].textContent.trim().toLowerCase() === "true" || cells[3].textContent.trim() === "+"; // зависит от твоего бина!
            hits.push({ x, y, r, hit });
        }
    }
    console.log("getHitHistoryFromTable: найдено точек", hits.length);
    return hits;
}

function drawHitsForCurrentR(currentR) {
    const hitHistory = getHitHistoryFromTable();
    let filtered = hitHistory.filter(point =>
        point && parseFloat(point.r) === parseFloat(currentR)
    );
    console.log(`drawHitsForCurrentR: найдено точек для r=${currentR}:`, filtered.length);
    filtered.forEach(pt => plotPoint(pt.x, pt.y, pt.hit, pt.r));
}

function handleCanvasClick(e) {
    if (!canvas) {
        console.error("handleCanvasClick: canvas не найден!");
        return;
    }
    const rect = canvas.getBoundingClientRect();
    const r = getR();
    const xClick = (e.clientX - rect.left - CONFIG.center) / CONFIG.scale;
    const yClick = -(e.clientY - rect.top - CONFIG.center) / CONFIG.scale;
    console.log(`handleCanvasClick: canvas click x=${xClick}, y=${yClick}, r=${r}`);

    if (xClick < -5 || xClick > 5) {
        alert('Ошибка: выбранная координата X вне диапазона [-5, 5].');
        return;
    }
    if (yClick < -3 || yClick > 3) {
        alert('Ошибка: выбранная координата Y вне диапазона (-3, 3).');
        return;
    }

    let rawX = Math.round(xClick);
    let xVal = Math.max(-5, Math.min(5, rawX));
    if (window.PF && PF('spinnerX')) {
        PF('spinnerX').setValue(xVal);
        console.log("handleCanvasClick: spinnerX установлен через PF =", xVal);
    } else {
        let xInput = document.getElementById('checkForm:x_input') ||
            document.getElementById('checkForm:x');
        if (xInput) {
            xInput.value = xVal;
            console.log("handleCanvasClick: X установлен через input =", xVal);
        }
    }
    const yInput = document.getElementById('checkForm:y');
    if (yInput) {
        yInput.value = yClick.toFixed(2);
        console.log("handleCanvasClick: Y установлен через input =", yClick.toFixed(2));
    }
    let checkBtn = document.getElementById('checkForm:checkBtn') || document.getElementById('checkBtn');
    if (checkBtn) {
        checkBtn.click();
        console.log("handleCanvasClick: Кнопка проверить нажата");
    }
}

function initCanvasAndDraw() {
    canvas = document.getElementById('coordinatePlane');
    if (!canvas) {
        console.error("initCanvasAndDraw: Не найден canvas с id=coordinatePlane");
        return;
    }
    ctx = canvas.getContext('2d');
    console.log('initCanvasAndDraw: canvas и ctx инициализированы');

    drawArea(getR());

    // Обработчики поля r
    const rInput = document.getElementById('checkForm:r');
    if (rInput) {
        rInput.addEventListener('input', function() {
            console.log("initCanvasAndDraw: r input изменён");
            drawArea(getR());
        });
        rInput.addEventListener('change', function() {
            console.log("initCanvasAndDraw: r change изменён");
            drawArea(getR());
        });
    }
    // Обработчик slideStop для PrimeFaces slider
    if (window.PF && PF('checkForm:rSlider')) {
        PF('checkForm:rSlider').jq.off('slideStop').on('slideStop', function() {
            console.log("initCanvasAndDraw: slideStop slider r изменён");
            drawArea(getR());
        });
    }
    // Canvas click обработчик
    canvas.removeEventListener('click', handleCanvasClick);
    canvas.addEventListener('click', handleCanvasClick);

    console.log('initCanvasAndDraw: обработчики событий привязаны');
}





window.onload = initCanvasAndDraw;
