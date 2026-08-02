from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

MU0 = 4 * np.pi * 1e-7


@dataclass
class FitMetrics:
    r2: float
    rmse: float
    aic: float
    rss: float


@dataclass
class FitCandidate:
    family: str
    model_id: str
    label: str
    params: list[float]
    param_names: list[str]
    metrics: FitMetrics


@dataclass
class FitResults:
    b_best: FitCandidate
    mu_best: FitCandidate
    b_all: list[FitCandidate]
    mu_all: list[FitCandidate]
    mu_max_exp: float
    h_at_mu_max_exp: float


def load_measurements(csv_path: Path) -> pd.DataFrame:
    """Load CSV with Russian decimal comma and normalize core columns."""
    raw = pd.read_csv(csv_path, sep=";", decimal=",", engine="python")

    # Keep measured/calculated columns from the table and use stable internal names.
    data = raw.iloc[:, :8].copy()
    data.columns = [
        "U_V",
        "X_mV",
        "Kx_V_div",
        "H_Apm",
        "Y_div_mV",
        "Ky_V_div",
        "B_T",
        "mu_r",
    ]

    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["H_Apm", "B_T", "mu_r"]).sort_values("H_Apm")
    return data.reset_index(drop=True)


def b_model(h: np.ndarray, bs: float, h0: float) -> np.ndarray:
    """Saturation model for ferromagnet initial magnetization curve."""
    return bs * np.tanh(h / h0)


def b_model_exp(h: np.ndarray, bs: float, h0: float) -> np.ndarray:
    """Monotonic saturation model with exponential approach to Bs."""
    return bs * (1.0 - np.exp(-h / h0))


def b_model_frac(h: np.ndarray, bs: float, h0: float) -> np.ndarray:
    """Rational saturation model: linear in weak field, saturates for large H."""
    return bs * h / (h + h0)


def mu_model(h: np.ndarray, mu_inf: float, mu_amp: float, h_peak: float) -> np.ndarray:
    """Phenomenological model with a permeability maximum near H=h_peak."""
    x = np.maximum(h, 1e-9) / h_peak
    return mu_inf + mu_amp * x * np.exp(1.0 - x)


def mu_model_lognorm(h: np.ndarray, mu_inf: float, mu_amp: float, h_peak: float, sigma: float) -> np.ndarray:
    """Log-normal shaped peak around h_peak with long-tail decay in strong fields."""
    x = np.maximum(h, 1e-9) / h_peak
    z = np.log(x)
    return mu_inf + mu_amp * np.exp(-(z**2) / (2.0 * sigma**2))


def mu_model_lorentz(h: np.ndarray, mu_inf: float, mu_amp: float, h_peak: float, width: float) -> np.ndarray:
    """Lorentz-like peak, used as a simple alternative phenomenological model."""
    z = (h - h_peak) / np.maximum(width, 1e-9)
    return mu_inf + mu_amp / (1.0 + z**2)


def metrics(y_true: np.ndarray, y_pred: np.ndarray, k_params: int) -> FitMetrics:
    residual = y_true - y_pred
    rmse = float(np.sqrt(np.mean(residual**2)))
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    n = len(y_true)
    aic = float(n * np.log(np.maximum(ss_res / n, 1e-18)) + 2 * k_params)
    return FitMetrics(r2=r2, rmse=rmse, aic=aic, rss=ss_res)


def fit_candidate(
    family: str,
    model_id: str,
    label: str,
    func: Callable[..., np.ndarray],
    param_names: list[str],
    p0: list[float],
    bounds: tuple[list[float], list[float]],
    h: np.ndarray,
    y: np.ndarray,
) -> FitCandidate:
    popt, _ = curve_fit(func, h, y, p0=p0, bounds=bounds, maxfev=100000)
    y_fit = func(h, *popt)
    cand_metrics = metrics(y, y_fit, len(popt))
    return FitCandidate(
        family=family,
        model_id=model_id,
        label=label,
        params=[float(v) for v in popt],
        param_names=param_names,
        metrics=cand_metrics,
    )


