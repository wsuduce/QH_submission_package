#!/usr/bin/env python3
"""
MIDIS Data Gate — validates Figure 2 input bins and sanity-checks k.

Usage:
  python scripts/midis_data_gate.py data/midis_bins.csv \
         --tol 0.05 --pred 0.530 --outdir artifacts/checks

Inputs (CSV required columns):
  z,g,g_err    # g = mean F560W flux per bin (as per manuscript §D3)
               # if g_err missing, an unweighted fit is used

Outputs:
  <outdir>/midis_validator_summary.json
  <outdir>/midis_validator_two_point.csv
  <outdir>/midis_validator_plot.pdf

Exit code:
  0 on PASS (|k_fit - 0.523| <= tol), 1 on FAIL
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fit_ln(z, g, w=None):
    """
    Weighted least squares in log space:
      ln g = ln g0 - k z
    Returns: (k, ln_g0, resid_sigma_ln)
    """
    ln_g = np.log(g)
    X = np.c_[np.ones_like(z), -z]  # [ln g0, k]
    if w is None:
        beta, *_ = np.linalg.lstsq(X, ln_g, rcond=None)
    else:
        W = np.diag(w)
        beta = np.linalg.inv(X.T @ W @ X) @ (X.T @ W @ ln_g)
    ln_g0, k = beta
    pred = ln_g0 - k * z
    resid = ln_g - pred
    sigma_ln = float(np.sqrt(np.mean(resid**2)))
    return float(k), float(ln_g0), sigma_ln

def two_point_slopes(z, g):
    ln_g = np.log(g)
    return (ln_g[:-1] - ln_g[1:]) / (z[1:] - z[:-1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="Path to MIDIS bins CSV (columns: z,g[,g_err])")
    ap.add_argument("--tol", type=float, default=0.05,
                    help="Acceptance tolerance for |k_fit - 0.523| (default 0.05)")
    ap.add_argument("--pred", type=float, default=0.530,
                    help="Parameter-free predicted k to overlay (default 0.530)")
    ap.add_argument("--outdir", default="artifacts/checks",
                    help="Directory for outputs (default artifacts/checks)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.csv)
    if not {"z", "g"}.issubset(df.columns):
        print("ERROR: CSV must contain columns: z,g[,g_err]", file=sys.stderr)
        sys.exit(1)

    z = df["z"].to_numpy(dtype=float)
    g = df["g"].to_numpy(dtype=float)
    gerr = df["g_err"].to_numpy(dtype=float) if "g_err" in df.columns else None

    # weights in log space
    w = None if gerr is None else 1.0 / ((gerr / g) ** 2)

    # Fit & diagnostics
    k_fit, ln_g0, sigma_ln = fit_ln(z, g, w=w)
    slopes = two_point_slopes(z, g)
    mean_two_point = float(slopes.mean())
    target_k = 0.523
    passed = abs(k_fit - target_k) <= args.tol

    # Save summary & slopes
    summary = {
        "k_fit": k_fit,
        "target_k": target_k,
        "tolerance": args.tol,
        "pass": passed,
        "ln_g0": ln_g0,
        "resid_sigma_ln": sigma_ln,
        "mean_two_point_k": mean_two_point,
        "n_bins": int(len(z))
    }
    with open(os.path.join(args.outdir, "midis_validator_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    pd.DataFrame(
        {"z_i": z[:-1], "z_ip1": z[1:], "k_two_point": slopes}
    ).to_csv(os.path.join(args.outdir, "midis_validator_two_point.csv"), index=False)

    # Quick visual
    zgrid = np.linspace(z.min(), z.max(), 200)
    gfit = np.exp(ln_g0 - k_fit * zgrid)
    gfit_pred = np.exp(ln_g0 - args.pred * zgrid)

    plt.figure(figsize=(6, 4.2))
    plt.semilogy(z, g, "o", label="data")
    plt.semilogy(zgrid, gfit, "-", label=f"fit: k={k_fit:.3f}")
    plt.semilogy(zgrid, gfit_pred, "--", label=f"pred: k={args.pred:.3f}")
    plt.xlabel("z")
    plt.ylabel("g (arb., log)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.outdir, "midis_validator_plot.pdf"))
    plt.close()

    print(f"[MIDIS Data Gate] k_fit={k_fit:.3f} vs target {target_k:.3f} (tol ±{args.tol:.3f}) ⇒ "
          f"{'PASS' if passed else 'FAIL'}")
    print(f"Outputs: {args.outdir}/midis_validator_summary.json, "
          f"{args.outdir}/midis_validator_two_point.csv, "
          f"{args.outdir}/midis_validator_plot.pdf")

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
