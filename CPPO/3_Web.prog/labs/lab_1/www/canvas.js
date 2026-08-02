let canvas, ctx;
const CONFIG = {
    size: 600,
    center: 300,
    scale: 60,
    padding: { outer: 25, inner: 35 },
    radius: { border: 20, inner: 15 }
};
let points = [];
let hitCounts = { q1: 0, q2: 0, q3: 0, q4: 0 }; // Счетчики попаданий по квадрантам

document.addEventListener('DOMContentLoaded', () => setTimeout(initializeCanvas, 200));

function initializeCanvas() {
    canvas = document.getElementById('coordinatePlane');
    if (!canvas || !(ctx = canvas.getContext('2d'))) {
        console.error('Canvas initialization failed');
        return;
    }
    canvas.addEventListener('click', handleCanvasClick);
    drawCoordinatePlane();
}

function drawCoordinatePlane() {
    if (!ctx) return;

    ctx.clearRect(0, 0, CONFIG.size, CONFIG.size);
    drawFrame();
    drawAxes();

    const r = window.currentR?.();
    if (r > 0) drawAreas(r);

    drawScale();
    drawAllPoints();
    drawHitCounters();
}

function drawFrame() {
    // Простой серый фон для всей области canvas
    ctx.save();
    ctx.fillStyle = 'rgba(50,48,48,0.67)';  // Светло-серый цвет
    ctx.fillRect(0, 0, CONFIG.size, CONFIG.size);
    ctx.restore();
}

function drawAxes() {
    ctx.save();

    ctx.strokeStyle = 'rgba(255,255,255,0.47)';
    ctx.lineWidth = 3

    // Горизонтальная ось X
    ctx.beginPath();
    ctx.moveTo(CONFIG.center-CONFIG.scale*4-20, CONFIG.center);
    ctx.lineTo( CONFIG.center+CONFIG.scale*4+20, CONFIG.center);
    ctx.stroke();

    // Вертикальная ось Y
    ctx.beginPath();
    ctx.moveTo(CONFIG.center, CONFIG.center-CONFIG.scale*4-20);
    ctx.lineTo(CONFIG.center, CONFIG.center+CONFIG.scale*4+20);
    ctx.stroke();

    // Стрелки осей (исправленные координаты)
    ctx.fillStyle = 'rgba(255,255,255,0.47)';
    const arrow = [
        // Стрелка X (в конце горизонтальной оси)
        [CONFIG.center+CONFIG.scale*4+20, CONFIG.center, CONFIG.center+CONFIG.scale*4+10, CONFIG.center - 5, CONFIG.center+CONFIG.scale*4+10, CONFIG.center + 5],
        // Стрелка Y (в конце вертикальной оси)
        [CONFIG.center, CONFIG.center-CONFIG.scale*4-20, CONFIG.center - 5, CONFIG.center-CONFIG.scale*4-10, CONFIG.center + 5, CONFIG.center-CONFIG.scale*4-10]
    ];

    arrow.forEach(pts => {
        ctx.beginPath();
        ctx.moveTo(pts[0], pts[1]);
        ctx.lineTo(pts[2], pts[3]);
        ctx.lineTo(pts[4], pts[5]);
        ctx.closePath();
        ctx.fill();
    });

    ctx.restore();
}

function drawAreas(r) {
    const rPx = r * CONFIG.scale;
    const halfR = rPx / 2;

    ctx.save();
    ctx.globalAlpha = 0.4;

    // Треугольник в 1 квадранте (справа вверху): вершины (0, R/2), (R/2, R), (0, R)
    ctx.fillStyle = 'rgba(0,123,255,0.8)';
    ctx.beginPath();
    ctx.moveTo(CONFIG.center, CONFIG.center ); // (0, 0)
    ctx.lineTo(CONFIG.center , CONFIG.center - halfR); // (R/2, R)
    ctx.lineTo(CONFIG.center+rPx, CONFIG.center ); // (0, R)
    ctx.closePath();
    ctx.fill();

    // Четверть круга в 3 квадранте (слева внизу): радиус R/2, центр в (0,0)
    ctx.fillStyle = 'rgba(255,165,0,0.8)';
    ctx.beginPath();
    ctx.arc(CONFIG.center, CONFIG.center, halfR, Math.PI/2, Math.PI );
    ctx.lineTo(CONFIG.center, CONFIG.center);
    ctx.closePath();
    ctx.fill();

    // Прямоугольник в 4 квадранте (справа внизу): 0 <= x <= R/2, -R <= y <= -R/2
    ctx.fillStyle = 'rgba(40,167,69,0.8)';
    ctx.fillRect(CONFIG.center, CONFIG.center , halfR, rPx);

    ctx.restore();
}

