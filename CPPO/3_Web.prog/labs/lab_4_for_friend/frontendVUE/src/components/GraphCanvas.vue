<template>
  <svg
    :width="size"
    :height="size"
    style="background: #fff; border: 1px solid #ccc; cursor: crosshair; display: block;"
    @click="handleClick"
  >
    <rect :width="size" :height="size" fill="white" />

    <!-- Зоны попадания (только если R > 0) -->
    <template v-if="numR > 0">
      <!-- I квадрант: пусто — не рисуем -->

      <!-- II квадрант (x<=0, y>=0): прямоугольник шириной R, высотой R/2 -->
      <!-- x: от -R до 0, y: от 0 до R/2 -->
      <rect
        :x="center - numR * scale"
        :y="center - (numR / 2) * scale"
        :width="numR * scale"
        :height="(numR / 2) * scale"
        fill="#BAFFC9"
        fill-opacity="0.6"
      />

      <!-- III квадрант (x<=0, y<=0): треугольник y >= -x - R/2 -->
      <!-- Вершины: (0,0), (-R/2, 0), (0, -R/2) -->
      <polygon
        :points="`
          ${center},${center}
          ${center - (numR / 2) * scale},${center}
          ${center},${center + (numR / 2) * scale}
        `"
        fill="#FFB3BA"
        fill-opacity="0.6"
      />

      <!-- IV квадрант (x>=0, y<=0): четверть круга радиуса R -->
      <path
        :d="`M ${center},${center}
             L ${center + numR * scale},${center}
             A ${numR * scale},${numR * scale} 0 0 1 ${center},${center + numR * scale}
             Z`"
        fill="#BAE1FF"
        fill-opacity="0.6"
      />
    </template>

    <!-- Оси -->
    <line :x1="size * 0.05" :y1="center" :x2="size * 0.95" :y2="center" stroke="black" stroke-width="1.5" />
    <line :x1="center" :y1="size * 0.05" :x2="center" :y2="size * 0.95" stroke="black" stroke-width="1.5" />

    <!-- Стрелки осей -->
    <polygon :points="`${size*0.95},${center} ${size*0.95-8},${center-4} ${size*0.95-8},${center+4}`" fill="black"/>
    <polygon :points="`${center},${size*0.05} ${center-4},${size*0.05+8} ${center+4},${size*0.05+8}`" fill="black"/>

    <!-- Подписи осей -->
    <text :x="size * 0.9" :y="center - 10" font-size="14" font-weight="bold">X</text>
    <text :x="center + 10" :y="size * 0.08" font-size="14" font-weight="bold">Y</text>

    <!-- Засечки X: -4..4 -->
    <template v-for="val in xTickValues" :key="'tx' + val">
      <line
        :x1="center + val * scale" :y1="center - 5"
        :x2="center + val * scale" :y2="center + 5"
        stroke="black" stroke-width="1"
      />
      <text
        :x="center + val * scale - (String(val).length > 1 ? 8 : 4)"
        :y="center + 20"
        font-size="11"
      >{{ val }}</text>
    </template>
    <text :x="center - 5" :y="center + 20" font-size="11">0</text>

    <!-- Засечки Y: -3..5 -->
    <template v-for="val in yTickValues" :key="'ty' + val">
      <line
        :x1="center - 5" :y1="center - val * scale"
        :x2="center + 5" :y2="center - val * scale"
        stroke="black" stroke-width="1"
      />
      <text
        :x="center - (val < -0.5 ? 25 : 18)"
        :y="center - val * scale + 5"
        font-size="11"
      >{{ val }}</text>
    </template>

    <!-- Точки — цвет пересчитывается при каждом изменении r -->
    <circle
      v-for="p in points"
      :key="p.id"
      :cx="center + p.x * scale"
      :cy="center - p.y * scale"
      r="5"
      :fill="numR <= 0 ? '#FF1744' : (isHitLocal(p.x, p.y, numR) ? '#00C853' : '#FF1744')"
      stroke="white"
      stroke-width="1.5"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Point } from '../models/types';

const props = defineProps<{
  points: Point[];
  r: number | null;
  size: number;
  scale: number;
}>();

const emit = defineEmits<{
  (e: 'point-click', coords: { x: number; y: number }): void;
}>();

const center = computed(() => props.size / 2);
const numR = computed(() => (props.r !== null && props.r > 0) ? props.r : 0);

// X: [-4, 4], Y: [-3, 5] — без нуля (нуль рисуется отдельно)
const xTickValues = [-4, -3, -2, -1, 1, 2, 3, 4];
const yTickValues = [-3, -2, -1, 1, 2, 3, 4, 5];

/**
 * Клиентский пересчёт попадания по текущему R.
 * Зеркалит логику HitChecker.java:
 *  I  (x>=0, y>=0) — пусто
 *  II (x<=0, y>=0) — y <= r/2 && x >= -r
 *  III(x<=0, y<=0) — y >= -x - r/2
 *  IV (x>=0, y<=0) — x²+y² <= r²
 */
function isHitLocal(x: number, y: number, r: number): boolean {
  if (r <= 0) return false;
  if (x >= 0 && y >= 0) return false;                        // I — пусто
  if (x <= 0 && y >= 0) return y <= r / 2 && x >= -r;       // II — прямоугольник
  if (x <= 0 && y <= 0) return y >= -x - r / 2;             // III — треугольник
  return x * x + y * y <= r * r;                             // IV — четверть круга
}

function handleClick(event: MouseEvent) {
  const svg = event.currentTarget as SVGSVGElement;
  const rect = svg.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const mathX = (mouseX - center.value) / props.scale;
  const mathY = (center.value - mouseY) / props.scale;

  emit('point-click', {
    x: Math.round(mathX * 10) / 10,
    y: Math.round(mathY * 10) / 10
  });
}
</script>

