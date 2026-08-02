<template>
  <div class="form-inner">

    <!-- X: checkbox -4..4 -->
    <div class="input-block">
      <label class="input-label">Координата X:</label>
      <div class="checkbox-group">
        <label v-for="opt in xOptions" :key="opt" class="checkbox-label" :class="{ active: localX === opt }">
          <input type="checkbox" :checked="localX === opt" @change="onXChange(opt)" />
          <span>{{ opt }}</span>
        </label>
      </div>
      <span v-if="xError" class="error-text">{{ xError }}</span>
    </div>

    <!-- Y: slider -3..5 -->
    <div class="input-block">
      <label class="input-label">
        Координата Y: <span class="hint">{{ localY }}</span>
        <span class="hint"> (от -3 до 5)</span>
      </label>
      <input
        type="range"
        min="-3"
        max="5"
        step="0.5"
        v-model.number="localY"
        class="slider"
      />
      <div class="slider-ticks">
        <span>-3</span>
        <span>-1</span>
        <span>1</span>
        <span>3</span>
        <span>5</span>
      </div>
      <span v-if="yError" class="error-text">{{ yError }}</span>
    </div>

    <!-- R: checkbox -4..4 -->
    <div class="input-block">
      <label class="input-label">Радиус R:</label>
      <div class="checkbox-group">
        <label v-for="opt in rOptions" :key="opt" class="checkbox-label" :class="{ active: localR === opt }">
          <input type="checkbox" :checked="localR === opt" @change="onRChange(opt)" />
          <span>{{ opt }}</span>
        </label>
      </div>
      <span v-if="rError" class="error-text">{{ rError }}</span>
    </div>

    <div class="btns">
      <button class="btn-check" @click="onSend">Проверить</button>
      <button class="btn-clear" @click="$emit('clear')">Очистить результаты</button>
      <button class="btn-exit" @click="$emit('logout')">Выйти</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  modelX: number | null;
  modelY: number;
  modelR: number | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelX', val: number | null): void;
  (e: 'update:modelY', val: number): void;
  (e: 'update:modelR', val: number | null): void;
  (e: 'send'): void;
  (e: 'clear'): void;
  (e: 'logout'): void;
}>();

const xOptions = [-4, -3, -2, -1, 0, 1, 2, 3, 4];
const rOptions = [-4, -3, -2, -1, 0, 1, 2, 3, 4];

const localX = ref<number | null>(props.modelX);
const localY = ref<number>(props.modelY ?? 0);
const localR = ref<number | null>(props.modelR);

const xError = ref('');
const yError = ref('');
const rError = ref('');

watch(() => props.modelX, (v) => { localX.value = v; });
watch(() => props.modelY, (v) => { localY.value = v; });
watch(() => props.modelR, (v) => { localR.value = v; });

watch(localX, (v) => { emit('update:modelX', v); xError.value = ''; });
watch(localY, (v) => { emit('update:modelY', v); yError.value = ''; });
watch(localR, (v) => { emit('update:modelR', v); rError.value = ''; });

// Checkbox ведёт себя как radio: повторный клик снимает выбор
function onXChange(opt: number) {
  localX.value = localX.value === opt ? null : opt;
}
function onRChange(opt: number) {
  localR.value = localR.value === opt ? null : opt;
  // Отрицательный и нулевой радиус недопустимы
  if (localR.value !== null && localR.value <= 0) {
    rError.value = 'Радиус должен быть положительным (1..4)';
  } else {
    rError.value = '';
  }
}

function onSend() {
  let valid = true;
  xError.value = '';
  yError.value = '';
  rError.value = '';

  if (localX.value === null) {
    xError.value = 'Выберите координату X';
    valid = false;
  }

  const yNum = localY.value;
  if (isNaN(yNum) || yNum < -3 || yNum > 5) {
    yError.value = 'Y должен быть от -3 до 5';
    valid = false;
  }

  if (localR.value === null) {
    rError.value = 'Выберите радиус R';
    valid = false;
  } else if (localR.value <= 0) {
    rError.value = 'Радиус должен быть положительным (1..4)';
    valid = false;
  }

  if (valid) emit('send');
}
</script>

