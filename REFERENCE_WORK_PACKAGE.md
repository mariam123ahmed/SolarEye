> AI-assisted original guidance. Use START_HERE.md for the current ownership and branch rules; reproduce any claimed results yourself.

# Work Package — Phase 1 (Milestones 1 & 2): Member 3 — Image Analysis & Enhancement

> **Document Status:** Active Phase 1 Specification (Milestones 1 & 2)  
> **Target Tags:** `m1-topic-settled` (Week 9), `m2-baselines-ready` (Week 10)  
> **Project:** SolarEye — Explainable PV Defect Detection & Quantification using Classical DIP  
> **Course:** CSE281 Digital Image Processing (Alamein International University)

---

## Milestone Quick Navigation (M1 vs M2)

| Dimension | Milestone 1 (Topic Settled — Week 9) | Milestone 2 (Baselines Ready — Week 10) |
| :--- | :--- | :--- |
| **Primary Goal** | Design the exploratory image analysis protocol, testable DIP hypotheses, and `notebooks/01_image_analysis.ipynb` skeleton | Execute full dev-set image analysis (stats, histograms, FFT spectra, spatial resolution & gray-level quantization studies) and Findings->Design Decisions table |
| **Key Files** | `notebooks/01_image_analysis.ipynb` (skeleton), `experiments/enhancement/.gitkeep` | `notebooks/01_image_analysis.ipynb` (completed M2 analysis), `src/enhancement.py` (sampling/quantization analysis helpers), `tests/test_enhancement.py`, `experiments/figures/` |
| **Branches** | `feature/m01-image-analysis-plan` | `feature/m02-exploratory-image-analysis` |
| **Reviewer** | Member 1 (Tech Lead) | Member 2 (checks data loader & FFT spectrum usage) & Member 1 |
| **Release Tag** | `m1-topic-settled` | `m2-baselines-ready` |

---

## 0. Quick Action Checklist

### Milestone 1 (Topic Settled — Week 9)
- [ ] Create branch `feature/m01-image-analysis-plan` from `main`.
- [ ] Write Image Analysis Plan & Hypothesis Matrix (H1–H4) in `notebooks/01_image_analysis.ipynb`.
- [ ] Verify notebook skeleton uses `src.data` and `data/splits/dev_manifest.csv` only (no hardcoded paths).
- [ ] Open PR reviewed by **Member 1** and merge before tag `m1-topic-settled`.

### Milestone 2 (Baselines Ready — Week 10)
- [ ] Create branch `feature/m02-exploratory-image-analysis` from `main`.
- [ ] Implement `quantize_gray_levels`, `downsample_and_restore`, and `compute_centered_log_spectrum` in `src/enhancement.py`.
- [ ] Complete `tests/test_enhancement.py` (3x3 quantization & 4x4 FFT DC hand examples) and pass `pytest tests/test_enhancement.py -v`.
- [ ] Run full dev-set stats, typical vs difficult histograms + centered log-FFT spectra, spatial resolution study, and gray-level quantization (`256->4`) in `notebooks/01_image_analysis.ipynb`.
- [ ] Save `experiments/figures/m02_*.png` + Findings -> Design Decisions table, open PR reviewed by **Member 2** & **Member 1**, and merge before tag `m2-baselines-ready`.

---

## 1. Member Identity & Role

- **Member ID:** Member 3
- **Primary Title:** Exploratory Image Analysis & Spatial Enhancement Lead
- **Scope in Phase 1 (M1 & M2):**
  - Formulate SolarEye's image-characteristic hypotheses (linking physical EL defects, noise, uneven illumination, and contrast compression to classical DIP choices).
  - Conduct the **complete Exploratory Image Analysis** on `data/splits/dev_manifest.csv` ONLY (never touch `test_manifest.csv`): dimensions, dtype, intensity distributions, histograms of typical vs difficult EL images, centered log-magnitude Fourier spectra, spatial-resolution reduction study, and gray-level quantization study (`256 -> 128 -> 64 -> 32 -> 16 -> 8 -> 4` levels) to determine the lowest usable bit-depth/gray-level setting.
  - Deliver an evidence-backed **Findings -> Design Decisions Table** guiding Milestone 3 enhancement, restoration, frequency filtering, and thresholding choices.
