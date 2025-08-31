#!/usr/bin/env python
"""
fit_d1.py - Hierarchical analysis of quantum decoherence scaling
Extracts delta (δ) parameter from quantum entanglement experiments

This script analyzes decoherence time scaling across quantum experiments,
fitting power laws τ ∝ S^δ to extract the universal scale coupling parameter.
"""

import numpy as np
import pandas as pd
import argparse
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Try importing platform mapper
try:
    from platform_mapper import PlatformMapper
    HAS_MAPPING = True
except ImportError:
    HAS_MAPPING = False
    print("Warning: platform_mapper not available, skipping scale mapping")

# Try importing visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams['figure.dpi'] = 100
    mpl.rcParams['font.size'] = 10
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib not available, plots will be skipped")

# Configuration
MIN_POINTS = 3  # Minimum points per series
NEG_SLOPE_THRESHOLD = 0.0  # Exclude slopes below this
MIN_LOG_RANGE_X = 0.5   # require ≥ ~3× span in S_norm inside chosen window
MIN_LOG_RANGE_Y = 0.5   # require ≥ ~3× span in tau inside chosen window
REL_ERR_FLOOR = 0.10    # if tau_err missing/too small, assume ≥10% relative
EPS = 1e-12  # Small epsilon for numerical stability


def ensure_outdirs(outdir):
    """Create output directory structure"""
    paths = {
        'csv': Path(outdir) / 'csv',
        'figs': Path(outdir) / 'figs',
        'per_exp': Path(outdir) / 'figs' / 'per_experiment'
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths


def validate_schema(df, required_cols, df_name):
    """Check required columns are present"""
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"{df_name} missing columns: {missing}")


def compute_S_norm_if_missing(points_df):
    """Fill S_norm = S_raw / S_ref if missing"""
    mask = points_df['S_norm'].isna()
    if mask.any():
        points_df.loc[mask, 'S_norm'] = (
            points_df.loc[mask, 'S_raw'] / points_df.loc[mask, 'S_ref']
        )
    return points_df


def select_protection_window(series_data):
    """
    Select the protection window: top-S tail with positive slope
    Returns selected subset of series_data
    """
    if len(series_data) < MIN_POINTS:
        return None
    
    # Sort by S_norm
    series_data = series_data.sort_values('S_norm').reset_index(drop=True)
    
    # Try windows from largest S values
    best_window = None
    best_length = 0
    
    for start in range(len(series_data) - MIN_POINTS + 1):
        for end in range(start + MIN_POINTS, len(series_data) + 1):
            window = series_data.iloc[start:end]
            
            # Quick slope check with range requirements
            x = np.log(window['S_norm'].values + EPS)
            y = np.log(window['tau'].values + EPS)
            if len(x) >= MIN_POINTS:
                x_range = x.max() - x.min()
                y_range = y.max() - y.min()
                
                # Simple linear regression
                A = np.vstack([x, np.ones(len(x))]).T
                slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
                
                if (slope > NEG_SLOPE_THRESHOLD and 
                    x_range >= MIN_LOG_RANGE_X and 
                    y_range >= MIN_LOG_RANGE_Y and 
                    len(window) > best_length):
                    best_window = window
                    best_length = len(window)
    
    return best_window


def weighted_loglog_slope(window_data):
    """
    Weighted least squares on log-log data
    Returns (slope, slope_se)
    """
    x = np.log(window_data['S_norm'].values + EPS)
    y = np.log(window_data['tau'].values + EPS)
    
    # Weights from error propagation with floor
    if 'tau_err' in window_data.columns and not window_data['tau_err'].isna().all():
        tau_err = window_data['tau_err'].values
        tau = window_data['tau'].values
        # σ_y ≈ τ_err / τ for log(τ), with floor
        sigma_y = np.clip(tau_err / np.clip(tau, EPS, None), REL_ERR_FLOOR, 1e6)
        weights = 1.0 / (sigma_y ** 2)
        weights = weights / weights.sum() * len(weights)  # Normalize
    else:
        weights = np.ones(len(x))
    
    # Weighted least squares
    W = np.diag(weights)
    X = np.vstack([x, np.ones(len(x))]).T
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ y
    
    try:
        coef = np.linalg.solve(XtWX, XtWy)
        slope = coef[0]
        
        # Standard error from covariance
        residuals = y - X @ coef
        s2 = (residuals.T @ W @ residuals) / (len(x) - 2)
        cov = s2 * np.linalg.inv(XtWX)
        slope_se = np.sqrt(cov[0, 0])
        
        return slope, slope_se
    except:
        return None, None


