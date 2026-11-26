# MSPS dataset validation record

**Owner:** Fatma — Member 2 (Data Engineer)  
**Milestone:** M1 — source and dataset validation setup  
**Status:** Pending real-archive inspection

> This is an evidence template, not a completed validation report. The supplied
> package did not include the MSPS archive, and no local MSPS inspection results
> are available yet. Do not fill fields from estimates or reference notes.

## 1. Dataset source and license

- Dataset candidate: MSPS photovoltaic electroluminescence dataset
- Zenodo record: https://zenodo.org/records/21549573
- DOI: https://doi.org/10.5281/zenodo.21549573
- Upstream repository: https://github.com/wch313/MSPS-Dataset
- License: reported as CC BY 4.0 in the project starter; confirm the live record
  and required attribution before redistribution.
- Access date: not recorded
- Archive filename, byte size, and checksum observed locally: not recorded

## 2. Reproducible commands

Run these from the repository root and retain the actual terminal output:

```bash
python data/download_dataset.py --dataset msps --out_dir data/raw/msps --dry_run
python data/download_dataset.py --dataset msps --out_dir data/raw/msps
python data/validate_dataset.py --data_dir data/raw/msps --out_report data/validation_report.json
```

If the extracted folders require explicit discovery, rerun validation with both
`--images_subdir` and `--masks_subdir` set to observed relative paths. Record
the exact command here.

## 3. Observations from the real archive

| Property | Observed result | Evidence / notes |
| --- | --- | --- |
| Image files found | Not inspected | |
| Mask files found | Not inspected | |
| Matched image-mask pairs | Not inspected | |
| Unmatched images / masks | Not inspected | |
| Image dimensions and shapes | Not inspected | |
| Mask dimensions and shapes | Not inspected | |
| Image data types / channel counts | Not inspected | |
| Raw mask modes and unique values | Not inspected | |
| RGB mask colors, if applicable | Not inspected | |
| Dimension mismatches / corrupt files | Not inspected | |
| Duplicate image SHA-256 groups | Not inspected | |
| Dark-defect polarity result | Not inspected | |
| Official train / test folder mapping | Not inspected | |

The reference package reports 1,500 images (1,000 train / 500 test) and
640 × 590 dimensions. These are reference claims to check against the live
source metadata and extracted files, not observations from this run.

## 4. Interpretation and limitations

Complete this section only after reviewing the generated JSON report and
confirming how the dataset encodes images, masks, and official splits.

- Pairing and dimensional integrity:
- Image dtype, channels, and intensity range:
- Mask encoding and foreground interpretation:
- Duplicate or leakage concerns:
- Confirmed official split and unresolved ambiguity:

Do not use the held-out test set for exploratory analysis, tuning, or threshold
selection.

## 5. AI assistance and individual contribution

The initial downloader, validator, and documentation were supplied as an
AI-assisted reference scaffold. Record which parts were independently reviewed,
adapted, executed, and interpreted, and disclose AI assistance in the final
course submission. Update this document with evidence collected from the
official dataset; do not present this template as proof that validation passed.