- **Future-Phase Continuity (M3/M4 Preview — Do Not Implement Full M3 Enhancers Yet):** In Milestone 3 you will implement all mandatory spatial enhancement methods in `src/enhancement.py` (negative, log, power-law/gamma, contrast stretching, histogram equalization, mean/Gaussian/median smoothing, Laplacian/gradient sharpening) including **2+ pure NumPy operations** (`convolve2d_numpy` and `histogram_equalization_numpy`). In M2, focus strictly on image analysis, spatial sampling, and gray-level quantization utilities.

---

## 2. Milestone Objectives

### Milestone 1 (Topic Settled — Week 9)
1. Author an **Image Analysis Plan & Hypothesis Matrix** mapping specific EL visual phenomena (dark micro-cracks, uneven background electroluminescence, bright busbars/fingers, low-contrast black spots, sensor noise) to concrete M2 measurements and M3/M4 classical DIP hypotheses.
2. Create the structured skeleton of `notebooks/01_image_analysis.ipynb` using `src.data.load_image`, `src.data.load_mask`, and `data/splits/dev_manifest.csv` (with `BGR -> RGB` display checks and zero hardcoded paths).
3. Prepare clean placeholder helper signatures for spatial downsampling and gray-level quantization analysis in `src/enhancement.py` (keeping M3 enhancement functions as `NotImplementedError` stubs).

### Milestone 2 (Baselines Ready — Week 10)
1. Run full quantitative and visual exploratory analysis across the **dev set** (`dev_manifest.csv`): image shapes, dtype, min/max/mean/std intensity, defect-area ratios, and foreground vs background pixel intensity separability.
2. Plot side-by-side **typical vs difficult EL images** and their **intensity histograms** (identifying bimodal vs unimodal/skewed distributions, uneven illumination gradients, low contrast, and visible noise).
3. Compute and interpret **2D centered log-magnitude Fourier spectra** ($\log(1 + |F(u,v)|)$) highlighting periodic busbar/finger grid harmonics vs broadband crack energy.
4. Execute the **Spatial-Resolution Reduction Study** (e.g., `1.0x -> 0.5x -> 0.25x -> 0.125x` with anti-aliased resize & PSNR/crack-visibility audit) and **Gray-Level Quantization Study** (`256 -> 128 -> 64 -> 32 -> 16 -> 8 -> 4` levels) to identify the lowest usable settings that preserve thin micro-cracks.
5. Produce the **Findings -> Design Decisions Table** and store all M2 analysis figures/tables cleanly under `experiments/figures/`.

---

## 3. Official Specification References (Pages 1–11)

| Spec Page | Section / Topic | Relevance to Member 3 (M1 & M2) |
| :--- | :--- | :--- |
| **Page 2** | Exploratory Image Analysis Requirements | Mandates dims, dtype, intensity range, histograms (typical vs difficult), visible noise, uneven illumination, low contrast, centered log-magnitude Fourier spectrum, spatial resolution reduction, and gray-level quantization (`256` down to `4`). |
| **Page 3** | Spatial Enhancement Methods (Preview for M3) | Your M2 Findings -> Design Decisions table must directly justify which M3 spatial transforms (gamma, CLA/contrast stretch, hist eq, smoothing, sharpening) are needed. |
| **Page 4** | Frequency Domain & NumPy Requirements | Centered log-magnitude Fourier spectrum analysis in M2 (`np.fft.fft2`, `np.fft.fftshift`) sets up Member 1 & 2's M3 frequency filters. |
| **Page 7** | Code Quality (`<=95` chars/line, docstrings, `BGR->RGB`) | All helper functions in `src/enhancement.py` and `tests/test_enhancement.py` obey style rules. |
| **Page 11** | Grading Rubric: 10% Image Analysis | M2 Image Analysis accounts directly for **10% of the total course grade**—completeness and depth here are critical. |

---

## 4. Prerequisites & Dependencies

### Milestone 1 (Week 9)
- Agreement on `docs/INTEGRATION_CONTRACT.md` (`uint8` `[0,255]` grayscale, `{0,1}` mask with `1 = dark defect`).
- Python packages: `numpy`, `matplotlib`, `pandas`, `scipy` or `opencv-python`.

