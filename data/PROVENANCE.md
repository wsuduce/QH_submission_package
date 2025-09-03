# MIDIS Flux Bins — Provenance

**Status:** Finalized. Data extracted and verified.

- **Source dataset(s):** JWST MIDIS / CEERS (VizieR Catalog: `J/A+A/696/A57`)
- **Selection/cuts:** `zph > 4`; `SNR_F560W > 5` (implicit via valid magnitude); `quality_flags_ok` (assumed for catalog sources). Note: `logMstar > 10` cut was not applied as stellar mass data is not available in the source catalog.
- **Binning:** 4 bins with edges at z = [4, 5, 6, 7, 8].
- **Observable definition:** `g` is the **mean F560W flux** per bin. `g_err` is the **standard error of the mean**.
- **Extraction script:** `scripts/midis_extract.py`
- **Extraction date (UTC):** 2025-09-03 18:53:51
- **Repro check:** `python scripts/midis_data_gate.py data/midis_bins.csv` → `k_fit` = 0.528 (PASS)
- **SHA256:** `EDF89D28BD2626C1B3193DCC262283101A80CACE8B555253CC1D7308DC792982`
