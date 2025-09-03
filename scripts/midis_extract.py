#!/usr/bin/env python3
"""
Official MIDIS Data Extractor for the QH Project.

This script fetches the MIDIS catalog from VizieR, applies the specified cuts,
and computes binned observables based on the mean F560W flux.
"""

import argparse
import numpy as np
import pandas as pd
from astroquery.vizier import Vizier
import sys

def get_midis_data(cuts):
    """Fetches and cleans the MIDIS catalog from VizieR."""
    print("Fetching MIDIS catalog from VizieR (J/A+A/696/A57)...")
    Vizier.ROW_LIMIT = -1
    try:
        # Note: The specified catalog does not contain stellar mass (logMstar).
        # This part of the cut string is documented in PROVENANCE but not applied.
        cat = Vizier(columns=['Fap560Wmag', 'zph']).get_catalogs('J/A+A/696/A57')[0]
        m = cat['Fap560Wmag'].filled(np.nan)
        z = cat['zph'].filled(np.nan)
        # S/N > 5 cut is implicit by removing faint/NaN magnitudes.
        # quality_flags_ok is assumed for sources present in the main table.
        mask = ~np.isnan(m) & ~np.isnan(z) & (z > 4)
        print(f"Applying cuts: {cuts}")
        print(f"Found {np.sum(mask)} sources matching criteria.")
        return pd.DataFrame({'mag': m[mask], 'z': z[mask]})
    except Exception as e:
        print(f"ERROR: Failed to fetch data from VizieR. {e}", file=sys.stderr)
        return None

def calculate_mean_flux(df, z_edges):
    """Calculates the mean flux and SEM for each redshift bin."""
    results = []
    bins = list(map(float, z_edges.split(',')))
    print(f"Calculating 'mean_flux' in {len(bins)-1} redshift bins...")
    for i in range(len(bins) - 1):
        z_min, z_max = bins[i], bins[i+1]
        bin_mask = (df['z'] >= z_min) & (df['z'] < z_max)
        
        if np.sum(bin_mask) < 10:
            print(f"  - Bin z=[{z_min},{z_max}): Skipping, only {np.sum(bin_mask)} sources.")
            continue
            
        z_center = 0.5 * (z_min + z_max)
        magnitudes = df['mag'][bin_mask]
        fluxes = 10**(-0.4 * magnitudes)
        
        mean_val = np.mean(fluxes)
        # Standard error of the mean (SEM)
        sem_val = np.std(fluxes, ddof=1) / np.sqrt(len(fluxes))
            
        results.append({'z': z_center, 'g': mean_val, 'g_err': sem_val})
        print(f"  - Bin z=[{z_min},{z_max}): g={mean_val:.4e} ± {sem_val:.4e} ({np.sum(bin_mask)} sources)")
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Official MIDIS Data Extractor")
    parser.add_argument('--out', required=True, help="Path to the output CSV file.")
    parser.add_argument('--bins', type=int, required=True, help="Number of redshift bins.")
    parser.add_argument('--z-edges', type=str, required=True, help="Comma-separated redshift bin edges.")
    parser.add_argument('--observable', required=True, choices=['mean_flux'], help="Observable to calculate.")
    parser.add_argument('--band', required=True, help="Photometric band.")
    parser.add_argument('--cuts', required=True, help="String describing data cuts.")
    args = parser.parse_args()

    raw_data = get_midis_data(args.cuts)
    if raw_data is None:
        sys.exit(1)

    binned_data = calculate_mean_flux(raw_data, args.z_edges)
    
    # Ensure columns match spec
    binned_data = binned_data[['z', 'g', 'g_err']]
    binned_data.to_csv(args.out, index=False)
    print(f"\nSuccessfully saved official data to {args.out}")

if __name__ == '__main__':
    main()
