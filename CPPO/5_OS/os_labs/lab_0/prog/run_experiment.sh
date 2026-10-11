#!/usr/bin/env bash
set -euo pipefail
N=22
ITER_READ_CACHED=20
ITER_READ_NOCACHE=1
ITER_MMAP_CACHED=400
ITER_MMAP_NOCACHE=400
ITER_WRITE_CACHED=20
ITER_WRITE_NOCACHE=1
ITER_WRITE_MMAP_CACHED=400
ITER_WRITE_MMAP_NOCACHE=300

# Пути. Скрипт запускается из lab_0/prog/, поэтому:
BIN_DIR=../../intro-exp/out    # где лежат собранные бинарники
DATA_DIR=../data            # где лежат графы
OUT="$DATA_DIR/results_all.csv"
for f in "$DATA_DIR/graph-seq.bin" "$DATA_DIR/graph-rand.bin"; do
  [[ -f "$f" ]] || { echo "нет файла $f"; exit 1; }
done
for b in graph_traverse graph_traverse_mmap; do
  [[ -x "$BIN_DIR/$b" ]] || { echo "нет бинарника $BIN_DIR/$b"; exit 1; }
done

echo "run_id,load,app,mode,graph,iter,wall_s,user_s,sys_s,cpu_pct,minflt,majflt,vol_ctx,invol_ctx,maxrss_kb,fs_in_blocks,fs_out_blocks" > "$OUT"
drop_cache() {
  sync # заставляет ядро немедленно сбросить все грязные (изменённые) страницы из памяти на диск и дождаться завершения записи.
  echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
}
warm_cache() {
  cat "$1" > /dev/null
}

# Аргументы:
#   $1 app      — имя бинарника (graph_traverse / graph_traverse_mmap)
#   $2 load     — read / write
#   $3 mode     — cached / no-cache
#   $4 graph    — имя файла графа
#   $5 iter     — число итераций
#   $6 i        — номер прогона (run_id)
run_one() {
  local app="$1" load="$2" mode="$3" graph="$4" iter="$5" i="$6"
  local flags=()

  # Для read — без флага.
  if [[ "$load" == "write" ]]; then
    flags+=(--write)
  fi

  # Режим кэша: либо сбрасываем кэш (no-cache), либо прогреваем (cached).
  if [[ "$mode" == "no-cache" ]]; then
    drop_cache
    flags+=(--no-cache)
  else
    warm_cache "$DATA_DIR/$graph"
  fi

  local fmt="$i,$load,$app,$mode,$graph,$iter,%e,%U,%S,%P,%R,%F,%w,%c,%M,%I,%O"

  # -a — дописать в конец файла, -o — файл вывода.
  /usr/bin/time -f "$fmt" -a -o "$OUT" \
    "$BIN_DIR/$app" "${flags[@]}" "$iter" "$DATA_DIR/$graph" > /dev/null
}

# --- основной цикл: интерливинг ---
# В каждом прогоне выполняем все 16 конфигураций подряд.
# Так систематический дрейф (нагрев, фон) размазывается равномерно
# по всем сериям, а не копится в одной.
for i in $(seq 1 "$N"); do
  # --- read/lseek, read ---
  run_one graph_traverse      read  cached   graph-seq.bin  "$ITER_READ_CACHED"        "$i"
  run_one graph_traverse      read  cached   graph-rand.bin "$ITER_READ_CACHED"        "$i"
  run_one graph_traverse      read  no-cache graph-seq.bin  "$ITER_READ_NOCACHE"       "$i"
  run_one graph_traverse      read  no-cache graph-rand.bin "$ITER_READ_NOCACHE"       "$i"

  # --- mmap, read ---
  run_one graph_traverse_mmap read  cached   graph-seq.bin  "$ITER_MMAP_CACHED"        "$i"
  run_one graph_traverse_mmap read  cached   graph-rand.bin "$ITER_MMAP_CACHED"        "$i"
  run_one graph_traverse_mmap read  no-cache graph-seq.bin  "$ITER_MMAP_NOCACHE"       "$i"
  run_one graph_traverse_mmap read  no-cache graph-rand.bin "$ITER_MMAP_NOCACHE"       "$i"

  # --- read/lseek, write ---
  run_one graph_traverse      write cached   graph-seq.bin  "$ITER_WRITE_CACHED"       "$i"
  run_one graph_traverse      write cached   graph-rand.bin "$ITER_WRITE_CACHED"       "$i"
  run_one graph_traverse      write no-cache graph-seq.bin  "$ITER_WRITE_NOCACHE"      "$i"
  run_one graph_traverse      write no-cache graph-rand.bin "$ITER_WRITE_NOCACHE"      "$i"

  # --- mmap, write ---
  run_one graph_traverse_mmap write cached   graph-seq.bin  "$ITER_WRITE_MMAP_CACHED"  "$i"
  run_one graph_traverse_mmap write cached   graph-rand.bin "$ITER_WRITE_MMAP_CACHED"  "$i"
  run_one graph_traverse_mmap write no-cache graph-seq.bin  "$ITER_WRITE_MMAP_NOCACHE" "$i"
  run_one graph_traverse_mmap write no-cache graph-rand.bin "$ITER_WRITE_MMAP_NOCACHE" "$i"
done

echo "готово: $OUT"