def choose_best(candidates: list[FitCandidate]) -> FitCandidate:
    ordered = sorted(candidates, key=lambda c: c.metrics.aic)
    best = ordered[0]
    if len(ordered) == 1:
        return best

    # If AIC scores are almost equal, prefer the simpler model.
    if ordered[1].metrics.aic - best.metrics.aic < 2.0:
        alt = min(ordered[:2], key=lambda c: len(c.params))
        return alt
    return best


def fit_all(data: pd.DataFrame) -> FitResults:
    h = data["H_Apm"].to_numpy()
    b = data["B_T"].to_numpy()
    mu = data["mu_r"].to_numpy()

    b_candidates = [
        fit_candidate(
            family="B(H)",
            model_id="tanh",
            label="B = Bs * tanh(H/H0)",
            func=b_model,
            param_names=["Bs", "H0"],
            p0=[float(np.max(b)), float(np.median(h))],
            bounds=([0.0, 1e-6], [1.0, 1e4]),
            h=h,
            y=b,
        ),
        fit_candidate(
            family="B(H)",
            model_id="exp_sat",
            label="B = Bs * (1 - exp(-H/H0))",
            func=b_model_exp,
            param_names=["Bs", "H0"],
            p0=[float(np.max(b)), float(np.median(h))],
            bounds=([0.0, 1e-6], [1.0, 1e4]),
            h=h,
            y=b,
        ),
        fit_candidate(
            family="B(H)",
            model_id="rational_sat",
            label="B = Bs * H / (H + H0)",
            func=b_model_frac,
            param_names=["Bs", "H0"],
            p0=[float(np.max(b)), float(np.median(h))],
            bounds=([0.0, 1e-6], [1.0, 1e4]),
            h=h,
            y=b,
        ),
    ]

    mu_candidates = [
        fit_candidate(
            family="mu(H)",
            model_id="gamma_peak",
            label="mu = mu_inf + A*x*exp(1-x)",
            func=mu_model,
            param_names=["mu_inf", "A", "H_peak"],
            p0=[float(np.min(mu)), float(np.max(mu) - np.min(mu)), float(h[np.argmax(mu)])],
            bounds=([0.0, 0.0, 1e-6], [5000.0, 5000.0, 500.0]),
            h=h,
            y=mu,
        ),
        fit_candidate(
            family="mu(H)",
            model_id="lognorm_peak",
            label="mu = mu_inf + A*exp(-(ln(H/Hp))^2/(2*sigma^2))",
            func=mu_model_lognorm,
            param_names=["mu_inf", "A", "H_peak", "sigma"],
            p0=[float(np.min(mu)), float(np.max(mu) - np.min(mu)), float(h[np.argmax(mu)]), 0.7],
            bounds=([0.0, 0.0, 1e-6, 0.1], [5000.0, 5000.0, 500.0, 3.0]),
            h=h,
            y=mu,
        ),
        fit_candidate(
            family="mu(H)",
            model_id="lorentz_peak",
            label="mu = mu_inf + A/(1 + ((H-Hp)/w)^2)",
            func=mu_model_lorentz,
            param_names=["mu_inf", "A", "H_peak", "width"],
            p0=[float(np.min(mu)), float(np.max(mu) - np.min(mu)), float(h[np.argmax(mu)]), 8.0],
            bounds=([0.0, 0.0, 1e-6, 0.1], [5000.0, 5000.0, 500.0, 500.0]),
            h=h,
            y=mu,
        ),
    ]

    # User-selected working model for B(H): exponential saturation.
    b_best = next(c for c in b_candidates if c.model_id == "exp_sat")
    mu_best = choose_best(mu_candidates)

    mu_max_exp_idx = int(np.argmax(mu))

    return FitResults(
        b_best=b_best,
        mu_best=mu_best,
        b_all=b_candidates,
        mu_all=mu_candidates,
        mu_max_exp=float(mu[mu_max_exp_idx]),
        h_at_mu_max_exp=float(h[mu_max_exp_idx]),
    )


