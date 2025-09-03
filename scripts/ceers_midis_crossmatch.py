#!/usr/bin/env python3
"""
Official Cross-Match Data Extractor for the QH Project.

This script queries two catalogs (MIDIS for F560W/zphot, CEERS for logM*),
performs a coordinate cross-match, applies scientific and completeness cuts,
and computes the mean F560W flux in redshift bins.
"""

import argparse
import numpy as np
import pandas as pd
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
from astropy import units as u
import sys
import hashlib
from datetime import datetime

def fetch_catalogs():
    """Fetches the two required catalogs from VizieR."""
    print("Fetching MIDIS (J/A+A/696/A57) and CEERS (J/AJ/168/113) catalogs...")
    Vizier.ROW_LIMIT = -1
    try:
        midis_cat = Vizier(columns=['RA_ICRS', 'DE_ICRS', 'Fap560Wmag', 'zph']).get_catalogs('J/A+A/696/A57')[0]
        ceers_cat = Vizier(columns=['RA_ICRS', 'DE_ICRS', 'logMst']).get_catalogs('J/AJ/168/113')[0]
        # Convert to pandas DataFrames for easier handling
        midis_df = midis_cat.to_pandas().dropna()
        ceers_df = ceers_cat.to_pandas().dropna()
        print(f"Fetched {len(midis_df)} MIDIS and {len(ceers_df)} CEERS sources.")
        return midis_df, ceers_df
    except Exception as e:
        print(f"ERROR: Failed to fetch data from VizieR. {e}", file=sys.stderr)
        return None, None

def cross_match_catalogs(df1, df2, radius_arcsec):
    """Performs a coordinate cross-match between two catalogs."""
    print(f"Performing {radius_arcsec}\" cross-match...")
    coords1 = SkyCoord(ra=df1['RA_ICRS'].values*u.deg, dec=df1['DE_ICRS'].values*u.deg)
    coords2 = SkyCoord(ra=df2['RA_ICRS'].values*u.deg, dec=df2['DE_ICRS'].values*u.deg)
    
    idx, d2d, _ = coords1.match_to_catalog_sky(coords2)
    
    match_mask = d2d < radius_arcsec * u.arcsec
    df1_matched = df1[match_mask].copy()
    df2_matched = df2.iloc[idx[match_mask]].copy()
    
    # Combine into a single DataFrame, resetting index
    df1_matched.reset_index(drop=True, inplace=True)
    df2_matched.reset_index(drop=True, inplace=True)
    
    matched_df = pd.concat([df1_matched, df2_matched[['logMst']]], axis=1)
    print(f"Found {len(matched_df)} cross-matched sources.")
    return matched_df

def apply_cuts(df, logm_min, z_min, completeness_mode):
    """Applies scientific and completeness cuts."""
    # Scientific cuts
    scientific_mask = (df['zph'] > z_min) & (df['logMst'] > logm_min)
    df_cut = df[scientific_mask].copy()
    print(f"{len(df_cut)} sources remaining after z > {z_min} and logM* > {logm_min} cuts.")

    # Uniform completeness cut
    z_high_bin_mask = (df_cut['zph'] >= 7) & (df_cut['zph'] < 8)
    faintest_mag = np.percentile(df_cut['Fap560Wmag'][z_high_bin_mask], 95)
    
    completeness_mask = df_cut['Fap560Wmag'] < faintest_mag
    df_final = df_cut[completeness_mask].copy()
    
    print(f"Completeness cut applied: Fap560Wmag < {faintest_mag:.2f} (95th percentile of z=[7,8) bin).")
    print(f"{len(df_final)} sources remaining in final sample.")
    return df_final, faintest_mag

def calculate_binned_data(df, z_edges_str):
    """Calculates mean flux and SEM for each redshift bin."""
    z_edges = list(map(float, z_edges_str.split(',')))
    results = []
    print("Calculating mean F560W flux in bins...")
    for i in range(len(z_edges) - 1):
        z_min, z_max = z_edges[i], z_edges[i+1]
        bin_mask = (df['zph'] >= z_min) & (df['zph'] < z_max)
        z_center = 0.5 * (z_min + z_max)
        magnitudes = df['Fap560Wmag'][bin_mask]
        fluxes = 10**(-0.4 * magnitudes)
        mean_flux = np.mean(fluxes)
        sem = np.std(fluxes, ddof=1) / np.sqrt(len(fluxes))
        results.append({'z': z_center, 'g': mean_flux, 'g_err': sem})
        print(f"  - Bin z=[{z_min},{z_max}): g={mean_flux:.4e} ± {sem:.4e} ({np.sum(bin_mask)} sources)")
    return pd.DataFrame(results)

def main():
    # Simplified arg parsing for this specific execution
    args = {
        'out': 'data/midis_bins.csv',
        'z_edges': '4,5,6,7,8',
        'match_radius': 1.0,
        'logm_min': 10.0,
        'completeness': 'highz_p95'
    }

    midis_df, ceers_df = fetch_catalogs()
    if midis_df is None: sys.exit(1)
    
    matched_df = cross_match_catalogs(midis_df, ceers_df, args['match_radius'])
    final_sample, faint_limit = apply_cuts(matched_df, args['logm_min'], 4, args['completeness'])
    binned_data = calculate_binned_data(final_sample, args['z_edges'])
    
    binned_data[['z', 'g', 'g_err']].to_csv(args['out'], index=False)
    print(f"\nSuccessfully saved mass-limited, completeness-corrected data to {args['out']}")

if __name__ == '__main__':
    main()
