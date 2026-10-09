import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from scipy import stats

# Read data
path = "data.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb["Лист1"]
vals_full = np.array([row[0] for row in ws.iter_rows(values_only=True) if row[0] is not None], dtype=float)

ns = [10, 20, 50, 100, 200, 300]

# Precompute statistics for all n
results = {}
for n in ns:
    sub = vals_full[:n]
    mean = np.mean(sub)
    var_unbiased = np.var(sub, ddof=1)
    std = np.std(sub, ddof=1)
    cv = std / mean if mean != 0 else np.nan

    z = {0.9: 1.643, 0.95: 1.960, 0.99: 2.576}
    se = std / np.sqrt(n)
    ci = {}
    for p, zv in z.items():
        half = zv * se
        ci[p] = (mean - half, mean + half, half)

    results[n] = {
        'mean': mean,
        'var': var_unbiased,
        'std': std,
        'cv': cv,
        'ci': ci,
        'data': sub,
    }

ref = results[300]
ref_mean = ref['mean']
ref_var = ref['var']
ref_std = ref['std']
ref_cv = ref['cv']

print(f"Reference (n=300): mean={ref_mean:.4f}, var={ref_var:.4f}, std={ref_std:.4f}, cv={ref_cv:.4f}")

print("\n=== Table 1 (Form 1) ===")
for char_name, key in [('Mean', 'mean'), ('Var', 'var'), ('Std', 'std'), ('CV', 'cv')]:
    row = [f"{results[n][key]:.4f}" for n in ns]
    row_pct = [f"{abs((results[n][key] - ref[key]) / ref[key] * 100):.2f}" if ref[key] != 0 else "-" for n in ns]
    print(f"{char_name:20} " + " ".join(f"{v:>10}" for v in row))
    print(f"{'% dev':20} " + " ".join(f"{v:>10}" for v in row_pct))

print("\n=== Confidence Intervals ===")
for p in [0.9, 0.95, 0.99]:
    row_vals = [f"±{results[n]['ci'][p][2]:.4f}" for n in ns]
    row_pct = [f"{abs((results[n]['ci'][p][2] - ref['ci'][p][2]) / ref['ci'][p][2] * 100):.2f}" if ref['ci'][p][
                                                                                                       2] != 0 else "-"
               for n in ns]
    print(f"p={p}: " + " ".join(row_vals))
    print(f"      %: " + " ".join(row_pct))

sub = vals_full[:300]


def autocorr(x, max_shift=10):
    n = len(x)
    xm = np.mean(x)
    c0 = np.sum((x - xm) ** 2) / n
    ac = []
    for k in range(1, max_shift + 1):
        ck = np.sum((x[:-k] - xm) * (x[k:] - xm)) / n
        ac.append(ck / c0 if c0 != 0 else 0)
    return ac


ac_300 = autocorr(sub, 10)
print("\n=== Autocorrelation (original, 300) ===")
for i, v in enumerate(ac_300, 1):
    print(f"Shift {i}: {v:.4f}")

# Histogram
plt.figure(figsize=(8, 5))
plt.hist(sub, bins=25, edgecolor='black', alpha=0.7, color='steelblue')
plt.title("Histogram of original sequence (n=300)")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    r"histogram_original.png",
    dpi=150)
plt.close()

# Sequence plot
plt.figure(figsize=(10, 4))
plt.plot(sub, marker='.', linestyle='-', markersize=3, alpha=0.7, color='darkblue')
plt.title("Sequence plot (original, n=300)")
plt.xlabel("Index")
plt.ylabel("Value")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(r"plot_sequence.png",
            dpi=150)
plt.close()

# Autocorrelation plot
plt.figure(figsize=(8, 4))
shifts = list(range(1, 11))
plt.bar(shifts, ac_300, color='coral', edgecolor='black', alpha=0.8)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.title("Autocorrelation coefficients (original, n=300)")
plt.xlabel("Shift (lag)")
plt.ylabel("Autocorrelation coefficient")
plt.xticks(shifts)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(r"plot_autocorr.png",
            dpi=150)
plt.close()

M = ref_mean
nu = ref_cv
k = 2
alpha_erl = k / M
print(f"\nApproximation: Normalized Erlang k={k}, alpha={alpha_erl:.6f}, mean={k / alpha_erl:.2f}")

