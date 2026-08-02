import math
import numpy as np
from scipy import stats

print('='*60)
print('ЗАДАЧА 3.1')
print('='*60)
# Дисперсия D = 0.04 (%^2), SE <= 0.01 %
# SE = sigma/sqrt(n)  =>  n >= (sigma/SE)^2
D_pct = 0.04   # дисперсия в %^2
SE_pct = 0.01  # желаемая SE в %

sigma_pct = math.sqrt(D_pct)
n_exact = (sigma_pct / SE_pct) ** 2
n_min = math.ceil(n_exact)

print(f'Дисперсия D = {D_pct} %^2')
print(f'СКО sigma = sqrt(D) = {sigma_pct:.4f} %')
print(f'Требуемая SE = {SE_pct} %')
print(f'n = (sigma/SE)^2 = ({sigma_pct}/{SE_pct})^2 = {n_exact:.1f}')
print(f'n_min = {n_min} дней')

print()
print('='*60)
print('ЗАДАЧА 3.2')
print('='*60)
# X_i ~ Exp(mu=5), N(t) - поток Пуассона с интенсивностью lambda=1/5
# P(N(480) > 100) = P(S_101 < 480)
# S_n = X_1+...+X_n ~ Gamma(n, scale=5)
lam = 1/5
mu = 5
sigma2 = 25
T = 480

n_clients = 101
mean_S = n_clients * mu
std_S = math.sqrt(n_clients * sigma2)

# ЦПТ
z2 = (T - mean_S) / std_S
p_clt2 = stats.norm.cdf(z2)

# Точное значение через Gamma CDF
p_exact2 = stats.gamma.cdf(T, a=n_clients, scale=mu)

# Пуассон (альтернативная проверка)
lam_pois = T / mu   # 96
p_poisson = 1 - stats.poisson.cdf(100, lam_pois)

print(f'mu = {mu} мин, sigma^2 = {sigma2}, T = {T} мин')
print(f'P(N > 100) = P(S_101 < 480)')
print(f'E[S_101] = {mean_S} мин, Std[S_101] = {std_S:.4f} мин')
print(f'z = (480 - {mean_S}) / {std_S:.4f} = {z2:.4f}')
print(f'P (ЦПТ)        = {p_clt2:.6f}')
print(f'P (Gamma CDF)  = {p_exact2:.6f}')
print(f'P (Пуассон CDF): lambda_T={lam_pois}, P(N>100) = {p_poisson:.6f}')

print()
print('='*60)
print('ЗАДАЧА 3.3')
print('='*60)
p_win = 0.49
p_lose = 0.51
n = 1000

E_X = p_win * 1 + p_lose * (-1)        # -0.02
E_X2 = p_win * 1 + p_lose * 1          # = 1 (т.к X^2=1 всегда)
Var_X = E_X2 - E_X**2                  # 1 - 0.0004 = 0.9996

E_S = n * E_X        # -20
Var_S = n * Var_X    # 999.6
std_S3 = math.sqrt(Var_S)

# ЦПТ: P(S_1000 > 0)
z3 = (0 - E_S) / std_S3   # = 20 / 31.616... = 0.6325
p_clt3 = 1 - stats.norm.cdf(z3)

# ЦПТ с поправкой на непрерывность (S принимает чётные значения -> шаг 2)
# Поправка: P(S > 0) ~ P(S >= 2) ~ P(S_norm > 1)
z3_cont = (1 - E_S) / std_S3
p_clt3_cont = 1 - stats.norm.cdf(z3_cont)

# Симуляция (100 000 испытаний — достаточно для точности ~0.001)
np.random.seed(42)
N_sim = 100_000
steps = np.random.choice([1, -1], size=(N_sim, n), p=[p_win, p_lose])
sums = steps.sum(axis=1)
p_sim = (sums > 0).mean()

print(f'E[X_i] = {E_X}')
print(f'Var[X_i] = {Var_X:.4f}')
print(f'E[S_1000] = {E_S}')
print(f'Var[S_1000] = {Var_S:.2f}')
print(f'Std[S_1000] = {std_S3:.4f}')
print(f'z = (0 - ({E_S})) / {std_S3:.4f} = {z3:.6f}')
print(f'P(S>0) ЦПТ          = 1 - Phi({z3:.4f}) = {p_clt3:.6f}')
print(f'P(S>0) ЦПТ+поправка = {p_clt3_cont:.6f}')
print(f'P(S>0) симуляция 10^6 = {p_sim:.6f}')
print(f'|ЦПТ - симуляция|   = {abs(p_clt3 - p_sim):.6f}')

