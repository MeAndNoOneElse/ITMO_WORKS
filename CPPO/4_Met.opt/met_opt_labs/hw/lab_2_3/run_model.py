from .model import Function2D, CoordinateDescent, GradientDescent, SteepestDescent
import numpy as np
from pathlib import Path
import json

def f(xy):
    x, y = xy
    return x**3 - 15*x**2 + 72*x + y**3 + y**2 - y - 113

def grad(xy):
    x, y = xy
    return np.array([3*x**2 - 30*x + 72, 3*y**2 + 2*y - 1])

def main():
    base = Path(__file__).resolve().parent
    figures = base.parent / 'figures'
    figures.mkdir(exist_ok=True)
    func = Function2D(f, grad)
    x0 = (5.5, 0.5)
    cd = CoordinateDescent(func, x0, eps=1e-4, maxiter=200).optimize()
    gd = GradientDescent(func, x0, eps=1e-4, maxiter=200).optimize()
    sd = SteepestDescent(func, x0, eps=1e-4, maxiter=200).optimize()
    res = {
        'coordinate_iters': len(cd.xs),
        'gradient_iters': len(gd.xs),
        'steepest_iters': len(sd.xs),
        'coordinate_last': cd.xs[-1],
        'gradient_last': gd.xs[-1],
        'steepest_last': sd.xs[-1]
    }
    (base / 'results_model.json').write_text(json.dumps(res, indent=2))

if __name__ == '__main__':
    main()


