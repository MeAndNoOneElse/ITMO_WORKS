import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

EQUATIONS = {
    1: {'name': 'Полином: -1.38x^3 - 5.42x^2 + 2.57x + 10.95',
        'f': lambda x: -1.38*x**3 - 5.42*x**2 + 2.57*x + 10.95,
        'df': lambda x: -4.14*x**2 - 10.84*x + 2.57,
        'd2f': lambda x: -8.28*x - 10.84},
    2: {'name': 'Кубическое: x^3 - 2x - 5',
        'f': lambda x: x**3 - 2*x - 5,
        'df': lambda x: 3*x**2 - 2,
        'd2f': lambda x: 6*x},
    3: {'name': 'Экспоненциальное: e^x - 3x',
        'f': lambda x: math.exp(x) - 3*x,
        'df': lambda x: math.exp(x) - 3,
        'd2f': lambda x: math.exp(x)},
    4: {'name': 'Тригонометрическое: sin(x) - x/2',
        'f': lambda x: math.sin(x) - x/2,
        'df': lambda x: math.cos(x) - 0.5,
        'd2f': lambda x: -math.sin(x)},
    5: {'name': 'Логарифмическое: ln(x) - 1',
        'f': lambda x: math.log(x) - 1 if x > 0 else float('nan'),
        'df': lambda x: 1/x if x > 0 else float('nan'),
        'd2f': lambda x: -1/x**2 if x > 0 else float('nan')}
}

SYSTEMS = {
    1: {'name': 'tan(xy+0.2)=x²; x²+2y²=1',
        'f': lambda x, y: math.tan(x*y + 0.2) - x**2,
        'g': lambda x, y: x**2 + 2*y**2 - 1,
        'fx': lambda x, y: y/(math.cos(x*y+0.2)**2) - 2*x,
        'fy': lambda x, y: x/(math.cos(x*y+0.2)**2),
        'gx': lambda x, y: 2*x, 
        'gy': lambda x, y: 4*y},
    2: {'name': 'sin(x+y)-1.4x=0; x²+y²=1',
        'f': lambda x, y: math.sin(x+y) - 1.4*x,
        'g': lambda x, y: x**2 + y**2 - 1,
        'fx': lambda x, y: math.cos(x+y) - 1.4,
        'fy': lambda x, y: math.cos(x+y),
        'gx': lambda x, y: 2*x, 
        'gy': lambda x, y: 2*y},
    3: {'name': 'x+sin(y)=-0.4; 2y=cos(x+1)',
        'f': lambda x, y: x + math.sin(y) + 0.4,
        'g': lambda x, y: 2*y - math.cos(x+1),
        'fx': lambda x, y: 1, 
        'fy': lambda x, y: math.cos(y),
        'gx': lambda x, y: math.sin(x+1), 
        'gy': lambda x, y: 2}
}

def find_root_intervals(f, search_range=(-10, 10), num_intervals=100):
    a_start, b_start = search_range
    step = (b_start - a_start) / num_intervals
    potential_roots = []
    for i in range(num_intervals):
        a = a_start + i * step
        b = a + step
        try:
            fa, fb = f(a), f(b)
            if not (math.isnan(fa) or math.isinf(fa) or math.isnan(fb) or math.isinf(fb)):
                if fa * fb < 0:
                    potential_roots.append((a, b))
        except:
            pass
    return potential_roots

def get_input(prompt, dtype=float):
    while True:
        try:
            val = input(prompt)
            if not val.strip():
                return None
            return dtype(val)
        except ValueError as e:
            print(f"Ошибка: неверный формат")
        except KeyboardInterrupt:
            return None
        except Exception as e:
            print(f"Ошибка: {e}")

