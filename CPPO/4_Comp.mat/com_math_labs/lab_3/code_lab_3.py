import sys
import math
from typing import Callable

IMPROPER_FUNCTIONS = {
    1: {
        'name': '1 / sqrt(x + 1)  [разрыв в точке a = -1]',
        'func': lambda x: 1.0 / math.sqrt(x + 1),
        'a': -1.0, 'b': 0.0, 'exact': 2.0,
        'convergent': True, 'sing': 'a',
        'p': 0.5,
    },
    2: {
        'name': '1 / (3 - x)^(1/3)  [разрыв в точке b = 3]',
        'func': lambda x: 1.0 / ((3 - x) ** (1.0 / 3.0)),
        'a': 0.0, 'b': 3.0, 'exact': 3 * 3**(2/3) / 2,
        'convergent': True, 'sing': 'b',
        'p': 1/3,
    },
    3: {
        'name': '1 / (x - 1)^2  [разрыв внутри отрезка [0, 2] в точке x = 1]',
        'func': lambda x: 1.0 / (x - 1) ** 2,
        'a': 0.0, 'b': 2.0, 'exact': None,
        'convergent': False, 'sing': 'center',
        'p': 2.0,
    },
}

VARIANTS = {
    1: {'name': '(-x^3 - 2x^2 - 2x + 1) от -2 до 0',
        'func': lambda x: -x**3 - 2*x**2 - 2*x + 1, 'a': -2, 'b': 0, 'exact': 14/3},
    2: {'name': '(-3x^3 - 5x^2 + 4x - 2) от -3 до -1',
        'func': lambda x: -3*x**3 - 5*x**2 + 4*x - 2, 'a': -3, 'b': -1, 'exact': -10/3},
    3: {'name': '(-2x^3 - 4x^2 + 8x - 4) от -3 до -1',
        'func': lambda x: -2*x**3 - 4*x**2 + 8*x - 4, 'a': -3, 'b': -1, 'exact': -104/3},
    4: {'name': '(-2x^3 - 3x^2 + x + 5) от -4 до 2',
        'func': lambda x: -2*x**3 - 3*x**2 + x + 5, 'a': -4, 'b': 2, 'exact': 72},
    5: {'name': '(3x^3 + 4x^2 + 7x - 17) от 1 до 2',
        'func': lambda x: 3*x**3 + 4*x**2 + 7*x - 17, 'a': 1, 'b': 2, 'exact': 169/12},
}


def left_rect(a, b, n, f):
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(n))


def right_rect(a, b, n, f):
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(1, n + 1))


def middle_rect(a, b, n, f):
    h = (b - a) / n
    return h * sum(f(a + (i + 0.5) * h) for i in range(n))


def trapezoid(a, b, n, f):
    h = (b - a) / n
    return h * ((f(a) + f(b)) / 2 + sum(f(a + i * h) for i in range(1, n)))


def simpson(a, b, n, f):
    if n % 2:
        n += 1
    h = (b - a) / n
    return h / 3 * (f(a) + f(b)
                    + 4 * sum(f(a + i * h) for i in range(1, n, 2))
                    + 2 * sum(f(a + i * h) for i in range(2, n, 2)))


def newton_cotes_6(a, b, f):
    h = (b - a) / 6
    coeffs = [41, 216, 27, 272, 27, 216, 41]
    return (b - a) / 840 * sum(c * f(a + i * h) for i, c in enumerate(coeffs))


def runge(I_new, I_old, k):
    return abs(I_new - I_old) / (2 ** k - 1)


METHODS = {
    1: ('Левые прямоугольники', left_rect, 2),
    2: ('Правые прямоугольники', right_rect, 2),
    3: ('Средние прямоугольники', middle_rect, 2),
    4: ('Трапеции', trapezoid, 2),
    5: ('Симпсон', simpson, 4),
}


def get_int(prompt, lo=1, hi=100000):
    while True:
        try:
            v = int(input(prompt))
            if lo <= v <= hi:
                return v
            print(f'  Значение должно быть от {lo} до {hi}')
        except ValueError:
            print('  Введите целое число')


def get_choice(options):
    while True:
        try:
            v = int(input('  > '))
            if 1 <= v <= options:
                return v
            print(f'  Выберите от 1 до {options}')
        except ValueError:
            print('  Введите число')


def get_precision():
    while True:
        try:
            s = input('  Точность (по умолч. 0.00001): ').strip()
            if s == '':
                return 0.00001
            v = float(s)
            return v
        except ValueError:
            print('  Введите число')


