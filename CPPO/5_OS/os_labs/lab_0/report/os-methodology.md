# Методичка: термины ОС, команды и флаги (для intro-exp)

## Термины ОС

| Термин | Значение | Контекст в задании |
|---|---|---|
| **Page fault** (стр. ошибка) | Обращение к виртуальному адресу, для которого нет физической страницы. Бывает `minor` (реклейм, без I/O) и `major` (требует чтения с диска). | Ключевая метрика для `mmap()` vs `read()`; `minflt`/`majflt` в CSV. |
| **Context switch** (контекстный переключатель) | Смена процесса на CPU планировщиком. `voluntary` (процесс отдаёт CPU сам) и `involuntary` (вытесняется). | Растёт при конкуренции (стресс-тест); минимизируем через `taskset`. |
| **CPU migration** (миграция CPU) | Процесс переехал с одного логического ядра на другое. При `taskset -c` должно быть ~0. | Метрика из `perf stat -e cpu-migrations`. |
| **Spatial locality** (пространственная локальность) | Переходы по данным близки в памяти/файле → лучше кэш, меньше page faults. | `graph-seq` (цепочка) имеет высокую локальность; `graph-rand` — нет. |
| **DVFS / CPU governor** | Dynamic Voltage and Frequency Scaling. `performance` = фикс. макс. частота; `powersave`/`ondemand` — меняют частоту. | Фиксируем `performance` перед серией (`cpupower frequency-set -g performance`). |
| **File page cache** | Кэш ОС для страниц файлов в RAM. `--no-cache` в программе обходит его (`O_DIRECT` или `fadvise`). | Не смешиваем `--no-cache` с ручным `drop_caches` в одной серии. |
| **mmap()` | Отображение файла в адресное пространство процесса. Не использует `read()`/`lseek()`; страничные ошибки происходят при доступе. | Этап 2 (`graph_traverse_mmap`). Может использовать `madvise`. |
| **MADV_SEQUENTIAL / MADV_RANDOM** | Подсказки ядру через `madvise` об ожидаемом паттерне доступа. `SEQUENTIAL` включает readahead. | Проверить в `graph_traverse_mmap.c`: если используется — учесть в выводе. |
| **cgroup v2** | Механизм изоляции ресурсов без перезагрузки (`cpuset.cpus`, `memory.max`). `test_isolate_*` — временная группа. | `run_isolated.sh`: создаёт, запускает в ней, удаляет при выходе (`trap cleanup`). |
| **SMT / Hyper-Threading** | Логические ядра на одном физическом. `lscpu -e` показывает `CPU(s) -> Core(s) -> Socket`. | Для чистого эксперимента лучше выбрать физическое ядро или отключить SMT. |

---

## Команды и их флаги (по мониторингу и окружению)

### Паспорт системы
```bash
uname -a                    # ядро, архитектура
lscpu                       # общая инфо о CPU
lscpu -e                    # топология: logical CPU -> core -> socket
cat /proc/cpuinfo | grep -i cache  # L1d/L1i/L2/L3
free -h                     # RAM, swap, buffers/cache
cat /sys/block/sda/queue/rotational  # 0 = SSD/NVMe, 1 = HDD
smartctl -a /dev/sda         # состояние диска (нужен sudo)
nproc                        # число логических CPU
numactl --hardware           # NUMA-топология
```

### Окружение (изоляция)
```bash
taskset -c 2 ./program ...   # привязать процесс к ядру 2
taskset -cp 2 <pid>          # привязать уже запущенный процесс
cpupower frequency-set -g performance  # фиксировать частоту
cat /sys/devices/system/cpu/intel_pstate/no_turbo  # 0 = turbo включён
renice -n -5 -p <pid>        # повысить приоритет (нужен root для отрицательных)
nice -n -5 ./program ...    # запустить с повышенным приоритетом
```

### Мониторинг (характеризация — допустимо «тяжёлое»)
```bash
# Точное время + метрики процесса
/usr/bin/time -v ./program ...     # Elapsed (wall clock), User time, System time,
                                   # Voluntary/Involuntary context switches,
                                   # Minor/Major page faults, Maximum RSS

# Аппаратные и программные счётчики (добавляет накладные расходы)
perf stat -e task-clock,context-switches,cpu-migrations,page-faults,\
cache-references,cache-misses,cycles,instructions \
  taskset -c 2 ./program ...

