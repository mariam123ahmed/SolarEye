# SolarEye Dataset Investigation & Validation Report

**Document Owner:** Member 2 (Data, Restoration & Frequency) & Planner  
**Status:** **MSPS Verified Locally (`data/validation_report.json` PASSED)**; Kaggle alternative remains `Pending verification` (scoped strictly for optional M4 generalization).

---

## 1. Candidate Dataset Comparison Matrix

| Attribute | Primary Dataset: **MSPS** | Alternative / Bonus: **Kaggle SolarCells / LMFF** | Status |
| :--- | :--- | :--- | :--- |
| **Source URLs** | GitHub: `https://github.com/wch313/MSPS-Dataset`<br>Zenodo: `https://zenodo.org/records/21549573` | Kaggle: `xiaoyunchen666/dataset-of-solar-cells-defect-segmentation` | **Verified** |
| **Persistent DOI / ID** | `10.5281/zenodo.21549573` | Kaggle slug `xiaoyunchen666/dataset-of-solar-cells-defect-segmentation` | **Verified** |
| **Authors & Publication** | Shenshen Zhao, Yumeng Hao, Chuhan Wang, Qidong Li (*DACN*, 2026) | Yao Zhang et al. (*LMFF* paper: `SolarCells`, `SolarCells-S`, `PVEL-S`) | **Verified (Metadata)** |
| **License** | **CC BY 4.0** (academic & derivative research permitted with citation) | Kaggle dataset page terms (verify per-subset terms before M4 use) | **Verified** (MSPS); `Pending` (Kaggle) |
| **Imaging Modality** | Production-line Electroluminescence (EL) two-cell monocrystalline crops | PV EL / cell defect segmentation subsets | **Verified** (MSPS) |
| **Verified Image Count** | **1,507 paired images** (`1,004` official `train`, `503` official `test`) | `SolarCells`: `190` images (`SolarCells-S` / `PVEL-S` separate) | **Verified Locally** (MSPS) |
| **Verified Dimensions & Dtype** | `590 x 640 x 3` (`H=590, W=640`), `uint8` PNG (`R == G == B` on all 1,507) | `SolarCells`: `448 x 448` reported | **Verified Locally** (MSPS) |
| **Verified Mask Format** | `labels01/`: `590 x 640`, mode `L` (`uint8`), strictly `{0, 1}` (`labels/`: `{0, 255}`) | Pixel-level segmentation masks | **Verified Locally** (MSPS) |
| **Archive Checksum** | `MSPS.zip` = `360,415,905` bytes (`360.42 MB`), MD5 `25d8fdaa8c9f2f7cf114d9c1f44c0bce` | Multi-subset Kaggle archive | **Verified Locally** (MSPS) |
| **Leakage / Corruption Audit** | `0` corrupt, `0` unmatched, `0` pairing collisions, `0` dim mismatches, `0` empty masks, `0` SHA-256 duplicates | `SolarCells-S` may include pre-augmented copies | **Verified Locally** (MSPS) |
| **Defect Polarity** | `98.27%` (`1,481 / 1,507`) exhibit darker defect mean than background (`mean(bg) > mean(fg)`) | Pending local inspection | **Verified Locally** (MSPS) |
| **Colab CPU Feasibility** | `10.27 s` (Baseline 0) & `53.29 s` (Baseline 1) across 1,004 Dev images (~`5–27 s` on 503 Test images) | Fast secondary benchmark | **Verified Locally** (MSPS) |

---

## 2. Verification Checklist (`data/validation_report.json`)

| Check ID | Criterion | Result | Evidence |
| :--- | :--- | :--- | :--- |
| **DV-01** | Public availability & CC BY 4.0 academic license | **Verified** | Zenodo API `records/21549573` (`cc-by-4.0`) + GitHub README |
| **DV-02** | Archive integrity (`MSPS.zip`, MD5) | **Verified** | `360,415,905` bytes, MD5 `25d8fdaa8c9f2f7cf114d9c1f44c0bce` |
| **DV-03** | Exact paired count (`train` + `test`) | **Verified** | `1,004` train + `503` test = `1,507` pairs (`0` unmatched) |
| **DV-04** | Spatial resolution & mask alignment | **Verified** | All `1,507` images `(590, 640, 3)` align with `(590, 640)` masks (`0` mismatches) |
| **DV-05** | Dtype, channels, and mask encoding | **Verified** | `uint8`; identical RGB channels; `labels01/` values `[0, 1]` |
| **DV-06** | Corrupted / empty / duplicate file audit | **Verified** | `0` corrupt, `0` empty masks, `0` SHA-256 duplicates |
| **DV-07** | Real-world challenges (>= 2 required) | **Verified** | Low contrast (`mean gap 36.9`, 17 images `<=0`), uneven illumination (`illum_range 186.1`), dark borders/gaps, periodic busbars, minute `1–821 px^2` defects |
| **DV-08** | Leakage-free official split preservation | **Verified** | `data/splits/dev_manifest.csv` (`1,004`), `data/splits/test_manifest.csv` (`503`), `0` ID/SHA overlap |
| **DV-09** | CPU runtime feasibility (`< 10` min) | **Verified (M2)** | Baseline 0 (`10.27 s`) + Baseline 1 (`53.29 s`) on 1,004 Dev images (`test` has 503 images) |

---

## 3. Split Policy Resolution

Per CSE281 Project Requirement Section 5 (*"If the dataset has an official development/training and testing split, preserve that split"*), SolarEye **preserves the official MSPS partition**:
- **`data/splits/dev_manifest.csv` (`1,004` images):** MSPS official `train/` split, used exclusively for EDA (`notebooks/01_image_analysis.ipynb`), baseline benchmarking, parameter tuning, and ablations.
- **`data/splits/test_manifest.csv` (`503` images):** MSPS official `test/` split, strictly held out until final frozen Milestone 4 evaluation.
- `src/data.py:create_dev_test_split()` preserves `"train"`/`"test"` official splits when present (`preserve_official_split=True`) and falls back to deterministic `70/30` (`seed=42`, group-aware) splitting for unsplit datasets.