### Milestone 2 (Week 10)
- **M1 Gate (`m1-topic-settled`) passed.**
- **From Member 2:** `src/data.py` (`load_image`, `load_mask`) and `data/splits/dev_manifest.csv` merged on `main`.
- **From Member 1:** `src/metrics.py` (`compute_mse`, `compute_psnr`) merged so your spatial resolution and gray-level quantization studies compute exact reconstruction PSNR/MSE!

---

## 5. Detailed Implementation Tasks

### Milestone 1 (Topic Settled — Week 9)
1. **Build the Hypothesis Matrix (inside `notebooks/01_image_analysis.ipynb` Section 1):**
   - *H1 (Foreground Polarity):* EL defects (cracks, black spots) have lower mean pixel intensity than surrounding active silicon, causing naive `raw > T` thresholding to invert foreground/background.
   - *H2 (Uneven Illumination):* Vignetting or non-uniform EL excitation shifts local background intensity across the cell, causing fixed global thresholding (`T=127`) to produce massive false positives in dim corners (motivating adaptive/local thresholding or illumination correction in M3).
   - *H3 (Periodic Grid Harmonics):* Parallel silver fingers and busbars create strong vertical/horizontal spikes in the 2D Fourier magnitude spectrum, enabling frequency/Hough analysis to separate structural grid lines from irregular micro-cracks.
   - *H4 (Resolution & Bit-Depth Floor):* Thin 1–3 pixel cracks vanish under aggressive spatial downsampling (`<= 0.25x`) or coarse quantization (`<= 8` levels), establishing minimum operational quality bounds.
2. **Initialize `notebooks/01_image_analysis.ipynb` Skeleton:**
   - Structure reproducible Markdown headers + code cells importing `src.config`, `src.data`, `src.metrics`, reading `data/splits/dev_manifest.csv`, and verifying zero access to `test_manifest.csv`.

### Milestone 2 (Baselines Ready — Week 10)
1. **Implement Analysis Helper Functions in `src/enhancement.py` (M2 Scope Only):**
   - `quantize_gray_levels(image: np.ndarray, levels: int) -> np.ndarray`: uniformly quantizes `uint8` `[0, 255]` into `levels` in `{256, 128, 64, 32, 16, 8, 4}` and rescales back to `[0, 255]` `uint8` for fair PSNR comparison and visual display.
   - `downsample_and_restore(image: np.ndarray, scale: float) -> np.ndarray`: downsamples by `scale` in `{1.0, 0.5, 0.25, 0.125}` (using area/bilinear averaging) and upsamples back to original `(H, W)` so pixel-aligned MSE/PSNR and crack visibility can be measured.
   - `compute_centered_log_spectrum(image: np.ndarray) -> np.ndarray`: computes $\log(1 + |\text{fftshift}(\text{fft2}(I))|)$ for frequency visualization.
2. **Run Dev-Set Summary Statistics:**
   - Loop over all dev images in `data/splits/dev_manifest.csv`: record shape, dtype, global min/max, per-image mean/std, defect pixel fraction, mean intensity inside defect (`mask == 1`) vs healthy silicon (`mask == 0`), and contrast gap $\Delta \mu = \mu_{\text{healthy}} - \mu_{\text{defect}}$.
3. **Typical vs Difficult Case Audit & Histograms:**
   - Select 3 **typical** dev images (high $\Delta \mu$, uniform illumination, crisp crack/spot) and 3 **difficult** dev images (low $\Delta \mu$, severe vignetting/dark edges, faint hairline crack, or heavy background noise).
   - Plot `Image | Ground-Truth Mask Overlay | Intensity Histogram (Healthy vs Defect Overlay) | Centered Log-Magnitude FFT Spectrum` for each.
4. **Spatial Resolution & Gray-Level Quantization Experiments:**
   - Spatial scales: `1.0x`, `0.5x`, `0.25x`, `0.125x` across 20 representative dev images (including hairline-crack cases). Compute MSE/PSNR vs original and visually inspect at what scale 1–2 px cracks break or disappear.
   - Gray levels: `256, 128, 64, 32, 16, 8, 4` across the same 20 dev images. Compute MSE/PSNR, intensity histogram collapse, and determine the **lowest usable gray-level setting** (typically `32` or `16` levels before false contouring destroys faint cracks).
