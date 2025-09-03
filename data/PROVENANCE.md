# MIDIS+CEERS Cross-Match Data — Provenance

**Status:** Finalized. Data extracted and verified.

- **Source Catalogs:**
  - `J/A+A/696/A57` (MIDIS/CEERS): For F560W magnitudes and photometric redshifts.
  - `J/AJ/168/113` (CEERS): For stellar masses (`logMst`).
- **Cross-Match:** 1.0" radius, nearest neighbor coordinate matching
- **Selection Cuts:**
  - `zph > 4` (redshift cut)
  - `logM* > 10` (stellar mass cut)
- **Completeness Cut:** Uniform faint-end magnitude limit of `Fap560Wmag < 26.85` applied to all sources. This limit was determined from the 95th percentile of sources in the highest redshift bin (`z=[7,8)`).
- **Binning:** 4 uniform bins with edges at z = [4, 5, 6, 7, 8].
- **Observable Definition:** `g` is the **mean F560W flux** per bin. `g_err` is the **standard error of the mean**.
- **Extraction Script:** `scripts/ceers_midis_crossmatch.py`
- **Extraction Date (UTC):** 2025-09-03 20:13:20
- **SHA256:** `370745AE4E9ADC8C4398A6E303AAB8A76E565FD1EB8380B363EBE014E6F89C53`
- **Validator Results:** `k_fit` = 0.519 (PASS) within tolerance of k_target = 0.523
