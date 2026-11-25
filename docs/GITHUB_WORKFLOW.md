# SolarEye GitHub Workflow, Branching & Issue Catalog

**Document Owner:** Member 1 (Tech Lead) & Planner  
**Policy:** Protected `main` branch, feature branches for Milestones M1–M4, mandatory peer review on **every** PR (including Member 1's PRs), milestone tags `m1-topic-settled` through `m4-results-frozen`, and final release tag `v1.0`.  
**Status:** `In progress`

---

## 1. Branching Strategy & Naming Conventions

- **`main`:** Always stable, tested, and tagged at milestone gates. **Zero direct commits to `main`.**
- **Feature Branches:** Created off the latest `main` using the exact pattern:
  - `feature/m01-<short-topic>` (Milestone 1 — Week 9)
  - `feature/m02-<short-topic>` (Milestone 2 — Week 10)
  - `feature/m03-<short-topic>` (Milestone 3 — Weeks 11–12)
  - `feature/m04-<short-topic>` (Milestone 4 — Weeks 13–14)
- **Fix / Docs Branches:** `fix/<issue-id>-<short-topic>` or `docs/<short-topic>`.

---

## 2. Step-by-Step Git Commands for Team Members

### 2.1 One-Time Clone & Identity Configuration
```bash
git clone https://github.com/<org-or-owner>/SolarEye.git
cd SolarEye

# Configure exact Git author identity (must match team roster on GitHub)
git config user.name "<Your Full Name>"
git config user.email "<your-university-or-github-email>"
```

### 2.2 Sync `main` & Start a Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/m02-data-loader-splits
```

### 2.3 Commit Conventions (Meaningful Atomic Commits)
Use Conventional-style prefixes with module scope:
- `feat(metrics): implement NumPy MSE/PSNR/IoU/Dice with empty-mask guards`
- `test(data): add leakage-free split and BGR->RGB loader unit tests`
- `exp(baselines): log Baseline 0 and Baseline 1 dev-set results`
- `docs(audit): update dataset validation status after local archive check`

```bash
git status
git add src/metrics.py tests/test_metrics.py
git commit -m "feat(metrics): implement NumPy MSE/PSNR/IoU/Dice with empty-mask guards"
```

### 2.4 Push & Open a Pull Request
```bash
git push -u origin feature/m02-data-loader-splits
```
1. Open a Pull Request targeting `main` on GitHub.
2. Link the corresponding Issue (`Closes #<issue_number>`).
3. Verify local tests pass before requesting review (`pytest -v`).
4. Assign a **different** member as Reviewer (see Peer Review Matrix below).

### 2.5 Peer Review Rules (Including Team Leader PRs)
- **No self-merging.** Every PR requires at least **1 explicit GitHub Approval** from a peer who did not author the PR.
- **Team Leader (Member 1) PRs:** MUST be peer-reviewed by **Member 2** or **Member 4** before merging.
- **Merge Policy:** Use **Merge Commit** (`Create a merge commit` or `git merge --no-ff`) so individual commit histories and author attribution remain intact for the CSE281 individual contribution audit (do *not* squash-merge multi-author work).

### 2.6 Milestone Checkpoint Tags & Final `v1.0` Tag (Member 1 after Gate Passes)
```bash
git checkout main
git pull origin main
git tag -a m1-topic-settled -m "Milestone 1: Topic, specification audit, and contracts settled"
git push origin m1-topic-settled

# Subsequent milestone tags:
# m2-baselines-ready
# m3-stages-working
# m4-results-frozen
# v1.0
```

---

## 3. GitHub Issues Catalog Across Milestones 1–4

### Milestone 1: Topic Settled (Week 9 — Tag `m1-topic-settled`)

| Issue ID | Title | Assignee | Req Ref | Dependencies | Acceptance Criteria & Evidence | Labels |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **#1** | Repo skeleton, `config.py`, `requirements.txt` & `experiment_log.csv` | M1 | REQ-01, REQ-17 | None | `load_config()` parses YAML; 16-col CSV header present (`baseline_0.yaml`, `baseline_1.yaml`); peer-reviewed by M2. | `milestone:m1`, `core`, `infra` |
| **#2** | Submit 4-member consolidation & `DATASET_VALIDATION.md` setup | M1, M2 | REQ-02, REQ-03 | None | Instructor approval requested; `download_dataset.py` & `validate_dataset.py` ready. | `milestone:m1`, `docs`, `data` |
| **#3** | Exploratory analysis plan & `01_image_analysis.ipynb` skeleton | M3 | REQ-05, REQ-07 | #1 | Notebook skeleton outlines histograms, FFT, resolution & quantization plans. | `milestone:m1`, `analysis` |
| **#4** | Baseline 0/1 design spec & dark-defect foreground polarity contract | M4 | REQ-08, REQ-09 | #1 | Polarity rule (`1=dark defect`) documented & stubbed in `segmentation.py`. | `milestone:m1`, `segmentation` |

### Milestone 2: Baselines Ready (Week 10 — Tag `m2-baselines-ready`)

| Issue ID | Title | Assignee | Req Ref | Dependencies | Acceptance Criteria & Evidence | Labels |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **#5** | Execute `validate_dataset.py` on MSPS & generate 70/30 splits (`seed=42`) | M2 | REQ-03, REQ-04, REQ-10 | #2 | `validation_report.json` logged; `dev_manifest.csv` & `test_manifest.csv` non-overlapping; `test_data.py` passes. | `milestone:m2`, `data` |
| **#6** | Implement `src/metrics.py`, `tests/test_metrics.py` & baseline runner | M1 | REQ-15, REQ-16, REQ-17 | #1, #5 | Hand-worked 4x4 checks + empty-mask/`MSE=0` tests pass; `evaluate.py` logs 16 columns. | `milestone:m2`, `metrics`, `numpy` |
| **#7** | Complete Dev-set EDA: histograms, FFT spectra, resolution & quantization | M3 | REQ-05, REQ-06, REQ-07 | #3, #5 | `01_image_analysis.ipynb` executed on Dev split; `256->4` quantization curve & Findings->Design table saved. | `milestone:m2`, `analysis` |
| **#8** | Implement & benchmark pure Baseline 0 (`raw < 127`) and Baseline 1 | M4 | REQ-08, REQ-15 | #4, #5, #6 | NumPy Otsu matches `cv2.THRESH_OTSU`; `EXP-M2-001` & `EXP-M2-002` logged; failure montage saved. | `milestone:m2`, `baselines`, `numpy` |

### Milestone 3: Stages Working (Weeks 11–12 — Tag `m3-stages-working`)

| Issue ID | Title | Assignee | Req Ref | Dependencies | Acceptance Criteria & Evidence | Labels |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **#9** | Implement restoration (`median_filter_numpy`, `alpha_trimmed_mean_filter_numpy`, order stats) | M2 | REQ-10, REQ-11, REQ-15 | #5, #6 | `median_filter_numpy` matches `cv2.medianBlur` (`reflect` parity); noise sweep PSNR table logged. | `milestone:m3`, `restoration`, `numpy` |
| **#10** | Implement frequency masks (`frequency_masks.py`) & DFT/IDFT (`frequency.py`) | M1, M2 | REQ-12, REQ-15 | #6, #9 | Ideal/Butterworth/Gaussian LP & HP masks + DFT/IDFT pass unit tests; $D_0$ cutoff & Pipeline B benchmarked. | `milestone:m3`, `frequency`, `numpy` |
| **#11** | Implement spatial enhancement (`histogram_equalization_numpy`, `convolve2d_numpy`, neg/log/gamma/stretch/sharpen) | M3 | REQ-13, REQ-15 | #7 | `convolve2d_numpy` matches `cv2.BORDER_REFLECT_101`; HE CDF matches `cv2.equalizeHist`; sweep logged. | `milestone:m3`, `enhancement`, `numpy` |
| **#12** | Implement Otsu/Sobel/Adaptive/Hough segmentation, NumPy erosion/dilation & CC decision rule | M4 | REQ-14, REQ-15 | #8, #11 | NumPy `erode`/`dilate`/`sobel` equal `cv2`; morphology (3+ sizes x 2+ shapes) & CC quantification pass tests. | `milestone:m3`, `segmentation`, `numpy` |
| **#13** | Assemble Pipelines A, B, C in `src/pipeline.py` & run Dev ablation suite | M1 | REQ-17 | #9, #10, #11, #12 | All 3 pipelines execute cleanly via `run_pipeline.py`; full Dev ablation matrix logged in `experiment_log.csv`. | `milestone:m3`, `integration` |

### Milestone 4: Frozen Results, Report & Defense (Weeks 13–14 — Tags `m4-results-frozen` & `v1.0`)

| Issue ID | Title | Assignee | Req Ref | Dependencies | Acceptance Criteria & Evidence | Labels |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **#14** | Freeze hyperparameters, evaluate once on `test_manifest.csv`, $\ge 20$ failures & Colab CPU benchmark | M1, M4 | REQ-17, REQ-18 | #13 | Frozen Test evaluation + 3x3 noise sweep logged; $\ge 20$ failure taxonomy saved; `02_results.ipynb` / Colab $< 10$ min. | `milestone:m4`, `eval`, `colab` |
| **#15** | Optional Bonus Tracks (CI, 6-module Streamlit demo `app/`, RLE/Huffman, Kaggle SolarCells) | All | BON-01..05 | #14 | Only merged if tests pass & core deliverables are 100% frozen. | `milestone:m4`, `bonus` |
| **#16** | Write 8–10 page IEEE Technical Report PDF + Appendix hand calculations | All (M1 lead) | REQ-20 | #14 | PDF compiles cleanly at 8–10 body pages (excl. refs/appendix); every number traced to `experiment_log.csv`. | `milestone:m4`, `report` |
| **#17** | Prepare 10-min Pitch, Canvas Live Demo, Unseen-Image CLI check & Defense Q&A | All | REQ-21 | #14, #16 | Dry-run timed at $\le 10$ min; `run_pipeline.py` tested on unseen images; `v1.0` tagged on `main`. | `milestone:m4`, `release` |