def plot_equation(f, a, b, root, title):
    try:
        width = b - a
        x_min, x_max = a - 2*width, b + 2*width
        x = np.linspace(x_min, x_max, 800)
        
        sample = [abs(f(xi)) for xi in np.linspace(x_min, x_max, 100) 
                  if not (math.isnan(f(xi)) or math.isinf(f(xi))) and abs(f(xi)) < 1e6]
        max_val = max((sorted(sample)[int(0.95*len(sample))] if sample else 10), 10)
        
        y = [f(xi) if not (math.isnan(f(xi)) or math.isinf(f(xi))) and abs(f(xi)) <= max_val else None for xi in x]
        
        valid_x = [xi for xi, yi in zip(x, y) if yi is not None]
        valid_y = [yi for yi in y if yi is not None]
        
        if not valid_x:
            return None
        
        plt.figure(figsize=(16, 9))
        plt.plot(valid_x, valid_y, 'b-', lw=2.5)
        plt.axvline(a, color='green', lw=2, linestyle=':', alpha=0.6)
        plt.axvline(b, color='green', lw=2, linestyle=':', alpha=0.6)
        plt.axvspan(a, b, alpha=0.1, color='green')
        
        if root is not None:
            try:
                f_root = f(root)
                if not math.isnan(f_root) and abs(f_root) <= max_val:
                    plt.plot(root, f_root, 'r*', markersize=35, label=f'x={root:.8f}', zorder=5)
            except:
                pass
        
        plt.axhline(0, color='gray', lw=2, linestyle='--', alpha=0.7)
        plt.grid(True, alpha=0.4)
        plt.xlabel('x', fontsize=13, fontweight='bold')
        plt.ylabel('f(x)', fontsize=13, fontweight='bold')
        plt.title(f'{title}', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        
        filename = f"solution_{int(datetime.now().timestamp())}.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  График: {filename}")
        
        try:
            import subprocess, sys
            if sys.platform == 'win32': os.startfile(os.path.abspath(filename))
            elif sys.platform == 'darwin': subprocess.Popen(['open', os.path.abspath(filename)])
            else: subprocess.Popen(['xdg-open', os.path.abspath(filename)])
        except:
            pass
        plt.close()
        return filename
    except:
        return None

def plot_system(f, g, xr, yr, root, title):
    try:
        x = np.linspace(xr[0], xr[1], 250)
        y = np.linspace(yr[0], yr[1], 250)
        X, Y = np.meshgrid(x, y)
        Z1, Z2 = np.zeros_like(X), np.zeros_like(X)
        
        sample_f, sample_g = [], []
        for xp in np.linspace(xr[0], xr[1], 20):
            for yp in np.linspace(yr[0], yr[1], 20):
                try:
                    vf, vg = f(xp, yp), g(xp, yp)
                    if not (math.isnan(vf) or math.isinf(vf)): sample_f.append(abs(vf))
                    if not (math.isnan(vg) or math.isinf(vg)): sample_g.append(abs(vg))
                except:
                    pass
        
        max_f = max((sorted(sample_f)[int(0.95*len(sample_f))] if sample_f else 5), 5)
        max_g = max((sorted(sample_g)[int(0.95*len(sample_g))] if sample_g else 5), 5)
        
        for i in range(len(x)):
            for j in range(len(y)):
                try:
                    val1, val2 = f(X[j, i], Y[j, i]), g(X[j, i], Y[j, i])
                    Z1[j, i] = np.nan if (math.isnan(val1) or math.isinf(val1) or abs(val1) > max_f) else val1
                    Z2[j, i] = np.nan if (math.isnan(val2) or math.isinf(val2) or abs(val2) > max_g) else val2
                except:
                    Z1[j, i], Z2[j, i] = np.nan, np.nan

        fig, ax = plt.subplots(figsize=(14, 12))
        try:
            ax.contour(X, Y, Z1, levels=[0], colors='blue', linewidths=3)
        except:
            pass
        try:
            ax.contour(X, Y, Z2, levels=[0], colors='red', linewidths=3)
        except:
            pass
        
        if root is not None:
            ax.plot(root[0], root[1], 'g*', markersize=40, zorder=10)
            ax.plot(root[0], root[1], 'g+', markersize=20, markeredgewidth=3, zorder=10)
        
        ax.set_xlabel('x', fontsize=14, fontweight='bold')
        ax.set_ylabel('y', fontsize=14, fontweight='bold')
        ax.set_title(f'{title}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(xr[0], xr[1])
        ax.set_ylim(yr[0], yr[1])
        
        handles = [plt.Line2D([0], [0], color='blue', lw=3, label='f = 0'),
                   plt.Line2D([0], [0], color='red', lw=3, label='g = 0')]
        ax.legend(handles=handles, fontsize=12, loc='best')
        
        plt.tight_layout()
        filename = f"system_{int(datetime.now().timestamp())}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  График: {filename}")
        
        try:
            import subprocess, sys
            if sys.platform == 'win32': os.startfile(os.path.abspath(filename))
            elif sys.platform == 'darwin': subprocess.Popen(['open', os.path.abspath(filename)])
            else: subprocess.Popen(['xdg-open', os.path.abspath(filename)])
        except:
            pass
        plt.close()
        return filename
    except:
        return None

