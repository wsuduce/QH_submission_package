#!/usr/bin/env python3
"""
Generate Fig. Φ2 - Reverse Viability Analysis
Three-panel plot showing φ_req vs theory bounds for δ = 0, 0.5, 1.0
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read reverse viability data
df = pd.read_csv('artifacts/csv/phi_reverse_viability.csv')

# Theory bounds per platform
theory_bounds = {
    'NV/DD': [0.9, 1.6],
    'Si:P': [0.8, 1.3], 
    'Cat': [1.0, 1.6],
    'Transmon': [0.8, 1.2],
    'Optomech': [0.8, 1.2],
    'Rydberg': [0.7, 1.3]
}

# Create figure with 3 panels
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Reverse Viability Analysis (φ_req vs Theory Bounds)', 
             fontsize=16, weight='bold')

delta_values = [0.0, 0.5, 1.0]
delta_cols = ['phi_req_delta_0', 'phi_req_delta_0p5', 'phi_req_delta_1p0']

for i, (delta, col) in enumerate(zip(delta_values, delta_cols)):
    ax = axes[i]
    
    # Platform positions
    platforms = df['platform'].unique()  # lowercase column name
    x_pos = np.arange(len(platforms))
    
    for j, platform in enumerate(platforms):
        row = df[df['platform'] == platform].iloc[0]
        phi_req = row[col]
        
        # Get theory bounds for this platform  
        bounds = [row['theory_bounds_min'], row['theory_bounds_max']]
        
        # Plot theory band with increased alpha for gray printing
        ax.fill_between([j-0.3, j+0.3], bounds[0], bounds[1], 
                       alpha=0.4, color='lightblue', label='Theory window' if j==0 and i==0 else "")
        
        # Plot φ_req point
        if phi_req == float('inf') or phi_req > 10:
            # For δ=0 case, show arrows pointing up
            ax.annotate('∞', xy=(j, bounds[1]+0.2), ha='center', va='bottom',
                       fontsize=14, weight='bold', color='red')
            ax.arrow(j, bounds[1]+0.1, 0, 0.1, head_width=0.05, 
                    head_length=0.05, fc='red', ec='red')
            viable = False
        else:
            # Check if in bounds
            viable = bounds[0] <= phi_req <= bounds[1]
            color = 'green' if viable else 'red'
            marker = 'o' if viable else 'x'
            
            # Add legend labels for first occurrence
            label = None
            if j == 0 and i == 0:
                if viable:
                    label = '● In-band'
                else:
                    label = '✗ Out-of-band'
            elif j == 1 and not viable and i == 0:  # Add red label if first was green
                label = '✗ Out-of-band'
                
            ax.scatter(j, phi_req, color=color, s=100, marker=marker, zorder=5, label=label)
    
    # Clean platform names to match Phi0 style
    platform_clean = [p.replace('NV/DD', 'NV Centers').replace('Si:P', 'Si:P Donors')
                      .replace('Cat', 'Cat Codes').replace('Transmon', 'Transmons')
                      .replace('Optomech', 'Optomech').replace('Rydberg', 'Rydberg') 
                      for p in platforms]
    
    # Count in-band fraction for annotation
    in_band_count = 0
    for j, platform in enumerate(platforms):
        row = df[df['platform'] == platform].iloc[0]
        phi_req = row[col]
        bounds = [row['theory_bounds_min'], row['theory_bounds_max']]
        if phi_req != float('inf') and phi_req <= 10:
            if bounds[0] <= phi_req <= bounds[1]:
                in_band_count += 1
    
    # Styling
    ax.set_xticks(x_pos)
    ax.set_xticklabels(platform_clean, rotation=45, ha='right')
    ax.set_ylabel('Required mapping factor φ_req = θ/δ' if i==0 else '')
    ax.set_title(f'δ = {delta}')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 3 if delta > 0 else 4)
    
    # Add in-band fraction annotation
    ax.text(0.98, 0.98, f'In-band: {in_band_count}/{len(platforms)}', 
            transform=ax.transAxes, fontsize=10, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    if i == 0:
        ax.legend(loc='upper left', fontsize=9)

plt.tight_layout()
plt.savefig('artifacts/figures/fig_Phi2.pdf', dpi=300, bbox_inches='tight')
plt.savefig('artifacts/figures/fig_Phi2.svg', bbox_inches='tight')
print("✅ Generated fig_Phi2.pdf and fig_Phi2.svg")

plt.close()