function drawScale() {
    ctx.save();
    ctx.fillStyle = 'rgba(255,255,255,0.47)';
    ctx.font = '13px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // 4 деления в каждую сторону от центра
    [ -4, -3, -2, -1, 1, 2, 3, 4].forEach(factor => {
        const px = factor * CONFIG.scale;
        const label = factor.toString();

        const x = CONFIG.center + px;
        if (x >= 50 && x <= CONFIG.size - 50) {
            ctx.fillText(label, x, CONFIG.center + 30);
            ctx.strokeStyle = 'rgba(255,255,255,0.47)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x, CONFIG.center - 8);
            ctx.lineTo(x, CONFIG.center + 8);
            ctx.stroke();
        }

        const y = CONFIG.center - px;
        if (y >= 50 && y <= CONFIG.size - 50) {
            ctx.fillText(label, CONFIG.center - 40, y);
            ctx.strokeStyle = 'rgba(255,255,255,0.47)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(CONFIG.center - 8, y);
            ctx.lineTo(CONFIG.center + 8, y);
            ctx.stroke();
        }
    });

    // Добавляем деление для 0 (центра)
    ctx.strokeStyle = 'rgba(255,255,255,0.47)';
    ctx.lineWidth = 2;

    // Деление для 0 на оси X
    ctx.beginPath();
    ctx.moveTo(CONFIG.center, CONFIG.center - 8);
    ctx.lineTo(CONFIG.center, CONFIG.center + 8);
    ctx.stroke();

    // Деление для 0 на оси Y
    ctx.beginPath();
    ctx.moveTo(CONFIG.center - 8, CONFIG.center);
    ctx.lineTo(CONFIG.center + 8, CONFIG.center);
    ctx.stroke();

    ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.47)';
    ctx.fillText('X', CONFIG.size - 50, CONFIG.center - 20);
    ctx.fillText('Y', CONFIG.center + 20, 50);
    ctx.fillText('0', CONFIG.center - 25, CONFIG.center + 25);

    ctx.restore();
}

