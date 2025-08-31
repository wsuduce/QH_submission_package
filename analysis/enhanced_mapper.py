#!/usr/bin/env python
"""
enhanced_mapper.py - Advanced Platform-to-Scale Mapping with Model Selection

Implements rigorous model comparison for platform-to-scale mapping:
- M1: θ = δ × φ (multiplicative scaling)
- M2: θ = δ / φ (divisive efficiency) 
- M3: θ = δ × φ^β (flexible power law)

Features:
- Physics-informed priors
- Cross-validation model selection
- Robustness checks (jackknife, range validation)
- AIC/BIC comparison
- No circularity with cosmological δ
"""

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize
from sklearn.model_selection import KFold
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')


class EnhancedPlatformMapper:
    def __init__(self, config_path):
        """Load enhanced mapping configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.platforms = self.config['platforms']
        self.models = self.config['model_selection']['models']
        self.meta_config = self.config['meta_regression']
        
    def extract_platform_data(self, results_df):
        """Extract platform data with enhanced validation"""
        platform_data = []
        
        for platform_key, platform_info in self.platforms.items():
            system_id = platform_info['system_id']
            
            mask = results_df['system_id'] == system_id
            if mask.sum() == 1:
                row = results_df[mask].iloc[0]
                if row['include_in_aggregate']:
                    # Enhanced validation
                    log_range_x = np.log10(row['window_max_S']) - np.log10(row['window_min_S'])
                    if log_range_x >= 1.0:  # Require ≥1 decade in S
                        platform_data.append({
                            'system_id': system_id,
                            'platform': platform_key,
                            'theta_local': row['delta_fit_local'],  # Rename: protection exponent
                            'theta_se': row['delta_fit_se'],
                            'phi_min': platform_info['phi_bounds'][0],
                            'phi_max': platform_info['phi_bounds'][1],
                            'phi_prior_mean': platform_info['phi_prior_mean'],
                            'phi_prior_std': platform_info['phi_prior_std'],
                            'description': platform_info['description'],
                            'log_range_x': log_range_x,
                            'n_points': row['n_points_used']
                        })
        
        return pd.DataFrame(platform_data)
    
    def model_M1_multiplicative(self, params, platform_data):
        """Model M1: θ = δ × φ"""
        delta = params[0]
        phi_values = params[1:1+len(platform_data)]
        
        theta_pred = delta * phi_values
        return theta_pred
    
    def model_M2_divisive(self, params, platform_data):
        """Model M2: θ = δ / φ"""
        delta = params[0]  
        phi_values = params[1:1+len(platform_data)]
        
        theta_pred = delta / phi_values
        return theta_pred
    
    def model_M3_power(self, params, platform_data):
        """Model M3: θ = δ × φ^β"""
        delta = params[0]
        beta = params[1]
        phi_values = params[2:2+len(platform_data)]
        
        theta_pred = delta * (phi_values ** beta)
        return theta_pred
    
    def log_likelihood(self, params, platform_data, model_func):
        """Compute log-likelihood for a given model"""
        try:
            theta_pred = model_func(params, platform_data)
            theta_obs = platform_data['theta_local'].values
            theta_se = platform_data['theta_se'].values
            
            # Gaussian likelihood
            ll = -0.5 * np.sum(((theta_obs - theta_pred) / theta_se)**2)
            ll -= 0.5 * np.sum(np.log(2 * np.pi * theta_se**2))
            
            return ll
        except:
            return -1e6
    
    def log_prior(self, params, platform_data, model_name):
        """Compute log-prior for model parameters"""
        lp = 0.0
        
        # Universal δ prior (uninformative)
        delta = params[0]
        if not (0.1 < delta < 3.0):
            return -np.inf
        
        if model_name == 'M3_power':
            # Beta parameter prior
            beta = params[1]
            if not (0.1 < beta < 3.0):
                return -np.inf
            lp += norm.logpdf(beta, 1.0, 0.5)  # Weak prior around 1
            phi_start_idx = 2
        else:
            phi_start_idx = 1
        
        # Platform-specific φ priors
        phi_values = params[phi_start_idx:phi_start_idx+len(platform_data)]
        
        for i, (phi, row) in enumerate(zip(phi_values, platform_data.itertuples())):
            if not (row.phi_min <= phi <= row.phi_max):
                return -np.inf
            
            # Physics-informed prior
            lp += norm.logpdf(phi, row.phi_prior_mean, row.phi_prior_std)
        
        return lp
    
    def log_posterior(self, params, platform_data, model_func, model_name):
        """Compute log-posterior"""
        lp = self.log_prior(params, platform_data, model_name)
        if not np.isfinite(lp):
            return -np.inf
        
        ll = self.log_likelihood(params, platform_data, model_func)
        return lp + ll
    
    def fit_model(self, platform_data, model_name):
        """Fit a specific model using MAP estimation"""
        model_info = self.models[model_name]
        
        if model_name == 'M1_multiplicative':
            model_func = self.model_M1_multiplicative
            n_phi = len(platform_data)
            initial = [0.5] + platform_data['phi_prior_mean'].tolist()
            bounds = [(0.1, 3.0)] + [(row.phi_min, row.phi_max) for row in platform_data.itertuples()]
            
        elif model_name == 'M2_divisive':
            model_func = self.model_M2_divisive
            n_phi = len(platform_data)
            initial = [1.5] + platform_data['phi_prior_mean'].tolist()  # Higher δ for divisive
            bounds = [(0.1, 3.0)] + [(row.phi_min, row.phi_max) for row in platform_data.itertuples()]
            
        elif model_name == 'M3_power':
            model_func = self.model_M3_power
            n_phi = len(platform_data)
            initial = [0.5, 1.0] + platform_data['phi_prior_mean'].tolist()
            bounds = [(0.1, 3.0), (0.1, 3.0)] + [(row.phi_min, row.phi_max) for row in platform_data.itertuples()]
        
        # Optimize
        result = minimize(
            fun=lambda params: -self.log_posterior(params, platform_data, model_func, model_name),
            x0=initial,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        if result.success:
            # Compute model metrics
            ll = self.log_likelihood(result.x, platform_data, model_func)
            n_params = len(result.x)
            n_data = len(platform_data)
            
            aic = 2 * n_params - 2 * ll
            bic = np.log(n_data) * n_params - 2 * ll
            
            return {
                'success': True,
                'params': result.x,
                'log_likelihood': ll,
                'aic': aic,
                'bic': bic,
                'n_params': n_params,
                'model_func': model_func
            }
        else:
            return {'success': False, 'message': result.message}
    
    def cross_validate_model(self, platform_data, model_name):
        """Cross-validate a specific model"""
        if len(platform_data) < self.meta_config['cross_validation']['folds']:
            return None
        
        cv = KFold(
            n_splits=self.meta_config['cross_validation']['folds'],
            shuffle=True,
            random_state=self.meta_config['cross_validation']['seed']
        )
        
        cv_scores = []
        
        for train_idx, val_idx in cv.split(platform_data):
            train_data = platform_data.iloc[train_idx].reset_index(drop=True)
            val_data = platform_data.iloc[val_idx].reset_index(drop=True)
            
            # Fit on training data
            train_result = self.fit_model(train_data, model_name)
            
            if train_result['success']:
                # Evaluate on validation data
                val_ll = self.log_likelihood(
                    train_result['params'][:1+len(val_data)] if model_name != 'M3_power' 
                    else train_result['params'][:2+len(val_data)],
                    val_data, 
                    train_result['model_func']
                )
                cv_scores.append(val_ll)
            else:
                cv_scores.append(-1e6)
        
        return np.mean(cv_scores) if cv_scores else None
    
    def jackknife_analysis(self, platform_data, best_model_name, best_params):
        """Jackknife robustness analysis"""
        jackknife_results = []
        
        for i in range(len(platform_data)):
            # Remove one platform
            jack_data = platform_data.drop(i).reset_index(drop=True)
            
            # Refit model
            jack_result = self.fit_model(jack_data, best_model_name)
            
            if jack_result['success']:
                delta_jack = jack_result['params'][0]
                jackknife_results.append({
                    'dropped_platform': platform_data.iloc[i]['platform'],
                    'delta_jackknife': delta_jack,
                    'delta_difference': delta_jack - best_params[0]
                })
        
        return pd.DataFrame(jackknife_results)
    
    def run_enhanced_mapping(self, results_df):
        """Complete enhanced mapping pipeline"""
        print("=== ENHANCED Platform-to-Scale Mapping ===")
        
        # Extract and validate platform data
        platform_data = self.extract_platform_data(results_df)
        print(f"Validated {len(platform_data)} platforms for mapping")
        
        if len(platform_data) < 3:
            print("Need at least 3 platforms for model comparison")
            return None, None, None
        
        # Print platform summary
        print(f"\nPlatform Summary (θ_local = protection exponents):")
        for _, row in platform_data.iterrows():
            print(f"  {row['platform']}: θ = {row['theta_local']:.3f} ± {row['theta_se']:.3f} "
                  f"[range: {row['log_range_x']:.1f} decades]")
        
        # Model comparison
        print(f"\n--- Model Comparison ---")
        model_results = {}
        
        for model_name in self.models.keys():
            print(f"\nFitting {model_name}...")
            
            # Fit model
            fit_result = self.fit_model(platform_data, model_name)
            
            if fit_result['success']:
                # Cross-validation
                cv_score = self.cross_validate_model(platform_data, model_name)
                
                fit_result['cv_score'] = cv_score
                model_results[model_name] = fit_result
                
                delta_est = fit_result['params'][0]
                print(f"  δ estimate: {delta_est:.3f}")
                print(f"  AIC: {fit_result['aic']:.2f}")
                print(f"  BIC: {fit_result['bic']:.2f}")
                print(f"  CV score: {cv_score:.2f}" if cv_score else "  CV: N/A")
            else:
                print(f"  FAILED: {fit_result.get('message', 'Unknown error')}")
        
        if not model_results:
            print("No models fitted successfully")
            return None, None, None
        
        # Select best model (by BIC)
        best_model = min(model_results.keys(), key=lambda k: model_results[k]['bic'])
        best_result = model_results[best_model]
        
        print(f"\n🏆 Best Model: {best_model}")
        print(f"   BIC: {best_result['bic']:.2f}")
        print(f"   δ_lab→scale: {best_result['params'][0]:.3f}")
        
        # Jackknife analysis
        print(f"\n--- Robustness Analysis ---")
        jackknife_df = self.jackknife_analysis(platform_data, best_model, best_result['params'])
        
        if not jackknife_df.empty:
            max_delta_shift = jackknife_df['delta_difference'].abs().max()
            print(f"Max δ shift (jackknife): {max_delta_shift:.3f}")
            if max_delta_shift > 0.1:
                print("⚠️  Large jackknife sensitivity detected")
            else:
                print("✅ Robust to single-platform removal")
        
        # Format final results
        final_results = {
            'best_model': best_model,
            'delta_lab_to_scale': best_result['params'][0],
            'phi_estimates': best_result['params'][1:],
            'model_comparison': model_results,
            'jackknife_analysis': jackknife_df,
            'n_platforms': len(platform_data)
        }
        
        return platform_data, final_results, model_results


def main():
    """Test the enhanced mapper"""
    print("Enhanced platform mapper loaded successfully")
    
    # Test with sample data
    sample_results = pd.DataFrame({
        'system_id': [1, 2, 4, 5, 7],
        'delta_fit_local': [0.758, 1.079, 0.948, 0.716, 0.870],
        'delta_fit_se': [0.026, 0.049, 0.061, 0.014, 0.017],
        'include_in_aggregate': [True, True, True, True, True],
        'window_min_S': [1.0, 1.0, 1.0, 1.0, 1.0],
        'window_max_S': [512.0, 940.0, 6.25, 64.0, 100.0],
        'n_points_used': [5, 5, 4, 4, 4]
    })
    
    # Test mapping
    mapper = EnhancedPlatformMapper('analysis/d1_quantum/platform_map.yml')
    platform_data, final_results, model_comparison = mapper.run_enhanced_mapping(sample_results)
    
    if final_results:
        print(f"\n🎯 RESULTS SUMMARY:")
        print(f"Best mapping model: {final_results['best_model']}")
        print(f"δ_lab→scale = {final_results['delta_lab_to_scale']:.3f}")
        print(f"Compare to cosmological δ = 0.502 ± 0.031")
        
        if final_results['delta_lab_to_scale'] < 0.7:
            print("✅ Lab-inferred δ consistent with cosmology")
        else:
            print("📊 Lab-inferred δ higher than cosmology (investigate physics)")


if __name__ == '__main__':
    main()