5. **Synthesize the Findings -> Design Decisions Table:**
   - Map every quantitative observation from Steps 2–4 to concrete M3 design parameters (e.g., which spatial enhancer fixes low $\Delta\mu$, why adaptive thresholding beats global thresholding on uneven illumination, minimum spatial resolution `>= 0.5x`, minimum gray levels).

---

## 6. Files to Create / Modify

### Milestone 1 (Week 9)
- `notebooks/01_image_analysis.ipynb` (create clean reproducible skeleton with Hypothesis Matrix)
- `experiments/enhancement/.gitkeep` (create folder marker)

### Milestone 2 (Week 10)
- `src/enhancement.py` (implement M2 analysis helpers: `quantize_gray_levels`, `downsample_and_restore`, `compute_centered_log_spectrum`; keep M3 spatial enhancement functions as `NotImplementedError` stubs)
- `notebooks/01_image_analysis.ipynb` (complete and execute all M2 dev-set analysis cells)
- `tests/test_enhancement.py` (implement M2 tests for quantization levels, downsampling shape parity, and centered FFT spectrum properties)
- `experiments/enhancement/dev_image_stats.csv` (per-image dev summary stats)
- `experiments/figures/m02_*.png` (histograms, FFT spectra, spatial resolution grid, quantization grid)

---

## 7. Proposed Function Signatures

```python
# src/enhancement.py (Milestone 2 Analysis Utilities)
def quantize_gray_levels(image: np.ndarray, levels: int) -> np.ndarray: ...

def downsample_and_restore(
    image: np.ndarray,
    scale: float,
) -> np.ndarray: ...

def compute_centered_log_spectrum(image: np.ndarray) -> np.ndarray: ...
```

---

## 8. Input / Output Contracts

1. **`quantize_gray_levels(image, levels)`:**
   - Input: `image` (`np.ndarray`, 2D `uint8` `[0, 255]`), `levels` (`int`, power of 2 in `{2, 4, 8, 16, 32, 64, 128, 256}`, raise `ValueError` otherwise).
   - Output: `np.ndarray`, `dtype=np.uint8`, same shape `(H, W)`, containing at most `levels` unique quantized intensity values in `[0, 255]`.
2. **`downsample_and_restore(image, scale)`:**
   - Input: `image` (`np.ndarray`, 2D `uint8`), `scale` (`float`, `0 < scale <= 1.0`, raise `ValueError` otherwise).
   - Output: `np.ndarray`, `dtype=np.uint8`, **exact original shape** `(H, W)` so pixel-aligned `compute_mse` and `compute_psnr` work cleanly.
3. **`compute_centered_log_spectrum(image)`:**
   - Input: `image` (`np.ndarray`, 2D `uint8` or `float`).
   - Output: `np.ndarray`, `dtype=np.float64`, shape `(H, W)`, non-negative values $\log(1 + |F_{\text{shifted}}(u, v)|)$ with DC component $(0, 0)$ shifted to `(H // 2, W // 2)`.

---

## 9. Mathematical Background

1. **Uniform Gray-Level Quantization ($L = 2^b$ levels from $256$):**
   Let bin width $\Delta = 256 / L$. For each pixel $I(r, c) \in \{0, \dots, 255\}$:
   $$q(r, c) = \left\lfloor \frac{I(r, c)}{\Delta} \right\rfloor \in \{0, 1, \dots, L - 1\}$$
   To reconstruct back into `[0, 255]` `uint8` using bin midpoints (or full-span scaling):
   $$\hat{I}_{\text{mid}}(r, c) = \text{round}\!\left(\left(q(r, c) + 0.5\right)\Delta - 0.5\right) \quad \text{or} \quad \hat{I}_{\text{span}}(r, c) = \text{round}\!\left(q(r, c) \cdot \frac{255}{L - 1}\right)$$
   *(Note: Use the bin-midpoint formula $\lfloor (q + 0.5)\Delta \rfloor$ or full-span scaling consistently and document which one you use! Full-span `round(q * 255 / (L - 1))` preserves `0` and `255` endpoints cleanly, while midpoint minimizes expected MSE $\approx \Delta^2 / 12$.)*
