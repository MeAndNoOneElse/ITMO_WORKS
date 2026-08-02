def mat_copy(A):
    """Глубокая копия матрицы."""
    return [row[:] for row in A]
def mat_hstack(A, b):
    """Расширенная матрица [A | b]."""
    return [A[i][:] + [b[i]] for i in range(len(A))]
def vec_dot(u, v):
    """Скалярное произведение."""
    return sum(u[k] * v[k] for k in range(len(u)))
def vec_norm(v):
    """Евклидова норма вектора."""
    return sum(x * x for x in v) ** 0.5
def mat_vec_mul(A, x):
    """Умножение матрицы на вектор."""
    return [vec_dot(A[i], x) for i in range(len(A))]
def vec_sub(u, v):
    """Поэлементная разность двух векторов."""
    return [u[i] - v[i] for i in range(len(u))]
def aug_row_str(row, n):
    """Строка расширенной матрицы в читаемом виде."""
    left = "  ".join(f"{row[j]:10.6f}" for j in range(n))
    return f"  {left}  |  {row[n]:10.6f}"

def gauss_solve_with_steps(A, b):
    """Метод Гаусса с выбором ведущего элемента по столбцу (partial pivoting).

    Перед каждым шагом прямого хода среди строк i..n-1 выбирается та,
    у которой |aug[j][i]| максимален, и переставляется на позицию i.
    Это гарантирует, что ведущий элемент никогда не будет равен нулю
    (пока матрица невырождена) и улучшает численную устойчивость.

    Каждая перестановка строк меняет знак определителя, поэтому
    det_product умножается на -1 при каждом swap.
    """

    n = len(A)
    forward_steps  = []
    backward_steps = []
    _store_matrix = (n <= 9)

    # Счётчик перестановок для знака определителя
    swap_count = 0

    aug = mat_hstack(A, b)
    forward_steps.append(("initial", "Начальная расширенная матрица [A|b]", mat_copy(aug)))

    for i in range(n):
        # ── Partial pivoting: ищем строку с макс. |элементом| в столбце i ──
        max_row = i
        max_val = abs(aug[i][i])
        for r in range(i + 1, n):
            if abs(aug[r][i]) > max_val:
                max_val = abs(aug[r][i])
                max_row = r

        if max_val < 1e-15:
            raise ValueError(
                f"Все элементы столбца {i+1} ниже строки {i+1} равны нулю — "
                f"матрица вырождена (система несовместна или имеет бесконечно много решений)"
            )

        if max_row != i:
            aug[i], aug[max_row] = aug[max_row], aug[i]
            swap_count += 1
            forward_steps.append((
                "swap",
                f"Итерация {i+1}: перестановка строк {i+1} <-> {max_row+1}"
                f"  (ведущий элемент |{aug[i][i]:.6f}|)",
                mat_copy(aug) if _store_matrix else None
            ))

        pivot = aug[i][i]

        forward_steps.append((
            "pivot",
            f"Итерация {i+1}: ведущий элемент  a[{i+1},{i+1}] = {pivot:.6f}",
            mat_copy(aug) if _store_matrix else None
        ))

        for j in range(i + 1, n):
            factor = aug[j][i] / pivot
            if abs(factor) > 1e-15:
                forward_steps.append((
                    "eliminate",
                    f"Строка {j+1}  −  ({factor:.6f}) · Строка {i+1}"
                    f"   [обнуляем a[{j+1},{i+1}]]",
                    None          # матрицу не копируем — она будет в result
                ))
                for k in range(i, n + 1):
                    aug[j][k] -= factor * aug[i][k]
                forward_steps.append((
                    "result",
                    f"Результат после исключения x{i+1} из строки {j+1}",
                    # При большой матрице храним только изменённую строку: (j, row_copy)
                    mat_copy(aug) if _store_matrix else ("row", j, aug[j][:])
                ))

    forward_steps.append((
        "final",
        "Верхняя треугольная матрица после прямого хода",
        mat_copy(aug)
    ))

    det_product = 1.0
    for i in range(n):
        det_product *= aug[i][i]
    # Каждая перестановка строк меняет знак определителя
    if swap_count % 2 == 1:
        det_product = -det_product

    x = [0.0] * n

    for i in range(n - 1, -1, -1):
        diag  = aug[i][i]
        rhs   = aug[i][n]
        sub_terms = [(aug[i][k], k) for k in range(i + 1, n)]

        if not sub_terms:
            formula = (f"x{i+1} = b'[{i+1}] / a'[{i+1},{i+1}]"
                       f" = {rhs:.6f} / {diag:.6f}")
        else:
            parts = "  +  ".join(
                f"({c:+.6f})·x{k+1}" for c, k in sub_terms
            )
            formula = (f"x{i+1} = ( {rhs:.6f}  −  [ {parts} ] )"
                       f" / {diag:.6f}")

        val = rhs
        for coef, k in sub_terms:
            val -= coef * x[k]
        x[i] = val / diag

        if sub_terms:
            num_parts = "  +  ".join(
                f"({c:+.6f})·({x[k]:.6f})" for c, k in sub_terms
            )
            numeric = (f"         = ( {rhs:.6f}  −  [ {num_parts} ] )"
                       f" / {diag:.6f}")
        else:
            numeric = f"         = {rhs:.6f} / {diag:.6f}"

        backward_steps.append((
            i,
            x[i],
            formula,
            numeric,
            [c for c, _ in sub_terms]
        ))

    return x, aug, forward_steps, backward_steps, det_product
