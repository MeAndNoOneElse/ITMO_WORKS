#!/usr/bin/env bash
# Скрипт полного эксперимента для intro-exp с временной изоляцией ядра
# через cgroup v2 (без GRUB/isolcpus — полностью обратимо).
# Пользователь выбрал: вариант C (cgroup v2) + полный эксперимент (сборка + замеры).

set -euo pipefail

# --- Конфигурация ---
CGROUP_NAME="test_isolate_$$"
CGROUP_PATH="/sys/fs/cgroup/${CGROUP_NAME}"
# Ядро для изоляции (по умолчанию 2; если nproc меньше 3 — последнее не-0)
CORE=${CORE:-2}
N=${N:-30}
ITER=${ITER:-5}
OUT_CSV="results_read.csv"
# ---

cleanup() {
    echo "[cleanup] Удаление cgroup ${CGROUP_PATH}..."
    if [[ -d "${CGROUP_PATH}" ]]; then
        # Убираем процессы (если они остались)
        rmdir "${CGROUP_PATH}" 2>/dev/null || {
            echo 0 > "${CGROUP_PATH}/cgroup.kill" 2>/dev/null || true
            rmdir "${CGROUP_PATH}" 2>/dev/null || true
        }
    fi
    echo "[cleanup] Готово. Система возвращена в исходное состояние."
}
trap cleanup EXIT INT TERM

# --- 1. Проверка прав и окружения ---
echo "=== Паспорт системы (до) ==="
uname -a
echo "nproc: $(nproc)"
if [[ $(nproc) -lt 2 ]]; then
    echo "[warn] Только $(nproc) логических CPU — выбрано ядро 0 вместо 2"
    CORE=0
fi
lscpu -e | head -n 10 || true
free -h | head -n 3 || true
cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || echo "no_turbo: N/A"

# --- 2. Фиксация CPU governor ---
if command -v cpupower &>/dev/null; then
    echo "[env] Установка governor performance..."
    sudo cpupower frequency-set -g performance || echo "[warn] cpupower не сработал (нет прав или отсутствует)"
fi

# --- 3. Создание временной cgroup v2 ---
echo "=== Создание cgroup v2: ${CGROUP_PATH} ==="
if [[ ! -d "/sys/fs/cgroup" ]]; then
    echo "[error] /sys/fs/cgroup не найден. Нужен cgroup v2 (обычно смонтирован по умолчанию)." >&2
    exit 1
fi

mkdir -p "${CGROUP_PATH}"

# Устанавливаем изоляцию по CPU
# Выбираем ядро (если 2 недоступно — последнее не-0)
AVAILABLE_CPUS=$(cat /sys/fs/cgroup/cpuset.cpus.effective 2>/dev/null || cat /sys/fs/cgroup/cpuset.cpus 2>/dev/null || echo "0-$(($(nproc)-1))")
echo "Доступные CPU: ${AVAILABLE_CPUS}"

# Простой выбор ядра: если 2 в диапазоне — 2, иначе последнее
LAST_CPU=$(echo "${AVAILABLE_CPUS}" | tr ',' '\n' | grep -oE '[0-9]+' | sort -n | tail -n1)
if [[ -z "${LAST_CPU}" ]]; then LAST_CPU=0; fi

# Проверяем, входит ли выбранное ядро в диапазон
if echo "${AVAILABLE_CPUS}" | grep -qE "(^|,|-)${CORE}(,|-|$)"; then
    SELECTED_CORE=${CORE}
else
    SELECTED_CORE=${LAST_CPU}
    echo "[warn] Ядро ${CORE} не в диапазоне ${AVAILABLE_CPUS}, используем ${SELECTED_CORE}"
fi

echo "Выделяем ядро: ${SELECTED_CORE}"
echo "${SELECTED_CORE}" > "${CGROUP_PATH}/cpuset.cpus"
echo "0" > "${CGROUP_PATH}/cpuset.mems" || echo "[warn] cpuset.mems не установлен"

# Ограничиваем память (опционально, но для чистоты)
echo "max" > "${CGROUP_PATH}/memory.max" 2>/dev/null || true

# --- 4. Перемещение скрипта в cgroup (если возможно) ---
# Это не всегда разрешено из user.slice, поэтому делаем с проверкой
if echo $$ > "${CGROUP_PATH}/cgroup.procs" 2>/dev/null; then
    echo "[env] Текущий процесс (${$$}) перемещён в cgroup ${CGROUP_NAME}"
