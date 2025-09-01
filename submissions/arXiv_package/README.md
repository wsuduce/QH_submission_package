# arXiv Submission Package

## Preprint Ready for arXiv

This folder contains the complete submission package for arXiv.

### Files Included:
- `main.tex` - Main manuscript in preprint format (single column)
- `content.tex` - Main content converted from markdown
- `refs.bib` - Complete bibliography with all 15 references
- `main.bbl` - Pre-compiled bibliography (prevents TeXLive version issues)
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

### arXiv Submission:

#### Option 1: Web Interface
1. Go to https://arxiv.org/submit
2. Upload this entire folder as a zip/tar file
3. Set primary classification: astro-ph.CO (Cosmology and Nongalactic Astrophysics)
4. Add cross-lists: gr-qc, quant-ph

#### Option 2: Email/FTP (if large)
Follow arXiv instructions for large submissions

### Submission Checklist:
- [ ] Compile PDF and verify formatting
- [ ] Check all figures display correctly
- [ ] Verify bibliography completeness
- [ ] Choose appropriate subject classifications
- [ ] Write clear abstract and title
- [ ] Review arXiv submission policies

### arXiv Categories:
- **Primary**: astro-ph.CO (Cosmology and Nongalactic Astrophysics)
- **Cross-lists**: 
  - gr-qc (General Relativity and Quantum Cosmology)
  - quant-ph (Quantum Physics)

### Formatting Notes:
- Using REVTeX 4.2 preprint style (single column)
- No table of contents for arXiv submission
- All figures sized appropriately for single column
- Bibliography style: apsrev4-2

### Version: v2.3-final
### Date: August 30, 2025

### arXiv Identifier:
Will be assigned upon submission (format: YYMM.NNNNN)