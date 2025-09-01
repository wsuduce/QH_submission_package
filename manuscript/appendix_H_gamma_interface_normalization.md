# Appendix H — Interface Area A_iface and γ Normalization

We define γ via the common basis
\[\gamma \equiv \frac{S_{\rm info}}{A_{\rm iface}/\ell_P^2}\]
where \(S_{\rm info}\) is the entropy/information at the measurement interface and \(A_{\rm iface}\)
is the *effective interface area* appropriate to the domain.

## Domain definitions
**Black hole (BH).** \(A_{\rm iface} = A_{\rm horizon} = 4\pi r_s^2\) (spin corrections handled
in the systematics). \(S_{\rm info} = S_{BH} = A_{\rm horizon}/(4G)\).

**Cosmology.** We use the comoving interface associated with the density-peak scale contributing
maximally to the observable, \(A_{\rm iface} \sim \pi R_{\rm peak}^2\), with \(R_{\rm peak}\) read
from the window of the estimator (e.g., BAO/growth kernel).

**Quantum platforms.** The interface is the effective coherence aperture of the readout/control
manifold: \(A_{\rm iface} \sim \pi L_{\perp}^2\), where \(L_{\perp}\) is the transverse coherence
extent defined by the experiment (mode waist, device scale, or ensemble radius).

## Sensitivity and alternatives
We vary each \(A_{\rm iface}\) by a conservative factor of 2 in radius (×4 in area). The combined γ
changes by ≤ 0.2σ, with per-domain shifts partially anti-correlated (see `gamma_iface_sensitivity.csv`).

This indicates that consistency of γ across domains is not the result of a finely tuned \(A_{\rm iface}\)
choice, but a robust feature under reasonable geometric alternatives.
