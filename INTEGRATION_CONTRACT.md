# SolarEye Integration Contract & Shared Interfaces

**Document Owner:** Planner (Architecture) & Member 1 (Tech Lead)  
**Target Codebase:** `src/`, `configs/`, `experiments/`, `tests/`  
**Status:** `In progress` (Canonical contract governing M1–M4 implementation)

> [!IMPORTANT]
> Every team member must conform strictly to the data types, foreground polarity, border modes, function signatures, and logging schemas defined here. Breaking a contract signature without a team-reviewed PR update to this document is a merge blocker.

---

## 1. Global Data Types, Value Ranges & Polarity Conventions

| Data Entity | Canonical `dtype` | Canonical Value Range / Semantics | Rules & Conversions |
| :--- | :--- | :--- | :--- |
| **Grayscale Image** | `np.uint8` | `[0, 255]` (`0` = black/dark, `255` = bright silicon) | Shape `(H, W)`. Never pass `(H, W, 1)` into pipeline stages. |
| **RGB Display / Input Image** | `np.uint8` | `[0, 255]` in **RGB** channel order | Shape `(H, W, 3)`. If loaded via `cv2.imread` (BGR), immediately apply `bgr_to_rgb()` (`cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`) before any display or processing. |
| **Binary Defect Mask** | `np.uint8` | `{0, 1}` ONLY:<br>`1` = **Defect Foreground** (dark cracks, black spots, busbar breaks)<br>`0` = **Healthy Silicon Background** | Shape `(H, W)`. Raw masks encoded as `{0, 255}` must be normalized via `(raw_mask > 0).astype(np.uint8)`. Never resize masks with bilinear/bicubic interpolation—always use `cv2.INTER_NEAREST`. |
| **Normalized Spatial Float** | `np.float32` or `np.float64` | `[0.0, 1.0]` (`img.astype(np.float64) / 255.0`) | Used inside spatial filters, gamma/log transforms, and noise generators. Must be rounded and clipped (`np.clip(..., 0, 255).astype(np.uint8)`) at stage exit unless explicitly returning float spectra/maps. |
| **Unbounded Gradient / FFT** | `np.float64` / `np.complex128` | Unbounded real or complex values | E.g., 2D FFT (`np.fft.fft2`), centered magnitude spectra, Sobel/Laplacian residuals. Only convert to `uint8` for visualization or after explicit normalization. |

### Foreground Polarity Rule (Critical for PV EL Images)
In Photovoltaic Electroluminescence (EL) images, active healthy silicon emits near-infrared light (bright pixels), while cracks, dead/black regions, and broken busbars impede current flow and appear **dark**.  
Because binary segmentation masks must use `1 = defect foreground`, every thresholding algorithm **must invert polarity** (`dark_defects=True` by default, e.g., `raw < thresh`, or threshold `(255 - gray)` so dark defects become bright foreground peaks).

---

## 2. Border Handling, Seed & Style Standards

- **Border Parity (`reflect`):**
  - NumPy implementations MUST use `np.pad(arr, pad_width=k, mode='reflect')`.
  - OpenCV equivalents MUST use `cv2.BORDER_REFLECT_101` (which mirrors `d c b | a b c d | c b a` without repeating the edge pixel—exact match to `np.pad(..., mode='reflect')`).
  - *Never* mix `cv2.BORDER_REFLECT` (`c b a | a b c d | d c b`) with `np.pad(..., mode='reflect')` in equivalence tests.
- **Determinism (`seed=42`):**
  - All stochastic operations (train/dev/test splitting, Gaussian/Salt-Pepper/Speckle/Poisson noise synthesis) MUST accept `seed: int = 42` and use `rng = np.random.default_rng(seed)`.
- **Code Style & Prohibitions:**
  - Max line length: **95 characters**.
  - Every module, class, and function must have docstrings; zero hard-coded machine paths (`pathlib.Path` relative to repo root or CLI/config).
  - Strict prohibition: **NO** `torch`, `tensorflow`, `keras`, `sklearn` classifiers/regressors, `timm`, `ultralytics`, or pretrained models anywhere in `src/` or `tests/`.

---

## 3. Canonical Module & Function Signatures

### 3.1 `src/config.py` (Owner: Member 1)
```python
from pathlib import Path
from typing import Any, Dict

DEFAULT_SEED: int = 42

def load_config(config_path: str | Path) -> Dict[str, Any]:
    """Load and validate a YAML/JSON pipeline configuration file."""

def validate_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Verify required top-level keys, pipeline name, and seed=42 defaults."""
```

