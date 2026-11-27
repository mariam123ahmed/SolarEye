# SolarEye — Fatma | Data Engineer

This package is a private learning/reference package derived from the AI-assisted Phase 1 repository. Do not upload this ZIP, its folder structure, or untouched generated code as independent student work. Disclose AI assistance. Implement/adapt, understand and test your own changes.

## Milestone 1 (now)
Branch: `feature/m01-fatma-data`

Check the official dataset source and license. Run the download and validator on real data. Document image/mask counts, dimensions, mask encoding, real image challenges, and the official split. Record actual evidence; no test-set tuning.

Target document: `docs/DATASET_VALIDATION.md`. Create your own document using the worksheet in this package.

M1 reference scripts to review, adapt and run; final paths: `data/README.md`, `data/download_dataset.py`, `data/validate_dataset.py`.

## Milestone 2 (after M1 merge)
Suggested branch: `feature/m02-fatma-data` (create from updated main after M1).

Only owned reference files are included under `M02_REFERENCE/`. Place your reviewed/adapted versions at the same paths relative to the repository root, not inside M02_REFERENCE. Some modules need dependencies owned by other members. Use the integrated branch for cross-module tests; do not copy their code into your PR.

Owned paths:
- `src/data.py`
- `tests/test_data.py`

Evidence to generate yourself: data/validation_report.json, data/splits/dev_manifest.csv, data/splits/test_manifest.csv (no test evaluation). Do not relabel or copy old AI-produced results as your own.

## Git workflow
Clone the repository (or use your existing clone).
```bash
git clone https://github.com/mariam123ahmed/SolarEye.git
cd SolarEye
git fetch origin
git switch --track origin/feature/m01-fatma-data
```
If already on a local branch, use `git switch feature/m01-fatma-data` instead. After editing the relevant paths, run applicable tests, inspect `git status` and `git diff`, stage only your actual files, commit with a truthful message, and push. Open a PR from your named branch into main. Ask another member to review. Do not merge before review. For M2, switch to main, pull the reviewed M1 changes, then create your new branch.

Keep all raw dataset files and ZIPs out of Git. Use Google Colab CPU for reproducible verification. The complete Phase 1 notebook needs the other modules and the dataset; it is not expected to run on isolated M1 branches.
