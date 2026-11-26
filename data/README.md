# SolarEye dataset acquisition and validation

**Owner:** Member 2 — Data Engineering  
**Milestone:** M1 — dataset source, acquisition, and local validation setup

## Candidate dataset

The current project README identifies the **MSPS photovoltaic electroluminescence
(EL) dataset** as the primary candidate:

- Zenodo: https://zenodo.org/records/21549573
- DOI: https://doi.org/10.5281/zenodo.21549573
- Upstream dataset repository: https://github.com/wch313/MSPS-Dataset
- License reported by the AI-assisted project starter: **CC BY 4.0**. Confirm the
  live record's license and attribution requirements before reuse or redistribution.
- The supplied reference package reports 1,500 images (1,000 train / 500 test) at
  640 × 590. Treat these as reference metadata pending verification, not local
  inspection results.

## Verification status

The MSPS archive has not been inspected locally by this branch. No pixel-level
or archive-layout property is claimed as verified.

| Check | Current status | Evidence needed |
| --- | --- | --- |
| Dataset source and DOI | Candidate identified in project starter | Confirm live Zenodo record |
| License and attribution | CC BY 4.0 reported by starter; confirm before reuse | Zenodo license field |
| Image count and official split | 1,500 total / 1,000 train / 500 test reported in reference package | Source metadata and extracted counts |
| Nominal image dimensions | 640 × 590 reported in reference package | Validator output |
| Image channels and bit depth | Pending | Inspect actual image arrays |
| Mask encoding and unique values | Pending | Inspect raw masks and RGB/palette colors |
| One-to-one image/mask pairing | Pending | Validator output |
| Image/mask dimensions | Pending | Validator output |
| Dark-defect polarity | Pending | Compare foreground/background intensities |
| Exact duplicate images | Pending | SHA-256 audit |

Do not change a pending item to verified until the corresponding evidence has
been collected and reviewed.

## Download and validate

Run from the repository root. The dry run makes no network request:

```bash
python data/download_dataset.py --dataset msps --out_dir data/raw/msps --dry_run
```

Download and safely extract the archive into the Git-ignored `data/raw/` directory:

```bash
python data/download_dataset.py --dataset msps --out_dir data/raw/msps
```

Inspect the extracted layout. When automatic discovery fits the actual structure:

```bash
python data/validate_dataset.py --data_dir data/raw/msps --out_report data/validation_report.json
```

When it does not, pass both observed relative folder names:

```bash
python data/validate_dataset.py --data_dir data/raw/msps --images_subdir <images-folder> --masks_subdir <masks-folder> --out_report data/validation_report.json
```

Record the actual command and output in `docs/DATASET_VALIDATION.md`. Do not
commit the raw archive or extracted images/masks. A small validation report may
be committed after it has been generated and checked.

## Expected outputs

- `data/validation_report.json` — generated audit report (not included yet).
- `data/splits/dev_manifest.csv` and `data/splits/test_manifest.csv` — produced
  during M2 after the official split layout has been confirmed.

Keep the official test set held out. Use development data for analysis and
parameter selection only.

## Assistance and review

The initial scripts and documentation were provided as an AI-assisted reference
scaffold. Review the code, verify the dataset source and checksum, run it against
the real archive, and make your own evidence-backed changes. Disclose AI assistance
in the project submission and follow the team's contribution rules.
