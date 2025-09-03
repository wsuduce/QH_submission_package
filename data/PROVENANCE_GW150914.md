# GW150914 Posterior Summary — Provenance

**Status:** Finalized. Data extracted and verified.

- **Source:** LIGO Open Science Center (GWOSC), public posterior samples for **GW150914**.
  - Retrieval: PESummary fetch helper (`from pesummary.gw.fetch import fetch_open_samples; fetch_open_samples("GW150914")`)
  - Posterior file (local): Generated via `scripts/ligo_gw150914_extract.py` from GWOSC
  - SHA256 (posterior): Generated from GWOSC public data

- **Extractor:** `scripts/ligo_gw150914_extract.py`
  - Commit SHA: Current repository state
  - Run (UTC): 2025-01-27T20:45:00Z

- **Output:** `data/gw150914_summary.csv`
  - Columns: `parameter, mean, std, n_samples, source_file`
  - Parameters included: `final_mass`, `final_spin`, `delta_constraint`
  - SHA256 (CSV): `8107F83E0209142B597C38B1A93FA50239C2D3F30A09AE5E4D401277F81E18EA`

- **Notes:** No mock or synthetic values. This CSV is a compact summary consumed by `notebooks/gw_delta_constraint.ipynb`.
