# QH Universal Scale Coupling - Submission Package

**Paper:** Evidence for Universal Scale Coupling Across 61 Orders of Magnitude  
**Version:** V2.0-pre  
**Date:** August 2025  
**Author:** Adam Murphy  

## Package Contents

```
QH_submission_package/
├── manuscript/
│   ├── QH_Paper_V2.md                  # Main paper manuscript (final version)
│   └── QH_Paper_V2_REVIEWER_READY.md   # Updated version addressing reviewer feedback
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
│   │   └── checksums.txt                     # SHA256 verification
│   └── figures/                # Figure PDFs (when generated)
│       ├── d1_delta_hist.pdf                 # D1 quantum δ distribution
│       ├── d1_mu_summary.pdf                 # D1 summary statistics
│       └── per_experiment/                   # Individual system panels
├── analysis/                   # Core analysis pipeline
│   ├── fit_d1.py              # D1 quantum decoherence analysis
│   ├── enhanced_mapper.py     # Platform-to-scale mapping with model selection
│   ├── platform_mapper.py     # Basic platform mapping
│   └── platform_map.yml       # Physics-informed configuration
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
- k_obs = 0.523 ± 0.058 (JWST/MIDIS) 
- Agreement: 0.1σ with no tuned parameters

**Platform-to-Scale Mapping:**
- Model M1 (θ = δ × φ) selected by AIC/BIC + CV
- δ_lab→scale ≈ 0.500 (consistent with universal δ)
- Jackknife robust, all φ within physics bounds

## Reproducibility

**Environment:**
- Python 3.8+
- Key packages: numpy, pandas, scipy, sklearn, yaml
- See analysis scripts for specific dependencies

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
✅ All data artifacts generated and validated  
✅ Analysis pipeline documented  
✅ **Reviewer feedback addressed**: QH terminology, φ mapping physics, TDF intuition, Methods derivations  
✅ **φ-prior sensitivity test**: 2x widened bounds show δ_lab→scale shift = 0.0000 (perfect stability)  
⏳ Figure PDFs (being generated)  
⏳ Jupyter notebooks (final organization)

## Reviewer Response Summary

**Added in V2.0-reviewer:**
- §2.1.1: Physical basis for platform-to-scale mapping with φ bounds  
- §6.3: Complete parameter provenance for α, β, γ, ε  
- TDF intuition paragraph in §3 Mathematical Framework  
- QH terminology clarification in Introduction  
- Methods supplement with derivation sketches for γ normalization and S^{-0.6}  
- Appendix D4 enhanced with φ-sensitivity analysis (perfect numerical stability)  
- Figure 1 caption clarification on consistency vs measurement bands  

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

## Contact

Adam Murphy  
Independent Researcher  
[Contact information for correspondence]

---

*This package contains all materials needed to reproduce the analysis and validate the claims in "Evidence for Universal Scale Coupling Across 61 Orders of Magnitude."*