def compute_improper(func, method, sing, a, b, n):
    d = 1e-10
    if sing == 'a':
        return method(a + d, b, n, func)
    if sing == 'b':
        return method(a, b - d, n, func)
    c = (a + b) / 2
    return method(a, c - d, n, func) + method(c + d, b, n, func)


def main_task():
    print('\nВыберите вариант:')
    for num, v in sorted(VARIANTS.items()):
        print(f'  {num}. {v["name"]}')
    variant = VARIANTS[get_choice(len(VARIANTS))]
    f, a, b, exact = variant['func'], variant['a'], variant['b'], variant['exact']

    print('\nРежим:')
    print('  1. Фиксированное n')
    print('  2. Контроль точности (Рунге)')
    print('  3. Ньютона-Котеса (n=6)')
    mode = get_choice(3)

    print('\nМетод:')
    for num, (name, _, _) in METHODS.items():
        print(f'  {num}. {name}')
    mid = get_choice(len(METHODS))
    m_name, method, k = METHODS[mid]

    if mode == 1:
        n = get_int('  Число разбиений n: ', 4)
        result = method(a, b, n, f)
    elif mode == 2:
        eps = get_precision()
        n, I_prev = 4, method(a, b, 4, f)
        while True:
            n *= 2
            I_curr = method(a, b, n, f)
            if runge(I_curr, I_prev, k) < eps:
                result = I_curr
                break
            I_prev = I_curr
    else:
        result = newton_cotes_6(a, b, f)
        print(f'\nРезультат (Ньютона-Котеса): {result:.10f}')
        print(f'Точное значение:             {exact:.10f}')
        print(f'Абс. погрешность:            {abs(exact - result):.2e}')
        return

    n_used = n if mode in (1, 2) else 6
    print(f'\nМетод: {m_name}, n = {n_used}')
    print(f'  Результат:   {result:.10f}')
    if exact is not None:
        print(f'  Точное зн-е: {exact:.10f}')
        print(f'  Абс. погр.:  {abs(exact - result):.2e}')


def extra_task():
    print('\nНесобственные интегралы II рода')
    print('Выберите функцию:')
    for num, v in sorted(IMPROPER_FUNCTIONS.items()):
        print(f'  {num}. {v["name"]}')
    info = IMPROPER_FUNCTIONS[get_choice(len(IMPROPER_FUNCTIONS))]

    p = info['p']
    print(f'\nАнализ сходимости: f(x) ~ 1/(x-c)^p, p = {p}')
    if p >= 1:
        print('  p >= 1 => интеграл расходится')
        print('  Интеграл не существует')
        return

    print(f'  p < 1 => интеграл сходится')

    print('\nМетод:')
    for num, (name, _, _) in METHODS.items():
        print(f'  {num}. {name}')
    mid = get_choice(len(METHODS))
    m_name, method, k = METHODS[mid]
    eps = get_precision()

    func, a, b, exact, sing = info['func'], info['a'], info['b'], info['exact'], info['sing']
    d = 1e-10
    labels = {'a': f'[{a+d}, {b}] (обход особенности в a)',
              'b': f'[{a}, {b-d}] (обход особенности в b)',
              'center': f'[{a}, {(a+b)/2-d}] + [{(a+b)/2+d}, {b}] (обход разрыва внутри)'}
    print(f'\nИнтегрирование: {labels[sing]}')

    n, I_prev = 4, compute_improper(func, method, sing, a, b, 4)
    print(f'\nИтерации ({m_name}):')
    print(f'  {"n":<8} {"Результат":<18} {"R":<12}')
    while True:
        n *= 2
        I_curr = compute_improper(func, method, sing, a, b, n)
        R = runge(I_curr, I_prev, k)
        print(f'  {n:<8} {I_curr:<18.10f} {R:<.2e}')
        if R < eps:
            break
        I_prev = I_curr
        if n > 4 * 10**6:
            print('  Достигнут предел итераций')
            break

    print(f'\nРезультат: {I_curr:.10f}  (n={n})')
    if exact is not None:
        print(f'Точное зн-е: {exact:.10f}')
        print(f'Абс. погр.:  {abs(exact - I_curr):.2e}')


def main():
    print('ЧИСЛЕННОЕ ИНТЕГРИРОВАНИЕ')
    while True:
        print('\n' + '=' * 40)
        print('  1. Основное задание')
        print('  2. Несобственный интеграл II рода (доп)')
        print('  3. Выход')
        choice = get_choice(3)
        if choice == 3:
            print('Всего хорошего')
            break
        if choice == 1:
            main_task()
        else:
            extra_task()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nПрограмма прервана')