2. **Theoretical Uniform Quantization Noise (MSE & PSNR):**
   For a uniformly distributed intensity signal with step $\Delta = 256 / L$:
   $$\text{MSE}_{\text{theory}} \approx \frac{\Delta^2}{12}, \qquad \text{PSNR}_{\text{theory}} \approx 10 \log_{10}\left(\frac{255^2}{\Delta^2 / 12}\right) \approx 6.02 b + 10.79\text{ dB}$$
   Comparing your measured EL image quantization PSNR against $6.02b + 10.79$ dB verifies your implementation and highlights EL histogram non-uniformity!
3. **2D Discrete Fourier Transform (Centered Log-Magnitude Spectrum):**
   $$F(u, v) = \sum_{x=0}^{H-1} \sum_{y=0}^{W-1} I(x, y) e^{-j 2\pi \left(\frac{ux}{H} + \frac{vy}{W}\right)}$$
   $$S_{\log}(u, v) = \ln\!\left(1 + \left|F_{\text{shift}}(u, v)\right|\right)$$
   Log compression is essential because DC energy $|F_{\text{shift}}(H/2, W/2)|$ exceeds high-frequency energy by $10^4\times$–$10^6\times$.

---

## 10. Pseudocode / Implementation Guidance

```python
# Pseudocode for src/enhancement.py (M2 analysis functions)

def quantize_gray_levels(image, levels):
    # 1. Validate image.ndim == 2 and image.dtype == np.uint8
    # 2. Validate levels in {2, 4, 8, 16, 32, 64, 128, 256}
    # 3. If levels == 256: return image.copy()
    # 4. step = 256.0 / levels
    # 5. bin_idx = np.floor(image.astype(np.float64) / step)
    # 6. Reconstruct with midpoint: out = np.floor((bin_idx + 0.5) * step)
    #    (or full-span: np.rint(bin_idx * (255.0 / (levels - 1))))
    # 7. Return np.clip(out, 0, 255).astype(np.uint8)

def compute_centered_log_spectrum(image):
    # 1. Validate 2D image, convert to np.float64
    # 2. F = np.fft.fft2(img_f)
    # 3. F_shift = np.fft.fftshift(F)
    # 4. Return np.log1p(np.abs(F_shift))
```

---

## 11. NumPy Implementation Requirements

- **Milestone 2 Requirement:** Implement `quantize_gray_levels` and `compute_centered_log_spectrum` in **pure NumPy** (`np.floor`, `np.clip`, `np.fft.fft2`, `np.fft.fftshift`, `np.log1p`, `np.abs`).
- **Milestone 3 Bridge (Know Now, Implement in M3):** Member 3 satisfies the official "2+ non-trivial NumPy DIP operations" requirement in Milestone 3 via `convolve2d_numpy` (checking output shape `(N - F + 2P)/S + 1` and matching `cv2.BORDER_REFLECT_101` via `np.pad(..., mode='reflect')`) and `histogram_equalization_numpy` (matching `cv2.equalizeHist`). Start building intuition for histogram CDFs during your M2 typical-vs-difficult histogram analysis!

---

## 12. Library Equivalence Checks

1. **`quantize_gray_levels` Equivalence:**
   Compare your vectorized `bin_idx` quantization against `np.digitize(image, bins=np.linspace(0, 256, levels + 1)[1:-1])` to assert `np.array_equal(q1, q2)` on `levels = 8, 16, 32`. Also assert `len(np.unique(out)) <= levels`.
2. **`compute_centered_log_spectrum` Equivalence:**
   Compare `np.fft.fft2` magnitude against `cv2.dft(image.astype(np.float32), flags=cv2.DFT_COMPLEX_OUTPUT)` (after `np.fft.fftshift` and `cv2.magnitude`) -> `max_abs_diff < 1e-4` (float32 vs float64 tolerance).
3. **`downsample_and_restore` Check:**
   Verify `downsample_and_restore(img, scale=1.0)` returns exact identity `np.array_equal(out, img)`.

---

## 13. Hand-Calculation Examples

