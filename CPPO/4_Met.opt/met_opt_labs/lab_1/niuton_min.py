from math import *


def f(x):
    return 2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x)
def df(x):
    return 2 * cos(x) + 3 * sin(2 * x) + 3 * cos(3 * x) + 2 * sin(4 * x)
def d2f(x):
    return -2 * sin(x) + 6 * cos(2 * x) - 9 * sin(3 * x) + 8 * cos(4 * x)


a = -3
b = -2.5
eps = 0.0001
n = 0
x = (a + b) / 2
while abs(df(x)) >= eps:
    n += 1
    x = a - (b - a) * df(a) / (df(b) - df(a))
    if df(a) * df(x) < 0:
        b = x
    else:
        a = x

print(f"x = {x:.6f}")
print(f"f(x) = {f(x):.6f}")
print(f"f'(x) = {df(x):.6f}")

d2 = d2f(x)
if d2 > 0:
    typ = "МИНИМУМ"
elif d2 < 0:
    typ = "МАКСИМУМ"
else:
    typ = "ТОЧКА ПЕРЕГИБА"
print(f"f'' = {d2:.6f}")
print(f"n: {n}")
