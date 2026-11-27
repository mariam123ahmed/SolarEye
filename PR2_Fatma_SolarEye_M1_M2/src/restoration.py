"""Spatial-domain noise restoration filters for PV EL images (Milestone 3).

Owner: Member 2 (Data, Restoration & Frequency).
Milestone 3 deliverable — all functions raise `NotImplementedError` until
Phase 2. Required NumPy ops: `median_filter_numpy` and
`alpha_trimmed_mean_filter_numpy`.
"""

from __future__ import annotations

import numpy as np


def median_filter_numpy(
    image: np.ndarray,
    ksize: int = 3,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Pure NumPy 2D median filter with `reflect` border parity.

    Contract:
    - `ksize` must be an odd integer >= 3.
    - Uses `np.pad(image, ksize // 2, mode=border_mode)` and sliding
      window views (`np.lib.stride_tricks.sliding_window_view`).
    - Returns `np.uint8` matching `scipy.ndimage.median_filter` /
      `cv2.medianBlur` border semantics.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Pad with mode=border_mode, extract ksize x ksize "
        "windows, take np.median, and return uint8."
    )


def alpha_trimmed_mean_filter_numpy(
    image: np.ndarray,
    ksize: int = 3,
    d: int = 2,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Pure NumPy alpha-trimmed mean filter for hybrid Gaussian+impulse noise.

    Formula: Sort the `m * n` neighborhood values, discard the `d // 2`
    lowest and `d // 2` highest values (`0 <= d < ksize * ksize`), and
    average the remaining `ksize * ksize - d` pixels.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Sort sliding windows along neighborhood axis, slice "
        "[d//2 : -d//2] (guarding d==0), average, and return uint8."
    )


def mean_filter_spatial(
    image: np.ndarray,
    ksize: int = 3,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Arithmetic mean restoration filter (`uint8` -> `uint8`)."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Compute arithmetic mean over ksize x ksize neighborhood."
    )


def max_filter_spatial(
    image: np.ndarray,
    ksize: int = 3,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Order-statistic maximum filter (removes pepper noise)."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Take neighborhood maximum over reflect-padded windows."
    )


def min_filter_spatial(
    image: np.ndarray,
    ksize: int = 3,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Order-statistic minimum filter (removes salt noise)."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Take neighborhood minimum over reflect-padded windows."
    )


def midpoint_filter_spatial(
    image: np.ndarray,
    ksize: int = 3,
    border_mode: str = "reflect",
) -> np.ndarray:
    """Midpoint filter: `0.5 * (max(window) + min(window))`."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Average neighborhood min and max in float64, cast uint8."
    )


def gaussian_filter_spatial(
    image: np.ndarray,
    ksize: int = 5,
    sigma: float = 1.0,
) -> np.ndarray:
    """Gaussian spatial smoothing filter (`uint8` -> `uint8`)."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Smooth with Gaussian kernel of size ksize and std sigma."
    )


def bilateral_denoise(
    image: np.ndarray,
    d: int = 5,
    sigma_color: float = 25.0,
    sigma_space: float = 5.0,
) -> np.ndarray:
    """Edge-preserving bilateral restoration preserving thin EL cracks."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Apply cv2.bilateralFilter or separable approximation."
    )


def wiener_filter_numpy(
    image: np.ndarray,
    psf: np.ndarray,
    k_reg: float = 0.01,
) -> np.ndarray:
    """Pure NumPy frequency-domain Wiener restoration filter.

    Formula: `H_W(u, v) = conj(H) / (|H|^2 + k_reg)`.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 2. "
        "TODO(M3): Pad PSF to image shape, compute FFT, apply Wiener "
        "transfer function, invert via ifft2, clip [0, 255] uint8."
    )
