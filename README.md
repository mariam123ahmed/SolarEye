# SolarEye — CSE281 Digital Image Processing

Alamein International University. Classical EL photovoltaic defect segmentation and quantification; no ML/DL.

## Phase 1 — Milestones 1 and 2

AI-assisted reference implementation and archived experimental evidence. Team review, independent implementation/adaptation, peer review and instructor approval of the four-member team remain required. This checkpoint covers the two required baselines only.

Dataset: MSPS, https://zenodo.org/records/21549573 (CC BY 4.0). Official split recorded in the local reference: 1,004 development and 503 held-out test. Primary metric: IoU. See `docs/PROJECT_FOUNDATION.md`, `docs/DATASET_VALIDATION.md`.

| Method | Archived development mean IoU |
|---|---:|
| Baseline 0 — raw threshold 127 | 0.001159 |
| Baseline 1 — Otsu + 3×3 opening | 0.001860 |

Both are intentionally simple; poor performance is documented rather than hidden. No final test metrics are included in this checkpoint.

## Run from repository root after all M1/M2 member PRs are integrated

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python data/download_dataset.py --dataset msps --out_dir data/raw/msps
python data/validate_dataset.py --data_dir data/raw/msps --out_report data/validation_report.json
python -m src.run_pipeline --config configs/baseline_0.yaml --manifest data/splits/dev_manifest.csv --evaluate
python -m src.run_pipeline --config configs/baseline_1.yaml --manifest data/splits/dev_manifest.csv --evaluate
```

Use `notebooks/00_SolarEye_Phase1_Colab.ipynb` for integrated verification and `notebooks/01_image_analysis.ipynb` for development-only EDA. Raw data must not be committed. The test manifest is for final evaluation only.

## Ownership

| Member | Role | Branch |
| --- | --- | --- |
| Mariam | Metrics, configuration, integration and evaluation | `feature/m01-mariam-foundation` |
| Fatma | Dataset, loader, validation and split | `feature/m01-fatma-data` |
| Fatima | Image analysis | `feature/m01-fatima-analysis` |
| Habiba | Segmentation, morphology and baseline algorithm tests | `feature/m01-habiba-segmentation` |

Every member reviews and adapts their assigned files, runs tests, documents AI assistance, commits genuine work on a feature branch and requests peer review before merging. Do not overwrite another member's contributions. The current integration PR alone does not establish a passing complete GitHub checkout.

See `docs/INTEGRATION_CONTRACT.md` and `docs/GITHUB_WORKFLOW.md` for shared conventions.