### 3.2 `src/data.py` (Owner: Member 2)
```python
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd

def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert BGR uint8 image (H,W,3) to RGB uint8 [0,255] before display."""

def load_image(
    path: str | Path, grayscale: bool = True, target_size: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """Load image as uint8 [0,255]. Grayscale -> (H,W); RGB -> (H,W,3) BGR-converted."""

def load_mask(
    path: str | Path, target_size: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """Load mask as uint8 {0,1} (1=defect). Resize with INTER_NEAREST if target_size=(H,W)."""

def create_dev_test_split(
    manifest_df: pd.DataFrame,
    test_ratio: float = 0.3,
    seed: int = 42,
    group_col: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create deterministic, leakage-free dev/test splits (respecting group_col if set)."""

def add_gaussian_noise(
    image: np.ndarray, mean: float = 0.0, sigma: float = 15.0, seed: int = 42
) -> np.ndarray:
    """Add Gaussian noise (uint8 [0,255] -> uint8 [0,255])."""

def add_salt_pepper_noise(
    image: np.ndarray, density: float = 0.05, salt_ratio: float = 0.5, seed: int = 42
) -> np.ndarray:
    """Add impulse Salt (255) & Pepper (0) noise using RNG(seed)."""

def add_speckle_noise(
    image: np.ndarray, variance: float = 0.04, seed: int = 42
) -> np.ndarray:
    """Add multiplicative speckle noise I + I * N(0, variance)."""

def add_poisson_noise(image: np.ndarray, peak: float = 30.0, seed: int = 42) -> np.ndarray:
    """Add signal-dependent Poisson shot noise scaled by peak."""
```

### 3.3 `src/metrics.py` (Owner: Member 1)
```python
import numpy as np

def compute_mse(ref: np.ndarray, target: np.ndarray) -> float:
    """Mean Squared Error in float64 intensity space [0, 255]."""

def compute_psnr(ref: np.ndarray, target: np.ndarray, max_val: float = 255.0) -> float:
    """PSNR in dB. Returns float('inf') when MSE == 0.0."""

def compute_iou(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Intersection-over-Union on {0,1} masks. Returns 1.0 if both empty, 0.0 if union>0 & inter==0."""

def compute_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Dice / F1 score on {0,1} masks. Returns 1.0 if both empty, 0.0 if denom>0 & inter==0."""

def compute_precision_recall(pred_mask: np.ndarray, gt_mask: np.ndarray) -> tuple[float, float]:
    """Return (precision, recall) on {0,1} masks with empty-mask guards."""

def compute_area_error(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Relative or absolute defect area error between predicted and ground-truth masks."""

def compute_count_error(pred_mask: np.ndarray, gt_mask: np.ndarray) -> int:
    """Connected-component defect count difference (pred_count - gt_count or abs diff)."""
```

### 3.4 `src/enhancement.py` (Owner: Member 3)
Mandatory spatial enhancements (M3): negative, log, power-law/gamma, contrast stretching, histogram equalization (`histogram_equalization_numpy`), mean, Gaussian, median smoothing, Laplacian & gradient sharpening, `convolve2d_numpy` (with `(N - F + 2P)/S + 1` shape check and `reflect` parity), plus optional histogram matching / CLAHE.
```python
import numpy as np

def convolve2d_numpy(
    image: np.ndarray, kernel: np.ndarray, border_mode: str = "reflect"
) -> np.ndarray:
    """Pure NumPy 2D spatial convolution with reflect border parity."""

def histogram_equalization_numpy(image: np.ndarray) -> np.ndarray:
    """Pure NumPy global histogram equalization via CDF mapping (uint8 -> uint8)."""

def apply_negative(image: np.ndarray) -> np.ndarray:
    """Intensity negative transform (255 - image)."""

def apply_log_transform(image: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Logarithmic dynamic-range compression scaled back to uint8 [0,255]."""

def apply_gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """Power-law intensity transform via normalized [0,1] LUT."""

def contrast_stretch(image: np.ndarray, low_pct: float = 2.0, high_pct: float = 98.0) -> np.ndarray:
    """Piecewise linear contrast stretching to uint8 [0,255]."""

def apply_clahe(
    image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)
) -> np.ndarray:
    """Contrast Limited Adaptive Histogram Equalization (uint8 -> uint8)."""
```

