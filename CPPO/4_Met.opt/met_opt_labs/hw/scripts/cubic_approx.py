"""Cubic approximation method for 1D optimization (HW Block 1, variant 12)

Function: f(x) = x^4 + x^2 + x + 1 on [a,b] = [-1,0]

Algorithm (practical implementation):
- At each iteration take 4 sample points in current interval [a,b]
- Fit cubic polynomial through them (np.polyfit degree 3)
- Find stationary points (roots of derivative) and pick real root inside [a,b]
- That root is the next approximation x_k
- Stop when |x_{k} - x_{k-1}| < eps

Produces per-iteration plots and returns the sequence of approximations.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from typing import List


def f(x: np.ndarray) -> np.ndarray:
    return x**4 + x**2 + x + 1


def cubic_step(a: float, b: float):
    xs = np.linspace(a, b, 4)
    ys = f(xs)
    coeffs = np.polyfit(xs, ys, 3)
    # derivative coefficients (degree 2)
    dcoeffs = np.polyder(coeffs)
    roots = np.roots(dcoeffs)
    # select real roots within (a,b)
    candidates = [r.real for r in roots if abs(r.imag) < 1e-8 and a <= r.real <= b]
    if not candidates:
        return None, coeffs, xs, ys
    # pick candidate with minimal f
    vals = [(c, f(np.array([c]))[0]) for c in candidates]
    vals.sort(key=lambda t: t[1])
    return vals[0][0], coeffs, xs, ys


def cubic_approx(a: float = -1.0, b: float = 0.0, eps: float = 1e-4, maxiter: int = 50,
                 out_dir: Path = Path("../figures")) -> List[float]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seq = []
    x_prev = None
    iter_data = []  # store for combined plot
    a_orig, b_orig = a, b
    
    for k in range(maxiter):
        res = cubic_step(a, b)
        xk, coeffs, xs, ys = res
        if xk is None:
            xk = 0.5 * (a + b)
        seq.append(xk)
        
        # store for combined plot
        xx = np.linspace(a, b, 400)
        cub_y = np.polyval(coeffs, xx)
        iter_data.append({
            'xx': xx, 'cub_y': cub_y, 'xs': xs, 'ys': ys, 'xk': xk, 'k': k,
            'a': a, 'b': b, 'coeffs': coeffs
        })

        # plot individual iteration (optional, for reference)
        # plt.figure(figsize=(6,4))
        # plt.plot(xx, f(xx), label='f(x)')
        # plt.plot(xx, cub_y, '--', label='cubic approx')
        # plt.scatter(xs, ys, c='red', label='sample points')
        # plt.axvline(xk, color='green', linestyle=':', label=f'approx x_{k}={xk:.6f}')
        # plt.title(f'Iteration {k}: x={xk:.6f}')
        # plt.legend()
        # plt.xlabel('x')
        # plt.ylabel('y')
        # plt.grid(True)
        # plt.tight_layout()
        # plt.savefig(out_dir / f'cubic_iter_{k:02d}.png')
        # plt.close()

        if x_prev is not None and abs(xk - x_prev) < eps:
            break
        x_prev = xk
        width = max(1e-6, (b - a) / 4)
        a = max(a, xk - width)
        b = min(b, xk + width)

    # create combined 2x2 plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, data in enumerate(iter_data[:4]):
        ax = axes[idx]
        xx = data['xx']
        xx_full = np.linspace(a_orig, b_orig, 400)
        
        ax.plot(xx_full, f(xx_full), 'b-', linewidth=2, label='f(x)')
        ax.plot(xx, data['cub_y'], 'r--', linewidth=1.5, label='cubic approx')
        ax.scatter(data['xs'], data['ys'], c='orange', s=50, zorder=5, label='sample points')
        ax.axvline(data['xk'], color='green', linestyle=':', linewidth=1.5, 
                   label=f'$x_{data["k"]}={data["xk"]:.5f}$')
        ax.set_title(f'Iteration {data["k"]}: $x_{data["k"]}={data["xk"]:.5f}$', fontsize=10)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_xlim(a_orig - 0.1, b_orig + 0.1)
    
    plt.suptitle('Cubic Approximation Method: All Iterations', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / 'cubic_combined.png', dpi=150)
    plt.close()

    return seq


if __name__ == '__main__':
    out = Path(__file__).resolve().parent.parent / 'figures'
    seq = cubic_approx(out_dir=out)
    print('Approximations:', seq)
