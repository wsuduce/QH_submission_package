# Training Wheels — PR Sprint (QH δ v2.3)

A clean, final checklist from the *current* bedrock state. Do these in order. If a step takes >5 minutes, park it and move on — we'll loop back.

---

## 0) Mindset (60s)

* We are integrating, not inventing. The single‑source dataset and validators keep us safe.
* Numbers live in captions; legends stay generic. Gate + smoke must pass.

---

## 1) Data & Provenance — Single Source of Truth (3 min)

* **Dataset of record:** `data/midis_f560w_masslim.csv` (F560W, CEERS×MIDIS cross‑match, logM\*>10, uniform faint‑end, 4 bins).
* **Provenance:** `data/PROVENANCE_CROSSMATCH.md` (real SHA256 + extraction details).
* **Gate:**

  ```bash
  python scripts/midis_data_gate.py data/midis_f560w_masslim.csv \
    --tol 0.05 --pred 0.530 --outdir artifacts/checks
  ```

  Expect **PASS**; commit the three outputs in `artifacts/checks/`.
* Canonicals used everywhere: **k\_obs = 0.519 ± 0.061**, **k\_pred = 0.530**, agreement ≈ **0.2σ**.

---

## 2) Notebooks — Paths & Smoke (6–8 min)

* Rule: notebooks execute with CWD = `notebooks/`. Use `../data/...` or a parameter cell.
* Ensure these paths (or parameters) exist:

  * `../data/midis_f560w_masslim.csv`
  * `../data/gw150914_summary.csv`
  * `../data/eht_priors.json`
* Clear outputs → Restart kernel → Run all for:

  * `notebooks/eht_delta_constraint.ipynb`
  * `notebooks/gw_delta_constraint.ipynb`
  * `notebooks/mcmc_k_equals_c_beta_over_alpha.ipynb`
* CI smoke (papermill) in PR:

  ```bash
  papermill notebooks/mcmc_k_equals_c_beta_over_alpha.ipynb artifacts/checks/mcmc_k.out.ipynb -p DATA_CSV ../data/midis_f560w_masslim.csv
  papermill notebooks/gw_delta_constraint.ipynb artifacts/checks/gw_delta.out.ipynb -p GW_SUMMARY ../data/gw150914_summary.csv
  papermill notebooks/eht_delta_constraint.ipynb artifacts/checks/eht_delta.out.ipynb -p EHT_PRIORS ../data/eht_priors.json
  ```

  PR must **fail** if any notebook fails.

---

## 3) Figure 2 — Final Files & Caption (4 min)

* Files (and only these):

  * `artifacts/figures/fig2a_midis_betaalpha_to_k.pdf`
  * `artifacts/figures/fig2b_k_posterior.pdf`
* Legend (generic): Best fit (MIDIS posterior) • Prediction from β/α • 68% credible • 68% posterior predictive.
* **Caption (paste verbatim):**

  > **Figure 2. Laboratory β/α maps to cosmological k with no tuned parameters.** (a) Mean F560W flux g(z) vs. redshift (log‑y; anchor z\_ref=6) after CEERS×MIDIS cross‑match with logM\* > 10 and a uniform faint‑end limit. **Solid:** best‑fit k\_obs = 0.519 ± 0.061; **thin band:** 68% credible; **wide band:** 68% posterior predictive. **Dashed:** parameter‑free prediction from β/α = 0.0503 mapped via E(z), k\_pred = 0.530. (b) Posterior for k with markers at k\_obs and k\_pred; 68% interval shaded. Agreement ≈ 0.2σ.

---

## 4) Manuscript Sync (5 min)

* **§D3 Methods:** mass‑limited F560W, 1.0″ CEERS×MIDIS match, faint‑end = 95th percentile of z∈\[7,8) applied to all bins; SEM uncertainties; k consistent with k\_pred.
* **§7 Key Limitations — Observable Sensitivity:** raw mean‑flux bias (k \~ 0.35–0.42) vs. convergence (\~0.52) under mass/completeness; peak‑proxy noted in Supplement.
* **Fig.1 caption:** ΔBIC = 27.4; LODO/LOSO max shift 0.18σ; GW/EHT **hatched/semi‑transparent**.
* **Abstract:** tempered‑universality sentence (two constrain; two compatibility checks).
* **PRD wrapper:**

  ```tex
  \documentclass[aps,prd,preprint,onecolumn,nofootinbib,longbibliography]{revtex4-2}
  ```

  No table of contents.

---

## 5) Repo Hygiene & Guardrails (3 min)

* Only SST CSV under `data/`; alternates live in `experiments/` and are excluded from builds.
* Pre‑commit hook blocks provisional filenames and edits to SST CSV unless provenance changes in same commit.
* CI must run **Data Gate** + **Notebook Smoke** as required checks before merge.
* Environment pinned (`requirements.txt` or `environment.yml`).

---

## 6) Open PR (2 min)

* Branch: `v2.3-cleanroom → main`.
* Required checks: **Data Gate PASS** + **Notebook Smoke PASS**.
* After merge: tag `v2.3-final-data`; record commit SHA + CSV SHA256 in Data Availability; update Zenodo to this tag.

---

## 7) Submission Sprint (5–8 min)

* **arXiv** (astro-ph.CO; cross‑list gr‑qc, quant‑ph): upload source (TeX + figs + `.bbl`).
* **PRD**: PDF for review + source zip; cover letter emphasizing falsifiable predictions, ΔBIC, β/α→k mapping, open artifacts.
* **JCAP** stays ready as Plan B.

---

## If something fails (triage)

* Gate fail: verify SST CSV hash + rerun extractor; ensure `--tol 0.05` set; check that caption numbers aren't leaking into code.
* Notebook fail: verify `../data/...` paths; clear outputs, restart, run all; re‑run smoke.
* Figure mismatch: rebuild fig2 from SST CSV; keep legend generic; numbers only in caption.

---

### Rally lines

Integration > invention. Numbers in captions. Gate + smoke keep us safe.
