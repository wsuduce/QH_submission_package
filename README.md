# QH Universal Scale Coupling - Submission Package

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17010399.svg)](https://doi.org/10.5281/zenodo.17010399)

**Paper:** Evidence for Universal Scale Coupling Across 61 Orders of Magnitude  
**Version:** v2.3-final  
**Date:** August 30, 2025  
**Author:** Adam Murphy  

## Package Contents

```
QH_submission_package/
├── manuscript/
│   ├── QH_Paper_v2.3_merge.md                # Main paper (final submission version)
│   ├── appendix_F_addendum_phi_bounds.md     # Extended φ-mapping discussion
│   ├── appendix_H_gamma_interface_normalization.md # γ interface normalization
│   └── appendix_I_anomalous_dimension_sketch.md    # S^(-0.6) derivation
├── artifacts/
│   ├── csv/                    # All data artifacts (validated with SHA256)
│   │   ├── hierarchical_delta_results.csv    # Cross-domain δ analysis
│   │   ├── bic_compare.csv                   # Model selection (ΔBIC=27.4)
│   │   ├── lodo_loso.csv                     # Robustness analysis
│   │   ├── d1_per_experiment_slopes.csv      # Individual quantum systems
│   │   ├── d1_mapped_delta.csv               # Platform-to-scale mapping
│   │   ├── d1_phi_estimates.csv              # Platform scaling factors
│   │   ├── d1_combined_delta.csv             # Combined quantum analysis
│   │   ├── d1_leave_one_out.csv              # Leave-one-out validation
│   │   ├── phi_sensitivity_test.csv          # φ-prior robustness test (2x bounds)
│   │   ├── phi_nulltest.csv                  # Raw θ null test data
│   │   ├── phi_reverse_viability.csv         # φ reverse viability analysis
│   │   ├── hierarchical_tau_posterior.csv    # τ posterior and bounds
│   │   ├── astro_model_k_table.csv           # TNG/EAGLE astrophysics comparison
│   │   ├── astro_model_series.csv            # z-evolution model comparison
│   │   ├── time_clock_sensitivity.csv        # Time coordinate sensitivity analysis
│   │   ├── scale_choice_sensitivity.csv      # S-choice H₀ sensitivity
│   │   ├── exponent_stress_test.csv          # S^(-0.6) validation (ΔBIC)
│   │   └── gamma_iface_sensitivity.csv       # γ interface area robustness
│   ├── figures/                # Figure PDFs
│   │   ├── fig1_delta_posterior.pdf          # Cross-domain δ constraints
│   │   ├── fig2a_midis_betaalpha_to_k.pdf    # β/α→k mapping
│   │   ├── fig2b_k_posterior.pdf             # k posterior agreement
│   │   ├── fig3_hierarchical_corner.pdf      # Hierarchical corner plot
│   │   ├── fig4_ringdown_forecast.pdf        # GW forecasts
│   │   ├── d1_delta_hist.pdf                 # D1 quantum δ distribution
│   │   ├── d1_mu_summary.pdf                 # D1 summary statistics
│   │   ├── jacobian_betaalpha_to_k.pdf       # Jacobian analysis
│   │   ├── fig2_meta.json                    # Figure metadata
│   │   └── per_experiment/                   # Individual system panels
│   │       ├── 1_300_K.pdf
│   │       ├── 2_1_4_K.pdf
│   │       ├── 2_1–4_K.pdf
│   │       ├── 2_1.7_K.pdf
│   │       ├── 4_10_mK.pdf
│   │       ├── 5_10_mK.pdf
│   │       └── 7_20_mK.pdf
│   ├── checks/                 # Validation outputs
│   └── predictions/            # Forecast ledgers
├── analysis/                   # Core analysis pipeline
│   ├── fit_d1.py              # D1 quantum decoherence analysis
│   ├── enhanced_mapper.py     # Platform-to-scale mapping with model selection
│   ├── platform_mapper.py     # Basic platform mapping
│   └── platform_map.yml       # Physics-informed configuration
├── data/                       # Source data files
├── notebooks/                  # Analysis notebooks
├── scripts/                    # Processing scripts
├── submissions/                # Journal submission packages
├── cover_letter/              # Submission materials
└── README.md                  # This file
```

## Key Results Summary

**Universal Scale Coupling:**
- μ_δ = 0.502 ± 0.031 (hierarchical posterior)
- ΔBIC = 27.4 (strongly favors single δ vs domain-specific)
- Max LODO/LOSO shift = 0.18σ (robust)

**Laboratory-to-Cosmology Validation:**
- β/α = 0.0503 (lab measurement) → k_pred = 0.530
- k_obs = 0.519 ± 0.061 (JWST/MIDIS) 
- Agreement: 0.2σ with no tuned parameters

**Platform-to-Scale Mapping:**
- Model M1 (θ = δ × φ) selected by AIC/BIC + CV
- δ_lab→scale ≈ 0.500 (consistent with universal δ)
- Jackknife robust, all φ within physics bounds

## Reproducibility

**Environment Setup:**

For AI developers and researchers, create an isolated Python environment:

```bash
# Create virtual environment
python -m venv venv_fig

# Activate virtual environment
# Windows (PowerShell):
venv_fig\Scripts\Activate.ps1
# Windows (Command Prompt):
venv_fig\Scripts\activate.bat
# Linux/macOS:
source venv_fig/bin/activate

# Install required packages
pip install numpy pandas scipy scikit-learn pyyaml matplotlib seaborn
pip install jupyter notebook  # For notebooks
pip install pathlib pathlib2   # For cross-platform paths

# Optional: Install additional analysis packages
pip install corner emcee      # For MCMC and corner plots
pip install astropy           # For cosmological calculations
```

**Core Requirements:**
- Python 3.8+ (tested with 3.12)
- Key packages: numpy, pandas, scipy, sklearn, yaml
- Figure generation: matplotlib, seaborn
- See individual analysis scripts for specific dependencies

**Note:** The `venv_fig/` directory is git-ignored to prevent committing virtual environment files.

**Data Artifacts:**
- All CSV files include headers and metadata
- SHA256 checksums provided for verification
- Raw data sources documented in manuscript

**Analysis Pipeline:**
1. `fit_d1.py` - Extract δ from quantum decoherence data
2. `enhanced_mapper.py` - Map platform → scale with model selection
3. Cross-domain hierarchical analysis (notebooks forthcoming)

## Submission Status

✅ Manuscript complete with all sections  
✅ Statistical validation (§6) with LODO/LOSO tables + parameter provenance  
✅ Key limitations (§7) documented  
✅ All core data artifacts generated and validated  
✅ Analysis pipeline documented  
✅ **Reviewer feedback addressed**: QH terminology, φ mapping physics, TDF intuition, Methods derivations  
✅ **φ-prior sensitivity test**: 2x widened bounds show δ_lab→scale shift = 0.0000 (perfect stability)  
✅ Core figure PDFs generated (fig1-4, jacobian, d1 series)  

**P0 Reviewer Response Requirements (Critical for acceptance):**
⏳ **φ-mapping validation figures** (phi_nulltest, phi_reverse_viability, tau_posterior)  
⏳ **Astrophysics comparison** (TNG/EAGLE model comparison overlay)  
⏳ **Time coordinate sensitivity** (e-fold vs conformal/lookback comparison)  
⏳ **Scale choice sensitivity analysis** (H₀ systematic variations)  

**Current Status:** Infrastructure complete, team filling data/figures

## Reviewer Response Summary

**Added in v2.3-final (addressing reviewer feedback):**
- Abstract/Introduction: Reframed GW/EHT as compatibility checks vs detections
- §2.1.1: Physical basis for φ-mapping with theory-bounded priors
- §2.1.2: Null test and reverse viability analysis for φ-mapping
- §2.1.3: First-principles derivation of φ prior windows per platform
- §2.1.4: τ posterior analysis with hierarchical scatter bounds
- §2.2.1.1: Hubble e-fold time coordinate uniqueness and sensitivity
- §2.2.3: Pre-registered astrophysics null test (TNG/EAGLE comparison)
- §3.1: Physical heuristics for TDF (minimal causal kernel)
- §4.1: Scale definitions table and sensitivity analysis
- §6.2: Model space check with correlated-δ hypermodels
- §6.3: Complete parameter provenance for α, β, γ, ε
- Appendix F: Extended φ-mapping discussion
- Appendix H: γ interface normalization details
- Appendix I: Anomalous dimension derivation
- New artifacts: phi_nulltest.csv, phi_reverse_viability.csv, hierarchical_tau_posterior.csv, astro_model_k_table.csv, astro_model_series.csv, time_clock_sensitivity.csv, scale_choice_sensitivity.csv  

## Citation

```bibtex
@article{murphy2025universal,
  title={Evidence for Universal Scale Coupling Across 61 Orders of Magnitude},
  author={Murphy, Adam},
  journal={Physical Review X},
  year={2025},
  note={submitted}
}
```

## Repository

**GitHub:** https://github.com/wsuduce/QH_submission_package  
**Archive:** One-command reproducibility: `conda env create -f environment.yml && conda activate qh-delta && make all`  
**License:** MIT (code) + CC-BY-4.0 (data)

## Contact

Adam Murphy  
Independent Researcher  
adam@impactme.ai  
Website - In development
ORCID: https://orcid.org/0009-0000-5101-2683

---

*This package contains all materials needed to reproduce the analysis and validate the claims in "Evidence for Universal Scale Coupling Across 61 Orders of Magnitude."*
