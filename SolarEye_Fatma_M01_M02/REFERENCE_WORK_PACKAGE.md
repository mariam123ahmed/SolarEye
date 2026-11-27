> AI-assisted original guidance. Use START_HERE.md for the current ownership and branch rules; reproduce any claimed results yourself.

# Work Package — Phase 1 (Milestones 1 & 2): Member 2 — Data, Restoration & Frequency

> **Document Status:** Active Phase 1 Specification (Milestones 1 & 2)  
> **Target Tags:** `m1-topic-settled` (Week 9), `m2-baselines-ready` (Week 10)  
> **Project:** SolarEye — Explainable PV Defect Detection & Quantification using Classical DIP  
> **Course:** CSE281 Digital Image Processing (Alamein International University)

---

## Milestone Quick Navigation (M1 vs M2)

| Dimension | Milestone 1 (Topic Settled — Week 9) | Milestone 2 (Baselines Ready — Week 10) |
| :--- | :--- | :--- |
| **Primary Goal** | Document dataset candidate validation (Verified metadata vs Pending inspection) and build download/validation scripts | Implement single shared `src/data.py` loader, immutable MSPS `train/test` (`1,000/500`) manifests (or `70/30` fallback), and reproducible noise generators (`seed=42`) |
| **Key Files** | `data/README.md`, `data/download_dataset.py`, `data/validate_dataset.py` | `src/data.py`, `data/splits/dev_manifest.csv`, `data/splits/test_manifest.csv`, `tests/test_data.py` |
| **Branches** | `feature/m01-fatma-data` | `feature/m02-data-loader-and-noise` |
| **Reviewer** | Member 1 (Tech Lead) | Member 1 (Tech Lead) or Member 3 |
| **Release Tag** | `m1-topic-settled` | `m2-baselines-ready` |

---

## 0. Quick Action Checklist

### Milestone 1 (Topic Settled — Week 9)
- [ ] Create branch `feature/m01-fatma-data` from `main`.
- [ ] Write `data/README.md` separating `Verified (Metadata)` vs `Pending verification` checks for MSPS (`1,000 train / 500 test`).
- [ ] Implement `data/download_dataset.py` (`--dry_run` verified) and `data/validate_dataset.py`.
- [ ] Open PR reviewed by **Member 1** and merge before tag `m1-topic-settled`.

### Milestone 2 (Baselines Ready — Week 10)
- [ ] Create branch `feature/m02-data-loader-and-noise` from `main`.
- [ ] Run `data/validate_dataset.py` on local/Colab MSPS archive and update `data/README.md` with observed pixel/mask values.
- [ ] Implement `load_image`, `load_mask` (nearest-neighbor resize, `{0,1}` mask), `bgr_to_rgb`, `create_dev_test_split`, and 4 seeded noise functions in `src/data.py`.
- [ ] Generate immutable `data/splits/dev_manifest.csv` (MSPS official `1,000 train`) and `test_manifest.csv` (MSPS official `500 test`, with `70/30` fallback for unsplit datasets).
- [ ] Complete and pass `pytest tests/test_data.py -v`, get PR reviewed by **Member 1** & **Member 3**, and merge before tag `m2-baselines-ready`.

---

## 1. Member Identity & Role

- **Member ID:** Member 2
- **Primary Title:** Data Engineering, Noise Modeling, Spatial Restoration & Frequency-Domain Filtering Lead
- **Scope in Phase 1 (M1 & M2):**
  - Own dataset acquisition, license verification, integrity validation (`data/download_dataset.py`, `data/validate_dataset.py`), and honest status tracking separating public Zenodo/GitHub metadata from local pixel-level inspection.
  - Implement the **single shared image & mask I/O contract** in `src/data.py` (`load_image`, `load_mask`, `bgr_to_rgb`) used by every pipeline, notebook, and test in the repository.
  - Create the leakage-free, deterministic **dev / test manifest split** (`create_dev_test_split`, saved to `data/splits/dev_manifest.csv` and `test_manifest.csv`) preserving MSPS's official `1,000 train (dev) / 500 test (held-out)` partition and supporting a deterministic `70/30` (`seed=42`) fallback for unsplit datasets.
  - Implement reproducible controlled noise corruption functions (`add_gaussian_noise`, `add_salt_pepper_noise`, `add_speckle_noise`, `add_poisson_noise`) with `seed=42` so Milestone 3 restoration and frequency filters have standardized noisy benchmarks.
