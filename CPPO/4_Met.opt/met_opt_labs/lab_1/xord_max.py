from math import *
from numpy import *

def f(x):
    return 2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x)

def df(x):  # f'(x)
    return 2 * cos(x) + 3 * sin(2 * x) + 3 * cos(3 * x) + 2 * sin(4 * x)

print("МЕТОД ХОРД (максимум)")
print("-"*27)

eps = 0.001
left, right = -0.5, 0  # интервал где f'>0 слева, f'<0 справа
it = 0

while abs(right - left) > eps:
    x_new = right - df(right) * (right - left) / (df(right) - df(left))
    left, right = right, x_new
    it += 1

x_max = (left + right) / 2
print(f"x={x_max:.6f} f={f(x_max):.6f} N={it} df={df(x_max):.6f}")