### 3.5 `src/restoration.py` (Owner: Member 2)
Mandatory spatial order-statistic & linear restoration filters (M3): mean, median (`median_filter_numpy`), max, min, midpoint, alpha-trimmed mean (`alpha_trimmed_mean_filter_numpy`).
```python
import numpy as np

def median_filter_numpy(
    image: np.ndarray, ksize: int = 3, border_mode: str = "reflect"
) -> np.ndarray:
    """Pure NumPy 2D median filter for impulse (Salt & Pepper) denoising."""

def alpha_trimmed_mean_filter_numpy(
    image: np.ndarray, ksize: int = 3, d_trim: int = 2, border_mode: str = "reflect"
) -> np.ndarray:
    """Pure NumPy alpha-trimmed mean filter (hybrid Gaussian + impulse restoration)."""

def mean_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Arithmetic mean spatial smoothing (uint8 -> uint8)."""

def max_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Order-statistic maximum filter (uint8 -> uint8)."""

def min_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Order-statistic minimum filter (uint8 -> uint8)."""

def midpoint_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Order-statistic midpoint filter (0.5 * (min + max))."""
```

### 3.6 `src/frequency_masks.py` (Owner: Member 1)
```python
from typing import Tuple
import numpy as np

def ideal_frequency_mask(
    shape: Tuple[int, int], cutoff: float, mode: str = "lowpass"
) -> np.ndarray:
    """Centered 2D Ideal LP/HP frequency mask in float64 [0.0, 1.0]."""

def butterworth_frequency_mask(
    shape: Tuple[int, int], cutoff: float, order: int = 2, mode: str = "lowpass"
) -> np.ndarray:
    """Centered 2D Butterworth LP/HP frequency mask in float64 [0.0, 1.0]."""

def gaussian_frequency_mask(
    shape: Tuple[int, int], cutoff: float, mode: str = "lowpass"
) -> np.ndarray:
    """Centered 2D Gaussian LP/HP frequency mask in float64 [0.0, 1.0]."""
```

### 3.7 `src/frequency.py` (Owner: Member 2)
```python
from typing import Tuple
import numpy as np

def compute_fft_spectrum(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return (centered_complex_fft, log_magnitude_spectrum_uint8) using NumPy FFT."""

def apply_frequency_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Multiply centered 2D FFT by float64 mask in [0,1] and invert back to uint8 [0,255]."""
```

### 3.8 `src/segmentation.py` (Owner: Member 4)
Mandatory M2/M3 methods: Baseline 0 (`raw < 127`), Baseline 1 (Otsu + 3x3 opening), `otsu_threshold_numpy`, `sobel_gradients_numpy`, Roberts, Prewitt, Laplacian, LoG, Global, Adaptive thresholding, line/point masks, Hough/edge linking (distinguishing straight busbars/fingers from irregular cracks).
```python
from typing import Tuple
import numpy as np

def baseline0_fixed_threshold(
    image: np.ndarray, threshold: int = 127, dark_defects: bool = True
) -> np.ndarray:
    """Strictly pure Baseline 0: (image < threshold).astype(np.uint8), NO pre/post-processing."""

def otsu_threshold_numpy(
    image: np.ndarray, dark_defects: bool = True
) -> Tuple[int, np.ndarray]:
    """Pure NumPy Otsu threshold -> (thresh, uint8 {0,1} mask)."""

def sobel_gradients_numpy(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pure NumPy Sobel Gx, Gy, and gradient magnitude."""

def adaptive_threshold_dark(
    image: np.ndarray, block_size: int = 31, c_offset: float = 8.0, method: str = "gaussian"
) -> np.ndarray:
    """Local adaptive thresholding targeting dark EL defects -> uint8 {0,1}."""
```

### 3.9 `src/morphology.py` (Owner: Member 4)
Mandatory M3 methods: `binary_erosion_numpy`, `binary_dilation_numpy`, opening/closing across 3+ sizes & 2+ structuring-element shapes, hole filling, small-object removal, connecting broken cracks, connected components (`count`, `defect_pixels`, `cell_region_area_pct`, `bboxes`), and experimental image-based decision rule (explicitly NOT electrical efficiency or safety certification).
```python
from typing import Dict
import numpy as np

def binary_erosion_numpy(mask: np.ndarray, ksize: int = 3, shape: str = "rect") -> np.ndarray:
    """Pure NumPy binary erosion on uint8 {0,1} mask."""

def binary_dilation_numpy(mask: np.ndarray, ksize: int = 3, shape: str = "rect") -> np.ndarray:
    """Pure NumPy binary dilation on uint8 {0,1} mask."""

def morphological_open_close(
    mask: np.ndarray, open_ksize: int = 3, close_ksize: int = 3, shape: str = "rect"
) -> np.ndarray:
    """Sequential opening + closing -> uint8 {0,1}."""

def remove_small_components(mask: np.ndarray, min_area_px: int = 15) -> np.ndarray:
    """Filter connected components smaller than min_area_px -> uint8 {0,1}."""

def quantify_defects(mask: np.ndarray, connectivity: int = 8) -> Dict[str, object]:
    """Return count, defect_pixels, cell_region_area_pct, bboxes, and experimental decision label."""
```

