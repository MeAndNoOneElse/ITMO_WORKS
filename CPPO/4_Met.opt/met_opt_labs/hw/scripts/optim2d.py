"""Optimizers and visualization for 2D homework (Block 2, variant 12)

Provides:
- CoordinateDescent
- GradientDescent (with backtracking Armijo)
- SteepestDescent (exact line search along -grad using scalar minimization)
- NewtonMethod (for DZ2.2)
- plotting utilities: contour + polyline where contour levels pass through iterates
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar


@dataclass
class Result2D:
    xs: List[Tuple[float,float]]
    fs: List[float]


def z_func(xy: np.ndarray) -> float:
    x, y = xy
    return x**3 - 15*x**2 + 72*x + y**3 + y**2 - y - 113


def grad_z(xy: np.ndarray) -> np.ndarray:
    x, y = xy
    gx = 3*x**2 - 30*x + 72
    gy = 3*y**2 + 2*y - 1
    return np.array([gx, gy])


def hess_z(xy: np.ndarray) -> np.ndarray:
    x, y = xy
    hxx = 6*x - 30
    hxy = 0.0
    hyy = 6*y + 2
    return np.array([[hxx, hxy], [hxy, hyy]])


def coordinate_descent(x0: Tuple[float,float], eps: float=1e-4, maxiter:int=100) -> Result2D:
    x = np.array(x0, dtype=float)
    xs = [tuple(x)]
    fs = [z_func(x)]

    for k in range(maxiter):
        fx_prev = z_func(x)

        # optimize x while y fixed (with smaller bounds to prevent divergence)
        def phi_x(t):
            val = z_func(np.array([t, x[1]]))
            if np.isnan(val) or np.isinf(val):
                return 1e10
            return val
        try:
            # tight bounds to prevent divergence
            resx = minimize_scalar(phi_x, bounds=(x[0]-2, x[0]+2), method='bounded')
            x_new = resx.x
            # check if result is reasonable
            if abs(x_new - x[0]) > 3:  # if jumped too far, reject
                x_new = x[0]
        except:
            x_new = x[0]

        x[0] = x_new

        # optimize y while x fixed
        def phi_y(t):
            val = z_func(np.array([x[0], t]))
            if np.isnan(val) or np.isinf(val):
                return 1e10
            return val
        try:
            resy = minimize_scalar(phi_y, bounds=(x[1]-2, x[1]+2), method='bounded')
            y_new = resy.x
            if abs(y_new - x[1]) > 3:  # if jumped too far, reject
                y_new = x[1]
        except:
            y_new = x[1]
        
        x[1] = y_new
        fx_curr = z_func(x)

        # check if we're making progress; if not, stop
        xs.append(tuple(x))
        fs.append(fx_curr)

        if np.linalg.norm(np.array(xs[-1]) - np.array(xs[-2])) < eps:
            break

        # safety: if function value explodes, stop
        if fx_curr > 1e10:
            break

    return Result2D(xs, fs)


def gradient_descent(x0: Tuple[float,float], eps: float=1e-4, maxiter:int=200, alpha0:float=0.1) -> Result2D:
    x = np.array(x0, dtype=float)
    xs=[tuple(x)]; fs=[z_func(x)]
    for k in range(maxiter):
        g = grad_z(x)
        if np.linalg.norm(g) < eps:
            break
        # backtracking Armijo with step bounds
        alpha = alpha0
        c = 1e-4
        rho = 0.5
        fx = z_func(x)
        for _ in range(100):  # max line search iterations
            x_new = x - alpha*g
            fx_new = z_func(x_new)
            if np.isnan(fx_new) or np.isinf(fx_new):
                alpha *= rho
                continue
            if fx_new <= fx - c*alpha*np.dot(g,g):
                break
            alpha *= rho
            if alpha < 1e-12:
                break
        x = x - alpha*g
        xs.append(tuple(x)); fs.append(z_func(x))
        if np.linalg.norm(np.array(xs[-1]) - np.array(xs[-2])) < eps:
            break
    return Result2D(xs, fs)


def steepest_descent(x0: Tuple[float,float], eps: float=1e-4, maxiter:int=200) -> Result2D:
    x = np.array(x0, dtype=float)
    xs=[tuple(x)]; fs=[z_func(x)]
    for k in range(maxiter):
        g = grad_z(x)
        if np.linalg.norm(g) < eps:
            break
        # exact line search along direction d = -g with bounds
        def phi(alpha):
            val = z_func(x - alpha*g)
            if np.isnan(val) or np.isinf(val):
                return 1e10
            return val
        try:
            res = minimize_scalar(phi, bounds=(0, 10), method='bounded')
            alpha = max(res.x, 1e-12)
        except:
            alpha = 0.01
        x = x - alpha*g
        xs.append(tuple(x)); fs.append(z_func(x))
        if np.linalg.norm(np.array(xs[-1]) - np.array(xs[-2])) < eps:
            break
    return Result2D(xs, fs)


def newton_method(x0: Tuple[float,float], eps: float=1e-4, maxiter:int=50) -> Result2D:
    x = np.array(x0, dtype=float)
    xs=[tuple(x)]; fs=[z_func(x)]
    H = hess_z(x)
    for k in range(maxiter):
        g = grad_z(x)
        if np.linalg.norm(g) < eps:
            break
        dx = np.linalg.solve(H, g)
        x = x - dx
        xs.append(tuple(x)); fs.append(z_func(x))
    return Result2D(xs, fs)


def plot_contours_with_path(res: Result2D, name: str, out_dir: Path, target: Tuple[float, float] = None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    xs = np.array([p[0] for p in res.xs])
    ys = np.array([p[1] for p in res.xs])
    
    # fixed viewing region
    x_min, x_max = 5.4, 6.4
    y_min, y_max = 0.0, 0.7
    
    # grid with higher resolution
    xg = np.linspace(x_min, x_max, 250)
    yg = np.linspace(y_min, y_max, 250)
    X, Y = np.meshgrid(xg, yg)
    Z = X**3 - 15*X**2 + 72*X + Y**3 + Y**2 - Y - 113
    
    # create figure with more space
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # filled contours (light background) + regular contours
    levels = np.linspace(np.min(Z), np.max(Z), 30)
    CS_fill = ax.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.4)
    CS = ax.contour(X, Y, Z, levels=levels[::2], colors='gray', linewidths=0.5, alpha=0.5)
    
    # highlight contour lines through iterates for better visibility
    iterate_levels = sorted(set(res.fs[:min(len(res.fs), 16)]))
    if iterate_levels and len(iterate_levels) > 1:
        CS_iter = ax.contour(X, Y, Z, levels=iterate_levels, colors='black', linewidths=0.7, alpha=0.7)

    # plot path with thinner line and smaller markers
    ax.plot(xs, ys, 'r-', linewidth=1.2, alpha=0.8, label='Path of iterations')
    ax.scatter(xs, ys, c=np.arange(len(xs)), cmap='Reds', s=40, edgecolors='darkred',
               linewidth=0.5, zorder=5, label='Iterations')
    
    # annotate each iteration with its number
    for i, (xv, yv) in enumerate(res.xs):
        ax.text(xv + 0.015, yv + 0.015, f'{i}', fontsize=7, fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='red', alpha=0.6))
    
    # mark target/theoretical minimum with large star
    if target:
        ax.scatter([target[0]], [target[1]], c='blue', marker='*', s=400, edgecolors='darkblue', 
                   linewidth=1, zorder=10, label=f'Target: ({target[0]}, {target[1]})')
    
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title(f'{name}: All {len(xs)} iterations', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    plt.savefig(out_dir / f'{name}.png', dpi=150)
    plt.close()


if __name__ == '__main__':
    out = Path(__file__).resolve().parent.parent / 'figures'
    cd = coordinate_descent((-2,5))
    plot_contours_with_path(cd, 'coordinate_descent', out)
    gd = gradient_descent((-2,5))
    plot_contours_with_path(gd, 'gradient_descent', out)
    sd = steepest_descent((-2,5))
    plot_contours_with_path(sd, 'steepest_descent', out)
    new = newton_method((-2,5))
    plot_contours_with_path(new, 'newton_method', out)
    print('Done. Figures saved to', out)
