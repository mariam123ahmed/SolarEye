# SolarEye Dataset Documentation & Validation Status

**Owner:** Member 2 (Data, Restoration & Frequency)  
**Primary Candidate:** **MSPS** (*Multi-type Solar cell defect Pixel-level Segmentation*)  
**Alternative Candidate (M4 Bonus Only):** **Kaggle SolarCells** (`xiaoyunchen666/dataset-of-solar-cells-defect-segmentation`)

---

## 1. Honest Verification Matrix

> **Integrity Policy:** Public Zenodo/GitHub metadata is marked `Verified (Metadata)`. Any
> property requiring local archive inspection remains `Pending verification` until
> `data/validate_dataset.py` has been executed on the downloaded dataset.

| Check | Description | Status | Source / Notes |
| :--- | :--- | :--- | :--- |
| **Source & DOI** | Zenodo `21549573` (`10.5281/zenodo.21549573`), GitHub `wch313/MSPS-Dataset` | `Verified (Metadata)` | Public Zenodo & GitHub records |
| **License** | Creative Commons Attribution 4.0 (**CC BY 4.0**) | `Verified (Metadata)` | Distinct from repository MIT code license |
| **Volume & Resolution** | 1,500 EL images (`1,000` train / `500` test), `640 x 590`, `MSPS.zip` (360.4 MB) | `Verified (Metadata)` | DACN paper & Zenodo record |
| **Defects & Labeling** | Cracks, black spots, busbar breaks; dual-expert + 3rd adjudicator masks | `Verified (Metadata)` | Public dataset documentation |
| **Channels & Bit Depth** | Exact channel count (`1` vs `3` identical RGB) & `dtype` (`uint8` vs `uint16`) | `Pending verification` | Run `data/validate_dataset.py` |
| **Mask Pixel Encoding** | Exact unique values (`{0,1}` vs `{0,255}` vs multi-class `{0,1,2,3}`) | `Pending verification` | Run `data/validate_dataset.py` |
| **1-to-1 Stem Pairing** | Every image has exactly one corresponding mask file | `Pending verification` | Run `data/validate_dataset.py` |
| **Defect Polarity** | Confirm `mean(image[mask > 0]) < mean(image[mask == 0])` | `Pending verification` | Run `data/validate_dataset.py` |
| **Duplicate / Leakage** | SHA-256 exact hash check across splits before `dev`/`test` manifests | `Pending verification` | Run `data/validate_dataset.py` |

---

## 2. Reproducible Commands

```bash
# Dry-run download check (no network transfer)
python data/download_dataset.py --dataset msps --out_dir data/raw/msps --dry_run

# Full download & unzip into git-ignored data/raw/msps/
python data/download_dataset.py --dataset msps --out_dir data/raw/msps

# Run dataset validation & generate data/validation_report.json
python data/validate_dataset.py --data_dir data/raw/msps --out_report data/validation_report.json
```

---

## 3. Split Manifests (`data/splits/`)

- `data/splits/dev_manifest.csv` (70% — exploratory analysis, tuning, ablations)
- `data/splits/test_manifest.csv` (30% — strictly held out until Milestone 4 frozen evaluation)
- Generated deterministically in Milestone 2 with `random_seed = 42`.
