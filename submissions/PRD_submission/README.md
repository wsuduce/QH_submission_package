# PRD Submission Package

## Physical Review D - Ready for Submission

This folder contains the complete submission package for Physical Review D.

### Files Included:
- `main.tex` - Main manuscript in REVTeX 4.2 format (two-column)
- `refs.bib` - Complete bibliography with all 15 references
- `COVER_LETTER_PRD.txt` - Cover letter to the editor
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
- [ ] Upload to PRD submission system
- [ ] Include cover letter
- [ ] Add suggested reviewers (optional)

### PRD Submission Portal:
https://authors.aps.org/

### Manuscript Classification:
- Section: Gravitation and Cosmology
- Keywords: scale coupling, cosmological tensions, dark energy, gravitational waves

### Formatting Notes:
- Using REVTeX 4.2 with `twocolumn` option for journal style
- Figures sized for single column width (0.9\columnwidth)
- Bibliography style: apsrev4-2
- All special characters (δ, α, β, etc.) properly escaped in LaTeX

### Version: v2.3-final
### Date: August 30, 2025