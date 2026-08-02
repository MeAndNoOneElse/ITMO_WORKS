from tkinter import messagebox, filedialog
import math


def validate_number(text):
    """Проверяет, что текст представляет конечное число (не NaN, не inf) и не строковые маркеры null/None.

    Возвращает True только если text можно преобразовать в float и значение является конечным.
    """
    if text is None:
        return False
    s = str(text).strip()
    if not s:
        return False
    low = s.lower()
    # Отклоняем явные текстовые маркеры отсутствия значения
    if low in ("null", "none", "nan"):
        return False
    try:
        v = float(s)
    except ValueError:
        return False
    # Отклоняем NaN и бесконечности
    if math.isnan(v) or math.isinf(v):
        return False
    return True


def _det_approx(A):

    n = len(A)
    M = [row[:] for row in A]   # копия
    det = 1.0
    for i in range(n):
        pivot = M[i][i]
        if abs(pivot) < 1e-15:
            return 0.0
        det *= pivot
        for k in range(i, n):
            M[i][k] /= pivot
        for j in range(i + 1, n):
            factor = M[j][i]
            for k in range(i, n):
                M[j][k] -= factor * M[i][k]
    return det

# аааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааа



def matrix_rank(A):

    return sum(1 for row in A if any(v != 0 for v in row))


def read_from_keyboard(n, matrix_entries, vector_entries):

    try:
        A = []
        for i in range(n):
            row = []
            for j in range(n):
                val = matrix_entries[i][j].get().strip()
                if not val:
                    messagebox.showerror("Ошибка",
                        f"Заполните все элементы матрицы (ячейка [{i + 1},{j + 1}])")
                    return None, None
                if not validate_number(val):
                    messagebox.showerror("Ошибка",
                        f"Элемент [{i + 1},{j + 1}] должен быть числом и не быть NaN/null/inf")
                    return None, None
                num = float(val)
                # дополнительная проверка на безопасность
                if math.isnan(num) or math.isinf(num):
                    messagebox.showerror("Ошибка",
                        f"Элемент [{i + 1},{j + 1}] содержит недопустимое значение")
                    return None, None
                row.append(num)
            A.append(row)

        b = []
        for i in range(n):
            val = vector_entries[i].get().strip()
            if not val:
                messagebox.showerror("Ошибка",
                    f"Заполните все элементы вектора (элемент {i + 1})")
                return None, None
            if not validate_number(val):
                messagebox.showerror("Ошибка",
                    f"Элемент вектора {i + 1} должен быть числом и не быть NaN/null/inf")
                return None, None
            num = float(val)
            if math.isnan(num) or math.isinf(num):
                messagebox.showerror("Ошибка",
                    f"Элемент вектора {i + 1} содержит недопустимое значение")
                return None, None
            b.append(num)



        # проверка на нулевые строки
        rA = (
            matrix_rank(A))
        if rA == 0:
            messagebox.showerror("Ошибка", "Матрица коэффициентов является нулевой")
            return None, None
        if rA < n:
            messagebox.showerror("Ошибка",
                f"Матрица содержит нулевые строки (ненулевых строк: {rA} из {n})")
            return None, None

        return A, b

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении данных: {str(e)}")
        return None, None


def browse_file():
    return filedialog.askopenfilename(
        title="Выберите файл с данными",
        filetypes=[("Text files", "*.txt"), ("All files", "*")]
    )


def read_from_file(filename):

    if not filename:
        messagebox.showerror("Ошибка", "Укажите путь к файлу")
        return None, None, None

    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) < 2:
            messagebox.showerror("Ошибка", "Файл содержит недостаточно данных")
            return None, None, None

        try:
            n = int(lines[0])
        except ValueError:
            messagebox.showerror("Ошибка",
                "Первая строка должна содержать целое число — размерность")
            return None, None, None

        if n <= 0 or n > 20:
            messagebox.showerror("Ошибка", "Размерность должна быть от 1 до 20")
            return None, None, None

        if len(lines) < n + 2:
            messagebox.showerror("Ошибка",
                f"Файл должен содержать {n} строк для матрицы и 1 строку для вектора")
            return None, None, None

        A = []
        for i in range(n):
            try:
                row = list(map(float, lines[i + 1].split()))
            except ValueError:
                messagebox.showerror("Ошибка",
                    f"Строка {i + 2} содержит некорректные числа")
                return None, None, None
            if len(row) != n:
                messagebox.showerror("Ошибка",
                    f"Строка {i + 2} должна содержать {n} чисел")
                return None, None, None
            # Проверим на NaN/inf
            for v in row:
                if math.isnan(v) or math.isinf(v):
                    messagebox.showerror("Ошибка",
                        f"Строка {i + 2} содержит недопустимое значение (NaN/inf)")
                    return None, None, None
            A.append(row)

        try:
            b = list(map(float, lines[n + 1].split()))
        except ValueError:
            messagebox.showerror("Ошибка", "Последняя строка содержит некорректные числа")
            return None, None, None

        if len(b) != n:
            messagebox.showerror("Ошибка",
                f"Вектор правых частей должен содержать {n} чисел")
            return None, None, None
        for idx, v in enumerate(b):
            if math.isnan(v) or math.isinf(v):
                messagebox.showerror("Ошибка",
                    f"Элемент вектора правых частей #{idx+1} содержит недопустимое значение (NaN/inf)")
                return None, None, None

        # проверка на нулевые строки
        rA = matrix_rank(A)
        if rA == 0:
            messagebox.showerror("Ошибка", "Матрица коэффициентов является нулевой")
            return None, None, None
        if rA < n:
            messagebox.showerror("Ошибка",
                f"Матрица содержит нулевые строки (ненулевых строк: {rA} из {n})")
            return None, None, None

        return n, A, b

    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {filename} не найден")
        return None, None, None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {str(e)}")
        return None, None, None