def combine_effects(slopes, ses):
    """
    Fixed-effect and random-effects (DerSimonian-Laird) combination
    Returns dict with μ_FE, μ_RE, SEs, Q, τ²_between
    """
    slopes = np.array(slopes)
    ses = np.array(ses)
    weights = 1 / ses**2
    
    # Fixed-effect
    μ_FE = np.sum(weights * slopes) / np.sum(weights)
    se_FE = 1 / np.sqrt(np.sum(weights))
    
    # Heterogeneity
    Q = np.sum(weights * (slopes - μ_FE)**2)
    k = len(slopes)
    C = np.sum(weights) - np.sum(weights**2) / np.sum(weights)
    τ2_between = max(0, (Q - (k - 1)) / C)
    
    # Random-effects
    weights_RE = 1 / (ses**2 + τ2_between)
    μ_RE = np.sum(weights_RE * slopes) / np.sum(weights_RE)
    se_RE = 1 / np.sqrt(np.sum(weights_RE))
    
    return {
        'μ_FE': μ_FE, 'se_FE': se_FE,
        'μ_RE': μ_RE, 'se_RE': se_RE,
        'Q': Q, 'τ2_between': τ2_between,
        'k': k
    }


def leave_one_out(slopes, ses):
    """
    Leave-one-out analysis for robustness
    Returns list of (drop_idx, μ_RE_drop, Δμ_in_σ)
    """
    results = []
    base = combine_effects(slopes, ses)
    
    for i in range(len(slopes)):
        slopes_loo = [s for j, s in enumerate(slopes) if j != i]
        ses_loo = [s for j, s in enumerate(ses) if j != i]
        
        if len(slopes_loo) > 1:
            loo = combine_effects(slopes_loo, ses_loo)
            Δμ = loo['μ_RE'] - base['μ_RE']
            Δμ_in_σ = Δμ / base['se_RE'] if base['se_RE'] > 0 else 0
            results.append((i, loo['μ_RE'], Δμ_in_σ))
    
    return results


