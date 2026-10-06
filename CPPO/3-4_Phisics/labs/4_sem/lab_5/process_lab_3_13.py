from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


MU0 = 4.0 * math.pi * 1e-7
N_TURNS = 100
R_COIL_M = 0.15

# NOAA WMM/IGRF typical horizontal field for Saint Petersburg is about 16.5 uT.
B_HORIZONTAL_REF_UT = 16.5

# Two-sided 95% Student t critical values for small samples.
T95_BY_DOF = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.080,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.060,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
}


@dataclass
class FitResult:
    slope: float
    intercept: float
    slope_se: float
    intercept_se: float
    r2: float
    ci95_low: float
    ci95_high: float


@dataclass
class FitThroughOriginResult:
    slope: float
    slope_se: float
    r2_like: float
    ci95_low: float
    ci95_high: float


def _to_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", ".", regex=False).str.strip(),
        errors="coerce",
    )


def _t95(dof: int) -> float:
    if dof <= 0:
        return float("nan")
    if dof in T95_BY_DOF:
        return T95_BY_DOF[dof]
    return 1.96


def load_measurements(csv_path: Path) -> tuple[pd.DataFrame, str]:
    raw = pd.read_csv(csv_path, sep=";")
    out = pd.DataFrame()

    out["alpha_raw_deg"] = _to_float_series(raw["α_i"])
    out["i1_mA"] = _to_float_series(raw["I1 мА"])
    out["i2_mA"] = _to_float_series(raw["I2"])
    out["i_avg_mA"] = _to_float_series(raw["<I>"])

    # If <I> is missing, reconstruct it from repeated measurements.
    out["i_avg_mA"] = out["i_avg_mA"].fillna((out["i1_mA"] + out["i2_mA"]) / 2.0)

    alpha_raw = out["alpha_raw_deg"].to_numpy(dtype=float)

    # In this file alpha is recorded as compass azimuth values (around 250...110).
    # Convert it to the protocol deflection series: alpha_i = 250 - alpha_raw
    alpha_from_raw = 250.0 - alpha_raw
    out["alpha_deg"] = alpha_from_raw
    alpha_mode = "250_minus_raw"

    return out.dropna().reset_index(drop=True), alpha_mode


def estimate_phi_deg(alpha_deg: np.ndarray, bc_uT: np.ndarray) -> float:
    max_alpha = float(np.max(alpha_deg))
    phi_candidates = np.linspace(max(max_alpha + 5.0, 120.0), 179.0, 700)

    best_phi = float("nan")
    best_sse = float("inf")
    for phi in phi_candidates:
        denom = np.sin(np.deg2rad(phi - alpha_deg))
        if np.any(np.isclose(denom, 0.0, atol=1e-9)):
            continue
        gamma = np.sin(np.deg2rad(alpha_deg)) / denom
        if not np.all(np.isfinite(gamma)):
            continue

        slope, intercept = np.polyfit(gamma, bc_uT, deg=1)
        pred = slope * gamma + intercept
        sse = float(np.sum((bc_uT - pred) ** 2))

        if sse < best_sse:
            best_sse = sse
            best_phi = float(phi)

    if not np.isfinite(best_phi):
        raise RuntimeError("Could not estimate phi from measurements")

    return best_phi


