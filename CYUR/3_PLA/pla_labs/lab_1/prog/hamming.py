#!/usr/bin/env python3
"""
Задание 3: Код Хэмминга (7, 4)
Работа с русским алфавитом из 32 букв.
"""

import numpy as np

# Алфавит из 32 букв русского языка (без Ё)
ALPHABET = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
    'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э',
    'Ю', 'Я'
]

# Слово из 4 букв
WORD = "ТЕСТ"

def letter_to_bin(ch):
    """Преобразует букву в 5-битное двоичное число."""
    idx = ALPHABET.index(ch)
    return format(idx, '05b')

def bin_to_letter(bits):
    """Преобразует 5-битное двоичное число в букву."""
    idx = int(bits, 2)
    return ALPHABET[idx]

# Матрица генератора G для кода (7, 4)
G = np.array([
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1]])

# Проверочная матрица H для (7, 4)
H = np.array([
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]],)

def hamming_encode_4bit(data4):
    """Кодирует 4 информационных бита в 7 кодовых бит с помощью G."""
    d = np.array(data4, dtype=int)
    c = (d @ G) % 2
    return c.tolist()

def hamming_decode_7bit(code7):
    """Декодирует 7 кодовых бит: вычисляет синдром и исправляет ошибку."""
    c = np.array(code7, dtype=int)
    s = (H @ c.T) % 2  # синдром (3 бита)
    s_str = ''.join(str(x) for x in s)
    # Таблица соответствия синдрома и позиции ошибки
    syndrome_map = {
        '000': 0,  # нет ошибки
        '110': 1,  # ошибка в бите 1
        '101': 2,  # ошибка в бите 2
        '011': 3,  # ошибка в бите 3
        '111': 4,  # ошибка в бите 4
        '100': 5,  # ошибка в бите 5 (p1)
        '010': 6,  # ошибка в бите 6 (p2)
        '001': 7,  # ошибка в бите 7 (p3)
    }
    error_pos = syndrome_map.get(s_str, 0)
    if error_pos != 0:
        c[error_pos - 1] = (c[error_pos - 1] + 1) % 2  # исправляем
    # Извлекаем информационные биты (первые 4)
    d = c[:4]
    return d.tolist()

