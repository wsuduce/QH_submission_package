#!/usr/bin/env python3
"""
Generate Fig. K1 - Astrophysics Model Comparison
Overlay of data, SCF prediction, and TNG/EAGLE models
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data
series_df = pd.read_csv('artifacts/csv/astro_model_series.csv')
k_table = pd.read_csv('artifacts/csv/astro_model_k_table.csv')

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(10, 7))

# Redshift bins
z_bins = [4.5, 5.5, 6.5, 7.5]

# Plot TNG100 models
tng_mean = series_df[(series_df['model'] == 'TNG100') & (series_df['proxy'] == 'mean')]
tng_peak = series_df[(series_df['model'] == 'TNG100') & (series_df['proxy'] == 'peak')]

ax.errorbar(tng_mean['z'], tng_mean['g'], yerr=tng_mean['g_err'], 
           fmt='s-', label='TNG100 Mean', color='blue', alpha=0.8)
ax.errorbar(tng_peak['z'], tng_peak['g'], yerr=tng_peak['g_err'],
           fmt='^--', label='TNG100 Peak', color='blue', alpha=0.6)

# Plot EAGLE models  
eagle_mean = series_df[(series_df['model'] == 'EAGLE') & (series_df['proxy'] == 'mean')]
eagle_peak = series_df[(series_df['model'] == 'EAGLE') & (series_df['proxy'] == 'peak')]

ax.errorbar(eagle_mean['z'], eagle_mean['g'], yerr=eagle_mean['g_err'],
           fmt='o-', label='EAGLE Mean', color='orange', alpha=0.8)  
ax.errorbar(eagle_peak['z'], eagle_peak['g'], yerr=eagle_peak['g_err'],
           fmt='v--', label='EAGLE Peak', color='orange', alpha=0.6)

# Plot SCF prediction - single exponential k=0.530
z_smooth = np.linspace(4.0, 8.0, 100)
g0_scf = 1.69e-8  # From manuscript
k_scf = 0.530
g_scf = g0_scf * np.exp(-k_scf * z_smooth)

ax.plot(z_smooth, g_scf, 'r-', linewidth=3, label='SCF: k = 0.530', zorder=10)

# Add observational data point (if available)
k_obs = 0.519
g_obs = g0_scf * np.exp(-k_obs * z_smooth)
ax.plot(z_smooth, g_obs, 'k:', linewidth=2, label='JWST/MIDIS: k = 0.519 ± 0.061', alpha=0.8)

# Styling
ax.set_xlabel('Redshift z', fontsize=14, weight='bold')
ax.set_ylabel('Flux Proxy g(z)', fontsize=14, weight='bold') 
ax.set_title('Fig. K1: Astrophysics Model Comparison', fontsize=16, weight='bold', pad=20)
ax.set_yscale('log')
ax.set_xlim(4.0, 8.0)
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)

# Add acceptance rule annotation
ax.text(0.02, 0.02, 'Acceptance Rule:\n• Single k across proxies\n• Within 1σ of k_obs = 0.519 ± 0.061\n• No z-bin retuning',
        transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

plt.tight_layout()
plt.savefig('artifacts/figures/fig_K1_astro_overlay.pdf', dpi=300, bbox_inches='tight')
plt.savefig('artifacts/figures/fig_K1_astro_overlay.svg', bbox_inches='tight')
print("✅ Generated fig_K1_astro_overlay.pdf and fig_K1_astro_overlay.svg")

plt.close()
