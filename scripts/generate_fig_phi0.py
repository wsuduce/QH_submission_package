#!/usr/bin/env python3
"""
Generate Fig. Φ0 - Raw θ (Null Test) Boxplot
Publication-quality figure showing raw protection exponents by platform
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set publication style
plt.style.use('default')
sns.set_palette("Set2")

# Read data
try:
    # Try phi_nulltest.csv first
    df = pd.read_csv('artifacts/csv/phi_nulltest.csv')
    theta_col = 'theta_raw'
    platform_col = 'platform'
    error_col = 'theta_error'
except:
    # Fall back to d1_per_experiment_slopes.csv
    df = pd.read_csv('artifacts/csv/d1_per_experiment_slopes.csv')
    theta_col = 'theta'
    platform_col = 'platform'
    error_col = 'theta_error'

print(f"Loaded {len(df)} experiments from CSV")
print("Platforms:", df[platform_col].unique())

# Clean platform names for better display
platform_mapping = {
    'NV_DD': 'NV Centers',
    'SiP_donor': 'Si:P Donors', 
    'Cat_code': 'Cat Qubits',
    'Transmon': 'Transmons',
    'Optomech': 'Optomech',
    'Rydberg': 'Rydberg'
}

df['Platform'] = df[platform_col].map(platform_mapping).fillna(df[platform_col])

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# Create boxplot
platforms = df['Platform'].unique()
theta_data = [df[df['Platform'] == p][theta_col].values for p in platforms]

# Boxplot with custom styling
box_plot = ax.boxplot(theta_data, labels=platforms, patch_artist=True)

# Color boxes
colors = plt.cm.Set2(np.linspace(0, 1, len(platforms)))
for patch, color in zip(box_plot['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Add jittered scatter points
for i, platform in enumerate(platforms):
    platform_data = df[df['Platform'] == platform]
    y_values = platform_data[theta_col].values
    x_values = np.random.normal(i+1, 0.04, size=len(y_values))  # Jitter
    
    ax.scatter(x_values, y_values, alpha=0.6, s=30, color='black', zorder=3)

# Add sample size annotations
for i, platform in enumerate(platforms):
    n = len(df[df['Platform'] == platform])
    median_val = df[df['Platform'] == platform][theta_col].median()
    ax.text(i+1, median_val + 0.05, f'N={n}', ha='center', va='bottom', 
            fontsize=9, weight='bold')

# Styling
ax.set_ylabel('Raw Protection Exponent θ', fontsize=14, weight='bold')
ax.set_xlabel('Platform', fontsize=14, weight='bold')
ax.set_title('Fig. Φ0: Raw θ Distribution (Null Test)', fontsize=16, weight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.set_ylim(0.5, 1.4)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Add note
ax.text(0.02, 0.98, 'Before physics-informed mapping', 
        transform=ax.transAxes, fontsize=10, style='italic',
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('artifacts/figures/fig_Phi0.pdf', dpi=300, bbox_inches='tight')
plt.savefig('artifacts/figures/fig_Phi0.svg', bbox_inches='tight')
print("✅ Generated fig_Phi0.pdf and fig_Phi0.svg")

plt.close()