### Hand Example A: `3x3` Gray-Level Quantization (`256 -> 4` levels, Midpoint Reconstruction)
Given `levels = 4`, bin width $\Delta = 256 / 4 = 64$.
Bins: `[0,63] -> 32`, `[64,127] -> 96`, `[128,191] -> 160`, `[192,255] -> 224` (using $\lfloor (q + 0.5) \cdot 64 \rfloor$).
Let input `3x3` patch be:
$$I = \begin{bmatrix} 10 & 63 & 64 \\ 127 & 128 & 191 \\ 192 & 224 & 255 \end{bmatrix}$$
Step-by-step:
- `10`: $\lfloor 10/64 \rfloor = 0 \rightarrow (0 + 0.5)\times 64 = 32$
- `63`: $\lfloor 63/64 \rfloor = 0 \rightarrow 32$
- `64`: $\lfloor 64/64 \rfloor = 1 \rightarrow (1 + 0.5)\times 64 = 96$
- `127`: $\lfloor 127/64 \rfloor = 1 \rightarrow 96$
- `128`: $\lfloor 128/64 \rfloor = 2 \rightarrow (2 + 0.5)\times 64 = 160$
- `191`: $\lfloor 191/64 \rfloor = 2 \rightarrow 160$
- `192`: $\lfloor 192/64 \rfloor = 3 \rightarrow (3 + 0.5)\times 64 = 224$
- `224`: $\lfloor 224/64 \rfloor = 3 \rightarrow 224$
- `255`: $\lfloor 255/64 \rfloor = 3 \rightarrow 224$

Quantized output $\hat{I}$ and squared errors $(I - \hat{I})^2$:
$$\hat{I} = \begin{bmatrix} 32 & 32 & 96 \\ 96 & 160 & 160 \\ 224 & 224 & 224 \end{bmatrix}, \qquad (I - \hat{I})^2 = \begin{bmatrix} 484 & 961 & 1024 \\ 961 & 1024 & 961 \\ 1024 & 0 & 961 \end{bmatrix}$$
$$\text{MSE} = \frac{484 + 961 + 1024 + 961 + 1024 + 961 + 1024 + 0 + 961}{9} = \frac{7400}{9} \approx 822.222$$
$$\text{PSNR} = 10 \log_{10}\left(\frac{65025}{822.222}\right) \approx 18.981\text{ dB}$$

### Hand Example B: `4x4` Centered 2D DFT DC Check
For a constant `4x4` patch $I(x,y) = 100$:
- $F(0, 0) = \sum_{x=0}^3 \sum_{y=0}^3 100 = 16 \times 100 = 1600$; all other $F(u,v) = 0$.
- After `fftshift`, the peak sits at `(4 // 2, 4 // 2) = (2, 2)`.
- $S_{\log}(2, 2) = \ln(1 + 1600) = \ln(1601) \approx 7.3784$, and $0.0$ everywhere else.

---

## 14. Required Experiments

### Milestone 1 (Week 9)
- Validate `notebooks/01_image_analysis.ipynb` executes cleanly top-to-bottom on a small dev sample (when data is ready) without hardcoded paths.

### Milestone 2 (Week 10 — Dev Set Only)
1. **Dev-Set Global & Defect-Separability Audit:** Compute shape, dtype, min, max, mean, std, defect area %, $\mu_{\text{healthy}}$, $\mu_{\text{defect}}$, and $\Delta \mu = \mu_{\text{healthy}} - \mu_{\text{defect}}$ across all images in `dev_manifest.csv`.
2. **Typical vs Difficult Case Analysis:** Histogram & centered log-magnitude Fourier spectrum comparison across 3 typical and 3 difficult dev images (documenting noise, uneven illumination, low contrast, and busbar periodicity).
3. **Spatial-Resolution Reduction Study:** Scales `1.0, 0.5, 0.25, 0.125` on 20 dev images -> report mean MSE, mean PSNR, and minimum scale preserving 1–2 px cracks.
4. **Gray-Level Quantization Study:** Levels `256, 128, 64, 32, 16, 8, 4` on 20 dev images -> report mean MSE, mean PSNR vs theoretical $6.02b + 10.79$ dB, and lowest usable gray-level setting.

---

## 15. Required Tables & Visualizations