def fit_line(x: np.ndarray, y: np.ndarray) -> FitResult:
    n = len(x)
    slope, intercept = np.polyfit(x, y, deg=1)
    pred = slope * x + intercept

    sse = float(np.sum((y - pred) ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")

    dof = n - 2
    s2 = sse / dof
    sxx = float(np.sum((x - np.mean(x)) ** 2))

    slope_se = math.sqrt(s2 / sxx)
    intercept_se = math.sqrt(s2 * (1.0 / n + (np.mean(x) ** 2) / sxx))

    t95 = _t95(dof)
    ci95_low = slope - t95 * slope_se
    ci95_high = slope + t95 * slope_se

    return FitResult(
        slope=float(slope),
        intercept=float(intercept),
        slope_se=float(slope_se),
        intercept_se=float(intercept_se),
        r2=float(r2),
        ci95_low=float(ci95_low),
        ci95_high=float(ci95_high),
    )


def fit_through_origin(x: np.ndarray, y: np.ndarray) -> FitThroughOriginResult:
    n = len(x)
    slope = float(np.divide(np.sum(x * y), np.sum(x**2)))
    pred = slope * x

    sse = float(np.sum((y - pred) ** 2))
    sst0 = float(np.sum(y**2))
    r2_like = 1.0 - sse / sst0 if sst0 > 0 else float("nan")

    dof = n - 1
    s2 = sse / dof
    slope_se = math.sqrt(s2 / float(np.sum(x**2)))

    t95 = _t95(dof)
    ci95_low = slope - t95 * slope_se
    ci95_high = slope + t95 * slope_se

    return FitThroughOriginResult(
        slope=slope,
        slope_se=float(slope_se),
        r2_like=float(r2_like),
        ci95_low=float(ci95_low),
        ci95_high=float(ci95_high),
    )


def build_plots(df: pd.DataFrame, fit: FitResult, fit0: FitThroughOriginResult, tex_dir: Path) -> None:
    tex_dir.mkdir(parents=True, exist_ok=True)

    fig1, ax1 = plt.subplots(figsize=(9, 5.5), dpi=180)
    ax1.plot(df["alpha_deg"], df["i_avg_mA"], "o-", lw=1.4, ms=4)
    ax1.set_xlabel("alpha, deg")
    ax1.set_ylabel("<I>, mA")
    ax1.grid(alpha=0.3)
    fig1.tight_layout()
    fig1.savefig(tex_dir / "plot_current_vs_alpha_3_13.png", bbox_inches="tight")
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(9, 5.5), dpi=180)
    ax2.plot(df["alpha_deg"], df["bc_uT"], "o-", lw=1.4, ms=4)
    ax2.set_xlabel("alpha, deg")
    ax2.set_ylabel("Bc, uT")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(tex_dir / "plot_bc_vs_alpha_3_13.png", bbox_inches="tight")
    plt.close(fig2)

    x = df["gamma"].to_numpy()
    y = df["bc_uT"].to_numpy()
    x_line = np.linspace(float(np.min(x)) * 0.95, float(np.max(x)) * 1.05, 300)

    fig3, ax3 = plt.subplots(figsize=(9, 5.5), dpi=180)
    ax3.scatter(x, y, s=28, label="experiment")
    ax3.plot(x_line, fit.slope * x_line + fit.intercept, "r-", lw=1.8, label="OLS: y = kx + b")
    ax3.plot(x_line, fit0.slope * x_line, "k--", lw=1.5, label="fit through origin")
    ax3.set_xlabel("gamma = sin(alpha)/sin(phi-alpha)")
    ax3.set_ylabel("Bc, uT")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(tex_dir / "plot_bc_vs_gamma_3_13.png", bbox_inches="tight")
    plt.close(fig3)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "lab_3_13_measurments.csv"
    tex_dir = base_dir / "tex"

    df, alpha_mode = load_measurements(csv_path)

    # In the protocol the working series starts from 10°; the raw 250° row is a zero-deflection control check.
    df = df[df["alpha_deg"] > 0].reset_index(drop=True)
    alpha_mode = f"{alpha_mode}; working_alpha_gt_0"

    # Helmholtz coil magnetic field (formula (5)/(9) from the methodical guide).
    df["bc_uT"] = MU0 * (4.0 / 5.0) ** 1.5 * N_TURNS * (df["i_avg_mA"] / 1000.0) / R_COIL_M * 1e6

    # The setup angle is taken from the alignment instruction in the methodical guide (~160°).
    phi_deg = 160.0
    df["gamma"] = np.sin(np.deg2rad(df["alpha_deg"])) / np.sin(np.deg2rad(phi_deg - df["alpha_deg"]))

    fit = fit_line(df["gamma"].to_numpy(), df["bc_uT"].to_numpy())
    fit0 = fit_through_origin(df["gamma"].to_numpy(), df["bc_uT"].to_numpy())

    delta_vs_ref_pct = abs(fit.slope - B_HORIZONTAL_REF_UT) / B_HORIZONTAL_REF_UT * 100.0

    processed_path = base_dir / "measurements_3_13_processed.csv"
    df.to_csv(processed_path, index=False)

    summary = pd.DataFrame(
        {
            "metric": [
                "alpha_mode",
                "n_points",
                "phi_effective_deg",
                "bh_fit_uT",
                "bh_fit_se_uT",
                "bh_fit_ci95_low_uT",
                "bh_fit_ci95_high_uT",
                "fit_intercept_uT",
                "fit_r2",
                "bh_fit0_uT",
                "bh_fit0_se_uT",
                "bh_fit0_ci95_low_uT",
                "bh_fit0_ci95_high_uT",
                "fit0_r2_like",
                "bh_ref_uT",
                "delta_vs_ref_percent",
            ],
            "value": [
                alpha_mode,
                len(df),
                phi_deg,
                fit.slope,
                fit.slope_se,
                fit.ci95_low,
                fit.ci95_high,
                fit.intercept,
                fit.r2,
                fit0.slope,
                fit0.slope_se,
                fit0.ci95_low,
                fit0.ci95_high,
                fit0.r2_like,
                B_HORIZONTAL_REF_UT,
                delta_vs_ref_pct,
            ],
        }
    )
    summary_path = base_dir / "summary_3_13.csv"
    summary.to_csv(summary_path, index=False)

    build_plots(df, fit, fit0, tex_dir)

    print("Saved:")
    print(f" - {processed_path}")
    print(f" - {summary_path}")
    print(f" - {tex_dir / 'plot_current_vs_alpha_3_13.png'}")
    print(f" - {tex_dir / 'plot_bc_vs_alpha_3_13.png'}")
    print(f" - {tex_dir / 'plot_bc_vs_gamma_3_13.png'}")
    print()
    print(f"Estimated phi = {phi_deg:.3f} deg")
    print(f"Bh (OLS) = {fit.slope:.3f} +/- {fit.slope_se:.3f} uT (95% CI: {fit.ci95_low:.3f}..{fit.ci95_high:.3f}), b={fit.intercept:.3f}, R^2={fit.r2:.4f}")
    print(f"Bh (through origin) = {fit0.slope:.3f} +/- {fit0.slope_se:.3f} uT (95% CI: {fit0.ci95_low:.3f}..{fit0.ci95_high:.3f})")


if __name__ == "__main__":
    main()

