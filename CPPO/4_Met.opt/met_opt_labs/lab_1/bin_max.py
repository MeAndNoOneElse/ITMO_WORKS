from math import  *

def f(x):
    return 2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x)
def mf(x):
    return -(2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x))

eps = 0.001;
n = 0
a = -2
b = 0
N_teor = log((b - a - eps) / eps) / log(2)
#### Max
while (b - a) > 2 * eps:
    n += 1

    x1 = (a + b - eps) / 2
    x2 = (a + b + eps) / 2
    if mf(x1) <= mf(x2):
        b = x2
    else:
        a = x1
x_min = (a + b) / 2
print("n: " + str(n))
print("n_teor: " + str(N_teor))
print("x_max: " + str(x_min))
print("f_max: " + str(f(x_min)))
print()
