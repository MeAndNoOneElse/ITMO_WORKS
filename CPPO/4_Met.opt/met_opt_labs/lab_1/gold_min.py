from math import *
from numpy import *

def f(x):
    return 2 * sin(x) - 1.5 * cos(2 * x) + sin(3 * x) - 0.5 * cos(4 * x)

def mf(x):
    return -f(x)

print("ЗОЛОТОЕ СЕЧЕНИЕ:")
print("-"*30)

eps = 0.001
phi = (1 + sqrt(5)) / 2
L = 2
N_theor = (log(L/eps) / log(phi))

# МИНИМУМ f(x)
left, right = -2, 0
c = left + (right-left)/phi**2
d = left + (right-left)/phi
it = 0
while right - left > eps:
    if f(c) < f(d):
        right = d
        d = c
        c = left + (right-left)/phi**2
    else:
        left = c
        c = d
        d = left + (right-left)/phi
    it += 1
print(f"Мин: {it}/{N_theor} x={((left+right)/2):.6f} f={f((left+right)/2):.6f}")
