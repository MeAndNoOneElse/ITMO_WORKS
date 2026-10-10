#!/usr/bin/env bash
set -euo pipefail

# --- параметры ---
N=30
ITER_READ_CACHED=10
ITER_READ_NOCACHE=1
ITER_MMAP_CACHED=200
ITER_MMAP_NOCACHE=200

OUT=results_all.csv

# --- проверка файлов ---
for f in graph-seq.bin graph-rand.bin; do
  [[ -f "$f" ]] || { echo "нет файла $f"; exit 1; }
done

# --- заголовок ---
echo "run_id,app,mode,graph,iter,wall_s,user_s,sys_s,cpu_pct,minflt,majflt,vol_ctx,invol_ctx,maxrss_kb,fs_in_blocks,fs_out_blocks" > "$OUT"

drop_cache() {
  sync
  echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
}

warm_cache() {
  cat "$1" > /dev/null
}

run_one() {
  local app="$1" mode="$2" graph="$3" iter="$4" i="$5"

  if [[ "$mode" == "no-cache" ]]; then
    drop_cache
    flags=(--no-cache)
  else
    warm_cache "$graph"
    flags=()
  fi

  # Формат /usr/bin/time: все поля через запятую
  local fmt="$i,$app,$mode,$graph,$iter,%e,%U,%S,%P,%R,%F,%w,%c,%M,%I,%O"

  /usr/bin/time -f "$fmt" -a -o "$OUT" \
    "./out/$app" "${flags[@]}" "$iter" "$graph" > /dev/null
}

# --- интерливинг по всем 8 конфигурациям ---
for i in $(seq 1 "$N"); do
  run_one graph_traverse      cached   graph-seq.bin  "$ITER_READ_CACHED"   "$i"
  run_one graph_traverse      cached   graph-rand.bin "$ITER_READ_CACHED"   "$i"
  run_one graph_traverse      no-cache graph-seq.bin  "$ITER_READ_NOCACHE"  "$i"
  run_one graph_traverse      no-cache graph-rand.bin "$ITER_READ_NOCACHE"  "$i"

  run_one graph_traverse_mmap cached   graph-seq.bin  "$ITER_MMAP_CACHED"   "$i"
  run_one graph_traverse_mmap cached   graph-rand.bin "$ITER_MMAP_CACHED"   "$i"
  run_one graph_traverse_mmap no-cache graph-seq.bin  "$ITER_MMAP_NOCACHE"  "$i"
  run_one graph_traverse_mmap no-cache graph-rand.bin "$ITER_MMAP_NOCACHE"  "$i"
done

echo "готово: $OUT"