def method_1_bisection(f, a, b, eps=0.01):
    try:
        fa = f(a)
        fb = f(b)
        if math.isnan(fa) or math.isinf(fa):
            return None, [], f"f({a}) = {fa}"
        if math.isnan(fb) or math.isinf(fb):
            return None, [], f"f({b}) = {fb}"
        if fa * fb > 0:
            return None, [], f"Нет смены знака: f({a:.4f})={fa:.4f}, f({b:.4f})={fb:.4f}"
    except Exception as e:
        return None, [], f"Ошибка в функции: {str(e)}"
    
    iterations = []
    count = 0
    while abs(b - a) > eps and count < 200:
        count += 1
        x_mid = (a + b) / 2
        try:
            f_mid = f(x_mid)
            iterations.append({'iter': count, 'x': x_mid, 'f_x': f_mid})
            if f(a) * f_mid < 0:
                b = x_mid
            else:
                a = x_mid
        except Exception as e:
            return None, iterations, f"Ошибка на итерации {count}: {str(e)}"
    
    return (a + b) / 2, iterations, None

def method_3_newton(f, df, d2f, a, b, eps=0.01):
    x0 = a if abs(f(a)) < abs(f(b)) else b
    x = x0
    iterations = []
    count = 0
    
    while count < 200:
        count += 1
        try:
            fx = f(x)
            dfx = df(x)
            
            if math.isnan(fx) or math.isinf(fx):
                return None, iterations, f"f({x}) = {fx}"
            if math.isnan(dfx) or math.isinf(dfx):
                return None, iterations, f"f'({x}) = {dfx}"
            if abs(dfx) < 1e-15:
                return None, iterations, f"Производная близка к нулю: f'({x})={dfx:.2e}"
            
            x_next = x - fx / dfx
            iterations.append({'iter': count, 'x': x_next, 'f_x': f(x_next), 'error': abs(x_next - x)})
            
            if abs(x_next - x) <= eps:
                return x_next, iterations, None
            x = x_next
        except Exception as e:
            return None, iterations, f"Ошибка на итерации {count}: {str(e)}"
    
    return None, iterations, "Превышено итераций"

