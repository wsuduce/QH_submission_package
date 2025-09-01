# JCAP Submission Package

## Journal of Cosmology and Astroparticle Physics - Ready for Submission

This folder contains the complete submission package for JCAP.

### Files Included:
- `main.tex` - Main manuscript in JCAP format (single column)
- `content.tex` - Main content converted from markdown
- `refs.bib` - Complete bibliography with all 15 references
- `COVER_LETTER_JCAP.txt` - Cover letter to the editor
- `Makefile` - Compilation script

### How to Compile:

#### Option 1: Local LaTeX
```bash
make pdf
# or manually:
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

#### Option 2: Overleaf
1. Upload this entire folder to Overleaf
2. Set `main.tex` as the main document
3. Compile will happen automatically

### Figures:
The LaTeX file expects figures at `../../artifacts/figures/`:
- `fig1_delta_posterior.pdf`
- `fig2_beta_over_alpha_to_k.pdf`
- `fig3_hierarchical_corner.pdf`
- `fig4_ringdown_forecast.pdf`

### Submission Checklist:
- [ ] Compile PDF and check formatting
- [ ] Verify all equations render correctly
- [ ] Check figure quality and captions
- [ ] Review references for completeness
- [ ] Upload to JCAP submission system
- [ ] Include cover letter
- [ ] Add suggested reviewers (optional)

### JCAP Submission Portal:
https://mc.manuscriptcentral.com/jcap

### Manuscript Classification:
- Section: Cosmology and Dark Energy
- Keywords: dark energy, modified gravity, quantum mechanics, cosmological tensions

### Formatting Notes:
- Using JHEP document class (standard for JCAP)
- Single column format with proper JCAP styling
- Bibliography style: JHEP
- All special characters (δ, α, β, etc.) properly escaped in LaTeX

### Version: v2.3-final
### Date: August 30, 2025