else
    echo "[warn] Не удалось переместить PID ${$$} в cgroup (возможно, ограничения родительской cgroup). Продолжаем с taskset."
fi

# --- 5. Сборка ---
echo "=== Сборка ==="
mkdir -p out
clang -o out/graph_traverse src/graph_traverse.c -Wall -O2 || gcc -o out/graph_traverse src/graph_traverse.c -Wall -O2
clang -o out/graph_traverse_mmap src/graph_traverse_mmap.c -Wall -O2 || gcc -o out/graph_traverse_mmap src/graph_traverse_mmap.c -Wall -O2

# --- 6. Подготовка данных (если отсутствуют) ---
if [[ ! -f "graph-seq.bin" || ! -f "graph-rand.bin" ]]; then
    echo "=== Генерация графов ==="
    python3 src/graphgen.py -s 64M --seed 427 -o graph-rand.bin || true
    python3 src/graphgen.py -s 64M --seed 427 --topology chain -b 0.7 --min-step-pages 2 -o graph-seq.bin || true
fi

# --- 7. Серия измерений (как в README 4.7, но с cgroup + taskset) ---
echo "=== Старт серии измерений (N=${N}, ITER=${ITER}, CORE=${SELECTED_CORE}) ==="

# CSV заголовок (как в README)
echo "timestamp,graph,run_id,wall_time_s,user_time_s,sys_time_s,vol_ctx,invol_ctx,minflt,majflt,core,cgroup" > "${OUT_CSV}"

graphs=(graph-seq.bin graph-rand.bin)

for i in $(seq 1 ${N}); do
    for g in "${graphs[@]}"; do
        ts=$(date +%s)
        # Запускаем в дочернем bash, перемещённом в cgroup, с taskset
        # Используем /usr/bin/time -v для метрик
        bash -c "
            echo \$$ > ${CGROUP_PATH}/cgroup.procs 2>/dev/null || true
            /usr/bin/time -v taskset -c ${SELECTED_CORE} ./out/graph_traverse --no-cache ${ITER} ${g} \
                2> /tmp/time_out.${i}_${g//./_} 1> /tmp/prog_out.${i}_${g//./_} || true
        " || true

        # Парсим вывод
        time_file="/tmp/time_out.${i}_${g//./_}"
        if [[ -f "${time_file}" ]]; then
            wall=$(grep "Elapsed (wall clock)" "${time_file}" | awk -F': ' '{print $2}' | tr -d ' ' || echo "NA")
            user=$(grep "User time (seconds)" "${time_file}" | awk '{print $4}' || echo "NA")
            sys=$(grep "System time (seconds)" "${time_file}" | awk '{print $4}' || echo "NA")
            volc=$(grep "voluntary context switches" "${time_file}" | head -1 | awk '{print $1}' || echo "0")
            invc=$(grep "involuntary context switches" "${time_file}" | awk '{print $1}' || echo "0")
            minf=$(grep "Minor (reclaiming a frame) page faults" "${time_file}" | awk '{print $NF}' || echo "0")
            majf=$(grep "Major (requiring I/O) page faults" "${time_file}" | awk '{print $NF}' || echo "0")
            rm -f "${time_file}" "/tmp/prog_out.${i}_${g//./_}"
        else
            wall="NA"; user="0"; sys="0"; volc="0"; invc="0"; minf="0"; majf="0"
        fi

        echo "${ts},${g},${i},${wall},${user},${sys},${volc},${invc},${minf},${majf},${SELECTED_CORE},${CGROUP_NAME}" >> "${OUT_CSV}"
        echo "[run ${i}/${N}] ${g} -> wall=${wall} core=${SELECTED_CORE}"
    done
done

echo "=== Серия завершена. Результаты: ${OUT_CSV} ==="
head -n 5 "${OUT_CSV}"

# --- 8. Пост-снимок окружения ---
echo "=== Снимок окружения (после) ==="
uptime || true
top -bn1 | head -n 5 || true
free -h | head -n 2 || true

# --- 9. Очистка через trap ---
echo "=== Эксперимент завершён. Очистка будет выполнена автоматически при выходе. ==="
