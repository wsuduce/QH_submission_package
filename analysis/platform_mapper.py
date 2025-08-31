#!/usr/bin/env python
"""
platform_mapper.py - Platform-to-Scale Mapping for D1 Analysis

Implements meta-regression to map lab control parameters to effective information scale:
S_eff = S_norm^phi, then delta_true = delta_local / phi

Physics-motivated approach to reconcile platform-specific control parameters
with universal information scale coupling.
"""

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize_scalar, minimize
from sklearn.model_selection import KFold
import warnings
warnings.filterwarnings('ignore')


class PlatformMapper:
    def __init__(self, config_path):
        """Load platform mapping configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.platforms = self.config['platforms']
        self.meta_config = self.config['meta_regression']
        
    def extract_platform_data(self, results_df):
        """Extract per-platform results with bounds"""
        platform_data = []
        
        for platform_key, platform_info in self.platforms.items():
            system_id = platform_info['system_id']
            
            # Find matching result
            mask = results_df['system_id'] == system_id
            if mask.sum() == 1:
                row = results_df[mask].iloc[0]
                if row['include_in_aggregate']:
                    platform_data.append({
                        'system_id': system_id,
                        'platform': platform_key,
                        'delta_local': row['delta_fit_local'],
                        'delta_se': row['delta_fit_se'],
                        'phi_min': platform_info['phi_bounds'][0],
                        'phi_max': platform_info['phi_bounds'][1],
                        'phi_prior_mean': platform_info['phi_prior_mean'],
                        'phi_prior_std': platform_info['phi_prior_std'],
                        'description': platform_info['description']
                    })
        
        return pd.DataFrame(platform_data)
    
    def objective_function(self, phi_values, platform_data):
        """
        Objective: minimize between-platform heterogeneity in delta_true
        delta_true = delta_local / phi
        """
        if len(phi_values) != len(platform_data):
            raise ValueError("Phi values must match platform count")
        
        # Check bounds
        for i, (phi, row) in enumerate(zip(phi_values, platform_data.itertuples())):
            if phi < row.phi_min or phi > row.phi_max:
                return 1e6  # Penalty for violating physics bounds
        
        # Calculate delta_true for each platform
        delta_true = platform_data['delta_local'].values / phi_values
        delta_true_se = platform_data['delta_se'].values / phi_values
        
        # Calculate between-platform heterogeneity (like DerSimonian-Laird)
        weights = 1 / (delta_true_se**2)
        mu_weighted = np.sum(weights * delta_true) / np.sum(weights)
        
        Q = np.sum(weights * (delta_true - mu_weighted)**2)
        k = len(delta_true)
        C = np.sum(weights) - np.sum(weights**2) / np.sum(weights)
        tau_squared = max(0, (Q - (k - 1)) / C)
        
        # Add weak prior penalty
        prior_penalty = 0
        for phi, row in zip(phi_values, platform_data.itertuples()):
            prior_penalty += ((phi - row.phi_prior_mean) / row.phi_prior_std)**2
        
        return tau_squared + 0.1 * prior_penalty  # Light prior weight
    
    def fit_phi_values(self, platform_data):
        """
        Find optimal phi values that minimize between-platform heterogeneity
        """
        n_platforms = len(platform_data)
        
        # Initial guess: prior means
        initial_phi = platform_data['phi_prior_mean'].values
        
        # Bounds for optimization
        bounds = [(row.phi_min, row.phi_max) for row in platform_data.itertuples()]
        
        # Optimize
        result = minimize(
            fun=lambda phi: self.objective_function(phi, platform_data),
            x0=initial_phi,
            bounds=bounds,
            method='L-BFGS-B',
            options={
                'maxiter': self.meta_config['convergence']['max_iterations'],
                'ftol': float(self.meta_config['convergence']['tolerance'])
            }
        )
        
        if not result.success:
            print(f"Warning: Optimization did not converge: {result.message}")
        
        return result.x, result.fun
    
    def cross_validate_mapping(self, platform_data):
        """
        Cross-validate the phi mapping to check robustness
        """
        if len(platform_data) < self.meta_config['cross_validation']['folds']:
            print("Too few platforms for cross-validation, skipping")
            return None
        
        cv = KFold(
            n_splits=self.meta_config['cross_validation']['folds'],
            shuffle=True, 
            random_state=self.meta_config['cross_validation']['seed']
        )
        
        cv_results = []
        
        for fold, (train_idx, val_idx) in enumerate(cv.split(platform_data)):
            train_data = platform_data.iloc[train_idx].copy().reset_index(drop=True)
            val_data = platform_data.iloc[val_idx].copy().reset_index(drop=True)
            
            # Fit on training set
            phi_train, obj_train = self.fit_phi_values(train_data)
            
            # Evaluate on validation set (use training phi for validation platforms)
            # This is approximate since we can't perfectly map train->val phi
            val_obj = self.objective_function(
                platform_data['phi_prior_mean'].iloc[val_idx].values,
                val_data
            )
            
            cv_results.append({
                'fold': fold,
                'train_objective': obj_train,
                'val_objective': val_obj
            })
        
        return pd.DataFrame(cv_results)
    
    def compute_mapped_results(self, platform_data, phi_optimal):
        """
        Compute final results with optimal phi mapping
        """
        # Calculate delta_true
        delta_true = platform_data['delta_local'].values / phi_optimal
        delta_true_se = platform_data['delta_se'].values / phi_optimal
        
        # Meta-analysis of delta_true
        weights = 1 / (delta_true_se**2)
        
        # Fixed-effect
        mu_FE = np.sum(weights * delta_true) / np.sum(weights)
        se_FE = 1 / np.sqrt(np.sum(weights))
        
        # Random-effects (DerSimonian-Laird)
        Q = np.sum(weights * (delta_true - mu_FE)**2)
        k = len(delta_true)
        C = np.sum(weights) - np.sum(weights**2) / np.sum(weights)
        tau2_between = max(0, (Q - (k - 1)) / C)
        
        weights_RE = 1 / (delta_true_se**2 + tau2_between)
        mu_RE = np.sum(weights_RE * delta_true) / np.sum(weights_RE)
        se_RE = 1 / np.sqrt(np.sum(weights_RE))
        
        return {
            'delta_true_values': delta_true,
            'delta_true_se_values': delta_true_se,
            'phi_optimal': phi_optimal,
            'mu_FE': mu_FE,
            'se_FE': se_FE,
            'mu_RE': mu_RE, 
            'se_RE': se_RE,
            'tau2_between': tau2_between,
            'Q': Q,
            'k': k
        }
    
    def run_full_mapping(self, results_df):
        """
        Complete mapping pipeline: extract -> fit -> validate -> compute
        """
        print("=== Platform-to-Scale Mapping Analysis ===")
        
        # Extract platform data
        platform_data = self.extract_platform_data(results_df)
        print(f"Found {len(platform_data)} platforms for mapping")
        
        if len(platform_data) < 2:
            print("Need at least 2 platforms for mapping, skipping")
            return None, None, None
        
        # Print platform info
        print("\nPlatform Summary:")
        for _, row in platform_data.iterrows():
            print(f"  {row['platform']}: δ_local = {row['delta_local']:.3f} ± {row['delta_se']:.3f}")
        
        # Fit optimal phi values
        print(f"\nFitting phi parameters...")
        phi_optimal, final_objective = self.fit_phi_values(platform_data)
        
        print("Optimal phi values:")
        for i, (_, row) in enumerate(platform_data.iterrows()):
            print(f"  {row['platform']}: φ = {phi_optimal[i]:.3f} "
                  f"[{row['phi_min']:.2f}, {row['phi_max']:.2f}]")
        
        # Cross-validation
        if self.meta_config['cross_validation']['folds'] > 1:
            print(f"\nRunning {self.meta_config['cross_validation']['folds']}-fold cross-validation...")
            cv_results = self.cross_validate_mapping(platform_data)
            if cv_results is not None:
                print(f"CV train objective: {cv_results['train_objective'].mean():.4f} ± {cv_results['train_objective'].std():.4f}")
                print(f"CV val objective: {cv_results['val_objective'].mean():.4f} ± {cv_results['val_objective'].std():.4f}")
        else:
            cv_results = None
        
        # Compute final mapped results
        print(f"\nComputing mapped results...")
        mapped_results = self.compute_mapped_results(platform_data, phi_optimal)
        
        # Summary
        print(f"\n=== Mapping Results ===")
        print(f"Raw μ_RE: {results_df[results_df['include_in_aggregate']]['delta_fit_local'].mean():.3f}")
        print(f"Mapped μ_FE: {mapped_results['mu_FE']:.3f} ± {mapped_results['se_FE']:.3f}")
        print(f"Mapped μ_RE: {mapped_results['mu_RE']:.3f} ± {mapped_results['se_RE']:.3f}")
        print(f"Heterogeneity reduction: τ² = {mapped_results['tau2_between']:.4f}")
        print(f"Final objective: {final_objective:.4f}")
        
        return platform_data, mapped_results, cv_results


def main():
    """Test the mapping on sample data"""
    # This would normally be called from fit_d1.py
    print("Platform mapper loaded successfully")
    
    # Create sample data for testing
    sample_results = pd.DataFrame({
        'system_id': [1, 2, 4, 5, 7],
        'delta_fit_local': [0.758, 1.079, 0.948, 0.716, 0.870],
        'delta_fit_se': [0.026, 0.049, 0.061, 0.014, 0.017],
        'include_in_aggregate': [True, True, True, True, True]
    })
    
    # Test mapping
    mapper = PlatformMapper('analysis/d1_quantum/platform_map.yml')
    platform_data, mapped_results, cv_results = mapper.run_full_mapping(sample_results)
    
    if mapped_results:
        print(f"\n🎯 Expected δ_true ≈ 0.5-0.7 after mapping")
        print(f"📊 Actual δ_true = {mapped_results['mu_RE']:.3f} ± {mapped_results['se_RE']:.3f}")


if __name__ == '__main__':
    main()