def method_5_simple_iteration(f, df, a, b, eps=0.01):
    try:
        # Проверяем знак производной на интервале
        f_prime_a = df(a)
        f_prime_b = df(b)
        f_prime_mid = df((a + b) / 2)
        
        if math.isnan(f_prime_a) or math.isinf(f_prime_a):
            return None, [], f"f'({a}) = {f_prime_a}"
        if math.isnan(f_prime_b) or math.isinf(f_prime_b):
            return None, [], f"f'({b}) = {f_prime_b}"
        if math.isnan(f_prime_mid) or math.isinf(f_prime_mid):
            return None, [], f"f'(середина) = {f_prime_mid}"
        
        # Проверяем, одного ли знака производная
        if (f_prime_a * f_prime_b <= 0) or (f_prime_a * f_prime_mid <= 0):
            return None, [], "Производная меняет знак на интервале - метод неприменим"
        
        # Выбираем λ так, чтобы |φ'(x)| = |1 - λ*f'(x)| < 1
        # Если f' одного знака, выбираем λ = 1 / max(|f'|) * 0.9
        q_max = max(abs(f_prime_a), abs(f_prime_b), abs(f_prime_mid))
        
        if q_max == 0:
            return None, [], "Производная равна нулю на интервале"
        
        # Более консервативный выбор λ
        lam = 0.5 / q_max
        
        # Проверка условия сходимости
        phi_prime_max = max(abs(1 - lam * f_prime_a), abs(1 - lam * f_prime_b), abs(1 - lam * f_prime_mid))
        if phi_prime_max >= 1:
            return None, [], f"Условие сходимости не выполнено: max|φ'| = {phi_prime_max:.4f} >= 1"
        
    except Exception as e:
        return None, [], f"Ошибка при анализе производной: {str(e)}"
    
    # Выбираем начальное приближение - точка с меньшей нормой функции
    x0 = a if abs(f(a)) < abs(f(b)) else b
    
    x = x0
    iterations = []
    count = 0
    
    while count < 200:
        count += 1
        try:
            fx = f(x)
            
            if math.isnan(fx) or math.isinf(fx):
                return None, iterations, f"f({x:.6f}) = {fx}"
            
            x_next = x - lam * fx
            
            if math.isnan(x_next) or math.isinf(x_next):
                return None, iterations, f"x_next неопределен: {x_next}"
            
            error = abs(x_next - x)
            iterations.append({'iter': count, 'x': x_next, 'f_x': f(x_next), 'error': error})
            
            if error <= eps:
                return x_next, iterations, None
            x = x_next
        except Exception as e:
            return None, iterations, f"Ошибка на итерации {count}: {str(e)}"
    
    return None, iterations, "Превышено итераций"

def method_7_simple_iteration_sys(f, g, fx, fy, gx, gy, x0, y0, eps=0.01):
    x, y = x0, y0
    iterations = []
    count = 0
    
    try:
        prev_norm = math.sqrt(f(x0, y0)**2 + g(x0, y0)**2)
    except Exception as e:
        return None, [], f"Ошибка функции: {str(e)}"
    
    norm_increase = 0
    
    while count < 200:
        count += 1
        try:
            fv, gv = f(x, y), g(x, y)
            
            if math.isnan(fv) or math.isinf(fv) or math.isnan(gv) or math.isinf(gv):
                return None, iterations, f"NaN/Inf на итерации {count}"
            
            j11, j12 = fx(x, y), fy(x, y)
            j21, j22 = gx(x, y), gy(x, y)
            
            det = j11 * j22 - j12 * j21
            if abs(det) < 1e-15:
                return None, iterations, f"Якобиан вырожден: det(J)={det:.2e}"
            
            x_next = x - (j22 * fv - j12 * gv) / det
            y_next = y - (-j21 * fv + j11 * gv) / det
            
            if abs(x_next) > 1e6 or abs(y_next) > 1e6:
                return None, iterations, f"Переполнение на итерации {count}"
            
            ex, ey = abs(x_next - x), abs(y_next - y)
            norm = math.sqrt(f(x_next, y_next)**2 + g(x_next, y_next)**2)
            
            iterations.append({
                'iter': count, 'x': x_next, 'y': y_next,
                'error_x': ex, 'error_y': ey, 'error_max': max(ex, ey)
            })
            
            if norm > prev_norm:
                norm_increase += 1
            else:
                norm_increase = 0
            
            if norm_increase > 5:
                return None, iterations, f"Расходимость на итерации {count}"
            
            prev_norm = norm
            
            if max(ex, ey) <= eps:
                return (x_next, y_next), iterations, None
            
            x, y = x_next, y_next
        except Exception as e:
            return None, iterations, f"Ошибка на итерации {count}: {str(e)}"
    
    return None, iterations, "Превышено итераций"

