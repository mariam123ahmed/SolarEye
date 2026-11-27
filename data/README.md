# MSPS dataset — M1/M2

AI-assisted reference handoff. Source: https://zenodo.org/records/21549573 and https://github.com/wch313/MSPS-Dataset (CC BY 4.0; attribution required). Archived validation report records 1,507 matched pairs (1,004 official train/development and 503 official test), 640×590 images, uint8 identical RGB channels, binary masks and no exact SHA-256 duplicates. Preserve official splits; no test tuning. Raw data is not included in Git.

From repository root:

```bash
python data/download_dataset.py --dataset msps --out_dir data/raw/msps
python data/validate_dataset.py --data_dir data/raw/msps --out_report data/validation_report.json
```

See `docs/DATASET_VALIDATION.md` and `data/validation_report.json`. The included reports and manifests come from the earlier AI-assisted Phase 1 run; rerun and review them before claiming personal verification.
