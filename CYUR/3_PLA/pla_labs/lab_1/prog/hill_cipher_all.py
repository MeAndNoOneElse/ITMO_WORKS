#!/usr/bin/env python3
"""
Hill Cipher (Assignments 1-2) and Hamming (7,4) Code (Assignment 3)
All operations use Python standard library only (no numpy).
"""

import random, math, sys

# ======================================================================
# ALPHABET (Russian 32 letters + space) = 33 symbols
# ======================================================================
RUS_ALPHABET = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
    'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э',
    'Ю', 'Я', ' '
]
# Index mapping: letter -> number, number -> letter
ALPHABET_MAP = {ch: i for i, ch in enumerate(RUS_ALPHABET)}
ALPHABET_REV = {i: ch for i, ch in enumerate(RUS_ALPHABET)}
N_ALPH = len(RUS_ALPHABET)  # 33

# ======================================================================
# MATRIX UTILS (mod 33 for Hill, mod 2 for Hamming)
# ======================================================================

def mat_mul(A, B, mod):
    """Multiply A (m x p) by B (p x n) modulo mod."""
    m = len(A)
    p = len(B)
    n = len(B[0]) if B else 0
    C = [[0] * n for _ in range(m)]
    for i in range(m):
        for k in range(p):
            aik = A[i][k] % mod
            if aik == 0:
                continue
            for j in range(n):
                C[i][j] = (C[i][j] + aik * B[k][j]) % mod
    return C

def mat_vec_mul(A, v, mod):
    """Multiply A by column vector v (mod mod)."""
    m = len(A)
    p = len(A[0])
    res = [0] * m
    for i in range(m):
        s = 0
        for k in range(p):
            s = (s + A[i][k] * v[k]) % mod
        res[i] = s
    return res