def solve_equation():
    print("\nНЕЛИНЕЙНЫЕ УРАВНЕНИЯ\n")
    
    print("Уравнения:")
    for num, data in EQUATIONS.items():
        print(f"  {num}. {data['name']}")
    
    while True:
        try:
            eq = int(input("\nВыбор (1-5): "))
            if eq in EQUATIONS:
                break
            print("Введите 1-5")
        except ValueError:
            print("Ошибка: введите целое число")
    
    eq_data = EQUATIONS[eq]
    f, df, d2f = eq_data['f'], eq_data['df'], eq_data['d2f']
    print(f"\n{eq_data['name']}\n")
    
    intervals = find_root_intervals(f)
    if intervals:
        print(f"1. ИНТЕРВАЛЫ: найдено {len(intervals)}")
        for i, (left, right) in enumerate(intervals[:5], 1):
            print(f"  {i}. [{left:.4f}, {right:.4f}]")
        if input("\nИспользовать? (y/n) ").strip().lower() == 'y':
            while True:
                try:
                    idx = int(input(f"Интервал (1-{min(5, len(intervals))}): ")) - 1
                    if 0 <= idx < min(5, len(intervals)):
                        a, b = intervals[idx]
                        break
                    print(f"Введите число от 1 до {min(5, len(intervals))}")
                except ValueError:
                    print("Ошибка: введите целое число")
        else:
            a = get_input("Левая граница: ")
            b = get_input("Правая граница: ")
    else:
        a = get_input("Левая граница: ")
        b = get_input("Правая граница: ")
    
    if a is None or b is None:
        return
    
    while a >= b:
        print("Ошибка: левая граница должна быть строго меньше правой!")
        a = get_input("Левая граница: ")
        b = get_input("Правая граница: ")
        if a is None or b is None:
            return
    
    print(f"\n2. ТОЧНОСТЬ")
    eps = get_input("ε (умолч. 0.001): ") or 0.001
    
    print(f"\n3. МЕТОД")
    print("  1. Половинного деления")
    print("  3. Ньютона")
    print("  5. Простой итерации")
    while True:
        try:
            method = int(input("\nМетод (1/3/5): "))
            if method in [1, 3, 5]:
                break
            print("Введите 1, 3 или 5")
        except ValueError:
            print("Ошибка: введите целое число")
    
    print(f"\n4. РЕШЕНИЕ")
    if method == 1:
        root, iter, err = method_1_bisection(f, a, b, eps)
    elif method == 3:
        root, iter, err = method_3_newton(f, df, d2f, a, b, eps)
    else:
        root, iter, err = method_5_simple_iteration(f, df, a, b, eps)
    
    if err:
        print(f"Ошибка: {err}")
        return
    
    print(f"\n5. РЕЗУЛЬТАТ")
    print(f"x = {root:.10f}")
    print(f"f(x) = {f(root):.2e}")
    
    print(f"\n6. ИТЕРАЦИИ: {len(iter)}")
    
    print(f"\n7. ТАБЛИЦА")
    print(f"{'Ит':>3} | {'x':>12} | {'f(x)':>10}")
    for it in iter[:20]:
        print(f"{it['iter']:3d} | {it['x']:12.6f} | {it['f_x']:10.2e}")
    if len(iter) > 20:
        print(f"  ... {len(iter)-20} еще")
    
    print(f"\n8. ГРАФИК")
    plot_equation(f, a, b, root, eq_data['name'])
    
    if input("\nСохранить? (y/n) ").strip().lower() == 'y':
        with open('results.txt', 'a', encoding='utf-8') as file:
            file.write(f"Уравнение: {eq_data['name']}\nx={root:.10f}\nf(x)={f(root):.2e}\nИтераций: {len(iter)}\n\n")

