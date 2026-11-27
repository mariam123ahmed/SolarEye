"""2D Fourier Transform, spectrum visualization, and filtering (Milestone 3).

Owner: Member 2 (Data, Restoration & Frequency).
Integrates Member 1's transfer-function masks from `src.frequency_masks`.
"""

from __future__ import annotations

import numpy as np


def compute_fft_spectrum(
    image: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute centered 2D DFT and `uint8` log-magnitude display spectrum.

    Returns:
    - `centered_fft`: `np.complex128` array from `fftshift(fft2(image))`.
    - `log_mag_uint8`: `np.uint8` normalized `log(1 + |F(u, v)|)` in
      `[0, 255]` for clear visualization.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Compute np.fft.fftshift(np.fft.fft2(image.astype("
        "np.float64))) and normalize np.log1p(np.abs(fshift)) to uint8."
    )


def apply_frequency_mask(
    image: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    """Filter `image` in the frequency domain using centered `mask` `[0, 1]`.

    Steps: `fft2 -> fftshift -> multiply by mask -> ifftshift -> ifft2 ->
    real -> clip [0, 255] -> uint8`.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Verify image.shape == mask.shape, apply centered FFT "
        "multiplication, invert via real(ifft2(ifftshift(...))), clip."
    )


def homomorphic_filter(
    image: np.ndarray,
    gamma_low: float = 0.5,
    gamma_high: float = 1.5,
    cutoff: float = 30.0,
    c: float = 1.0,
) -> np.ndarray:
    """Log-domain frequency illumination normalization & reflectance boost.

    Model: `ln(I(x, y) + 1) = ln(L(x, y)) + ln(R(x, y))`. Attenuates
    low-frequency illumination (`gamma_low < 1`) while boosting high-frequency
    crack reflectance (`gamma_high > 1`).
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Take np.log1p(image), apply high-emphasis Gaussian "
        "filter in centered FFT domain, invert via np.expm1, rescale uint8."
    )
