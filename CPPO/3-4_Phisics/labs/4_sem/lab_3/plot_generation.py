from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from calculate_results import fit_all, load_measurements, predict_candidate


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    tex_dir = base_dir / "tex"
    tex_dir.mkdir(exist_ok=True)

    data = load_measurements(base_dir / "measurements_3_07.csv")
    fit = fit_all(data)

    h = data["H_Apm"].to_numpy()
    b = data["B_T"].to_numpy()
    mu = data["mu_r"].to_numpy()

    h_dense = np.linspace(float(h.min()), float(h.max()), 700)

    # Linear interpolation (piecewise linear through measurement points).
    b_interp = interp1d(h, b, kind="linear")
    mu_interp = interp1d(h, mu, kind="linear")

    b_approx = predict_candidate(h_dense, fit.b_best)
    mu_approx = predict_candidate(h_dense, fit.mu_best)

    h_err = 0.02 * h
    b_err = 0.02 * b
    mu_err = 0.03 * mu

    # ----- Figure 1: B(H) -----
    fig_b, ax_b = plt.subplots(figsize=(10, 7), dpi=180)
    ax_b.errorbar(h, b, xerr=h_err, yerr=b_err, fmt="o", ms=4, capsize=2, label="Эксперимент")
    ax_b.plot(h_dense, b_interp(h_dense), "--", lw=1.8, label="Линейная интерполяция")
    ax_b.plot(h_dense, b_approx, lw=2.2, label=f"Аппроксимация: {fit.b_best.label}")
    ax_b.set_title("Кривая намагничивания B(H)")
    ax_b.set_xlabel("H, А/м")
    ax_b.set_ylabel("B, Тл")
    ax_b.grid(True, alpha=0.3)
    ax_b.legend(fontsize=10)
    fig_b.tight_layout()

    out_b = tex_dir / "plot_bh_with_errors.png"
    fig_b.savefig(out_b, bbox_inches="tight")
    plt.close(fig_b)

    # ----- Figure 2: mu(H) -----
    fig_mu, ax_mu = plt.subplots(figsize=(10, 7), dpi=180)
    ax_mu.errorbar(h, mu, xerr=h_err, yerr=mu_err, fmt="o", ms=4, capsize=2, label="Эксперимент")
    ax_mu.plot(h_dense, mu_interp(h_dense), "--", lw=1.8, label="Линейная интерполяция")
    ax_mu.plot(h_dense, mu_approx, lw=2.2, label=f"Аппроксимация: {fit.mu_best.label}")
    if len(fit.mu_best.params) >= 3:
        h_peak = fit.mu_best.params[2]
        ax_mu.axvline(h_peak, color="gray", ls=":", lw=1.2, label=f"$H_{{peak}}={h_peak:.2f}$ А/м")
    ax_mu.set_title("Магнитная проницаемость μ(H)")
    ax_mu.set_xlabel("H, А/м")
    ax_mu.set_ylabel("μ")
    ax_mu.grid(True, alpha=0.3)
    ax_mu.legend(fontsize=10)
    fig_mu.tight_layout()

    out_mu = tex_dir / "plot_mu_with_errors.png"
    fig_mu.savefig(out_mu, bbox_inches="tight")
    plt.close(fig_mu)

    print(f"Saved plot: {out_b}")
    print(f"Saved plot: {out_mu}")


if __name__ == "__main__":
    main()

