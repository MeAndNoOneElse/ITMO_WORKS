#!/usr/bin/env python3
"""Task 1. Image compression via truncated SVD.

Loads a grayscale image, performs full SVD, builds truncated reconstructions
for 9+ values of k, evaluates compression ratio and reconstruction quality.
Outputs: data/source_image.png, data/recon_k*.png, data/compression.csv,
graphics/*.png. Run: python3 prog/svd_compression.py (from lab_6 root).
"""

import os
import math
import csv

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GRAPHICS = os.path.join(ROOT, "graphics")

SOURCE_IMAGE_JPG = os.path.join(DATA, "source_image.jpg")
SOURCE_IMAGE = os.path.join(DATA, "source_image.png")
COMPRESSION_CSV = os.path.join(DATA, "compression.csv")

K_VALUES = [1, 2, 5, 10, 20, 50, 100, 200, 300]  # 9 different k


def load_source_image(path=SOURCE_IMAGE, jpg_path=SOURCE_IMAGE_JPG):
    """Source grayscale image for SVD compression (user file)."""
    if os.path.exists(path):
        return Image.open(path).convert("L")
    if os.path.exists(jpg_path):
        img = Image.open(jpg_path).convert("L")
        img.save(path)
        return img
    raise FileNotFoundError(
        f"Source image file not found: {jpg_path} or {path}"
    )


def truncated_svd_reconstruct(U, s, Vt, k):
    """Reconstruct matrix from first k SVD components."""
    kk = min(k, len(s))
    Uk = U[:, :kk]
    Sk = np.diag(s[:kk])
    Vtk = Vt[:kk, :]
    return Uk @ Sk @ Vtk


def compression_ratio(m, n, k):
    """Fraction of original data to store for truncated SVD."""
    return k * (m + n + 1) / (m * n)


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(GRAPHICS, exist_ok=True)

    img = load_source_image()
    A = np.asarray(img, dtype=np.float64)
    m, n = A.shape
    print(f"Image: {m}x{n} pixels")

    # Full SVD
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    total_energy = float(np.sum(s ** 2))
    fro_full = float(np.linalg.norm(A, "fro"))

    rows = []
    recon_images = []
    for k in K_VALUES:
        kk = min(k, len(s))
        Ak = truncated_svd_reconstruct(U, s, Vt, kk)
        err = float(np.linalg.norm(A - Ak, "fro"))
        err_rel = err / fro_full
        energy = float(np.sum(s[:kk] ** 2)) / float(np.sum(s ** 2))
        ratio = compression_ratio(m, n, kk)
        rows.append({
            "k": kk,
            "compression_ratio": ratio,
            "percent_of_original": ratio * 100.0,
            "frobenius_error": err,
            "relative_error": err_rel,
            "energy_kept": energy,
        })
        recon_images.append((kk, Ak))
        print(
            f"k={kk:3d}  compression={ratio*100:5.1f}%  "
            f"||A-Ak||_F={err:8.1f}  rel_err={err_rel:.4f}  "
            f"energy={energy:.4f}"
        )

    # Compression table
    with open(COMPRESSION_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "k", "compression_ratio", "percent_of_original",
            "frobenius_error", "relative_error", "energy_kept"])
        w.writeheader()
        w.writerows(rows)
    print(f"Table saved: {COMPRESSION_CSV}")

    # Save reconstructions
    for kk, Ak in recon_images:
        out = os.path.join(DATA, f"recon_k{kk}.png")
        Image.fromarray(np.clip(Ak, 0, 255).astype(np.uint8)).save(out)

    # ---- Graphs ----
    # 1. Singular values
    plt.figure(figsize=(7, 4))
    plt.semilogy(s, marker="o", markersize=3, lw=1.2)
    plt.xlabel("Index of singular number i")
    plt.ylabel("Singular number sigma_i (log scale)")
    plt.title("Singular numbers of image matrix")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "svd_singular_values.png"), dpi=300)
    plt.close()

    # 2. Energy vs k
    ks = [r["k"] for r in rows]
    energy = [r["energy_kept"] for r in rows]
    plt.figure(figsize=(7, 4))
    plt.plot(ks, energy, marker="o", lw=1.5)
    for x, y in zip(ks, energy):
        plt.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8)
    plt.xlabel("k (number of components)")
    plt.ylabel("Fraction of preserved energy sum(s[:k]^2) / sum(s^2)")
    plt.title("Energy preserved by truncated SVD vs k")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "svd_energy_vs_k.png"), dpi=300)
    plt.close()

    # 3. Reconstruction error and compression vs k
    err_rel = [r["relative_error"] for r in rows]
    ratio = [r["compression_ratio"] for r in rows]
    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(ks, err_rel, marker="o", color="tab:red", lw=1.5,
             label="relative error ||A-Ak||_F/||A||_F")
    ax1.set_xlabel("k")
    ax1.set_ylabel("Relative error", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax2 = ax1.twinx()
    ax2.plot(ks, ratio, marker="s", color="tab:blue", lw=1.5,
             label="compression ratio (fraction of original data)")
    ax2.set_ylabel("Fraction of original data (compression ratio)", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")
    plt.title("Quality and compression vs k")
    fig.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "svd_quality_compression_vs_k.png"), dpi=300)
    plt.close()

    # 4. Reconstructions for selected k (grid)
    show_ks = [1, 5, 20, 50, 100, 200, 300]
    fig, axes = plt.subplots(2, 4, figsize=(10, 6))
    axes = axes.ravel()
    axes[0].imshow(A, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title("Original (k = full)")
    axes[0].axis("off")
    recon_map = {kk: Ak for kk, Ak in recon_images}
    for ax, kk in zip(axes[1:], show_ks):
        ax.imshow(recon_map[kk], cmap="gray", vmin=0, vmax=255)
        ratio_k = compression_ratio(m, n, kk)
        ax.set_title(f"k={kk}, data={ratio_k*100:.1f}%")
        ax.axis("off")
    fig.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "svd_reconstructions.png"), dpi=300)
    plt.close()

    print(f"Graphs saved to {GRAPHICS}")
    print("Done.")


if __name__ == "__main__":
    main()