def predict_candidate(h: np.ndarray, candidate: FitCandidate) -> np.ndarray:
    if candidate.family == "B(H)":
        if candidate.model_id == "tanh":
            return b_model(h, *candidate.params)
        if candidate.model_id == "exp_sat":
            return b_model_exp(h, *candidate.params)
        return b_model_frac(h, *candidate.params)

    if candidate.model_id == "gamma_peak":
        return mu_model(h, *candidate.params)
    if candidate.model_id == "lognorm_peak":
        return mu_model_lognorm(h, *candidate.params)
    return mu_model_lorentz(h, *candidate.params)


def candidates_to_df(candidates: list[FitCandidate]) -> pd.DataFrame:
    rows = []
    for c in candidates:
        row = {
            "family": c.family,
            "model_id": c.model_id,
            "label": c.label,
            "r2": c.metrics.r2,
            "rmse": c.metrics.rmse,
            "aic": c.metrics.aic,
            "rss": c.metrics.rss,
        }
        for key, val in zip(c.param_names, c.params):
            row[key] = val
        rows.append(row)
    return pd.DataFrame(rows)


def save_results(results: FitResults, base_dir: Path) -> None:
    b_df = candidates_to_df(results.b_all).sort_values("aic")
    mu_df = candidates_to_df(results.mu_all).sort_values("aic")
    b_df.to_csv(base_dir / "fit_compare_B_3_07.csv", index=False)
    mu_df.to_csv(base_dir / "fit_compare_mu_3_07.csv", index=False)

    mu_max_fit = float(np.max(predict_candidate(np.linspace(0.35, 96.69, 2000), results.mu_best)))
    summary = pd.DataFrame(
        {
            "parameter": [
                "B_best_model",
                "B_best_R2",
                "B_best_RMSE",
                "B_best_AIC",
                "mu_best_model",
                "mu_best_R2",
                "mu_best_RMSE",
                "mu_best_AIC",
                "mu_fit_max",
                "mu_exp_max",
                "H_at_mu_exp_max_Apm",
            ],
            "value": [
                results.b_best.label,
                results.b_best.metrics.r2,
                results.b_best.metrics.rmse,
                results.b_best.metrics.aic,
                results.mu_best.label,
                results.mu_best.metrics.r2,
                results.mu_best.metrics.rmse,
                results.mu_best.metrics.aic,
                mu_max_fit,
                results.mu_max_exp,
                results.h_at_mu_max_exp,
            ],
        }
    )
    summary.to_csv(base_dir / "fit_results_3_07.csv", index=False)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_measurements(base_dir / "measurements_3_07.csv")
    results = fit_all(data)

    save_results(results, base_dir)

    print("=== Fit results for lab 3.07 ===")
    print(f"Best B(H) model: {results.b_best.label}")
    print(f"  params = {results.b_best.params}")
    print(
        f"  R^2 = {results.b_best.metrics.r2:.6f}, "
        f"RMSE = {results.b_best.metrics.rmse:.6f}, AIC = {results.b_best.metrics.aic:.3f}"
    )
    print(f"Best mu(H) model: {results.mu_best.label}")
    print(f"  params = {results.mu_best.params}")
    print(
        f"  R^2 = {results.mu_best.metrics.r2:.6f}, "
        f"RMSE = {results.mu_best.metrics.rmse:.6f}, AIC = {results.mu_best.metrics.aic:.3f}"
    )
    print(f"Saved: {base_dir / 'fit_results_3_07.csv'}")
    print(f"Saved: {base_dir / 'fit_compare_B_3_07.csv'}")
    print(f"Saved: {base_dir / 'fit_compare_mu_3_07.csv'}")


if __name__ == "__main__":
    main()