np.random.seed(42)
generated = np.random.gamma(shape=k, scale=1 / alpha_erl, size=300)

print(
    f"Generated (Erlang): mean={np.mean(generated):.4f}, std={np.std(generated, ddof=1):.4f}, cv={np.std(generated, ddof=1) / np.mean(generated):.4f}")

# Histogram comparison
plt.figure(figsize=(10, 5))
bins = np.linspace(min(min(sub), min(generated)), max(max(sub), max(generated)), 30)
plt.hist(sub, bins=bins, alpha=0.6, label='Original', color='steelblue', edgecolor='black')
plt.hist(generated, bins=bins, alpha=0.6, label='Generated (Erlang k=2)', color='coral', edgecolor='black')
plt.title("Histogram comparison: Original vs Generated (Erlang k=2)")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    r"histogram_compare.png",
    dpi=150)
plt.close()

# Generated sequence plot
plt.figure(figsize=(10, 4))
plt.plot(generated, marker='.', linestyle='-', markersize=3, alpha=0.7, color='coral')
plt.title("Sequence plot (generated, Erlang k=2, n=300)")
plt.xlabel("Index")
plt.ylabel("Value")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    r"plot_sequence_gen.png",
    dpi=150)
plt.close()

# Autocorrelation for generated
ac_gen = autocorr(generated, 10)
plt.figure(figsize=(8, 4))
plt.bar(shifts, ac_gen, color='seagreen', edgecolor='black', alpha=0.8)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.title("Autocorrelation coefficients (generated, n=300)")
plt.xlabel("Shift (lag)")
plt.ylabel("Autocorrelation coefficient")
plt.xticks(shifts)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(
    r"plot_autocorr_gen.png",
    dpi=150)
plt.close()

corr_coeff = np.corrcoef(sub, generated[:300])[0, 1]
print(f"\nCorrelation between original and generated: {corr_coeff:.4f}")

print("\n=== Autocorrelation Table (Form 3) ===")
print(f"Shift  Original  Generated  %dev")
for i in range(10):
    orig_v = ac_300[i]
    gen_v = ac_gen[i]
    pct = abs((gen_v - orig_v) / orig_v * 100) if orig_v != 0 else 0
    print(f"{i + 1:5d} {orig_v:9.4f} {gen_v:9.4f} {pct:6.2f}")

# Generated characteristics table (Form 2)
print("\n=== Generated characteristics (Form 2) ===")
for char_name, key in [('Mean', 'mean'), ('Var', 'var'), ('Std', 'std'), ('CV', 'cv')]:
    row_vals = [f"{np.mean(generated[:n]):.4f}" for n in ns]
    row_pct = []
    for n in ns:
        gen_sub = np.random.gamma(shape=k, scale=1 / alpha_erl, size=n)
        # Just use fixed seed per n for reproducibility? Actually we want consistent comparison.
        # Let's use the first n values from the full generated array
        val_gen = np.mean(generated[:n]) if char_name == 'Mean' else (
            np.var(generated[:n], ddof=1) if char_name == 'Var' else np.std(generated[:n],
                                                                            ddof=1) if char_name == 'Std' else np.std(
                generated[:n], ddof=1) / np.mean(generated[:n]))
        ref_val_n = results[n][key]
        pct = abs((val_gen - ref_val_n) / ref_val_n * 100) if ref_val_n != 0 else 0
        row_pct.append(f"{pct:.2f}")
    # Print just for 300
    gen_sub = generated[:300]
    val_gen_300 = np.mean(gen_sub) if char_name == 'Mean' else np.var(gen_sub,
                                                                      ddof=1) if char_name == 'Var' else np.std(gen_sub,
                                                                                                                ddof=1) if char_name == 'Std' else np.std(
        gen_sub, ddof=1) / np.mean(gen_sub)
    ref_300 = results[300][key]
    pct_300 = abs((val_gen_300 - ref_300) / ref_300 * 100) if ref_300 != 0 else 0
    print(f"{char_name} (300): original={ref_300:.4f}, generated={val_gen_300:.4f}, %dev={pct_300:.2f}")

print("\n=== Analysis done. Files saved to labs folder ===")
