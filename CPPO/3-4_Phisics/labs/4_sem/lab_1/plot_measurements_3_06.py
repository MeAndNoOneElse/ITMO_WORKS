from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "measurements_3_06.csv"
OUTPUT_PATH = BASE_DIR / "tex" / "epsilon_interp_approx.png"


def _to_float(value: str) -> float:
    return float(value.strip().replace(",", "."))


def load_measurements(csv_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs: list[float] = []
    ys: list[float] = []
    eps: list[float] = []

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader, None)
        for row in reader:
            if not row or len(row) < 9 or not row[0].strip().isdigit():
                continue
            xs.append(_to_float(row[6]))
            eps.append(_to_float(row[8]))
            ys.append(_to_float(row[7]))

    return np.asarray(xs, dtype=float), np.asarray(eps, dtype=float), np.asarray(ys, dtype=float)


def group_by_x(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grouped: dict[float, list[float]] = defaultdict(list)
    for xi, yi in zip(x, y):
        grouped[float(xi)].append(float(yi))

    xs = np.array(sorted(grouped.keys()), dtype=float)
    ys = np.array([np.mean(grouped[xi]) for xi in xs], dtype=float)
    return xs, ys


def build_plot(x: np.ndarray, eps: np.ndarray, output_path: Path) -> None:
    # Exclude the leftmost point on the plot (minimum E) by user request.
    leftmost_idx = int(np.argmin(x))
    x = np.delete(x, leftmost_idx)
    eps = np.delete(eps, leftmost_idx)

    xs, ys = group_by_x(x, eps)
    if len(xs) < 4:
        raise ValueError("Need at least 4 unique points for 3rd-degree approximation.")

    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]

    dense_x = np.linspace(xs.min(), xs.max(), 600)
    interp_y = np.interp(dense_x, xs, ys)

    degree = 3
    scale = 1e8
    coeffs = np.polyfit(xs / scale, ys, degree)
    approx_y = np.polyval(coeffs, dense_x / scale)

    max_idx = int(np.argmax(eps))
    max_x = float(x[max_idx])
    max_y = float(eps[max_idx])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, eps, s=35, color="#1f77b4", label="Экспериментальные точки", zorder=3)
    ax.plot(dense_x, interp_y, color="#d62728", linewidth=2.2, label="Интерполяция (линейная)")
    ax.plot(dense_x, approx_y, color="#2ca02c", linewidth=2.2, linestyle="--", label=f"Аппроксимация (полином {degree}-й степени)")
    ax.scatter([max_x], [max_y], s=80, color="gold", edgecolor="black", zorder=4, label=f"Максимум: {max_y:.6f}")

    ax.set_title("Зависимость ε(E) по данным измерений")
    ax.set_xlabel("E, В/м")
    ax.set_ylabel("ε")
    ax.grid(True, which="both", linestyle=":", linewidth=0.8, alpha=0.8)
    ax.legend(loc="best", fontsize=9)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved plot to: {output_path}")
    print(f"Loaded {len(x)} measurements, unique x values: {len(xs)}")
    print(f"Maximum ε = {max_y:.9f} at E = {max_x:.1f}")
    print("Polynomial coefficients (highest degree first):")
    print(coeffs)


def main() -> None:
    x, eps, _y = load_measurements(CSV_PATH)
    build_plot(x, eps, OUTPUT_PATH)


if __name__ == "__main__":
    main()

