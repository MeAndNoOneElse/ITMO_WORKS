"""
Лабораторная работа 3.05
Температурная зависимость электрического сопротивления металла и полупроводника
Скрипт для обработки данных и построения графиков
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import t as t_dist

# =====================================================================
# Данные измерений
# =====================================================================

# --- Полупроводник ---
T_sc = np.array([293, 298, 301, 304, 307, 310, 313, 316, 319, 322,
                 325, 328, 331, 334, 337, 340, 343, 346, 349, 352, 355])  # K
I_sc = np.array([1039, 1090, 1220, 1260, 1330, 1383, 1443, 1503, 1549, 1588,
                 1637, 1680, 1720, 1750, 1780, 1808, 1834, 1862, 1882, 1900, 1918])  # мкА
U_sc = np.array([0.715, 0.715, 0.58, 0.54, 0.50, 0.470, 0.420, 0.387, 0.359, 0.333,
                 0.295, 0.270, 0.247, 0.228, 0.206, 0.188, 0.171, 0.153, 0.141, 0.129, 0.116])  # В

# --- Металл ---
T_m = np.array([295, 298, 301, 304, 307, 310, 313, 316, 319, 322,
                325, 328, 331, 334, 337, 340, 343, 346, 349, 352, 355])  # K
I_m = np.array([846, 842, 837, 831, 826, 821, 816, 811, 805, 801,
                796, 791, 786, 781, 776, 769, 766, 762, 757, 752, 747])  # мкА
U_m = np.array([0.966, 0.970, 0.974, 0.978, 0.982, 0.987, 0.991, 0.995, 0.999, 1.003,
                1.006, 1.010, 1.014, 1.018, 1.022, 1.025, 1.030, 1.033, 1.037, 1.041, 1.045])  # В

# =====================================================================
# Погрешности приборов
# =====================================================================
# Амперметр: класс точности 0.5, предел 2000 мкА => delta_I = 0.5/100 * 2000 = 10 мкА
# Вольтметр: класс точности 0.5, предел 2 В => delta_U = 0.5/100 * 2 = 0.01 В
# Термометр: delta_T = 1 K (цена деления)

delta_I = 10.0   # мкА
delta_U = 0.01   # В
delta_T = 1.0    # K

# =====================================================================
# Расчёт сопротивлений
# =====================================================================
R_sc = U_sc / I_sc * 1e6   # Ом (I в мкА -> делим на 1e6, потом умножаем)
R_m  = U_m  / I_m  * 1e6   # Ом

t_m = T_m - 273.15          # Цельсий

# Погрешность R = U/I => dR/R = sqrt((dU/U)^2 + (dI/I)^2)
dR_sc = R_sc * np.sqrt((delta_U / U_sc)**2 + (delta_I / I_sc)**2)
dR_m  = R_m  * np.sqrt((delta_U / U_m )**2 + (delta_I / I_m )**2)

# =====================================================================
# Полупроводник: ln(R) от 1/T
# =====================================================================
lnR_sc  = np.log(R_sc)
inv_T_sc = 1.0 / T_sc          # 1/K
inv_T_sc_1000 = 1e3 / T_sc     # 10^3/K

dlnR_sc  = dR_sc / R_sc
dinvT_sc = delta_T / T_sc**2   # погрешность 1/T

# =====================================================================
# Метод пар: ширина запрещённой зоны Eg
# =====================================================================
k_B = 1.380649e-23  # Дж/К
eV  = 1.60218e-19   # Дж/эВ

n = len(T_sc)
half = n // 2
Eg_vals = []

print("=== МЕТОД ПАР: ПОЛУПРОВОДНИК ===")
for i in range(half):
    j = i + half
    Eg_ij = 2 * k_B * (lnR_sc[i] - lnR_sc[j]) / (1/T_sc[i] - 1/T_sc[j])
    Eg_vals.append(Eg_ij)
    print(f"  Пара ({i+1:2d},{j+1:2d}): Eg = {Eg_ij:.4e} Дж = {Eg_ij/eV:.4f} эВ")

Eg_arr  = np.array(Eg_vals)
Eg_mean = np.mean(Eg_arr)
Eg_std  = np.std(Eg_arr, ddof=1)
Eg_sem  = Eg_std / np.sqrt(half)

# Доверительный интервал (t-критерий, 95%, n=half)
t_crit = t_dist.ppf(0.975, df=half - 1)
Eg_conf = t_crit * Eg_sem

print(f"\n<Eg> = {Eg_mean:.4e} Дж  =  {Eg_mean/eV:.4f} эВ")
print(f"σEg  = {Eg_std:.4e} Дж  =  {Eg_std/eV:.4f} эВ")
print(f"ΔEg  = {Eg_conf:.4e} Дж  =  {Eg_conf/eV:.4f} эВ  (95%, t={t_crit:.2f})")

# Линейная аппроксимация ln(R) = a + b*(1/T)  =>  b = Eg/(2k)
coeffs_sc, cov_sc = np.polyfit(inv_T_sc, lnR_sc, 1, cov=True)
b_sc, a_sc = coeffs_sc
db_sc = np.sqrt(cov_sc[0, 0])
Eg_fit     = 2 * k_B * b_sc
dEg_fit    = 2 * k_B * db_sc
print(f"\nМНК-аппроксимация: b = {b_sc:.1f} ± {db_sc:.1f}")
print(f"Eg (МНК) = {Eg_fit:.4e} Дж = {Eg_fit/eV:.4f} эВ ± {dEg_fit/eV:.4f} эВ")

# =====================================================================
# Металл: метод пар, alpha
# =====================================================================
n_m  = len(T_m)
half_m = n_m // 2
alpha_vals = []

print("\n=== МЕТОД ПАР: МЕТАЛЛ ===")
for i in range(half_m):
    j = i + half_m
    denom = R_m[j]*t_m[i] - R_m[i]*t_m[j]
    alpha_ij = (R_m[i] - R_m[j]) / denom
    alpha_vals.append(alpha_ij)
    print(f"  Пара ({i+1:2d},{j+1:2d}): α = {alpha_ij:.6e} °C⁻¹")

alpha_arr  = np.array(alpha_vals)
alpha_mean = np.mean(alpha_arr)
alpha_std  = np.std(alpha_arr, ddof=1)
alpha_sem  = alpha_std / np.sqrt(half_m)
t_crit_m   = t_dist.ppf(0.975, df=half_m - 1)
alpha_conf = t_crit_m * alpha_sem

print(f"\n<α> = {alpha_mean:.5e} °C⁻¹")
print(f"σα  = {alpha_std:.5e} °C⁻¹")
print(f"Δα  = {alpha_conf:.5e} °C⁻¹  (95%, t={t_crit_m:.2f})")

# R0 через МНК: R = R0 + R0*alpha*t  =>  линейная R(t)
coeffs_m, cov_m = np.polyfit(t_m, R_m, 1, cov=True)
slope_m, R0_fit = coeffs_m
alpha_fit = slope_m / R0_fit
print(f"\nМНК: R0 = {R0_fit:.2f} Ом, slope = {slope_m:.4f} Ом/°C")
print(f"α (МНК) = {alpha_fit:.5e} °C⁻¹")

# =====================================================================
# ПЕЧАТЬ ТАБЛИЦ
# =====================================================================
print("\n=== ТАБЛИЦА: ПОЛУПРОВОДНИК ===")
print(f"{'№':>3} {'T,K':>5} {'I,мкА':>7} {'U,В':>7} {'R,Ом':>9} {'dR,Ом':>8} {'lnR':>8} {'1000/T':>8}")
for i in range(len(T_sc)):
    print(f"{i+1:3d} {T_sc[i]:5d} {I_sc[i]:7d} {U_sc[i]:7.3f} {R_sc[i]:9.2f} {dR_sc[i]:8.2f} {lnR_sc[i]:8.4f} {inv_T_sc_1000[i]:8.4f}")

print("\n=== ТАБЛИЦА: МЕТАЛЛ ===")
print(f"{'№':>3} {'T,K':>5} {'t,°C':>7} {'I,мкА':>7} {'U,В':>7} {'R,Ом':>10} {'dR,Ом':>8}")
for i in range(len(T_m)):
    print(f"{i+1:3d} {T_m[i]:5d} {t_m[i]:7.2f} {I_m[i]:7d} {U_m[i]:7.3f} {R_m[i]:10.3f} {dR_m[i]:8.3f}")

# =====================================================================
# ГРАФИКИ
# =====================================================================
plt.rcParams.update({
    'font.size': 12,
    'axes.grid': True,
    'grid.alpha': 0.4,
    'figure.dpi': 150,
})
out_dir = r'C:\Users\Eternal_Core\OneDrive - MSFT\github_file\PythonProject\ФИЗИКА\lab_2\tex'

# -------  График 1: ln(R) vs 1000/T  (полупроводник)  ---------------
fig1, ax1 = plt.subplots(figsize=(8, 5))

x_fit = np.linspace(inv_T_sc.min(), inv_T_sc.max(), 200)
y_fit = b_sc * x_fit + a_sc
y_fit_1000 = b_sc * (x_fit * 1e3 / 1e3) + a_sc   # same but for display

ax1.errorbar(inv_T_sc_1000, lnR_sc,
             xerr=dinvT_sc * 1e3,
             yerr=dlnR_sc,
             fmt='o', color='steelblue', markersize=5,
             ecolor='steelblue', elinewidth=1, capsize=3,
             label='Экспериментальные данные')

# fit line (x in 1/K units, plot in 1000/K)
x_fit_1000 = np.linspace(inv_T_sc_1000.min(), inv_T_sc_1000.max(), 200)
y_fit_line = b_sc * (x_fit_1000 / 1e3) + a_sc
ax1.plot(x_fit_1000, y_fit_line, 'r-', linewidth=1.5,
         label=f'МНК: $E_g = {Eg_fit/eV:.3f}$ эВ')

ax1.set_xlabel(r'$10^3/T$, К$^{-1}$', fontsize=13)
ax1.set_ylabel(r'$\ln R$', fontsize=13)
ax1.set_title('Зависимость $\\ln R$ от $10^3/T$ (полупроводник)', fontsize=13)
ax1.legend()
fig1.tight_layout()
fig1.savefig(f'{out_dir}\\plot_semiconductor.png', bbox_inches='tight')
print(f"\nСохранён: plot_semiconductor.png")

# -------  График 2: R(t)  (металл)  ---------------------------------
fig2, ax2 = plt.subplots(figsize=(8, 5))

t_fit = np.linspace(t_m.min() - 2, t_m.max() + 2, 200)
R_fit = R0_fit + slope_m * t_fit

ax2.errorbar(t_m, R_m,
             xerr=delta_T,
             yerr=dR_m,
             fmt='o', color='tomato', markersize=5,
             ecolor='tomato', elinewidth=1, capsize=3,
             label='Экспериментальные данные')
ax2.plot(t_fit, R_fit, 'b-', linewidth=1.5,
         label=f'МНК: $\\alpha = {alpha_fit:.4f}$ °C$^{{-1}}$')

ax2.set_xlabel(r'$t$, °C', fontsize=13)
ax2.set_ylabel(r'$R$, Ом', fontsize=13)
ax2.set_title('Зависимость $R(t)$ (металл)', fontsize=13)
ax2.legend()
fig2.tight_layout()
fig2.savefig(f'{out_dir}\\plot_metal.png', bbox_inches='tight')
print(f"Сохранён: plot_metal.png")

plt.close('all')
print("\n=== ИТОГОВЫЕ РЕЗУЛЬТАТЫ ===")
print(f"Ширина запрещённой зоны:")
print(f"  Eg (метод пар) = ({Eg_mean/eV:.3f} ± {Eg_conf/eV:.3f}) эВ")
print(f"  Eg (МНК)       = ({Eg_fit/eV:.3f} ± {dEg_fit/eV:.3f}) эВ")
print(f"\nТемпературный коэффициент сопротивления металла:")
print(f"  α (метод пар) = ({alpha_mean*1e3:.4f} ± {alpha_conf*1e3:.4f}) × 10⁻³ °C⁻¹")
print(f"  α (МНК)       = {alpha_fit*1e3:.4f} × 10⁻³ °C⁻¹")
print(f"\nПо справочным данным:")
print(f"  Германий (Ge): Eg ≈ 0.67 эВ")
print(f"  Кремний  (Si): Eg ≈ 1.12 эВ")
print(f"  Никель  (Ni): α ≈ 6.0×10⁻³ °C⁻¹")
print(f"  Медь    (Cu): α ≈ 4.3×10⁻³ °C⁻¹")
print(f"  Алюминий(Al): α ≈ 4.0×10⁻³ °C⁻¹")
print(f"  Вольфрам (W): α ≈ 4.5×10⁻³ °C⁻¹")