# Общесистемные наблюдатели (в другом терминале, параллельно)
vmstat 1          # память, CPU %, swap, блочный IO (bi/bo)
mpstat -P ALL 1   # загрузка каждого CPU отдельно
pidstat -urd 1    # по PID: %CPU, память, диск
pidstat -u -p $(pgrep program) 1
iostat -x 1        # %util диска, await (задержка в мс), r/s, rkB/s
```

### Фоновая нагрузка (демонстрация шума)
```bash
stress-ng --cpu 2 --io 1 --vm 1 --vm-bytes 256M --timeout 30s
# --cpu N: N воркеров CPU
# --io N: N воркеров sync()
# --vm N --vm-bytes SIZE: нагрузка на память
```

### Управление кэшем (для экспериментов с памятью/диском)
```bash
# Холодный кэш (ручной, требует root, не смешивать с --no-cache в одной серии)
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches
# 1 = только pagecache, 2 = dentries/inodes, 3 = всё
```

### Генерация данных (графы)
```bash
python3 intro-exp/src/graphgen.py -s 64M --seed 427 -o graph-rand.bin
python3 intro-exp/src/graphgen.py -s 64M --seed 427 --topology chain -b 0.7 \
  --min-step-pages 2 -o graph-seq.bin
# -s: размер файла (приблизительно)
# --seed: сид псевдослучайного генератора (воспроизводимость)
# --topology: chain или default (random)
# -b/--branching: доля переходов по цепочке для chain
# --min-step-pages: минимальный шаг в страницах памяти (избегает вырождения в одну страницу)
```

### Сбор данных (скрипт изоляции)
```bash
# Пример вызова
chmod +x run_isolated.sh
CORE=2 N=30 ITER=5 ./run_isolated.sh
# Переменные скрипта:
# CORE — ядро для taskset
# N — число повторов
# ITER — число итераций обхода на запуск
# Вывод: results_read.csv (или аналогичный для mmap)
```

---

## Флаги программ из задания

### `graph_traverse` / `graph_traverse_mmap` (CLI)
```bash
<traverser> [--write] [--no-cache] <iterations> <file1> [file2 ...]
```
- `<iterations>`: число полных обходов графа.
- `--write`: режим записи (модифицирует узлы; ожидается больше `sys time`).
- `--no-cache`: отключает файловый кэш (кроссплатформенно; предпочтительнее `drop_caches`).

### `graph_traverse_mmap.c` (проверка `madvise`)
```bash
grep -n "madvise\|MADV" intro-exp/src/graph_traverse_mmap.c
```
- Если используется `MADV_SEQUENTIAL` — ядро включает `readahead`; если `MADV_RANDOM` — отключает. Учитывать в выводе.

---

## Связь метрик и инструментов (таблица из `monitoring.md`)

| Метрика | Основной источник | Альтернатива / Уточнение |
|---|---|---|
| Wall time | `/usr/bin/time -v` (`Elapsed (wall clock)`) | `perf stat` (`task-clock`) |
| User time | `/usr/bin/time -v` (`User time`) | `perf stat -e task-clock` |
| System time | `/usr/bin/time -v` (`System time`) | `/proc/[pid]/stat` |
| %CPU (в моменте) | `pidstat -u 1`, `top` | `mpstat -P ALL 1` |
| Context switches | `/usr/bin/time -v` (`voluntary`/`involuntary`) | `perf stat -e context-switches` |
| CPU migrations | — | `perf stat -e cpu-migrations` |
| Page faults (min/maj) | `/usr/bin/time -v` (`Minor`/`Major`) | `perf stat -e page-faults`, `/proc/[pid]/stat` (`minflt`/`majflt`) |
| RAM / RSS | `/usr/bin/time -v` (`Maximum RSS`) | `/proc/[pid]/status` (`VmRSS`) |
| Диск / задержка | `iostat -x 1` (`%util`, `await`) | `pidstat -d 1` |
| CPU cache misses | — | `perf stat -e cache-misses,cache-references` |
| TLB misses | — | `perf stat -e dTLB-load-misses,dTLB-store-misses` |
| Page cache state | `free -h` (`Cached`, `Buffers`) | `/proc/meminfo` |

---

## Примечания для защиты

- При объяснении `taskset`: показать `mpstat -P ALL 1` до/после, убедиться, что миграции (`cpu-migrations`) ~0.
- При объяснении `cgroup v2`: показать `ls /sys/fs/cgroup/test_isolate_*`, объяснить `cpuset.cpus`, `memory.max`, `trap cleanup`.
- При объяснении `--no-cache`: показать исходный код или `--help` конкретной сборки; объяснить, что это предпочтительнее ручного `drop_caches` (переносимость Linux/macOS, не требует root).
- При объяснении `N`: использовать формулу `std / sqrt(N)`; показать, что при `N=30` ДИ уже узкий, и прирост от `N=60` незначителен.
- При объяснении `read` vs `mmap`: сравнить `context-switches` и `minflt`/`majflt` из CSV или из `perf stat` на характерном запуске; объяснить разницу через `man 2 read`, `man 2 mmap`, `man 2 madvise`.