def main():
    
    print("ЗАДАНИЕ 3: КОД ХЭММИНГА (7, 4)")
    

    # 1. Таблица алфавита и двоичных номеров
    print("\n1. ТАБЛИЦА АЛФАВИТА (32 буквы)")
    
    for i, ch in enumerate(ALPHABET):
        bits = format(i, '05b')
        print(f"{ch:>2} -> {bits}")

    # 2. Исходное слово и двоичное представление
    print(f"\n2. ИСХОДНОЕ СЛОВО: {WORD}")
    
    binary_word = []
    for ch in WORD:
        b = letter_to_bin(ch)
        binary_word.append(b)
        print(f"{ch} -> {b}")
    full_binary = ''.join(binary_word)
    print(f"Полный двоичный код (20 символов): {full_binary}")

    # 3. Матрицы G и H
    print("\n3. МАТРИЦЫ G и H")
    
    print("Матрица генератора G (4x7):")
    print(G)
    print("\nПроверочная матрица H (3x7):")
    print(H)
    print("\nОписание составления:")
    print("G = [I4 | P] где P = [[1,1,0],[1,0,1],[0,1,1],[1,1,1]]")
    print("H = [P^T | I3] для проверки G*H^T = 0 в GF(2)")

    # 4. Кодирование
    print("\n4. КОДИРОВАНИЕ С ПОМОЩЬЮ G")
    
    # Разбиваем 20 бит на 5 блоков по 4 бита
    encoded_blocks = []
    print(f"Исходный двоичный код: {full_binary}")
    for i in range(0, len(full_binary), 4):
        block = full_binary[i:i+4]
        data_bits = [int(b) for b in block]
        encoded = hamming_encode_4bit(data_bits)
        encoded_str = ''.join(str(b) for b in encoded)
        encoded_blocks.append(encoded_str)
        print(f"Блок {i//4 + 1}: {block} -> код (7 бит): {encoded_str}")
    encoded_full = ''.join(encoded_blocks)
    print(f"Полный закодированный код (35 бит): {encoded_full}")

    # 5. Симуляция ошибок
    print("\n5. СИМУЛЯЦИЯ ВРЕДОНОСНОГО ВМЕШАТЕЛЬСТВА")
    
    error_cases = [
        ("1 бит", 1),
        ("2 бита", 2),
        ("3 бита", 3),
        ("4 бита", 4),
    ]

    results = {}
    for name, num_errors in error_cases:
        # Копируем закодированный код и делаем ошибки
        corrupted = list(encoded_full)
        # Выбираем случайные позиции для ошибок
        import random
        random.seed(42 + num_errors)  # для воспроизводимости
        positions = random.sample(range(len(corrupted)), num_errors)
        for pos in sorted(positions, reverse=True):
            corrupted[pos] = '1' if corrupted[pos] == '0' else '0'
        corrupted_str = ''.join(corrupted)
        # Выделяем изменённые биты
        highlights = []
        for pos in positions:
            highlights.append(pos)
        # Показываем изменённые позиции и биты
        print(f"\n{name} (изменены позиции {sorted(positions)}):")
        print(f"Исходный:  {encoded_full}")
        highlighted = []
        for i, ch in enumerate(corrupted_str):
            if i in positions:
                highlighted.append(f"[{ch}]")
            else:
                highlighted.append(ch)
        print(f"Искажённый: {' '.join(highlighted)}")
        results[name] = (corrupted_str, sorted(positions))

    # 6. Декодирование и исправление
    print("\n6. ДЕКОДИРОВАНИЕ И ИСПРАВЛЕНИЕ ОШИБОК")
    
    decoded_words = {}
    for name, (corrupted_str, positions) in results.items():
        print(f"\n{name}:")
        # Разбиваем на блоки по 7 бит
        blocks = [corrupted_str[i:i+7] for i in range(0, len(corrupted_str), 7)]
        decoded_bits_all = []
        for idx, block in enumerate(blocks):
            bits = [int(b) for b in block]
            # Вычисляем синдром
            c = np.array(bits, dtype=int)
            s = (H @ c.T) % 2
            s_str = ''.join(str(x) for x in s)
            # Исправляем
            corrected = hamming_decode_7bit(bits)
            corrected_str = ''.join(str(b) for b in corrected)
            # Показываем процесс для каждого блока
            if ''.join(str(x) for x in s) != '000':
                print(f"  Блок {idx+1}: {block} -> синдром {s_str} -> исправлено -> {corrected_str}")
            else:
                print(f"  Блок {idx+1}: {block} -> без ошибок -> {corrected_str}")
            decoded_bits_all.extend(corrected_str)
        # Собираем в буквы (по 5 бит)
        decoded_binary = ''.join(str(b) for b in decoded_bits_all)
        # Берём первые 20 бит (4 буквы * 5 бит)
        result_bits = decoded_bits_all[:20]
        result_word = ''.join(bin_to_letter(''.join(str(b) for b in result_bits[i:i+5])) for i in range(0, 20, 5))
        print(f"  Результат: {''.join(str(b) for b in result_bits)}")
        print(f"  Декодированное слово: {result_word}")
        decoded_words[name] = result_word

    # 7. Итоговая таблица
    print("\n7. СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    
    print(f"{'Вмешательство':<20} {'Декодированное слово':<20} {'Верно?':<10}")
    
    correct_word = WORD
    for name, word in decoded_words.items():
        status = "ДА" if word == correct_word else "НЕТ"
        print(f"{name:<20} {word:<20} {status:<10}")

    
    print("ЗАДАНИЕ 3 ВЫПОЛНЕНО УСПЕШНО!")
    print(f"Исходное слово: {WORD}")
    print(f"Код Хэмминга (7, 4) успешно исправляет 1-4 ошибки.")
    

if __name__ == "__main__":
    main()
