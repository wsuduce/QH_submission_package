# EHT Priors — Provenance

**Status:** Finalized. Priors encoded from published EHT results.

- **Sources:**
  - Sgr A* 2017 EHT results (ApJL 930 L12–L20 series). Key values mapped to (delta, sigma).
  - M87* 2017–2018 EHT shadow measurements (2019 results and follow-ons). Key values mapped to (delta, sigma).

- **File:** `data/eht_priors.json`
  - Schema: 
    ```json
    {
      "SgrA": {"delta": <float>, "sigma": <float>},
      "M87":  {"delta": <float>, "sigma": <float>},
      "metadata": {"notes": "...", "units": "dimensionless", "ref": ["<citations>"]}
    }
    ```
  - SHA256 (JSON): `11A91E27ED89A983D48398FE3EE40E9D93A4F9DD3B8FD62562B667840B65AE05`
  - Created (UTC): 2025-01-27T20:45:00Z
  - Script/Notebook: `scripts/eht_extract.py`

- **Notes:** These are priors consumed by `notebooks/eht_delta_constraint.ipynb`. No synthetic entries.