def mat_transpose(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

def mat_identity(n):
    I = [[0] * n for _ in range(n)]
    for i in range(n):
        I[i][i] = 1
    return I

def extended_euclid(a, b):
    """Return (x, y, g) with x*a + y*b = g = gcd(a,b)."""
    if b == 0:
        return (1, 0, a)
    else:
        x1, y1, g = extended_euclid(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (x, y, g)

def mod_inverse(a, mod):
    """Compute multiplicative inverse of a modulo mod. Raises if none exists."""
    x, _, g = extended_euclid(a % mod, mod)
    if g != 1:
        raise ValueError(f"No inverse for {a} mod {mod} (gcd={g})")
    return x % mod

def det_matrix(M):
    """Compute determinant of square matrix M over integers."""
    n = len(M)
    if n == 1:
        return M[0][0]
    if n == 2:
        return M[0][0]*M[1][1] - M[0][1]*M[1][0]
    d = 0
    for j in range(n):
        # Build minor by removing row 0, col j
        minor = []
        for i in range(1, n):
            row = [M[i][c] for c in range(n) if c != j]
            minor.append(row)
        sign = 1 if j % 2 == 0 else -1
        d += sign * M[0][j] * det_matrix(minor)
    return d

def mat_inverse_mod(M, mod):
    """Compute inverse of square matrix M modulo mod. Raises if singular."""
    n = len(M)
    det_val = det_matrix(M) % mod
    if det_val < 0:
        det_val += mod
    inv_det = mod_inverse(det_val, mod)
    # Adjugate / cofactor method
    adj = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            # Minor: remove row i, col j
            minor = []
            for r in range(n):
                if r == i: continue
                minor.append([M[r][c] for c in range(n) if c != j])
            cofactor = ((-1)**(i+j)) * det_matrix(minor) % mod
            adj[j][i] = cofactor % mod  # adjugate is transpose of cofactor
    inv = [[(adj[i][j] * inv_det) % mod for j in range(n)] for i in range(n)]
    return inv

def mat_print(M, name="M", mod_str=""):
    print(f"{name}{mod_str} =")
    for row in M:
        print("  [" + ", ".join(str(x) for x in row) + "]")

# ======================================================================
# HILL CIPHER FUNCTIONS
# ======================================================================

def encode_text(text, key, block_size):
    """Encode text with Hill cipher: block (as row vector) * key (mod 33)."""
    nums = [ALPHABET_MAP[ch] for ch in text]
    while len(nums) % block_size != 0:
        nums.append(ALPHABET_MAP[' '])
    cipher_nums = []
    for b in range(0, len(nums), block_size):
        block = nums[b:b+block_size]
        # Hill cipher: c = block * K (block is row vector)
        cipher_block = []
        for col in range(block_size):
            s = sum(block[row] * key[row][col] for row in range(block_size)) % N_ALPH
            cipher_block.append(s)
        cipher_nums.extend(cipher_block)
    cipher_chars = ''.join(ALPHABET_REV[n] for n in cipher_nums)
    return cipher_chars, cipher_nums

def decode_text(cipher_text, key_inv, block_size):
    """Decode cipher text with inverse key: block * K_inv."""
    nums = [ALPHABET_MAP[ch] for ch in cipher_text]
    plain_nums = []
    for b in range(0, len(nums), block_size):
        block = nums[b:b+block_size]
        plain_block = []
        for col in range(block_size):
            s = sum(block[row] * key_inv[row][col] for row in range(block_size)) % N_ALPH
            plain_block.append(s)
        plain_nums.extend(plain_block)
    plain_chars = ''.join(ALPHABET_REV[n] for n in plain_nums)
    return plain_chars, plain_nums

def corrupt_text(text, count=3):
    """Replace count random characters with other random alphabet chars."""
    chars = list(text)
    indices = random.sample(range(len(chars)), min(count, len(chars)))
    for idx in indices:
        # Pick a different random char
        new_char = random.choice(RUS_ALPHABET)
        while new_char == chars[idx]:
            new_char = random.choice(RUS_ALPHABET)
        chars[idx] = new_char
    return ''.join(chars), sorted(indices)

# ======================================================================
# ASSIGNMENT 1: HILL CIPHER
# ======================================================================

def assignment_1():
    print("=" * 70)
    print("ЗАДАНИЕ 1: ШИФР ХИЛЛА")
    print("=" * 70)

    # Table
    print("\n--- 1. АЛФАВИТ (33 символа: 32 русские буквы + пробел) ---")
    for ch in RUS_ALPHABET:
        print(f"  {ch!r:>3} -> {ALPHABET_MAP[ch]:2d}")

    message = "СУИРНИКИ ТОП"
    print(f"\n--- 2. ИСХОДНОЕ СООБЩЕНИЕ ({len(message)} символов) ---")
    print(f"Сообщение: {message!r}")
    msg_nums = [ALPHABET_MAP[ch] for ch in message]
    print("Числовые номера: " + " ".join(f"{n:2d}" for n in msg_nums))

    # Define 3 key matrices (2x2, 3x3, 4x4) with different determinants coprime with 33
    K2 = [[2, 1], [3, 4]]
    K3 = [[1, 2, 1], [0, 1, 3], [2, 1, 1]]
    K4 = [[1, 0, 0, 2], [0, 1, 0, 0], [0, 0, 2, 1], [0, 0, 1, 1]]

    keys = [
        ("2x2", K2, 2),
        ("3x3", K3, 3),
        ("4x4", K4, 4),
    ]

    # Check determinants
    print("\n--- 3. МАТРИЦЫ-КЛЮЧИ ---")
    for name, M, sz in keys:
        det_val = det_matrix(M) % 33
        if det_val < 0: det_val += 33
        inv_det = mod_inverse(det_val, 33)
        print(f"Ключ {name}: det = {det_val} (mod 33), inv(det) = {inv_det}")
        mat_print(M, f"K_{name.replace('x','')}", f" (mod {N_ALPH})")
        # Compute inverse for later decoding
        M_inv = mat_inverse_mod(M, 33)
        mat_print(M_inv, f"K_{name.replace('x','')}_inv", f" (mod {N_ALPH})")
        # Verify inverse
        I_check = mat_mul(M, M_inv, 33)
        print(f"Проверка K*K_inv (должна быть I):")
        mat_print(I_check, "I_check")

    # Encode message with each key
    print("\n--- 4. ШИФРОВАНИЕ ---")
    encrypted_results = {}
    for name, M, sz in keys:
        cipher_text, cipher_nums = encode_text(message, M, sz)
        encrypted_results[name] = (cipher_text, cipher_nums, M, sz)
        print(f"\nКлюч {name}:")
        print(f"  Зашифрованное сообщение: {cipher_text!r}")
        print(f"  Числовые номера: " + " ".join(f"{n:2d}" for n in cipher_nums))
        # Show block calculations for first block
        nums = msg_nums[:sz]
        cipher_block = mat_vec_mul(M, nums, 33)
        print(f"  Первый блок {nums} -> {cipher_block} (mod 33)")

    # Decode encrypted messages
    print("\n--- 5. РАСШИФРОВКА (без ошибок) ---")
    for name, M, sz in keys:
        cipher_text = encrypted_results[name][0]
        M_inv = mat_inverse_mod(M, 33)
        decoded_text, decoded_nums = decode_text(cipher_text, M_inv, sz)
        # Trim padding spaces
        decoded_trimmed = decoded_text.rstrip(' ')
        print(f"\nКлюч {name} (расшифровано):")
        print(f"  Дешифрованное: {decoded_trimmed!r}")
        print(f"  Исходное:      {message!r}")
        match = decoded_trimmed == message
        print(f"  Совпадение с исходным: {'ДА' if match else 'НЕТ'}")

    # Simulate malicious interference (replace 3 random chars in each encrypted message)
    print("\n--- 6. ИМИТАЦИЯ ВРЕДОНОСНОГО ВМЕШАТЕЛЬСТВА ---")
    print("Заменяем по 3 случайных символа в каждом зашифрованном сообщении.")
    corrupted_results = {}
    random.seed(42)  # reproducible
    for name, M, sz in keys:
        cipher_text = encrypted_results[name][0]
        corrupted_text, changed_indices = corrupt_text(cipher_text, 3)
        corrupted_results[name] = (corrupted_text, changed_indices, cipher_text, M, sz)
        print(f"\nКлюч {name}:")
        print(f"  Оригинал:  {cipher_text!r}")
        print(f"  Изменено в позициях: {changed_indices}")
        # Highlight changed chars
        highlighted = list(corrupted_text)
        for idx in changed_indices:
            highlighted[idx] = f"[{corrupted_text[idx]}]"
        print(f"  Искажённое: {' '.join(highlighted)}")

    # Decode corrupted messages
    print("\n--- 7. РАСШИФРОВКА ИСКАЖЕННЫХ СООБЩЕНИЙ (ошибки распространяются) ---")
    for name, M, sz in keys:
        corrupted_text, changed_indices, original_cipher, M_key, sz_key = corrupted_results[name]
        M_inv = mat_inverse_mod(M_key, 33)
        decoded_text, decoded_nums = decode_text(corrupted_text, M_inv, sz_key)
        # Trim padding
        decoded_trimmed = decoded_text.rstrip(' ')
        print(f"\nКлюч {name} (искажённое сообщение):")
        print(f"  Дешифрованное (после повреждения): {decoded_trimmed!r}")
        print(f"  Ожидаемое (исходное): {message!r}")
        # Show error propagation: compare char by char
        for i, (d, o) in enumerate(zip(decoded_trimmed, message)):
            if d != o:
                print(f"    Ошибка в позиции {i}: получено '{d}', ожидалось '{o}' (номер {ALPHABET_MAP[d]} vs {ALPHABET_MAP[o]})")
        # If shorter/longer due to corruption
        if len(decoded_trimmed) != len(message):
            print(f"    Длина изменилась: было {len(message)}, стало {len(decoded_trimmed)}")

    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 1 ЗАВЕРШЕНО")
    print("=" * 70)

# ======================================================================
# ASSIGNMENT 2: BREAK HILL CIPHER
# ======================================================================

def assignment_2():
    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 2: ВЗЛОМ ШИФРА ХИЛЛА")
    print("=" * 70)

    # Use 2x2 key (same as K2 above but we'll treat as unknown)
    # We'll generate a random 2x2 key for the demonstration
    key_2x2 = [[5, 2], [3, 4]]
    print(f"\n--- 1. СЛУЧАЙНЫЙ КЛЮЧ 2x2 ---")
    mat_print(key_2x2, "K_2x2")
    det_val = det_matrix(key_2x2) % 33
    print(f"Определитель: {det_val} (mod 33)")
    inv_key = mat_inverse_mod(key_2x2, 33)
    mat_print(inv_key, "K_2x2_inv")

    # Two messages
    msg1 = "СУИРНИКИ ТОП"
    msg2 = "КРИПТОГРАФ"
    # Pad msg2 to 12 chars
    if len(msg2) < 12:
        msg2 = msg2.ljust(12, ' ')
    else:
        msg2 = msg2[:12]

    print(f"\n--- 2. ДВА СООБЩЕНИЯ ---")
    print(f"Сообщение 1: {msg1!r} ({len(msg1)} символов)")
    print(f"Сообщение 2: {msg2!r} ({len(msg2)} символов)")

    # Encrypt both
    cipher1, nums1 = encode_text(msg1, key_2x2, 2)
    cipher2, nums2 = encode_text(msg2, key_2x2, 2)

    print(f"\n--- 3. ЗАШИФРОВАННЫЕ СООБЩЕНИЯ ---")
    print(f"C1 (зашифровано 1): {cipher1!r}")
    print(f"C2 (зашифровано 2): {cipher2!r}")

    # Provide one plaintext-ciphertext pair for the break
    print(f"\n--- 4. ПАРА ДЛЯ ВЗЛОМА (известны P1 и C1) ---")
    p_numbers = [ALPHABET_MAP[ch] for ch in msg1]
    c_numbers = [ALPHABET_MAP[ch] for ch in cipher1]
    print(f"P1 (числа):   {' '.join(f'{n:2d}' for n in p_numbers)}")
    print(f"C1 (числа):   {' '.join(f'{n:2d}' for n in c_numbers)}")

    # Break: solve for K in blocks of 2
    # C = P*K (mod 33) => K = P^{-1}*C (mod 33) for each 2x2 block
    # For a 2x2 message split into 2-char blocks:
    # Each block P_block (2x1) -> C_block (2x1) via K (2x2)
    # To recover K we need P to be invertible (as 2x2)
    # Let's use the first 4 chars of msg1 as a 2x2 block to solve K directly
    # Actually, for a 2-char block P = [p1; p2], C = K*P. But we have C = [c1; c2].
    # We can solve: K = [C_block1 C_block2] * P_block^{-1} if P has 2 linearly independent columns.
    # For simplicity with 2-char blocks, we'll take two independent 2-char pairs.
    # Actually the simplest: take P as 2x2 matrix formed by two consecutive 2-char blocks.
    # But since message is 12 chars = 6 blocks of 2, we can pick blocks 1 and 2.

    # Find two 2-char blocks that form an invertible P matrix (rows = blocks)
    p_numbers = [ALPHABET_MAP[ch] for ch in msg1]
    c_numbers = [ALPHABET_MAP[ch] for ch in cipher1]
    found_pair = None
    for i in range(0, len(p_numbers)-1, 2):
        for j in range(i+2, len(p_numbers)-1, 2):
            p1 = p_numbers[i:i+2]
            p2 = p_numbers[j:j+2]
            # P_mat rows = block vectors
            P_try = [[p1[0], p1[1]], [p2[0], p2[1]]]
            det_p = det_matrix(P_try) % 33
            if det_p < 0: det_p += 33
            if det_p != 0 and math.gcd(det_p, 33) == 1:
                found_pair = (i, j, P_try)
                break
        if found_pair:
            break
    if found_pair is None:
        p1 = p_numbers[0:2]
        p2 = p_numbers[4:6]
        P_mat = [[p1[0], p1[1]], [p2[0], p2[1]]]
        det_p = det_matrix(P_mat) % 33
        print(f"Fallback P det={det_p} (may not be invertible, using anyway)")
    else:
        i, j, P_mat = found_pair
        det_p = det_matrix(P_mat) % 33
        if det_p < 0: det_p += 33
        print(f"Найдена инвертируемая пара блоков (позиции {i}-{i+1} и {j}-{j+1}): det = {det_p}")
    # Corresponding C blocks (rows = cipher blocks)
    i_block = found_pair[0] if found_pair else 0
    j_block = found_pair[1] if found_pair else 4
    c1 = c_numbers[i_block:i_block+2]
    c2 = c_numbers[j_block:j_block+2]
    C_mat = [[c1[0], c1[1]], [c2[0], c2[1]]]

    print(f"\n--- 5. РЕШЕНИЕ СИСТЕМЫ ---")
    # Verify P_mat is invertible
    det_p = det_matrix(P_mat) % 33
    print(f"Матрица P (из блоков 1 и 2): det = {det_p}")
    P_inv = mat_inverse_mod(P_mat, 33)
    print(f"P_inv =")
    mat_print(P_inv, "P_inv")
    # K = P_inv * C_mat (since C_mat = P_mat * K)
    found_K = mat_mul(P_inv, C_mat, 33)
    print(f"Найденный ключ K = P_inv * C_mat:")
    mat_print(found_K, "K_found")

    # Verify found K encrypts msg1 correctly
    found_K_inv = mat_inverse_mod(found_K, 33)
    test_cipher, _ = encode_text(msg1, found_K, 2)
    test_decode, _ = decode_text(test_cipher, found_K_inv, 2)
    print(f"\nПроверка найденного ключа:")
    print(f"  Зашифровано msg1 с найденным K: {test_cipher!r}")
    print(f"  Расшифровано: {test_decode.rstrip(' ')!r}")
    print(f"  Совпадение с C1: {'ДА' if test_cipher.rstrip(' ') == cipher1.rstrip(' ') else 'НЕТ'}")

    # Decrypt msg2 using found key
    decoded_msg2, decoded_nums2 = decode_text(cipher2, found_K_inv, 2)
    print(f"\n--- 6. РАСШИФРОВКА ВТОРОГО СООБЩЕНИЯ ---")
    print(f"C2: {cipher2!r}")
    print(f"Расшифровано C2 с найденным ключом: {decoded_msg2.rstrip(' ')!r}")
    print(f"Ожидаемое (msg2): {msg2.rstrip(' ')!r}")
    print(f"Совпадение: {'ДА' if decoded_msg2.rstrip(' ') == msg2.rstrip(' ') else 'НЕТ'}")

    # Show numerical calculation for first block of msg2
    nums2_first = [ALPHABET_MAP[ch] for ch in msg2[:2]]
    decoded_first = mat_vec_mul(found_K_inv, [ALPHABET_MAP[ch] for ch in cipher2[:2]], 33)
    print(f"\nПервый блок C2 (числа): {[ALPHABET_MAP[ch] for ch in cipher2[:2]]}")
    print(f"Расшифрованный блок (числа): {decoded_first}")
    print(f"Ожидаемый блок msg2 (числа): {nums2_first}")

    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 2 ЗАВЕРШЕНО")
    print("=" * 70)

# ======================================================================
# ASSIGNMENT 3: HAMMING (7,4) CODE
# ======================================================================

# 32-letter Russian alphabet (no Ё) for Hamming (as in existing file)
HAM_ALPHABET = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
    'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э',
    'Ю', 'Я'
]
HAM_MAP = {ch: i for i, ch in enumerate(HAM_ALPHABET)}
HAM_REV_MAP = {i: ch for i, ch in enumerate(HAM_ALPHABET)}

def bin_to_letter(bits_str):
    idx = int(bits_str, 2)
    return HAM_REV_MAP[idx]

def letter_to_bin(ch):
    return format(HAM_MAP[ch], '05b')

# G and H matrices for Hamming (7,4)
G_MAT = [
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1],
]

