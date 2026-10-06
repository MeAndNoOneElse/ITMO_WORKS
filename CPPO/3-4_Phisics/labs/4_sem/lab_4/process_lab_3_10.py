from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd


@dataclass
class CapacitorBlock:
    name: str
    c_f: float
    l_nominal_h: float
    data: pd.DataFrame
    rm_critical_ohm: float | None = None


def _to_float(value: str) -> float:
    return float(value.strip().replace(",", "."))


def parse_measurements(csv_path: Path) -> list[CapacitorBlock]:
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    blocks: list[CapacitorBlock] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip().lstrip("\ufeff")
        if not line:
            i += 1
            continue

        header = re.match(r"^[сc](\d+)\s*=\s*;([^;]+);L\s*=\s*;([^;]+)", line)
        if not header:
            i += 1
            continue

        block_name = f"c{header.group(1)}"
        c_f = _to_float(header.group(2))
        l_nominal_h = _to_float(header.group(3))

        # Skip table header row: Rm;T;2U_i;2U_i+1;n
        i += 2

        rows: list[dict[str, float]] = []
        rm_critical_ohm: float | None = None

        while i < len(lines):
            raw = lines[i].strip()
            if not raw:
                break
            if raw.lower().startswith(("с", "c")):
                i -= 1
                break

            parts = [p.strip() for p in raw.split(";")]
            if len(parts) < 5:
                i += 1
                continue

            if len(parts) >= 2 and "крит" in parts[1].lower():
                rm_critical_ohm = _to_float(parts[0])
                i += 1
                continue

            rows.append(
                {
                    "Rm_ohm": _to_float(parts[0]),
                    "T_s": _to_float(parts[1]),
                    "U2_i_div": _to_float(parts[2]),
                    "U2_i_plus_n_div": _to_float(parts[3]),
                    "n": _to_float(parts[4]),
                }
            )
            i += 1

        df = pd.DataFrame(rows)
        if df.empty:
            raise ValueError(f"No numeric measurements found for {block_name}")

        blocks.append(
            CapacitorBlock(
                name=block_name,
                c_f=c_f,
                l_nominal_h=l_nominal_h,
                data=df,
                rm_critical_ohm=rm_critical_ohm,
            )
        )
        i += 1

    if not blocks:
        raise ValueError("No capacitor blocks found in CSV")
    return blocks