def solve_system():
    print("\nСИСТЕМЫ УРАВНЕНИЙ\n")
    
    print("Системы:")
    for num, data in SYSTEMS.items():
        print(f"  {num}. {data['name']}")
    
    while True:
        try:
            sys_num = int(input("\nВыбор (1-3): "))
            if sys_num in SYSTEMS:
                break
            print("Введите 1, 2 или 3")
        except ValueError:
            print("Ошибка: введите целое число")
    
    sys_data = SYSTEMS[sys_num]
    f, g = sys_data['f'], sys_data['g']
    fx, fy = sys_data['fx'], sys_data['fy']
    gx, gy = sys_data['gx'], sys_data['gy']
    print(f"\n{sys_data['name']}\n")
    
    print("1. ГРАФИК")
    plot_system(f, g, (-2.5, 2.5), (-2.5, 2.5), None, sys_data['name'])
    
    print("\n2. НАЧАЛЬНЫЕ ПРИБЛИЖЕНИЯ")
    x0 = get_input("x₀ = ")
    y0 = get_input("y₀ = ")
    eps = get_input("ε (умолч. 0.001) = ") or 0.001
    
    if x0 is None or y0 is None:
        return
    
    print(f"\n3. ПРОВЕРКА")
    try:
        dist = math.sqrt(f(x0, y0)**2 + g(x0, y0)**2)
        print(f"||F(x₀)|| = {dist:.6f}")
        if dist > 1.0 and input("Продолжить? (y/n) ").strip().lower() != 'y':
            return
    except:
        print("Ошибка функции")
        return
    
    print(f"\n4. ЯКОБИАН")
    try:
        j11, j12 = fx(x0, y0), fy(x0, y0)
        j21, j22 = gx(x0, y0), gy(x0, y0)
        print(f"J = | {j11:7.4f}  {j12:7.4f} |")
        print(f"    | {j21:7.4f}  {j22:7.4f} |")
        det = j11*j22 - j12*j21
        print(f"det(J) = {det:.6f}")
        if abs(det) < 1e-10:
            print("Якобиан вырожден!")
            return
    except:
        print("Ошибка")
    
    print(f"\n5. РЕШЕНИЕ")
    root, iter, err = method_7_simple_iteration_sys(f, g, fx, fy, gx, gy, x0, y0, eps)
    
    if err:
        print(f"Ошибка: {err}")
        return
    
    x, y = root
    print(f"\n6. ВЕКТОР НЕИЗВЕСТНЫХ")
    print(f"x₁ = {x:.10f}")
    print(f"x₂ = {y:.10f}")
    
    fv, gv = f(x, y), g(x, y)
    print(f"\n7. ПРОВЕРКА РЕШЕНИЯ")
    print(f"f(x,y) = {fv:.2e}")
    print(f"g(x,y) = {gv:.2e}")
    
    print(f"\n8. ИТЕРАЦИИ: {len(iter)}")
    print(f"Погрешности:")
    print(f"{'Ит':>3} | {'x':>12} | {'y':>12} | {'|Δx|':>10} | {'|Δy|':>10}")
    for it in iter:
        print(f"{it['iter']:3d} | {it['x']:12.6f} | {it['y']:12.6f} | {it['error_x']:10.2e} | {it['error_y']:10.2e}")
    
    print(f"\n9. ГРАФИК РЕШЕНИЯ")
    plot_system(f, g, (-2.5, 2.5), (-2.5, 2.5), root, sys_data['name'])
    
    if input("\nСохранить? (y/n) ").strip().lower() == 'y':
        with open('results.txt', 'a', encoding='utf-8') as file:
            file.write(f"Система: {sys_data['name']}\nx₁={x:.10f}\nx₂={y:.10f}\nИтераций: {len(iter)}\n\n")

def main():
    while True:
        print("\n" + "="*40)
        print("ЧИСЛЕННЫЕ МЕТОДЫ")
        print("="*40)
        print("\n1. Уравнение")
        print("2. Система")
        print("3. Выход")
        
        choice = input("\nВыбор (1/2/3): ").strip()
        
        if choice == "1":
            solve_equation()
        elif choice == "2":
            solve_system()
        elif choice == "3":
            print("\nДо свидания!")
            break
        else:
            print("Ошибка: введите 1, 2 или 3")

if __name__ == "__main__":
    main()