1. **Table 1 (M2): Dev-Set Exploratory Image Statistics Summary** (dims, dtype, intensity range, $\mu_{\text{healthy}}$, $\mu_{\text{defect}}$, $\Delta \mu$, defect area %).
2. **Table 2 (M2): Spatial Resolution Reduction Results** (`Scale | Effective Dims | Mean MSE | Mean PSNR (dB) | Crack Integrity Observation`).
3. **Table 3 (M2): Gray-Level Quantization Study** (`Levels | Bits | Step Δ | Mean MSE | Mean PSNR (dB) | Theoretical PSNR (dB) | Lowest Usable?`).
4. **Table 4 (M2): Findings -> Design Decisions Matrix** (`Observed EL Property | Quantitative Evidence | DIP Design Decision for M3 | Target Module`).
5. **Visualizations (`experiments/figures/`):**
   - `m02_typical_vs_difficult_histograms.png` (images + GT overlays + dual histograms).
   - `m02_fourier_spectra_busbar_vs_crack.png` (spatial patch + centered log-magnitude spectrum).
   - `m02_spatial_resolution_grid.png` (`1.0x -> 0.125x` zoom on micro-crack).
   - `m02_gray_level_quantization_grid.png` (`256 -> 4` levels + PSNR curve).

---

## 16. Unit Tests & Acceptance Criteria

```bash
pytest tests/test_enhancement.py -v
```
**Mandatory M2 Test Cases in `tests/test_enhancement.py`:**
1. `test_quantize_4_levels_hand_example`: asserts exact `3x3` output matrix from Hand Example A and MSE `7400/9`.
2. `test_quantize_unique_counts_and_invalid_levels`: verifies `len(np.unique(out)) <= levels` for `{256, 128, 64, 32, 16, 8, 4}` and raises `ValueError` for invalid `levels=7`.
3. `test_downsample_and_restore_shape_and_identity`: checks output shape `(H, W)` and `scale=1.0` exact match.
4. `test_centered_log_spectrum_constant_patch`: asserts peak at `(2, 2)` equals `np.log1p(1600)` on `4x4` constant `100` patch (Hand Example B).

---

## 17. Expected GitHub Branch Names & Exact Git Commands

- **Milestone 1 Branch:** `feature/m01-image-analysis-plan`
- **Milestone 2 Branch:** `feature/m02-exploratory-image-analysis`

```bash
# Milestone 1
git checkout main && git pull origin main
git checkout -b feature/m01-image-analysis-plan
git add notebooks/01_image_analysis.ipynb experiments/enhancement/.gitkeep
git commit -m "docs(m01): add EL image analysis plan, hypothesis matrix, and notebook skeleton"
git push -u origin feature/m01-image-analysis-plan

# Milestone 2
git checkout main && git pull origin main
git checkout -b feature/m02-exploratory-image-analysis
pytest tests/test_enhancement.py -v
git add src/enhancement.py notebooks/01_image_analysis.ipynb tests/test_enhancement.py experiments/figures/
git commit -m "feat(m02): complete dev-set exploratory analysis, FFT spectra, and resolution/quantization studies"
git push -u origin feature/m02-exploratory-image-analysis
```

---

## 18. Suggested Meaningful Commit Messages

- **M1:**
  - `docs(m01): define EL defect DIP hypothesis matrix and M2 analysis notebook skeleton`
- **M2:**
  - `feat(m02): implement gray-level quantization, spatial downsampling, and centered log-FFT helpers`
  - `exp(m02): run dev-set histograms, Fourier spectra, resolution and quantization studies`
  - `docs(m02): add Findings-to-Design-Decisions table and analysis figures`
  - `test(m02): add unit tests for quantization hand example and centered FFT DC peak`

---

## 19. Pull Request Checklist

- [ ] All analysis executed strictly on `data/splits/dev_manifest.csv` (`test_manifest.csv` untouched!).
- [ ] Notebook `01_image_analysis.ipynb` executes cleanly top-to-bottom with cleared/clean outputs or saved figures.
- [ ] All `.py` files pass `<= 95` characters/line and include docstrings.
- [ ] `BGR->RGB` applied whenever plotting color overlays in Matplotlib.
- [ ] Findings -> Design Decisions table explicitly connects observations to M3 enhancement/segmentation choices.
- [ ] `pytest tests/test_enhancement.py -v` passes 100%.

---

## 20. Reviewer Assignment

- **Milestone 1 PR (`feature/m01-image-analysis-plan`):** Reviewed by **Member 1** (Tech Lead).
- **Milestone 2 PR (`feature/m02-exploratory-image-analysis`):** Reviewed by **Member 2** (verifies `src.data` usage and Fourier spectrum correctness) and **Member 1** (checks Findings -> Design Decisions traceability).

---

## 21. Report-Section Responsibilities