def add_basic_derived(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["T_period_s"] = out["T_s"] / out["n"]
    ratio = out["U2_i_div"] / out["U2_i_plus_n_div"]
    out["lambda"] = np.log(ratio) / out["n"]
    out["Q"] = math.pi / out["lambda"]
    return out


def fit_lambda_linear(df: pd.DataFrame) -> tuple[float, float]:
    part = df[df["Rm_ohm"] <= 100.0]
    mask = np.isfinite(part["Rm_ohm"].to_numpy()) & np.isfinite(part["lambda"].to_numpy())
    x = part.loc[mask, "Rm_ohm"].to_numpy()
    y = part.loc[mask, "lambda"].to_numpy()
    if len(x) < 2:
        raise ValueError("Not enough finite points for lambda(Rm) linear fit on Rm<=100")
    k, b = np.polyfit(x, y, deg=1)
    return float(k), float(b)


def fit_q_inverse_r(df: pd.DataFrame) -> float:
    """Least-squares fit for model Q(R) = A / R on measured c1 data."""
    r = df["R_total_ohm"].to_numpy()
    q = df["Q"].to_numpy()
    numerator = float(np.sum(q / r))
    denominator = float(np.sum(1.0 / (r**2)))
    return numerator / denominator


def compute_l_and_r_for_c1(df_c1: pd.DataFrame, c1_f: float, r0_ohm: float) -> tuple[pd.DataFrame, float, float]:
    out = df_c1.copy()
    out["R_total_ohm"] = out["Rm_ohm"] + r0_ohm
    out["L_h"] = np.nan

    small_r = out["Rm_ohm"] <= 100.0
    l_values = c1_f * (math.pi * out.loc[small_r, "R_total_ohm"] / out.loc[small_r, "lambda"]) ** 2
    out.loc[small_r, "L_h"] = l_values

    l_avg = float(np.nanmean(out["L_h"]))
    l_sem = float(np.nanstd(out["L_h"], ddof=1) / np.sqrt(np.sum(np.isfinite(out["L_h"]))))
    return out, l_avg, l_sem


def theoretical_period(l_h: float, c_f: float, r_total_ohm: float) -> float:
    inside = 1.0 / (l_h * c_f) - (r_total_ohm**2) / (4.0 * l_h**2)
    if inside <= 0:
        return float("nan")
    return 2.0 * math.pi / math.sqrt(inside)


def make_plots(
    blocks_map: dict[str, CapacitorBlock],
    c1_df: pd.DataFrame,
    fit_k: float,
    fit_b: float,
    l_avg_h: float,
    r0_ohm: float,
    q_fit_a: float,
    tex_dir: Path,
) -> None:
    tex_dir.mkdir(parents=True, exist_ok=True)

    # Plot 1: lambda(Rm) for all capacitors with linear fits on full range for each block.
    fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=180)
    for name, block in blocks_map.items():
        data = add_basic_derived(block.data)
        line, = ax1.plot(
            data["Rm_ohm"],
            data["lambda"],
            "o-",
            ms=4,
            lw=0.9,
            alpha=0.55,
            label=f"{name}, C={block.c_f * 1e6:.3g} uF",
            zorder=2,
        )

        fit_mask = np.isfinite(data["Rm_ohm"].to_numpy()) & np.isfinite(data["lambda"].to_numpy())
        fit_part = data.loc[fit_mask, ["Rm_ohm", "lambda"]]
        if len(fit_part) < 2:
            continue

        k_i, b_i = np.polyfit(fit_part["Rm_ohm"].to_numpy(), fit_part["lambda"].to_numpy(), deg=1)

        x_fit = np.linspace(float(fit_part["Rm_ohm"].min()), float(fit_part["Rm_ohm"].max()), 150)
        y_fit = k_i * x_fit + b_i
        fit_line, = ax1.plot(
            x_fit,
            y_fit,
            "--",
            lw=2.4,
            color=line.get_color(),
            label=f"fit {name}: lambda={k_i:.5f}*Rm+{b_i:.3f}",
            zorder=4,
        )
        # White stroke keeps fit visible even when colors overlap or lines coincide.
        fit_line.set_path_effects([pe.Stroke(linewidth=3.6, foreground="white"), pe.Normal()])

    ax1.set_xlabel("Rm, ohm")
    ax1.set_ylabel("lambda")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=9)
    fig1.tight_layout()
    fig1.savefig(tex_dir / "plot_lambda_vs_rm.png", bbox_inches="tight")
    plt.close(fig1)

    # Plot 2: Q(R) for c1.
    fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=180)
    ax2.plot(c1_df["R_total_ohm"], c1_df["Q"], "o", ms=4, label="experiment")

    r_grid = np.linspace(float(c1_df["R_total_ohm"].min()), float(c1_df["R_total_ohm"].max()), 250)
    q_fit = q_fit_a / r_grid
    ax2.plot(r_grid, q_fit, "r--", lw=2.0, label=f"fit: Q={q_fit_a:.1f}/R")

    ax2.set_xlabel("R_total, ohm")
    ax2.set_ylabel("Q")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=9)
    fig2.tight_layout()
    fig2.savefig(tex_dir / "plot_q_vs_r_total.png", bbox_inches="tight")
    plt.close(fig2)

    # Plot 3: Texp(C) and Ttheory(C) for Rm=0.
    c_values = []
    t_exp_ms = []
    t_theory_ms = []
    for _, block in sorted(blocks_map.items(), key=lambda kv: kv[1].c_f):
        row0 = block.data.loc[block.data["Rm_ohm"] == 0.0].iloc[0]
        t_exp = float(row0["T_s"] / row0["n"])
        t_theory = theoretical_period(l_avg_h, block.c_f, r0_ohm)
        c_values.append(block.c_f * 1e6)
        t_exp_ms.append(t_exp * 1e3)
        t_theory_ms.append(t_theory * 1e3)

    fig3, ax3 = plt.subplots(figsize=(10, 6), dpi=180)
    ax3.plot(c_values, t_exp_ms, "o-", lw=1.4, label="Texp")
    ax3.plot(c_values, t_theory_ms, "s--", lw=1.4, label="Ttheory")
    ax3.set_xlabel("C, uF")
    ax3.set_ylabel("T, ms")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(tex_dir / "plot_period_vs_c.png", bbox_inches="tight")
    plt.close(fig3)

    # Plot 4: schematic reconstructed U(t) for c1 at several Rm values.
    fig4, ax4 = plt.subplots(figsize=(10, 6), dpi=180)
    for rm in [0.0, 200.0, 400.0]:
        row = c1_df.loc[c1_df["Rm_ohm"] == rm].iloc[0]
        t_period = float(row["T_period_s"])
        lam = float(row["lambda"])
        u0 = float(row["U2_i_div"]) / 2.0
        beta = lam / t_period
        omega_d = 2.0 * math.pi / t_period
        t = np.linspace(0.0, 8.0 * t_period, 1400)
        u = u0 * np.exp(-beta * t) * np.cos(omega_d * t)
        ax4.plot(t * 1e3, u, lw=1.8, label=f"Rm={int(rm)} ohm")

    ax4.set_xlabel("t, ms")
    ax4.set_ylabel("U, div")
    ax4.grid(alpha=0.3)
    ax4.legend()
    fig4.tight_layout()
    fig4.savefig(tex_dir / "plot_u_t_reconstructed_c1.png", bbox_inches="tight")
    plt.close(fig4)

    # Plot 5: schematic U(t) and I(t) with phase shift for one moderate damping mode.
    rm_for_ui = 40.0
    row_ui = c1_df.loc[c1_df["Rm_ohm"] == rm_for_ui].iloc[0]
    t_period = float(row_ui["T_period_s"])
    lam = float(row_ui["lambda"])
    c1_f = float(blocks_map["c1"].c_f)

    beta = lam / t_period
    omega0 = 1.0 / math.sqrt(l_avg_h * c1_f)
    omega_d = math.sqrt(max(omega0**2 - beta**2, 1e-12))
    cos_delta = -beta / omega0
    sin_delta = omega_d / omega0
    delta = math.atan2(sin_delta, cos_delta)

    t = np.linspace(0.0, 8.0 * t_period, 1600)
    envelope = np.exp(-beta * t)
    u_norm = envelope * np.cos(omega_d * t)
    i_norm = envelope * np.cos(omega_d * t + delta)

    fig5, ax5 = plt.subplots(figsize=(10, 6), dpi=180)
    ax5.plot(t * 1e3, u_norm, lw=2.0, label="U/U0")
    ax5.plot(t * 1e3, i_norm, lw=2.0, label="I/I0")
    ax5.plot(t * 1e3, envelope, "k--", lw=1.2, alpha=0.8, label="exp(-beta t)")
    ax5.plot(t * 1e3, -envelope, "k--", lw=1.2, alpha=0.8)
    ax5.set_xlabel("t, ms")
    ax5.set_ylabel("normalized amplitude")
    ax5.grid(alpha=0.3)
    ax5.legend()
    fig5.tight_layout()
    fig5.savefig(tex_dir / "plot_ui_t_reconstructed_c1.png", bbox_inches="tight")
    plt.close(fig5)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "measurements_3_10.csv"
    tex_dir = base_dir / "tex"

    blocks = parse_measurements(csv_path)
    blocks_map = {b.name: b for b in blocks}

    # Compute lambda and Q for all blocks and save extended tables.
    derived_map: dict[str, pd.DataFrame] = {}
    for block in blocks:
        derived = add_basic_derived(block.data)
        derived_map[block.name] = derived
        derived.to_csv(base_dir / f"measurements_3_10_{block.name}_processed.csv", index=False)

    c1 = blocks_map["c1"]
    c1_df = derived_map["c1"]

    fit_k, fit_b = fit_lambda_linear(c1_df)
    rm_at_lambda0 = -fit_b / fit_k
    r0_ohm = -rm_at_lambda0

    c1_df, l_avg_h, l_sem_h = compute_l_and_r_for_c1(c1_df, c1.c_f, r0_ohm)
    derived_map["c1"] = c1_df
    c1_df.to_csv(base_dir / "measurements_3_10_c1_processed.csv", index=False)

    q_fit_a = fit_q_inverse_r(c1_df)

    # Compare measured and theoretical periods for c1 at selected Rm.
    selected_rm = [0.0, 200.0, 400.0]
    period_compare_rows: list[dict[str, float]] = []
    for rm in selected_rm:
        row = c1_df.loc[c1_df["Rm_ohm"] == rm].iloc[0]
        r_total = float(row["R_total_ohm"])
        t_exp_s = float(row["T_period_s"])
        t_theor_s = theoretical_period(l_avg_h, c1.c_f, r_total)
        period_compare_rows.append(
            {
                "Rm_ohm": rm,
                "R_total_ohm": r_total,
                "T_exp_ms": t_exp_s * 1e3,
                "T_theory_ms": t_theor_s * 1e3,
                "delta_percent": abs(t_exp_s - t_theor_s) / t_theor_s * 100.0,
            }
        )

    period_compare_df = pd.DataFrame(period_compare_rows)
    period_compare_df.to_csv(base_dir / "period_compare_c1_3_10.csv", index=False)

    # Table 2 values for each C at Rm=0.
    table2_rows: list[dict[str, float]] = []
    for block in sorted(blocks, key=lambda b: b.c_f):
        row0 = block.data.loc[block.data["Rm_ohm"] == 0.0].iloc[0]
        t_exp_s = float(row0["T_s"] / row0["n"])
        t_theor_s = theoretical_period(l_avg_h, block.c_f, r0_ohm)
        table2_rows.append(
            {
                "block": block.name,
                "C_uF": block.c_f * 1e6,
                "T_exp_ms": t_exp_s * 1e3,
                "T_theory_ms": t_theor_s * 1e3,
                "delta_percent": abs(t_exp_s - t_theor_s) / t_theor_s * 100.0,
            }
        )

    table2_df = pd.DataFrame(table2_rows)
    table2_df.to_csv(base_dir / "table2_3_10.csv", index=False)

    r_crit_theory_c1 = 2.0 * math.sqrt(l_avg_h / c1.c_f)

    # There is an explicit critical Rm marker only in c4 block in the source table.
    c4 = blocks_map.get("c4")
    r_crit_exp_total: float | None = None
    r_crit_theory_c4: float | None = None
    if c4 is not None:
        r_crit_theory_c4 = 2.0 * math.sqrt(l_avg_h / c4.c_f)
    if c4 is not None and c4.rm_critical_ohm is not None:
        r_crit_exp_total = c4.rm_critical_ohm + r0_ohm

    summary = pd.DataFrame(
        {
            "metric": [
                "fit_k_lambda_per_ohm",
                "fit_b_lambda",
                "Rm_at_lambda0_ohm",
                "R0_ohm",
                "L_avg_mH",
                "L_sem_mH",
                "L_nominal_mH",
                "fit_A_for_Q_equals_A_div_R",
                "R_crit_theory_c1_ohm",
                "R_crit_theory_c4_ohm",
                "R_crit_exp_total_from_c4_ohm",
            ],
            "value": [
                fit_k,
                fit_b,
                rm_at_lambda0,
                r0_ohm,
                l_avg_h * 1e3,
                l_sem_h * 1e3,
                c1.l_nominal_h * 1e3,
                q_fit_a,
                r_crit_theory_c1,
                r_crit_theory_c4 if r_crit_theory_c4 is not None else np.nan,
                r_crit_exp_total if r_crit_exp_total is not None else np.nan,
            ],
        }
    )
    summary.to_csv(base_dir / "summary_3_10.csv", index=False)

    make_plots(
        blocks_map=blocks_map,
        c1_df=c1_df,
        fit_k=fit_k,
        fit_b=fit_b,
        l_avg_h=l_avg_h,
        r0_ohm=r0_ohm,
        q_fit_a=q_fit_a,
        tex_dir=tex_dir,
    )

    print("Saved processed tables and plots for lab 3.10")
    print(f"R0 = {r0_ohm:.3f} ohm")
    print(f"L_avg = {l_avg_h * 1e3:.3f} mH +/- {l_sem_h * 1e3:.3f} mH")


if __name__ == "__main__":
    main()









