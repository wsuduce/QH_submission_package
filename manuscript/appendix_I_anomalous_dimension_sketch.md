# Appendix I — Sketch: Why S^{-0.6}? (Anomalous-Dimension Motive)

**Goal.** Motivate the empirical correction ∝ S^{-(1-η)} with η≈0.4 that appears in late-time, large-S limits.

**Setup.** Coarse-grain the system by a linear factor b (so S → b^2 S under scale pooling). Let the
interface-correlated part of fluctuations carry an anomalous dimension η, such that the two-point
correlator of the protected mode family scales as G_b(ℓ) ∝ b^{-(d-2+η)} G(ℓ/b), with d≈3 the
embedding dimension relevant to our observational kernels.

**Integrated correction.** The observable correction δO at scale S receives contributions from
modes up to a cutoff Λ(S) ∝ S^{-1/2}. With spectral density ∝ k^{-(1+η)} at low k (matching
1/f^{1+η} noise observed across quantum platforms), the integrated variance scales as
∫^{Λ(S)} k^2 · k^{-(1+η)} dk ∝ Λ(S)^{(2-η)} ∝ S^{-(1-η)}.

Thus, for η≈0.4 we obtain the empirical exponent 1−η≈0.6 used in the text. This matches the
mild, slowly-decaying corrections required by the H(z,S) and growth-runner terms.

**Stress tests (pre-registered).** We fit exponents in the window 0.5–0.7:
- β_alt = 0.5 (i.e., S^{-0.5}) yields a modest ΔBIC penalty relative to 0.6.
- β_alt = 0.7 (i.e., S^{-0.7}) also degrades fit quality.
See `exponent_stress_test.csv` for the summary; code path in `methods/exponent_scan.ipynb`.
