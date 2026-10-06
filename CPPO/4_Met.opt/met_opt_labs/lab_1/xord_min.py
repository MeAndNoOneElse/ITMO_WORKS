from math import *
from numpy import *

def f(x):
    return 2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x)

def df(x):  # f'(x)
    return 2 * cos(x) + 3 * sin(2 * x) + 3 * cos(3 * x) + 2 * sin(4 * x)

print("МЕТОД ХОРД (минимум)")
print("-"*25)

eps = 0.001
left, right = -2, 0
it = 0

while abs(right - left) > eps:
    # хорда: x_new = b - f'(b)*(b-a)/(f'(b)-f'(a))
    x_new = right - df(right) * (right - left) / (df(right) - df(left))
    left, right = right, x_new
    it += 1

x_min = (left + right) / 2
print(f"x={x_min:.6f} f={f(x_min):.6f} N={it} df={df(x_min):.6f}")