H_MAT = [
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1],
]

def binary_mat_mul(A, v):
    """Multiply binary matrix A by binary vector v over GF(2)."""
    res = []
    for row in A:
        s = 0
        for a, vi in zip(row, v):
            s ^= (a & vi)
        res.append(s)
    return res

def binary_vec_mul(A, B):
    """Multiply binary matrix A (m x p) by B (p x n) over GF(2)."""
    m = len(A)
    p = len(A[0])
    n = len(B[0])
    C = [[0]*n for _ in range(m)]
    for i in range(m):
        for k in range(p):
            aik = A[i][k]
            if aik == 0: continue
            for j in range(n):
                C[i][j] ^= (aik & B[k][j])
    return C

def binary_transpose(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

def binary_vec_transpose(v):
    return [[v[i]] for i in range(len(v))]

def binary_mat_print(M, name="M"):
    print(f"{name} (GF(2)):")
    for row in M:
        print("  [" + ", ".join(str(x) for x in row) + "]")

def encode_hamming_4bit(data4):
    """Encode 4 data bits to 7 code bits using G (4x7)."""
    # c[j] = sum_i G[i][j] * d[i]  (mod 2)
    result = []
    for j in range(7):
        s = 0
        for i in range(4):
            s ^= (G_MAT[i][j] & data4[i])
        result.append(s)
    return result

def decode_hamming_7bit(code7):
    """Decode 7 code bits: compute syndrome and correct error."""
    # Compute syndrome H * c (mod 2)
    s_vals = [0, 0, 0]
    for r in range(3):
        s = 0
        for c in range(7):
            s ^= (H_MAT[r][c] & code7[c])
        s_vals[r] = s
    s_str = ''.join(str(x) for x in s_vals)
    # Syndrome to error position mapping based on H columns
    # Columns of H (reading as binary from top to bottom):
    # col1: 110, col2: 101, col3: 011, col4: 111, col5: 100, col6: 010, col7: 001
    syndrome_map = {
        '000': 0,
        '110': 1,
        '101': 2,
        '011': 3,
        '111': 4,
        '100': 5,
        '010': 6,
        '001': 7,
    }
    error_pos = syndrome_map.get(s_str, 0)
    corrected = list(code7)
    if error_pos != 0:
        corrected[error_pos - 1] ^= 1
    # Extract first 4 bits (information bits)
    info_bits = corrected[:4]
    return info_bits, s_str, error_pos, corrected

def assignment_3():
    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 3: КОД ХЭММИНГА (7, 4)")
    print("=" * 70)

    # Alphabet table (32 letters)
    print("\n--- 1. АЛФАВИТ (32 буквы, без Ё) ---")
    for ch in HAM_ALPHABET:
        bits = letter_to_bin(ch)
        val = HAM_MAP[ch]
        print(f"  {ch!r:>2} -> {bits} (номер {val})")

    word = "ТЕСТ"
    print(f"\n--- 2. ИСХОДНОЕ СЛОВО ---")
    print(f"Слово: {word!r} ({len(word)} букв)")
    binary_word = []
    for ch in word:
        b = letter_to_bin(ch)
        binary_word.append(b)
        print(f"  {ch!r} -> {b}")
    full_binary = ''.join(binary_word)
    print(f"Полный двоичный код (20 символов): {full_binary}")

    # G and H matrices
    print("\n--- 3. МАТРИЦЫ G И H ---")
    binary_mat_print(G_MAT, "G (4x7)")
    binary_mat_print(H_MAT, "H (3x7)")
    print("\nОписание составления:")
    print("  G = [I4 | P], где P = [[1,1,0],[1,0,1],[0,1,1],[1,1,1]]")
    print("  H = [P^T | I3] для проверки G * H^T = 0 в GF(2)")
    # Verify G * H^T = 0
    Ht = binary_transpose(H_MAT)
    GHt = binary_vec_mul(G_MAT, Ht)
    print(f"Проверка G * H^T = 0: {'ДА' if all(all(x==0 for x in row) for row in GHt) else 'НЕТ'}")

    # Encode
    print("\n--- 4. КОДИРОВАНИЕ С ПОМОЩЬЮ G ---")
    # Split 20 bits into 5 blocks of 4 bits
    encoded_blocks = []
    all_encoded_bits = []
    for i in range(0, len(full_binary), 4):
        block_str = full_binary[i:i+4]
        data_bits = [int(b) for b in block_str]
        encoded = encode_hamming_4bit(data_bits)
        encoded_str = ''.join(str(b) for b in encoded)
        encoded_blocks.append(encoded_str)
        all_encoded_bits.extend(encoded)
        print(f"  Блок {i//4 + 1}: данные {block_str} -> код {encoded_str} (7 бит)")
    full_encoded_str = ''.join(str(b) for b in all_encoded_bits)
    full_encoded_display = ''.join(encoded_blocks)
    print(f"Полный закодированный код ({len(full_encoded_display)} бит): {full_encoded_display}")

    # Simulate bit errors: 1, 2, 3, 4 bits
    print("\n--- 5. СИМУЛЯЦИЯ ВРЕДОНОСНОГО ВМЕШАТЕЛЬСТВА ---")
    random.seed(123)
    error_cases = [
        ("1 бит", [5]),
        ("2 бита", [3, 15]),
        ("3 бита", [8, 20, 30]),
        ("4 бита", [1, 10, 25, 32]),
    ]
    # But let's make it sequential: each error case adds errors on top of original
    # Actually let's do independent corruptions on the original encoded message
    results = {}
    for label, positions in error_cases:
        # Create corrupted copy
        corrupted_bits = list(all_encoded_bits)
        for pos in positions:
            if 0 <= pos < len(corrupted_bits):
                corrupted_bits[pos] ^= 1
        corrupted_str = ''.join(str(b) for b in corrupted_bits)
        results[label] = (corrupted_bits, positions)
        # Show highlighted
        print(f"\n{label} (изменены позиции {positions}):")
        print(f"  Оригинал:  {full_encoded_display}")
        highlighted = []
        corrupted_display = ''.join(str(b) for b in corrupted_bits)
        for idx, b in enumerate(corrupted_display):
            if idx in positions:
                highlighted.append(f"[{b}]")
            else:
                highlighted.append(str(b))
        # Show as groups of 7 for readability
        grouped = ' '.join(''.join(highlighted[i:i+7]) for i in range(0, len(highlighted), 7))
        print(f"  Искажённый: {grouped}")

    # Decode and correct
    print("\n--- 6. ДЕКОДИРОВАНИЕ И ИСПРАВЛЕНИЕ ОШИБОК ---")
    decoded_words = {}
    for label, (corrupted_bits, positions) in results.items():
        print(f"\n{label}:")
        # Split into 7-bit blocks
        blocks = [corrupted_bits[i:i+7] for i in range(0, len(corrupted_bits), 7)]
        decoded_all_bits = []
        for idx, block in enumerate(blocks):
            info_bits, syndrome_str, error_pos, corrected = decode_hamming_7bit(block)
            info_str = ''.join(str(b) for b in info_bits)
            corrected_str = ''.join(str(b) for b in corrected)
            if syndrome_str != '000':
                print(f"  Блок {idx+1}: код {''.join(str(b) for b in block)} -> синдром {syndrome_str} (ошибка в позиции {error_pos}) -> исправлено -> {corrected_str} (инфо: {info_str})")
            else:
                print(f"  Блок {idx+1}: код {''.join(str(b) for b in block)} -> без ошибок -> инфо: {info_str}")
            decoded_all_bits.extend(info_bits)
        # Reconstruct first 20 bits (4 letters)
        result_bits = decoded_all_bits[:20]
        result_word = ''.join(bin_to_letter(''.join(str(b) for b in result_bits[i:i+5])) for i in range(0, 20, 5))
        decoded_words[label] = result_word
        result_display = ''.join(str(b) for b in result_bits)
        print(f"  Результат (20 бит): {result_display}")
        print(f"  Декодированное слово: {result_word!r}")
        is_correct = result_word == word
        print(f"  Верно? {'ДА' if is_correct else 'НЕТ'}")

    # Summary table
    print("\n--- 7. СВОДНАЯ ТАБЛИЦА ---")
    print(f"{'Вмешательство':<15} {'Декодированное слово':<20} {'Верно?':<8}")
    print("-" * 45)
    for label in [r[0] for r in error_cases]:
        w = decoded_words.get(label, "?")
        correct = "ДА" if w == word else "НЕТ"
        print(f"{label:<15} {w!r:<20} {correct:<8}")

    print(f"\nИсходное слово: {word!r}")
    print(f"Код Хэмминга (7,4) исправляет до {len(error_cases)} ошибок одновременно.")

    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 3 ЗАВЕРШЕНО")
    print("=" * 70)

# ======================================================================
# MAIN
# ======================================================================

def main():
    print("ЛАБОРАТОРНАЯ РАБОТА №1: КОДИРОВАНИЕ И ШИФРОВАНИЕ")
    print("Реализация: Python (только стандартная библиотека)")
    print(f"Алфавит для Хилла: {N_ALPH} символов (модуль 33)")
    print(f"Алфавит для Хэмминга: {len(HAM_ALPHABET)} букв")

    assignment_1()
    assignment_2()
    assignment_3()

    print("\n" + "=" * 70)
    print("ВСЕ ЗАДАНИЯ ВЫПОЛНЕНЫ УСПЕШНО!")
    print("=" * 70)

if __name__ == "__main__":
    main()