function drawHitCounters() {
    ctx.save();

    const boxSize = 40;
    const fontSize = 14;
    // Уменьшаем отступы от краев и приближаем к центру
    const positions = [
        { x: CONFIG.center - boxSize-200 , y: CONFIG.center - boxSize - 200, quadrant: 'q2' }, // Левый верхний (2 квадрант)
        { x: CONFIG.center + 200, y: CONFIG.center - boxSize - 200, quadrant: 'q1' }, // Правый верхний (1 квадрант)
        { x: CONFIG.center - boxSize - 200, y: CONFIG.center + 200, quadrant: 'q3' }, // Левый нижний (3 квадрант)
        { x: CONFIG.center + 200, y: CONFIG.center + 200, quadrant: 'q4' } // Правый нижний (4 квадрант)
    ];

    positions.forEach(pos => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(pos.x, pos.y, boxSize, boxSize);

        ctx.fillStyle = 'rgba(170,255,0,0.7)';
        ctx.font = `bold ${fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(
            hitCounts[pos.quadrant].toString(),
            pos.x + boxSize / 2,
            pos.y + boxSize / 2
        );

        ctx.fillStyle = 'rgba(170,255,0,0.7)';
        ctx.font = '18px -apple-system, BlinkMacSystemFont, sans-serif'; // Исправлено: добавлены кавычки
        const quadrantLabel = getQuadrantLabel(pos.quadrant);
        ctx.fillText(
            quadrantLabel,
            pos.x + boxSize / 2,
            pos.y + boxSize + 15
        );
    });

    ctx.restore();
}

function getQuadrantLabel(quadrant) {
    const labels = {
        'q1': 'I четверть',
        'q2': 'II четверть',
        'q3': 'III четверть',
        'q4': 'IV четверть'
    };
    return labels[quadrant] || quadrant;
}

function updateHitCounters() {
    hitCounts = { q1: 0, q2: 0, q3: 0, q4: 0 };

    points.forEach(point => {
        if (point.hit) {
            const quadrant = getPointQuadrant(point.x, point.y);
            if (quadrant && hitCounts[quadrant] !== undefined) {
                hitCounts[quadrant]++;
            }
        }
    });
}

function getPointQuadrant(x, y) {
    if (x > 0 && y > 0) return 'q1';
    if (x < 0 && y > 0) return 'q2';
    if (x < 0 && y < 0) return 'q3';
    if (x > 0 && y < 0) return 'q4';
    return null; х
}

function drawAllPoints() {
    points.forEach(({ x, y, hit }) => {
        if (typeof x === 'number' && typeof y === 'number') drawPoint(x, y, hit);
    });
}

function drawPoint(x, y, hit) {
    const pixelX = CONFIG.center + x * CONFIG.scale;
    const pixelY = CONFIG.center - y * CONFIG.scale;

    ctx.save();
    ctx.shadowColor = hit ? 'rgba(34,139,34,0.4)' : 'rgba(220,20,60,0.4)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 3;

    const grad = ctx.createRadialGradient(pixelX - 3, pixelY - 3, 0, pixelX, pixelY, 12);
    const colors = hit
        ? ['rgba(255,255,255,0.9)', 'rgba(50,205,50,0.9)', 'rgba(34,139,34,0.95)', 'rgba(0,100,0,0.8)']
        : ['rgba(255,255,255,0.9)', 'rgba(255,69,0,0.9)', 'rgba(220,20,60,0.95)', 'rgba(139,0,0,0.8)'];
    colors.forEach((color, i) => grad.addColorStop([0, 0.3, 0.7, 1][i], color));

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(pixelX, pixelY, 11, 0, 2 * Math.PI);
    ctx.fill();

    ctx.shadowColor = 'transparent';
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.beginPath();
    ctx.arc(pixelX - 3, pixelY - 3, 3, 0, 2 * Math.PI);
    ctx.fill();

    ctx.restore();
}

function handleCanvasClick(event) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();

    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const canvasX = (event.clientX - rect.left) * scaleX;
    const canvasY = (event.clientY - rect.top) * scaleY;

    const mathX = (canvasX - CONFIG.center) / CONFIG.scale;
    const mathY = -(canvasY - CONFIG.center) / CONFIG.scale;

    const preciseX = mathX.toString().substring(0, 100);
    const preciseY = mathY.toString().substring(0, 100);

    console.log('Click:', { canvasX, canvasY, mathX, mathY });

    window.addPointFromCanvas?.(preciseX, preciseY);
}

function addPointToCanvas(x, y, hit, r) {
    if (typeof x === 'number' && typeof y === 'number') {
        points.push({ x, y, hit, r });
        updateHitCounters();
        setTimeout(drawCoordinatePlane, 10);
    }
}

function removePointFromCanvas(x, y) {
    points = points.filter(p => !(Math.abs(p.x - x) < 0.001 && Math.abs(p.y - y) < 0.001));
    updateHitCounters();
    drawCoordinatePlane();
}

Object.assign(window, {
    drawCoordinatePlane,
    addPointToCanvas,
    clearCanvas: () => {
        points = [];
        hitCounts = { q1: 0, q2: 0, q3: 0, q4: 0 };
        drawCoordinatePlane();
    },
    clearAllPoints: () => {
        points = [];
        hitCounts = { q1: 0, q2: 0, q3: 0, q4: 0 };
        drawCoordinatePlane();
    },
    removePointFromCanvas,
    getAllPoints: () => [...points],
    setScale: newScale => { if (newScale > 0) { CONFIG.scale = newScale; drawCoordinatePlane(); } },
    resizeCanvas: newSize => {
        if (newSize > 0) {
            CONFIG.size = newSize;
            CONFIG.center = newSize / 2;
            if (canvas) { canvas.width = newSize; canvas.height = newSize; }
            drawCoordinatePlane();
        }
    },
    currentR: window.currentR
});