- **Future-Phase Continuity (M3/M4 Preview — Do Not Implement Yet):** You will implement `src/restoration.py` (mean, median, max, min, midpoint, alpha-trimmed mean, including pure NumPy `median_filter_numpy` and `alpha_trimmed_mean_filter_numpy`) and `src/frequency.py` (DFT, centered spectrum, IDFT, integrating Member 1's masks).

---

## 2. Milestone Objectives

### Milestone 1 (Topic Settled — Week 9)
1. Document the Primary Candidate (**MSPS EL Dataset**, Zenodo `21549573` / GitHub `wch313/MSPS-Dataset`, CC BY 4.0, 1,500 images `640x590`) vs Alternative Candidate (**Kaggle SolarCells**, `xiaoyunchen666/dataset-of-solar-cells-defect-segmentation`, 190 images `448x448`) in `data/README.md`.
2. Strictly enforce truth-in-reporting: mark public metadata as `Verified (Metadata)` and mark pixel/archive properties (channel count, bit depth, exact mask values `{0,1}` vs `{0,255}` vs multi-class, filename pairing, duplicate check) as `Pending verification` until local archive inspection completes.
3. Build `data/download_dataset.py` (automated Zenodo/GitHub fetch + SHA/size check, no manual login gate) and `data/validate_dataset.py` (auditing actual downloaded files and generating a validation summary).

### Milestone 2 (Baselines Ready — Week 10)
1. Run `data/validate_dataset.py` on the downloaded MSPS dataset and update `data/README.md` with observed pixel statistics, channel count, and raw mask encoding.
2. Implement `src/data.py` (`load_image`, `load_mask`, `bgr_to_rgb`, `create_dev_test_split`, `add_gaussian_noise`, `add_salt_pepper_noise`, `add_speckle_noise`, `add_poisson_noise`).
3. Generate immutable `data/splits/dev_manifest.csv` (MSPS official `1,000 train` split) and `data/splits/test_manifest.csv` (MSPS official `500 test` held-out split) preserving official splits, while ensuring `create_dev_test_split` supports a deterministic `70/30` (`seed=42`, group-aware if `group_col` is given) fallback for unsplit datasets.
4. Write `tests/test_data.py` verifying `{0,1}` mask loading, nearest-neighbor resize preservation, `BGR->RGB` channel ordering, split disjointness, and deterministic `seed=42` noise generation with analytical variance/density checks.

---

## 3. Official Specification References (Pages 1–11)

| Spec Page | Section / Topic | Relevance to Member 2 (M1 & M2) |
| :--- | :--- | :--- |
| **Page 2** | Dataset Selection, Size/QualityJustification & Metadata | Justify MSPS EL dataset (1,500 images, dual-expert pixel masks, CC BY 4.0) and verify raw image/mask properties. |
| **Page 3** | Dataset Splitting (Leakage-Free Dev/Test) & Noise Types | Preserve MSPS official `1,000 train (dev) / 500 test (held-out)` split (`70/30` fallback on unsplit datasets) and implement Gaussian + Salt-and-Pepper (+ Speckle/Poisson) noise generators. |
| **Page 4** | NumPy Implementation & Border Rules (`reflect`) | Establish `np.random.default_rng(seed)` and `uint8` clipping contracts for M2 noise and M3 restoration filters. |
| **Page 7** | Code Quality (`<=95` chars/line, BGR->RGB rule, no hardcoded paths) | Enforce `bgr_to_rgb`, `pathlib.Path`, and single shared loader in `src/data.py`. |
| **Page 8** | Reproducibility (`seed=42`) | Lock `seed=42` in splits and noise functions so every team member evaluates on identical inputs. |
| **Page 11** | Grading Rubric (10% Problem & Data, 10% Code Quality & Reproducibility) | Directly graded on dataset integrity, split hygiene, and clean I/O contracts. |

---

## 4. Prerequisites & Dependencies

### Milestone 1 (Week 9)
- Member 1's `.gitignore` (must ignore `data/raw/`, `data/processed/`, and `*.zip` so 360.4 MB `MSPS.zip` is NEVER committed to Git!).
- Python packages: `numpy`, `pandas`, `pillow`, `opencv-python` (optional fallback to `PIL`), `pyyaml`.

### Milestone 2 (Week 10)
- **M1 Gate (`m1-topic-settled`) passed:** `configs/dataset.yaml` and `src/config.py` merged.
- Local or Colab download of `MSPS.zip` completed into `data/raw/` (ignored by Git) and validated via `data/validate_dataset.py`.

---

## 5. Detailed Implementation Tasks

### Milestone 1 (Topic Settled — Week 9)
1. **Write `data/README.md`:**
   - Document Primary Candidate (MSPS: DOI `10.5281/zenodo.21549573`, 1,500 images `640x590`, CC BY 4.0, cracks/black spots/busbar breaks) and Alternative Candidate (Kaggle `SolarCells`: 190 images `448x448`, reserved only for optional M4 generalization).
   - Include a two-column Verification Checklist separating `Verified (Metadata)` from `Pending verification` (channel count, bit depth, mask unique values, pairing, duplicate check).
2. **Write `data/download_dataset.py`:**
   - Download `MSPS.zip` from Zenodo record `21549573` into `data/raw/MSPS.zip`, verify file size/MD5 if available, extract into `data/raw/msps/`, and support `--dry_run` and `--output_dir`.
3. **Write `data/validate_dataset.py`:**
   - Scan extracted image and mask directories, assert 1-to-1 stem matching, inspect image extensions, dimensions, channel counts (`1` vs `3`), dtype, intensity min/max, and raw mask unique values (`{0,1}` vs `{0,255}` vs multi-class `{0,1,2,3}`), check MD5 hashes for exact duplicates, and print/write a JSON/Markdown validation summary.

### Milestone 2 (Baselines Ready — Week 10)
1. **Run Validation & Inspect Raw Mask Encoding:**
   - Execute `python data/validate_dataset.py --data-dir data/raw/msps`. Record exact raw image shape, channels, and mask values in `data/README.md`.
2. **Implement `src/data.py` Single Shared Loader:**
   - `bgr_to_rgb(image)`: swaps channel 0 and 2 (`image[..., ::-1].copy()` or `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)`), raising `ValueError` if not 3-channel `(H, W, 3)`.
   - `load_image(path, grayscale=True, target_size=None)`: reads image safely (via `cv2.imread` or `PIL.Image`), converts `BGR->RGB` when `grayscale=False`, converts to 2D `uint8` `[0, 255]` when `grayscale=True`, optionally resizes with `cv2.INTER_AREA` / `cv2.INTER_LINEAR`, returns `np.ndarray` `dtype=uint8`.
   - `load_mask(path, target_size=None)`: reads mask as single-channel, normalizes whatever raw encoding MSPS uses (e.g., `> 0` if binary `{0,255}` or multi-class defect IDs `{1,2,3}` -> binary `1`, while `0` -> `0`) into canonical `uint8` `{0, 1}` (`1 = dark defect foreground`), and if `target_size` is provided, resizes **strictly with nearest-neighbor interpolation** (`INTER_NEAREST`) so non-binary values never appear.
3. **Implement Leakage-Free Split Generator (`create_dev_test_split`):**
   - Build full sample manifest DataFrame (`image_id, image_path, mask_path, source_split, width, height, defect_pixels`).
   - MSPS provides an official `1,000 train / 500 test` split (`dev` = official `train`, `test` = official `test`). `create_dev_test_split()` preserves official `source_split` assignments when present (mapping `train -> dev`, `test -> test`) and falls back to a deterministic `70/30` split using `np.random.default_rng(seed=42)` (or `group_col` if cell/module IDs exist) for unsplit datasets (such as Kaggle `SolarCells`), always enforcing zero path overlap and relative POSIX paths (`data/raw/...`).
   - Save `data/splits/dev_manifest.csv` and `data/splits/test_manifest.csv` (commit these small CSV manifests to Git so all 4 members share identical splits).
4. **Implement Controlled Noise Generators (`src/data.py`):**
   - `add_gaussian_noise(image, mean=0.0, sigma=15.0, seed=42)`
   - `add_salt_pepper_noise(image, density=0.05, salt_ratio=0.5, seed=42)`
   - `add_speckle_noise(image, var=0.04, seed=42)`
   - `add_poisson_noise(image, scale=1.0, seed=42)`
   - All operate in `float64` internally, use `rng = np.random.default_rng(seed)`, clip to `[0, 255]`, and return `np.uint8`.
5. **Write `tests/test_data.py`** and run on synthetic + sample data.

---

## 6. Files to Create / Modify

### Milestone 1 (Week 9)
- `data/README.md` (create: dataset metadata, license, Pending vs Verified matrix)
- `data/download_dataset.py` (create)
- `data/validate_dataset.py` (create)
- `data/splits/.gitkeep` (verify)

### Milestone 2 (Week 10)
- `data/README.md` (update with actual `validate_dataset.py` findings)
- `src/data.py` (implement all 8 functions)
- `data/splits/dev_manifest.csv` (generate & commit relative-path manifest)
- `data/splits/test_manifest.csv` (generate & commit relative-path manifest)
- `tests/test_data.py` (implement unit tests)

---

## 7. Proposed Function Signatures

```python
# src/data.py (Milestone 2)
def bgr_to_rgb(image: np.ndarray) -> np.ndarray: ...

def load_image(
    path: str | Path,
    grayscale: bool = True,
    target_size: tuple[int, int] | None = None,
) -> np.ndarray: ...

def load_mask(
    path: str | Path,
    target_size: tuple[int, int] | None = None,
) -> np.ndarray: ...

def create_dev_test_split(
    manifest_df: pd.DataFrame,
    test_ratio: float = 0.3,
    seed: int = 42,
    group_col: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]: ...

def add_gaussian_noise(
    image: np.ndarray,
    mean: float = 0.0,
    sigma: float = 15.0,
    seed: int = 42,
) -> np.ndarray: ...

def add_salt_pepper_noise(
    image: np.ndarray,
    density: float = 0.05,
    salt_ratio: float = 0.5,
    seed: int = 42,
) -> np.ndarray: ...

def add_speckle_noise(
    image: np.ndarray,
    var: float = 0.04,
    seed: int = 42,
) -> np.ndarray: ...

def add_poisson_noise(
    image: np.ndarray,
    scale: float = 1.0,
    seed: int = 42,
) -> np.ndarray: ...
```

---

## 8. Input / Output Contracts

1. **`load_image`:**
   - Input: valid path (`str | Path`). Raise `FileNotFoundError` if path does not exist or fails to decode.
   - Output: `np.ndarray`, `dtype=np.uint8`, range `[0, 255]`. Shape `(H, W)` if `grayscale=True`, or `(H, W, 3)` in **RGB** order if `grayscale=False`. Note: `target_size=(width, height)` or `(height, width)` — standardize explicitly as `(height, width)` across the entire codebase and convert to `(width, height)` internally if calling `cv2.resize`!
2. **`load_mask`:**
   - Input: valid mask path. Raise `FileNotFoundError` if unreadable.
   - Output: `np.ndarray`, `dtype=np.uint8`, 2D shape `(H, W)`, values strictly `{0, 1}` where `1` = dark defect foreground and `0` = healthy background.
3. **`create_dev_test_split`:**
   - Input: `manifest_df` containing `image_path` and `mask_path` columns (and optional `group_col`).
   - Output: `(dev_df, test_df)` with zero intersection of image IDs (and zero intersection of `group_col` values if provided), deterministic under `seed=42`.
4. **Noise Functions (`add_*_noise`):**
   - Input: `image` (`np.ndarray`, `uint8`, 2D or 3D), parameters, `seed: int = 42`.
   - Output: new `np.ndarray` (`dtype=np.uint8`, same shape as `image`, clipped to `[0, 255]`). Must NEVER mutate `image` in-place!

---

## 9. Mathematical Background

1. **Additive White Gaussian Noise (AWGN):**
   $$I_{\text{noisy}}(r, c) = \text{clip}_{[0,255]}\!\left(\text{round}\!\left(I(r, c) + \eta(r, c)\right)\right), \qquad \eta(r, c) \stackrel{\text{i.i.d.}}{\sim} \mathcal{N}(\mu, \sigma^2)$$
   Expected MSE on non-clipped pixels approaches $\sigma^2$ (when $\mu = 0$).
2. **Impulse (Salt & Pepper) Noise:**
   With total corruption probability $d \in [0, 1]$ and salt proportion $p_s \in [0, 1]$:
   $$I_{\text{noisy}}(r, c) = \begin{cases} 255, & \text{with probability } d \cdot p_s \quad (\text{salt}) \\ 0, & \text{with probability } d \cdot (1 - p_s) \quad (\text{pepper}) \\ I(r, c), & \text{with probability } 1 - d \end{cases}$$
3. **Multiplicative Speckle Noise:**
   $$I_{\text{noisy}}(r, c) = \text{clip}_{[0,255]}\!\left(\text{round}\!\left(I(r, c) + I(r, c) \cdot \eta_u(r, c)\right)\right), \qquad \eta_u \sim \text{Uniform}\!\left(-\sqrt{3v},\, +\sqrt{3v}\right) \text{ or } \mathcal{N}(0, v)$$
   where variance of $\eta_u$ equals $v$.
4. **Shot (Poisson) Noise:**
   Using scaled intensity $\lambda(r, c) = \text{scale} \cdot I(r, c) \ge 0$:
   $$I_{\text{noisy}}(r, c) = \text{clip}_{[0,255]}\!\left(\text{round}\!\left(\frac{\text{Poisson}(\lambda(r, c))}{\text{scale}}\right)\right)$$
   Signal-dependent variance: $\text{Var}(I_{\text{noisy}}) = I(r, c) / \text{scale}$.

---

## 10. Pseudocode / Implementation Guidance

```python
# Pseudocode for src/data.py (Member 2 writes the actual code)

def load_mask(path, target_size=None):
    # 1. Check Path(path).exists(), else raise FileNotFoundError
    # 2. Read raw array as grayscale / single-channel (cv2.IMREAD_GRAYSCALE or PIL .convert("L"))
    # 3. If target_size is not None:
    #    h, w = target_size
    #    Resize with NEAREST-NEIGHBOR ONLY (cv2.INTER_NEAREST or Image.NEAREST)!
    # 4. Binarize: mask = (raw > 0).astype(np.uint8)
    # 5. Assert set(np.unique(mask)).issubset({0, 1})
    # 6. Return mask

def add_gaussian_noise(image, mean=0.0, sigma=15.0, seed=42):
    # 1. rng = np.random.default_rng(seed)
    # 2. noise = rng.normal(loc=mean, scale=sigma, size=image.shape)
    # 3. noisy = np.clip(np.rint(image.astype(np.float64) + noise), 0, 255)
    # 4. Return noisy.astype(np.uint8)

def add_salt_pepper_noise(image, density=0.05, salt_ratio=0.5, seed=42):
    # 1. Validate 0.0 <= density <= 1.0 and 0.0 <= salt_ratio <= 1.0
    # 2. rng = np.random.default_rng(seed)
    # 3. out = image.copy()
    # 4. u = rng.random(image.shape[:2])  # apply impulse across pixel locations (H, W)
    # 5. salt_thresh = density * salt_ratio
    #    salt_mask = u < salt_thresh
    #    pepper_mask = (u >= salt_thresh) & (u < density)
    # 6. out[salt_mask] = 255
    #    out[pepper_mask] = 0
    # 7. Return out
```

---

## 11. NumPy Implementation Requirements

- **Milestone 2 Requirement:** Implement all 4 noise generators (`add_gaussian_noise`, `add_salt_pepper_noise`, `add_speckle_noise`, `add_poisson_noise`), `bgr_to_rgb`, and mask binarization using **pure NumPy** (`np.random.default_rng`, `np.clip`, `np.rint`, boolean indexing) without relying on `skimage.util.random_noise`.
- **Milestone 3 Bridge (Know Now, Implement in M3):** Member 2 fulfills the official "2+ non-trivial NumPy DIP operations" requirement in Milestone 3 inside `src/restoration.py` (`median_filter_numpy` and `alpha_trimmed_mean_filter_numpy` with `np.pad(..., mode="reflect")` matching `cv2.BORDER_REFLECT_101`) and `src/frequency.py` (DFT/IDFT filtering). Practicing `uint8 <-> float64` conversion and deterministic RNG in M2 prevents dtype bugs in M3.

---

## 12. Library Equivalence Checks

1. **`bgr_to_rgb` Equivalence:**
   Compare your NumPy channel slice `image[..., ::-1].copy()` against `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` using `assert np.array_equal(out_np, out_cv2)`.
2. **`load_mask` Nearest-Neighbor Resize Parity:**
   Compare `cv2.resize(..., interpolation=cv2.INTER_NEAREST)` vs `PIL.Image.resize(..., resample=Image.NEAREST)` on a test binary mask and assert output values are strictly `{0, 1}` (unlike bilinear resize, which introduces fractional gray values at defect edges!).
3. **Noise Statistical Sanity Checks (Equivalence to Theoretical Distribution):**
   - On a flat mid-gray `128x128` image of constant value `128`, `add_gaussian_noise(img, mean=0.0, sigma=15.0, seed=42)` must produce sample mean within `128 ± 1.0` and sample std within `15.0 ± 1.0`.
   - `add_salt_pepper_noise(img, density=0.10, salt_ratio=0.5, seed=42)` must produce fraction of `255` pixels near `0.05 ± 0.01` and `0` pixels near `0.05 ± 0.01`.

---

## 13. Hand-Calculation Examples

### Hand Example A: `3x3` Gaussian Noise + Clipping
Suppose a `3x3` patch from a dark EL defect boundary is (`uint8`):
$$I = \begin{bmatrix} 5 & 12 & 250 \\ 18 & 120 & 254 \\ 220 & 240 & 2 \end{bmatrix}$$
Suppose `rng.normal(0, 15.0)` draws the following rounded noise matrix:
$$\eta = \begin{bmatrix} -8.2 & +4.6 & +9.1 \\ -2.4 & -15.3 & +3.7 \\ +12.0 & -5.5 & -6.8 \end{bmatrix}$$
Step-by-step calculation (`clip(round(I + eta), 0, 255)`):
- `(0,0)`: $5 + (-8.2) = -3.2 \xrightarrow{\text{round}} -3 \xrightarrow{\text{clip}} 0$ *(prevents `uint8` underflow to 253!)*
- `(0,1)`: $12 + 4.6 = 16.6 \xrightarrow{\text{round}} 17$
- `(0,2)`: $250 + 9.1 = 259.1 \xrightarrow{\text{round}} 259 \xrightarrow{\text{clip}} 255$ *(prevents `uint8` overflow to 3!)*
- `(1,1)`: $120 - 15.3 = 104.7 \xrightarrow{\text{round}} 105$
- `(2,2)`: $2 - 6.8 = -4.8 \xrightarrow{\text{round}} -5 \xrightarrow{\text{clip}} 0$

Resulting `uint8` array:
$$I_{\text{noisy}} = \begin{bmatrix} 0 & 17 & 255 \\ 16 & 105 & 255 \\ 232 & 234 & 0 \end{bmatrix}$$

### Hand Example B: `3x3` Salt & Pepper Noise Thresholds
With `density = 0.20`, `salt_ratio = 0.50`:
- `salt_thresh = 0.20 * 0.50 = 0.10`
- `total_thresh = 0.20`
Given `u` drawn from `Uniform[0, 1)`:
$$u = \begin{bmatrix} 0.04 & 0.51 & 0.88 \\ 0.17 & 0.33 & 0.09 \\ 0.72 & 0.12 & 0.95 \end{bmatrix}$$
- `u < 0.10` -> Salt (`255`): `(0,0)=0.04`, `(1,2)=0.09` (2 pixels)
- `0.10 <= u < 0.20` -> Pepper (`0`): `(1,0)=0.17`, `(2,1)=0.12` (2 pixels)
- Remaining 5 pixels keep original intensity.

---

## 14. Required Experiments

### Milestone 1 (Week 9)
- Run `data/download_dataset.py` (or local inspection of `MSPS.zip`) and execute `data/validate_dataset.py` to replace every `Pending verification` item with exact empirical measurements (image count, dimensions, channels, dtype, raw mask values, duplicate count).

### Milestone 2 (Week 10)
- **Split Integrity Audit:** Generate `data/splits/dev_manifest.csv` (official MSPS `1,000 train`) and `data/splits/test_manifest.csv` (official MSPS `500 test`, with `70/30` fallback verified for unsplit datasets at `seed=42`). Verify zero overlapping stems/groups, balanced defect presence across dev vs test, and report exact split counts.
- **Controlled Noise Benchmark Calibration:** On 5 sample dev images, generate Gaussian (`sigma=15`), Salt & Pepper (`density=0.05`), Speckle (`var=0.04`), and Poisson (`scale=1.0`) noisy images (`seed=42`), compute MSE/PSNR against the clean dev images using Member 1's `src/metrics.py`, and save a visual verification grid for M3 restoration baselines.

---

## 15. Required Tables & Visualizations

### Milestone 1 (Week 9)
1. **Dataset Candidate Comparison & Verification Matrix** in `data/README.md`: comparing MSPS vs Kaggle SolarCells across modality, size, resolution, annotation protocol, license, and explicit `Verified (Metadata)` vs `Pending verification` / `Observed` status.

### Milestone 2 (Week 10)
1. **Dev/Test Split Summary Table:** `Split | Image Count | % of Total | Mean Defect Area % | Empty-Mask Count | Random Seed`.
2. **Controlled Noise Baseline Table:** `Noise Type | Parameters | Seed | Measured Mean MSE | Measured Mean PSNR (dB)`.
3. **Visual Grid (1 figure):** Clean EL image + ground-truth `{0,1}` mask overlay (`BGR->RGB` compliant) + Gaussian + Salt & Pepper + Speckle + Poisson corrupted versions.

---

## 16. Unit Tests & Acceptance Criteria

```bash
pytest tests/test_data.py -v
```
**Mandatory Test Cases in `tests/test_data.py`:**
1. `test_bgr_to_rgb_equivalence`: asserts `np.array_equal(bgr_to_rgb(bgr), cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))`.
2. `test_load_mask_binary_and_nearest_resize`: writes a synthetic `{0, 255}` PNG mask to `tmp_path`, calls `load_mask(path, target_size=(32, 32))`, asserts `dtype == np.uint8` and `set(np.unique(mask)).issubset({0, 1})`.
3. `test_dev_test_split_disjoint_and_deterministic`: verifies official `train/test` split preservation when `source_split` is provided AND verifies `create_dev_test_split` fallback on unsplit DataFrames twice with `seed=42` -> identical splits, zero overlap, exact 70/30 ratio (±1 row for rounding).
4. `test_noise_reproducibility_seed42`: calling `add_gaussian_noise` and `add_salt_pepper_noise` twice with `seed=42` yields `np.array_equal` identical results, without mutating input array.
5. `test_noise_statistical_accuracy`: verifies empirical variance of Gaussian noise (`sigma=15`) and impulse fraction of Salt & Pepper (`density=0.10`) on constant `128` test patch.

---

## 17. Expected GitHub Branch Names & Exact Git Commands

- **Milestone 1 Branch:** `feature/m01-fatma-data`
- **Milestone 2 Branch:** `feature/m02-data-loader-and-noise`

```bash
# Milestone 1
git checkout main && git pull origin main
git checkout -b feature/m01-fatma-data
git add data/README.md data/download_dataset.py data/validate_dataset.py
git commit -m "feat(m01): add MSPS dataset documentation, download script, and validation audit"
git push -u origin feature/m01-fatma-data

# Milestone 2
git checkout main && git pull origin main
git checkout -b feature/m02-data-loader-and-noise
pytest tests/test_data.py -v
git add src/data.py data/README.md data/splits/dev_manifest.csv data/splits/test_manifest.csv tests/test_data.py
git commit -m "feat(m02): implement shared data loader, MSPS dev/test splits, and seeded noise generators"
git push -u origin feature/m02-data-loader-and-noise
```

---

## 18. Suggested Meaningful Commit Messages

- **M1:**
  - `docs(m01): document MSPS vs Kaggle dataset validation matrix in data/README.md`
  - `feat(m01): add reproducible Zenodo downloader and dataset archive validator`
- **M2:**
  - `feat(m02): implement load_image, load_mask, and bgr_to_rgb with nearest-neighbor mask resize`
  - `data(m02): generate immutable MSPS dev (train) and test split manifests (with 70/30 fallback, seed=42)`
  - `feat(m02): add deterministic Gaussian, salt-pepper, speckle, and poisson noise generators`
  - `test(m02): add unit tests for data contracts, split disjointness, and noise determinism`

---

## 19. Pull Request Checklist

- [ ] `data/raw/` and `*.zip` are NOT staged or committed (`git status` clean of large binaries).
- [ ] All manifest paths in `data/splits/*.csv` are relative POSIX paths (no `C:\Users\...`).
- [ ] `load_mask` strictly enforces `{0, 1}` `uint8` output (`1 = dark defect`).
- [ ] `bgr_to_rgb` applied on RGB loads; `load_image` does not mutate inputs.
- [ ] All `.py` files pass `<= 95` characters per line and have docstrings.
- [ ] `pytest tests/test_data.py -v` passes 100%.

---

## 20. Reviewer Assignment

- **Milestone 1 PR (`feature/m01-fatma-data`):** Reviewed by **Member 1** (Tech Lead).
- **Milestone 2 PR (`feature/m02-data-loader-and-noise`):** Reviewed by **Member 1** (checks config/split contract) and **Member 3** (confirms `src/data.py` works cleanly in `notebooks/01_image_analysis.ipynb`).

---

## 21. Report-Section Responsibilities

- **Section II (Dataset & Problem Setup):** Dataset source (MSPS, Zenodo 21549573, CC BY 4.0), validation statistics, MSPS `1,000 train (dev) / 500 test` split hygiene (`70/30` fallback policy), and controlled noise simulation equations.
- *(In M3/M4 you will write the Spatial Restoration and Frequency-Domain Filtering methodology and experiment sections.)*

---

## 22. Common Implementation Mistakes

1. **Committing `MSPS.zip` or `data/raw/` to Git:** Bloats repository history beyond GitHub limits. Always verify `.gitignore` before `git add`.
2. **Using Bilinear Interpolation on Masks:** `cv2.resize(mask, size)` defaults to `INTER_LINEAR`, creating anti-aliased edge values like `127` or `0.5`! Always pass `cv2.INTER_NEAREST`.
3. **Hardcoding Windows Backslashes in CSV Manifests:** Use `.as_posix()` so manifests work seamlessly on both Windows laptops and Google Colab Linux!
4. **Using Global `np.random.seed()`:** Mutates global RNG state across modules. Always use local `rng = np.random.default_rng(seed)`.
5. **Forgetting `clip(0, 255)` Before `.astype(np.uint8)`:** Causes negative noise values or values `> 255` to wrap modulo 256, creating severe black/white speckle artifacts inside Gaussian noise!

---

## 23. Likely Individual Defense Questions (Own Work + Full Pipeline)

1. **Own Work:** *"Why must `load_mask` use nearest-neighbor interpolation when resizing, whereas `load_image` uses area/bilinear?"*
   - *Key points:* Masks are categorical `{0, 1}` labels; bilinear averaging creates invalid intermediate labels along boundaries, corrupting IoU/Dice.
2. **Own Work:** *"How did you ensure zero data leakage between `dev_manifest.csv` and `test_manifest.csv`, and why was `seed=42` fixed?"*
   - *Key points:* Single deterministic split via `np.random.default_rng(42)`, disjoint IDs/groups, committed immutable CSV manifests, test set locked until M4 config freeze.
3. **Own Work:** *"What happens numerically if you cast a `float64` noisy image containing `-3.2` or `259.1` directly to `np.uint8` without `np.clip(..., 0, 255)`?"*
   - *Key points:* Modulo-256 wraparound turns `-3` into `253` (bright white pixel) and `259` into `3` (black pixel).
4. **Full Pipeline:** *"Why is Salt-and-Pepper noise evaluated alongside Gaussian noise in SolarEye?"*
   - *Key points:* Sensor readout / transmission glitches produce impulse outliers (which linear mean filters smear, motivating median/alpha-trimmed filters in M3), while thermal/readout electronics produce additive Gaussian noise.
5. **Full Pipeline:** *"Why are masks encoded with `1 = dark defect` when raw EL defects are dark pixels?"*
   - *Key points:* Foreground `1` must represent the target defect class for IoU, Dice, connected components, and morphological opening/closing—requiring explicit polarity inversion during thresholding.

---

## 24. Definition of Done

### Milestone 1 (Topic Settled — Week 9) DoD
- [ ] `data/README.md`, `data/download_dataset.py`, and `data/validate_dataset.py` merged to `main` after Member 1 review.
- [ ] All metadata vs unverified archive checks accurately labeled (`Verified (Metadata)` vs `Pending verification`).

### Milestone 2 (Baselines Ready — Week 10) DoD
- [ ] `data/validate_dataset.py` executed on local/Colab MSPS archive and `data/README.md` updated with empirical image/mask properties.
- [ ] `src/data.py`, `data/splits/dev_manifest.csv`, `data/splits/test_manifest.csv`, and `tests/test_data.py` merged to `main`.
- [ ] `pytest tests/test_data.py -v` passes 100%, and Members 3 & 4 successfully load dev images via `src.data` for M2 analysis and baselines.
