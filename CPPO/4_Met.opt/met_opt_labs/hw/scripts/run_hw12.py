"""Runner script to produce results and figures for HW variant 12.

Generates:
- figures/cubic_iter_*.png (1D cubic approximation iterations)
- figures/coordinate_descent.png, gradient_descent.png, steepest_descent.png, newton_method.png

And writes a small JSON/YAML summary (optional) for embedding into LaTeX.
"""
from pathlib import Path
import json
from hw.scripts import cubic_approx as ca  # type: ignore
from hw.scripts import optim2d as o2  # type: ignore


def main():
    base = Path(__file__).resolve().parent.parent
    figures = base / 'figures'
    figures.mkdir(exist_ok=True)

    print('Running 1D cubic approximation...')
    seq = ca.cubic_approx(a=-1.0, b=0.0, eps=1e-4, out_dir=figures)
    print('Sequence:', seq)

    print('Running 2D optimizers...')
    target = (6.0, 1.0/3.0)  # theoretical local minimum
    cd = o2.coordinate_descent((5.5, 0.5))
    o2.plot_contours_with_path(cd, 'coordinate_descent', figures, target=target)
    gd = o2.gradient_descent((5.5, 0.5))
    o2.plot_contours_with_path(gd, 'gradient_descent', figures, target=target)
    sd = o2.steepest_descent((5.5, 0.5))
    o2.plot_contours_with_path(sd, 'steepest_descent', figures, target=target)
    new = o2.newton_method((5.5, 0.5))
    o2.plot_contours_with_path(new, 'newton_method', figures, target=target)

    summary = {
        'cubic_sequence': seq,
        'coordinate_iters': len(cd.xs),
        'gradient_iters': len(gd.xs),
        'steepest_iters': len(sd.xs),
        'newton_iters': len(new.xs),
        'newton_result': new.xs[-1]
    }
    (base / 'figures' / 'summary.json').write_text(json.dumps(summary, indent=2))
    print('Done. Figures and summary saved to', figures)


if __name__ == '__main__':
    main()