def plot_series(window_data, system_id, env_tag, slope, slope_se, save_path):
    """Plot log-log data with fit line"""
    if not HAS_PLOTTING:
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    
    x = np.log(window_data['S_norm'].values)
    y = np.log(window_data['tau'].values)
    
    # Data points
    ax.scatter(x, y, s=50, alpha=0.7, label='Data')
    
    # Fit line
    if slope is not None:
        x_fit = np.linspace(x.min(), x.max(), 100)
        y_fit = slope * x_fit + (y.mean() - slope * x.mean())
        ax.plot(x_fit, y_fit, 'r-', alpha=0.8, 
                label=f'δ = {slope:.3f} ± {slope_se:.3f}')
    
    ax.set_xlabel('log(S_norm)')
    ax.set_ylabel('log(τ [s])')
    ax.set_title(f'System {system_id} ({env_tag})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_histogram(slopes, combined, save_path):
    """Plot δ histogram with FE/RE lines"""
    if not HAS_PLOTTING:
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    
    ax.hist(slopes, bins=15, alpha=0.7, edgecolor='black')
    
    # Add vertical lines for combined estimates
    ax.axvline(combined['μ_FE'], color='blue', linestyle='--', 
               label=f"FE: {combined['μ_FE']:.3f} ± {combined['se_FE']:.3f}")
    ax.axvline(combined['μ_RE'], color='red', linestyle='-', 
               label=f"RE: {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}")
    
    ax.set_xlabel('δ_local')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Local δ Values')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_summary(combined, save_path):
    """Create text summary figure"""
    if not HAS_PLOTTING:
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    ax.axis('off')
    
    text = f"""
    D1 Quantum Decoherence Analysis
    ================================
    
    Fixed-Effect δ:  {combined['μ_FE']:.3f} ± {combined['se_FE']:.3f}
    Random-Effect δ: {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}
    
    Heterogeneity:
      Q statistic: {combined['Q']:.2f}
      τ² between: {combined['τ2_between']:.4f}
      k (included): {combined['k']}
    
    Result: δ_quantum = {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}
    """
    
    ax.text(0.5, 0.5, text, transform=ax.transAxes,
            fontsize=12, verticalalignment='center',
            horizontalalignment='center', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Fit D1 quantum decoherence scaling')
    parser.add_argument('--meta', default='analysis/d1_quantum/D1_experiments_meta.csv',
                        help='Path to experiments meta CSV')
    parser.add_argument('--points', default='analysis/d1_quantum/D1_points.csv',
                        help='Path to data points CSV')
    parser.add_argument('--outdir', default='artifacts/v2/d1_quantum',
                        help='Output directory')
    parser.add_argument('--neg_slope_threshold', type=float, default=0.0,
                        help='Exclude slopes below this value')
    parser.add_argument('--platform_map', default='analysis/d1_quantum/platform_map.yml',
                        help='Path to platform mapping configuration')
    parser.add_argument('--enable_mapping', action='store_true',
                        help='Enable platform-to-scale mapping')
    args = parser.parse_args()
    
    global NEG_SLOPE_THRESHOLD
    NEG_SLOPE_THRESHOLD = args.neg_slope_threshold
    
    # Setup directories
    paths = ensure_outdirs(args.outdir)
    
    # Load data
    print(f"Loading data from {args.meta} and {args.points}")
    meta_df = pd.read_csv(args.meta)
    points_df = pd.read_csv(args.points)
    
    # Validate schemas
    validate_schema(meta_df, ['id', 'system', 'include_flag'], 'meta')
    validate_schema(points_df, ['system_id', 'S_raw', 'S_ref', 'tau', 'env_tag'], 'points')
    
    # Compute S_norm if missing
    points_df = compute_S_norm_if_missing(points_df)
    
    # Process each series
    results = []
    slopes_for_combination = []
    ses_for_combination = []
    
    for (system_id, env_tag), group in points_df.groupby(['system_id', 'env_tag']):
        # Get meta info
        meta = meta_df[meta_df['id'] == system_id].iloc[0]
        
        # Check include flag
        if meta['include_flag'] != 'Include':
            results.append({
                'system_id': system_id,
                'system': meta['system'],
                'env_tag': env_tag,
                'n_points_used': 0,
                'window_min_S': np.nan,
                'window_max_S': np.nan,
                'delta_fit_local': np.nan,
                'delta_fit_se': np.nan,
                'include_in_aggregate': False,
                'rationale': 'Excluded by meta flag'
            })
            continue
        
        # Select protection window
        window = select_protection_window(group)
        if window is None:
            results.append({
                'system_id': system_id,
                'system': meta['system'],
                'env_tag': env_tag,
                'n_points_used': 0,
                'window_min_S': np.nan,
                'window_max_S': np.nan,
                'delta_fit_local': np.nan,
                'delta_fit_se': np.nan,
                'include_in_aggregate': False,
                'rationale': f'Too few points ({len(group)} < {MIN_POINTS})'
            })
            continue
        
        # Fit slope
        slope, slope_se = weighted_loglog_slope(window)
        
        # Check slope threshold
        if slope is None or slope < NEG_SLOPE_THRESHOLD:
            results.append({
                'system_id': system_id,
                'system': meta['system'],
                'env_tag': env_tag,
                'n_points_used': len(window),
                'window_min_S': window['S_norm'].min(),
                'window_max_S': window['S_norm'].max(),
                'delta_fit_local': slope if slope else np.nan,
                'delta_fit_se': slope_se if slope_se else np.nan,
                'include_in_aggregate': False,
                'rationale': f'Negative/weak slope ({slope:.3f} < {NEG_SLOPE_THRESHOLD})' if slope else 'Fit failed'
            })
            continue
        
        # Good fit - include
        results.append({
            'system_id': system_id,
            'system': meta['system'],
            'env_tag': env_tag,
            'n_points_used': len(window),
            'window_min_S': window['S_norm'].min(),
            'window_max_S': window['S_norm'].max(),
            'delta_fit_local': slope,
            'delta_fit_se': slope_se,
            'include_in_aggregate': True,
            'rationale': 'Included'
        })
        
        slopes_for_combination.append(slope)
        ses_for_combination.append(slope_se)
        
        # Plot
        plot_path = paths['per_exp'] / f"{system_id}_{env_tag.replace(' ', '_')}.pdf"
        plot_series(window, system_id, env_tag, slope, slope_se, plot_path)
    
    # Save per-experiment results
    results_df = pd.DataFrame(results)
    results_df.to_csv(paths['csv'] / 'd1_per_experiment_slopes.csv', index=False)
    print(f"\nPer-experiment results saved to {paths['csv'] / 'd1_per_experiment_slopes.csv'}")
    
    # Combine effects
    if len(slopes_for_combination) > 1:
        combined = combine_effects(slopes_for_combination, ses_for_combination)
        
        # Save combined results
        combined_df = pd.DataFrame([{
            'μ_FE': combined['μ_FE'],
            'se_FE': combined['se_FE'],
            'μ_RE': combined['μ_RE'],
            'se_RE': combined['se_RE'],
            'τ2_between': combined['τ2_between'],
            'Q': combined['Q'],
            'k_included': combined['k']
        }])
        combined_df.to_csv(paths['csv'] / 'd1_combined_delta.csv', index=False)
        print(f"Combined results saved to {paths['csv'] / 'd1_combined_delta.csv'}")
        
        # Leave-one-out
        loo_results = leave_one_out(slopes_for_combination, ses_for_combination)
        loo_df = pd.DataFrame(loo_results, columns=['drop_index', 'μ_RE_drop', 'Δμ_in_σ'])
        loo_df.to_csv(paths['csv'] / 'd1_leave_one_out.csv', index=False)
        print(f"LOO results saved to {paths['csv'] / 'd1_leave_one_out.csv'}")
        
        # Plots
        plot_histogram(slopes_for_combination, combined, paths['figs'] / 'd1_delta_hist.pdf')
        plot_summary(combined, paths['figs'] / 'd1_mu_summary.pdf')
        
        # Print summary
        print("\n" + "="*60)
        print("D1 Quantum Decoherence Analysis Results")
        print("="*60)
        print(f"Systems analyzed: {len(results_df)}")
        print(f"Systems included: {combined['k']}")
        print(f"\nFixed-Effect δ:  {combined['μ_FE']:.3f} ± {combined['se_FE']:.3f}")
        print(f"Random-Effect δ: {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}")
        print(f"\nHeterogeneity Q: {combined['Q']:.2f}")
        print(f"τ² between: {combined['τ2_between']:.4f}")
        print(f"\nMax LOO deviation: {max(abs(r[2]) for r in loo_results):.3f}σ")
        print("="*60)
        print(f"\n✓ Result: δ_quantum = {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}")
        
        # Platform-to-scale mapping (optional)
        if args.enable_mapping and HAS_MAPPING:
            print(f"\n" + "="*60)
            print("PLATFORM-TO-SCALE MAPPING ANALYSIS")
            print("="*60)
            
            try:
                mapper = PlatformMapper(args.platform_map)
                platform_data, mapped_results, cv_results = mapper.run_full_mapping(results_df)
                
                if mapped_results:
                    # Save mapped results
                    mapped_df = pd.DataFrame([{
                        'μ_FE_mapped': mapped_results['mu_FE'],
                        'se_FE_mapped': mapped_results['se_FE'],
                        'μ_RE_mapped': mapped_results['mu_RE'],
                        'se_RE_mapped': mapped_results['se_RE'],
                        'τ2_between_mapped': mapped_results['tau2_between'],
                        'Q_mapped': mapped_results['Q'],
                        'k_mapped': mapped_results['k']
                    }])
                    mapped_df.to_csv(paths['csv'] / 'd1_mapped_delta.csv', index=False)
                    
                    # Save phi estimates
                    phi_df = pd.DataFrame([{
                        f'phi_{i}': phi for i, phi in enumerate(mapped_results['phi_optimal'])
                    }])
                    phi_df.to_csv(paths['csv'] / 'd1_phi_estimates.csv', index=False)
                    
                    print(f"\nMapped results saved to:")
                    print(f"  {paths['csv'] / 'd1_mapped_delta.csv'}")
                    print(f"  {paths['csv'] / 'd1_phi_estimates.csv'}")
                    
                    print(f"\n🎯 COMPARISON:")
                    print(f"  Raw δ_quantum: {combined['μ_RE']:.3f} ± {combined['se_RE']:.3f}")
                    print(f"  Mapped δ_true: {mapped_results['mu_RE']:.3f} ± {mapped_results['se_RE']:.3f}")
                    
                    if mapped_results['mu_RE'] < combined['μ_RE']:
                        print(f"  ✅ Mapping reduced δ (as expected)")
                    else:
                        print(f"  ⚠️  Mapping increased δ (physics investigation needed)")
                        
            except Exception as e:
                print(f"Mapping failed: {e}")
                
        
    else:
        print("\nInsufficient data for combination (need at least 2 series)")
    
    print(f"\nAll outputs saved to {args.outdir}")


if __name__ == '__main__':
    main()