### 3.10 `src/pipeline.py`, `src/evaluate.py`, `src/run_pipeline.py` (Owner: Member 1)
```python
# src/pipeline.py
def run_baseline_0(image: np.ndarray, threshold: int = 127, dark_defects: bool = True) -> dict:
    """Execute pure Baseline 0 and return {'mask', 'stage_outputs', 'timings_s'}."""

def run_baseline_1(image: np.ndarray, opening_size: int = 3, dark_defects: bool = True) -> dict:
    """Execute Baseline 1 (Otsu + 3x3 opening) and return {'mask', 'stage_outputs', 'timings_s'}."""

def run_pipeline_a(image: np.ndarray, config: dict) -> dict:
    """Pipeline A: Spatial enhancement -> Global or Otsu threshold."""

def run_pipeline_b(image: np.ndarray, config: dict) -> dict:
    """Pipeline B: Noise removal (spatial/frequency) -> Adaptive threshold or edge segmentation."""

def run_pipeline_c(image: np.ndarray, config: dict) -> dict:
    """Pipeline C: Enhancement+restoration -> Adaptive/edge -> Morphology -> CC + decision rule."""
```

---

## 4. `experiments/experiment_log.csv` — Canonical 16-Column Schema

Every experiment run appends **one row** to `experiments/experiment_log.csv` with this exact header:
```csv
run_id,date,author,pipeline,stage,method,parameters,random_seed,processing_time_s,dataset_split,metric_name,metric_value,secondary_metrics,config_file,git_commit,notes
```

| Col # | Column Name | Type / Format | Purpose |
| :---: | :--- | :--- | :--- |
| 1 | `run_id` | `str` (`EXP-M2-001`) | Unique experiment identifier |
| 2 | `date` | ISO-8601 UTC (`2026-11-28`) | Execution date/timestamp |
| 3 | `author` | `M1` \| `M2` \| `M3` \| `M4` | Responsible team member |
| 4 | `pipeline` | `baseline_0` \| `baseline_1` \| `pipeline_a` \| `pipeline_b` \| `pipeline_c` | Pipeline under test |
| 5 | `stage` | `restoration` \| `enhancement` \| `segmentation` \| `end_to_end` | Evaluated stage |
| 6 | `method` | `str` | Primary method / variant name |
| 7 | `parameters` | JSON/semicolon string | Key parameters (`threshold=127`, `d0=30`) |
| 8 | `random_seed` | `int` (`42`) | RNG seed used |
| 9 | `processing_time_s` | `float` | Wall-clock runtime in seconds |
| 10 | `dataset_split` | `dev` \| `test` \| `kaggle_solarcells` | Evaluated split |
| 11 | `metric_name` | `mean_iou` \| `mean_psnr` \| `mean_dice` | Primary metric name |
| 12 | `metric_value` | `float` | Primary metric value |
| 13 | `secondary_metrics` | JSON string | e.g., `{"dice": ..., "area_err": ..., "count_err": ...}` |
| 14 | `config_file` | relative path | e.g., `configs/baseline_0.yaml` |
| 15 | `git_commit` | short SHA | Git commit hash at run time |
| 16 | `notes` | `str` | Observations / failure summary |

---

## 5. YAML Configuration Files (`configs/*.yaml`)

Standard config files under `configs/`:
- `configs/dataset.yaml`
- `configs/baseline_0.yaml`
- `configs/baseline_1.yaml`
- `configs/pipeline_a.yaml`
- `configs/pipeline_b.yaml`
- `configs/pipeline_c.yaml`

---

## 6. Error Handling Contract

1. **Missing / Corrupt File:** `load_image` and `load_mask` MUST raise `FileNotFoundError` or `ValueError` with the offending path—never silently return `None`.
2. **Shape / Dtype Mismatch:** `src/metrics.py` MUST validate `pred_mask.shape == gt_mask.shape` and verify binary values `{0, 1}` (raising `ValueError` on non-binary masks or mismatched shapes).
3. **Zero-Division Guards:**
   - `compute_psnr`: if `mse == 0.0`, return `float("inf")` without dividing by zero.
   - `compute_iou` / `compute_dice`: if `union == 0` (both prediction and GT have zero defect pixels), return `1.0` (exact empty-mask agreement). If `union > 0` and `intersection == 0`, return `0.0`.
   - `compute_precision_recall` & `compute_area_error`: handle `gt_area == 0` deterministically without `ZeroDivisionError`.
4. **Unseen-Image Inference Mode:** `run_pipeline_*` and `src/run_pipeline.py` without `--manifest` MUST run cleanly with **no ground-truth mask** required, outputting overlay visualizations and defect quantification stats (labeled strictly as an **experimental image-based decision rule**, explicitly NOT electrical efficiency or safety certification).
