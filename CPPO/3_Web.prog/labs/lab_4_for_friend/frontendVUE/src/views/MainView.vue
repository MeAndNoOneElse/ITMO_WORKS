<template>
  <div class="app-container">
    <header class="header">
      <div class="header-content">
        <span><b>ФИО:</b> Федяев Михаил Дмитриевич</span>
        <span><b>Группа:</b> P3219</span>
        <span><b>Вариант:</b> 454</span>
      </div>
      <div class="header-controls">
        <button class="btn-exit" @click="onLogout">Выйти</button>
      </div>
    </header>

    <!-- Desktop (>=1218): слева [форма + таблица], справа [график] -->
    <div v-if="layoutMode === 'mode-desktop'" class="layout-desktop">
      <div class="left-panel">
        <div class="card form-container">
          <PointForm
            v-model:modelX="x"
            v-model:modelY="y"
            v-model:modelR="r"
            @send="onSend"
            @clear="onClear"
            @logout="onLogout"
          />
        </div>
        <div class="card table-card">
          <ResultsTable :points="points" />
        </div>
      </div>
      <div class="card graph-container">
        <GraphCanvas
          :points="points"
          :r="r"
          :size="graphSize"
          :scale="scale"
          @point-click="onGraphClick"
        />
      </div>
    </div>

    <!-- Tablet (711..1217): слева 1/3 форма, справа 2/3 график, снизу таблица -->
    <div v-else-if="layoutMode === 'mode-tablet'" class="layout-tablet">
      <div class="card form-container">
        <PointForm
          v-model:modelX="x"
          v-model:modelY="y"
          v-model:modelR="r"
          @send="onSend"
          @clear="onClear"
          @logout="onLogout"
        />
      </div>
      <div class="card graph-container">
        <GraphCanvas
          :points="points"
          :r="r"
          :size="graphSize"
          :scale="scale"
          @point-click="onGraphClick"
        />
      </div>
      <div class="card table-card tablet-table">
        <ResultsTable :points="points" />
      </div>
    </div>

    <!-- Mobile (<711): всё вертикально -->
    <div v-else class="layout-mobile">
      <div class="card form-container">
        <PointForm
          v-model:modelX="x"
          v-model:modelY="y"
          v-model:modelR="r"
          @send="onSend"
          @clear="onClear"
          @logout="onLogout"
        />
      </div>
      <div class="card graph-container">
        <GraphCanvas
          :points="points"
          :r="r"
          :size="graphSize"
          :scale="scale"
          @point-click="onGraphClick"
        />
      </div>
      <div class="card table-card">
        <ResultsTable :points="points" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import GraphCanvas from '../components/GraphCanvas.vue';
import PointForm from '../components/PointForm.vue';
import ResultsTable from '../components/ResultsTable.vue';
import { addPoint, getPoints, clearPoints } from '../services/pointService';
import { logout, isLoggedIn } from '../services/authService';
import type { Point } from '../models/types';

const router = useRouter();

const x = ref<number | null>(null);
const y = ref<number>(0);
const r = ref<number | null>(null);
const points = ref<Point[]>([]);
const windowWidth = ref(window.innerWidth);

// Брейкпоинты по ТЗ: desktop >= 1218, tablet >= 711, mobile < 711
const layoutMode = computed(() => {
  if (windowWidth.value >= 1218) return 'mode-desktop';
  if (windowWidth.value >= 711)  return 'mode-tablet';
  return 'mode-mobile';
});

const graphSize = computed(() => {
  if (layoutMode.value === 'mode-desktop') {
    // Правая половина минус отступы
    return Math.min(Math.floor((windowWidth.value - 340) * 0.62) - 32, 620);
  }
  if (layoutMode.value === 'mode-tablet') {
    // 2/3 экрана минус отступы
    return Math.min(Math.floor(windowWidth.value * 2 / 3) - 48, 520);
  }
  // Mobile: полная ширина минус отступы
  return Math.min(windowWidth.value - 40, 420);
});

const scale = computed(() => Math.max(graphSize.value / 12, 18));

onMounted(async () => {
  if (!isLoggedIn()) { router.push('/login'); return; }

  const savedR = localStorage.getItem('last_radius');
  if (savedR !== null) {
    const val = parseFloat(savedR);
    if (!isNaN(val) && [1, 2, 3, 4].includes(val)) r.value = val;
  }

  await loadPoints();
  window.addEventListener('resize', onResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', onResize);
});

function onResize() { windowWidth.value = window.innerWidth; }

async function loadPoints() {
  try { points.value = await getPoints(); }
  catch (err) { console.error('Ошибка загрузки точек:', err); }
}

async function onSend() {
  if (x.value === null || r.value === null || isNaN(y.value)) return;
  try {
    const newPoint = await addPoint(x.value, y.value, r.value);
    points.value = [newPoint, ...points.value];
    localStorage.setItem('last_radius', String(r.value));
  } catch (err) { console.error('Ошибка отправки точки:', err); }
}

async function onGraphClick({ x: gx, y: gy }: { x: number; y: number }) {
  if (r.value === null || r.value <= 0) {
    alert('Выберите положительный радиус R (1..4)!'); return;
  }
  if (gx < -4 || gx > 4 || gy < -3 || gy > 5) {
    alert('Клик вне допустимого диапазона!\nX: [-4, 4], Y: [-3, 5]'); return;
  }
  try {
    const newPoint = await addPoint(gx, gy, r.value);
    points.value = [newPoint, ...points.value];
  } catch (err) { console.error('Ошибка при клике на граф:', err); }
}

async function onClear() {
  if (!confirm('Вы уверены, что хотите удалить все результаты?')) return;
  try { await clearPoints(); points.value = []; }
  catch (err) { console.error('Ошибка очистки:', err); }
}

async function onLogout() {
  await logout();
  router.push('/login');
}
</script>

