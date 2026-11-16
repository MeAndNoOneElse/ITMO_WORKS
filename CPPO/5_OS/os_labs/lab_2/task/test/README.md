# Тестовые данные для VTSH

## Как собрать бинарник

```bash
cd /home/eter-core/ITMO_WORKS/CPPO/5_OS/os_labs/lab_2/task
mkdir -p build/bin
gcc -std=gnu11 -Wall -Wextra -O2 vtsh_v2.c -o build/bin/vtsh
```

Бинарник будет лежать в `build/bin/vtsh` — тесты ищут его именно там.

## Как просто запустить vtsh



```bash
./build/bin/vtsh
```

### Через stdin (одна команда)

```bash
echo "/bin/echo hello world" | ./build/bin/vtsh
```

### Через stdin (несколько команд)

```bash
echo -e "/bin/echo first\n/bin/echo second\nexit" | ./build/bin/vtsh
```

### С конвейером

```bash
echo "/bin/echo hello world | /bin/cat" | ./build/bin/vtsh
echo "cat test/search.txt | grep -i search" | ./build/bin/vtsh
```

## Как запустить тесты

Автоматические тесты:

```bash
# Запустить новые тесты (базовые + конвейеры + фон)
python3 -m unittest test_vtsh_more.py -v

# Запустить оригинальные базовые тесты
python3 -m unittest test_vtsh.BasicTests test_vtsh.BackgroundTests test_vtsh.FsizeTests -v
```

## Что можно проверить вручную

### 1. Код возврата 126 (не исполняемый файл)

```bash
# Пытаемся запустить .py файл без прав +x — получим 126
echo "./test/no_exec.py" | ./build/bin/vtsh; echo "код: $?"

# А через python3 — должно работать
echo "python3 test/no_exec.py" | ./build/bin/vtsh; echo "код: $?"
```

**Ожидание:**
-Первый вызов — stderr содержит `Permission denied`, код возврата оболочки `126`
- Второй вызов — stdout содержит `Hello from Python script!`, код `0`

### 2. Конвейер `|` с поиском в файле

```bash
# Ищем строки со словом "search" (без учёта регистра)
echo "cat test/search.txt | grep -i search" | ./build/bin/vtsh

# Ищем строки со словом "apple"
echo "cat test/search.txt | grep apple" | ./build/bin/vtsh

# Считаем сколько строк содержат "search"
echo "cat test/search.txt | grep -i search | wc -l" | ./build/bin/vtsh
```

**Ожидание:**
- Вывод stdout содержит строки из `search.txt` с искомым словом
- `wc -l` выводит число найденных строк
- stderr содержит время выполнения: `vtsh: [pipeline] 0.XXXXXX s`

### 3. Фоновый режим `&`

```bash
# Фоновая задача не блокирует оболочку
echo -e "sleep 0.3 &\n/bin/echo done" | ./build/bin/vtsh
```

**Ожидание:** stdout содержит `done`, stderr содержит `[1] <pid>` и затем `[1] Done (exit 0) sleep 0.3 &`

### 4. Измерение времени

```bash
# Время одной команды
echo "/bin/echo hello" | ./build/bin/vtsh

# Время конвейера
echo "cat test/search.txt | grep -i search | wc -l" | ./build/bin/vtsh
```

**Ожидание:** stderr содержит `vtsh: [/bin/echo] 0.XXXXXX s` или `vtsh: [pipeline] 0.XXXXXX s`

### 5. Коды возврата

```bash
# Программа не найдена — код 127
echo "/bin/nonexistent" | ./build/bin/vtsh; echo "код: $?"

# Успешная команда — код 0
echo "/bin/echo ok" | ./build/bin/vtsh; echo "код: $?"

# exit с кодом
echo "exit 7" | ./build/bin/vtsh; echo "код: $?"
```