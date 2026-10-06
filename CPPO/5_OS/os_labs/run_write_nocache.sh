#!/bin/bash
# Полная серия с --write --no-cache (без cgroup из-за systemd, с taskset)
for i in $(seq 1 ${N:-30}); do
  for g in intro-exp/graph-seq.bin intro-exp/graph-rand.bin; do
    /usr/bin/time -v taskset -c ${CORE:-2} ./out/graph_traverse --write --no-cache ${ITER:-5} $g 2>> /tmp/time_write_nocache.$i 1>> /dev/null || echo "FAIL $i $g"
    echo "run $i $(basename $g) write+nocache OK"
  done
done
echo "=== Серия завершена, файлы: /tmp/time_write_nocache.* ==="
