<template>
  <div class="table-wrapper">
    <div v-if="points.length === 0" class="no-data">Нет результатов</div>
    <div v-else class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>X</th>
            <th>Y</th>
            <th>R</th>
            <th>Результат</th>
            <th>Время выполнения</th>
            <th>Время создания</th>
          </tr>
        </thead>
        <tbody>
          <!-- Итерируем по formattedPoints — computed зависит от now,
               поэтому при смене таймзоны/перезагрузке все строки пересчитаются -->
          <tr v-for="fp in formattedPoints" :key="fp.id">
            <td>{{ fp.x }}</td>
            <td>{{ fp.y }}</td>
            <td>{{ fp.r }}</td>
            <td :class="fp.hit ? 'hit-yes' : 'hit-no'">{{ fp.hit ? '✓ Попал' : '✗ Мимо' }}</td>
            <td>{{ fp.executionTime }} мкс</td>
            <td>{{ fp.createdAtFormatted }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import type { Point } from '../models/types';

const props = defineProps<{ points: Point[] }>();

/**
 * now обновляется при монтировании и раз в 60с.
 * formattedPoints — computed, который читает now.value,
 * поэтому Vue автоматически пересчитает все строки таблицы
 * при перезагрузке страницы или смене системной таймзоны.
 */
const now = ref(Date.now());
let timer: ReturnType<typeof setInterval>;

onMounted(() => {
  now.value = Date.now();
  timer = setInterval(() => { now.value = Date.now(); }, 60_000);
});

onUnmounted(() => { clearInterval(timer); });

/**
 * Computed массив: читает now.value → Vue отслеживает зависимость →
 * при изменении now пересчитывает все строки (в т.ч. старые точки).
 *
 * Логика времени:
 *   сервер хранит UTC epoch millis (абсолютное время)
 *   new Date(epochMillis).toLocaleString() применяет смещение
 *   ТЕКУЩЕЙ таймзоны браузера — корректно при любом часовом поясе.
 */
const formattedPoints = computed(() => {
  return props.points.map(p => ({
    ...p,
    createdAtFormatted: formatEpoch(p.createdAt, now.value),
  }));
});

function formatEpoch(epochMillis: number, _tick: number): string {
  if (!epochMillis) return '—';
  try {
    return new Date(epochMillis).toLocaleString('ru-RU', {
      year:   'numeric',
      month:  '2-digit',
      day:    '2-digit',
      hour:   '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return String(epochMillis);
  }
}
</script>
