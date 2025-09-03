#!/usr/bin/env python3
"""
MIDIS Data Gate - Validator for MIDIS flux data
Based on team member's exact specifications
Verifies that data gives k ≈ 0.523 before using in Figure 2
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import sys
from pathlib import Path

def validate_midis_data(csv_path="artifacts/data/midis_flux_bins.csv"):
    """
    Validate MIDIS data and compute diagnostics
    Following team member's exact methodology
    """
    
    print(f"🔍 MIDIS Data Gate - Validating {csv_path}")
    
    # Load data
    if not Path(csv_path).exists():
        print(f"❌ ERROR: File not found: {csv_path}")
        return None
        
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded data: {len(df)} rows")
        print(df.head())
    except Exception as e:
        print(f"❌ ERROR loading CSV: {e}")
        return None
    
    # Extract data
    z = df['z'].values if 'z' in df.columns else df.iloc[:,0].values
    g = df['g'].values if 'g' in df.columns else df.iloc[:,1].values  
    g_err = df['g_err'].values if 'g_err' in df.columns else df.iloc[:,2].values
    
    print(f"📊 Data range: z=[{z.min():.1f}, {z.max():.1f}], g=[{g.min():.1f}, {g.max():.1f}]")
    
    # 1. OLS slope in log space (team member's primary diagnostic)
    lny = np.log(g)
    A = np.vstack([np.ones(len(z)), z]).T  # [1, z] design matrix
    coef = np.linalg.lstsq(A, lny, rcond=None)[0]
    ln_g0_raw, neg_k_fit = coef
    k_fit = -neg_k_fit  # Convert to positive k
    
    # Compute residuals and uncertainty
    lny_pred = ln_g0_raw - k_fit * z
    resid = lny - lny_pred
    k_fit_err = np.sqrt(np.sum(resid**2) / (len(z) - 2)) / np.sqrt(np.sum((z - z.mean())**2))
    
    print(f"\n📈 OLS Fit Results:")
    print(f"   k_fit = {k_fit:.3f} ± {k_fit_err:.3f}")
    print(f"   ln(g0) = {ln_g0_raw:.2f} → g0 = {np.exp(ln_g0_raw):.1f}")
    
    # 2. Mean two-point slopes across adjacent bins (quick sanity)
    two_point_slopes = []
    for i in range(len(z)-1):
        k_pair = (lny[i] - lny[i+1]) / (z[i+1] - z[i])
        two_point_slopes.append(k_pair)
    
    k_two_point_mean = np.mean(two_point_slopes)
    k_two_point_std = np.std(two_point_slopes)
    
    print(f"\n🔍 Two-point slopes:")
    print(f"   Mean k_two_point = {k_two_point_mean:.3f} ± {k_two_point_std:.3f}")
    print(f"   Individual slopes: {[f'{k:.3f}' for k in two_point_slopes]}")
    
    # 3. Validation against paper's k = 0.523 ± 0.058
    k_paper = 0.523
    k_paper_err = 0.058
    k_pred = 0.530
    
    deviation = abs(k_fit - k_paper)
    sigma_deviation = deviation / k_paper_err
    
    print(f"\n📋 Validation Results:")
    print(f"   Paper k = {k_paper} ± {k_paper_err}")
    print(f"   Fitted k = {k_fit:.3f}")
    print(f"   Deviation = {deviation:.3f} ({sigma_deviation:.2f}σ)")
    
    if sigma_deviation < 2.0:
        print(f"   ✅ PASS: Data consistent with paper (< 2σ)")
        validation_status = "PASS"
    else:
        print(f"   ❌ FAIL: Data inconsistent with paper (> 2σ)")
        validation_status = "FAIL"
    
    # 4. Agreement with prediction
    pred_deviation = abs(k_fit - k_pred)
    pred_sigma = pred_deviation / k_fit_err
    print(f"   Prediction agreement: |{k_fit:.3f} - {k_pred}| = {pred_deviation:.3f} ({pred_sigma:.2f}σ)")
    
    # 5. Create diagnostic plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), 
                                   gridspec_kw={'height_ratios': [3, 1]})
    
    # Top panel: Data with fits
    z_model = np.linspace(z.min()-0.1, z.max()+0.1, 200)
    g_fit = np.exp(ln_g0_raw - k_fit * z_model)
    g_paper = np.exp(ln_g0_raw - k_paper * z_model)
    g_pred = np.exp(ln_g0_raw - k_pred * z_model)
    
    ax1.errorbar(z, g, yerr=g_err, fmt='o', color='darkblue', 
                capsize=3, label='MIDIS data')
    ax1.plot(z_model, g_fit, 'purple', lw=2, 
            label=f'OLS fit: k={k_fit:.3f}')
    ax1.plot(z_model, g_paper, '--', color='red', lw=2,
            label=f'Paper: k={k_paper}')
    ax1.plot(z_model, g_pred, '--', color='green', lw=2,
            label=f'Prediction: k={k_pred}')
    
    ax1.set_yscale('log')
    ax1.set_ylabel('MIDIS flux g(z)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f'MIDIS Data Gate - Status: {validation_status}')
    
    # Bottom panel: Residuals
    g_data_fit = np.exp(ln_g0_raw - k_fit * z)
    residuals_pct = 100 * (g - g_data_fit) / g_data_fit
    
    ax2.errorbar(z, residuals_pct, yerr=100*g_err/g, fmt='o', color='darkblue')
    ax2.axhline(0, color='purple', linestyle='-', alpha=0.7)
    ax2.axhline(10, color='gray', linestyle='--', alpha=0.5)
    ax2.axhline(-10, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Redshift z')
    ax2.set_ylabel('Residuals (%)')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-25, 25)
    
    plt.tight_layout()
    
    # Save outputs
    output_dir = Path("artifacts/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save plot
    plot_path = output_dir / "midis_validator_plot.pdf"
    fig.savefig(plot_path, bbox_inches='tight', dpi=300)
    print(f"📊 Saved diagnostic plot: {plot_path}")
    
    # Save summary JSON
    summary = {
        "validation_status": validation_status,
        "csv_path": str(csv_path),
        "n_points": len(z),
        "z_range": [float(z.min()), float(z.max())],
        "g_range": [float(g.min()), float(g.max())],
        "k_fit": float(k_fit),
        "k_fit_err": float(k_fit_err),
        "k_two_point_mean": float(k_two_point_mean),
        "k_two_point_std": float(k_two_point_std),
        "k_paper": float(k_paper),
        "k_pred": float(k_pred),
        "deviation_from_paper": float(deviation),
        "sigma_deviation": float(sigma_deviation),
        "prediction_deviation": float(pred_deviation),
        "g0_fit": float(np.exp(ln_g0_raw))
    }
    
    summary_path = output_dir / "midis_validator_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"📋 Saved summary: {summary_path}")
    
    # Save two-point analysis
    two_point_df = pd.DataFrame({
        'z_pair': [f"{z[i]:.1f}-{z[i+1]:.1f}" for i in range(len(z)-1)],
        'k_two_point': two_point_slopes
    })
    
    two_point_path = output_dir / "midis_validator_two_point.csv"  
    two_point_df.to_csv(two_point_path, index=False)
    print(f"📊 Saved two-point analysis: {two_point_path}")
    
    plt.show()
    
    return summary

def main():
    """Run MIDIS Data Gate validation"""
    
    # Default path, or from command line
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "artifacts/data/midis_flux_bins.csv"
    
    print("🚪 MIDIS Data Gate - Team Member's Validator")
    print("=" * 50)
    
    summary = validate_midis_data(csv_path)
    
    if summary and summary["validation_status"] == "PASS":
        print("\n✅ MIDIS Data VALIDATED - Ready for Figure 2!")
    else:
        print("\n❌ MIDIS Data FAILED validation - Check data before proceeding!")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