- **Section III (Exploratory Image Analysis & Findings):** Dataset intensity/contrast characterization, typical vs difficult EL histograms, Fourier spectrum interpretation (busbars vs cracks), spatial resolution & gray-level quantization tables, and the Findings -> Design Decisions table.
- *(In M3/M4 you will write the Spatial Enhancement methodology and ablation sections.)*

---

## 22. Common Implementation Mistakes

1. **Running Image Analysis on the Held-Out Test Set:** Inspecting `test_manifest.csv` histograms or contrast ranges during M2 causes data leakage! Always filter strictly to `dev_manifest.csv`.
2. **Plotting Unshifted or Non-Log FFT Magnitude:** Raw `np.abs(np.fft.fft2(img))` appears completely black except for 4 tiny corner pixels. Always apply `np.fft.fftshift` and `np.log1p`.
3. **Quantizing with `int` Division in `uint8` Without Re-scaling:** Dividing `uint8` by `64` gives `{0, 1, 2, 3}`—appearing pure black when plotted or compared in PSNR against `[0, 255]`. Always rescale quantized bins back to `[0, 255]`.
4. **Confusing `cv2.resize` `(width, height)` vs NumPy `(height, width)`:** Passing `(H, W)` directly to `cv2.resize` silently transposes rectangular `640x590` images! Always pass `(W, H)` to `cv2.resize`.
5. **Prematurely Implementing M3 Filters in M2:** Keep M2 focused on analysis, sampling, and quantization; leave M3 spatial enhancers as clean stubs until M3.

---

## 23. Likely Individual Defense Questions (Own Work + Full Pipeline)

1. **Own Work:** *"Why do we apply $\log(1 + |F|)$ and `fftshift` before visualizing the 2D Fourier magnitude spectrum of an EL solar cell?"*
   - *Key points:* `fftshift` centers low frequencies `(0,0)` at `(H/2, W/2)` for human interpretability; `log(1 + |F|)` compresses the huge dynamic range between DC energy and high-frequency crack/grid components without `log(0)` undefinedness.
2. **Own Work:** *"In your gray-level quantization study (`256 -> 4`), what was the lowest usable setting and what visual artifact appeared below it?"*
   - *Key points:* Below `16`–`32` levels, false contouring (banding) merges subtle dark micro-cracks with uneven EL background shading, causing sharp drops in PSNR and defect separability.
3. **Own Work:** *"What periodic structures appear as bright axes or peaks in the EL Fourier spectrum, and how does that inform later pipeline stages?"*
   - *Key points:* Periodic vertical/horizontal solar cell fingers and busbars produce concentrated harmonics along the axes, whereas irregular cracks spread energy across non-axial high frequencies.
4. **Full Pipeline:** *"How did your M2 Findings -> Design Decisions table influence Baseline 1 vs Pipeline A/B/C?"*
   - *Key points:* Uneven illumination and low defect contrast explain why fixed global thresholding (`Baseline 0`) and even global Otsu (`Baseline 1`) fail on dim corners, motivating contrast enhancement + local/adaptive thresholding + morphology in M3.
5. **Full Pipeline:** *"Why does `downsample_and_restore` upsample back to `(H, W)` before computing PSNR against the original image?"*
   - *Key points:* Pixel-wise MSE/PSNR requires identical spatial dimensions `(H, W)` and aligned coordinates to quantify high-frequency crack detail loss from downsampling.

---

## 24. Definition of Done

### Milestone 1 (Topic Settled — Week 9) DoD
- [ ] `notebooks/01_image_analysis.ipynb` skeleton with Image Analysis Plan & Hypothesis Matrix merged to `main` after Member 1 review.

### Milestone 2 (Baselines Ready — Week 10) DoD
- [ ] `src/enhancement.py` M2 analysis utilities, `tests/test_enhancement.py`, completed `notebooks/01_image_analysis.ipynb`, and `experiments/figures/m02_*.png` merged to `main`.
- [ ] All 4 required studies (dev stats, typical vs difficult histograms + FFT, spatial resolution reduction, gray-level quantization `256->4`) completed strictly on `dev_manifest.csv`.
- [ ] Findings -> Design Decisions table documented and reviewed by Member 1 & Member 2; `pytest tests/test_enhancement.py -v` passes 100%.
