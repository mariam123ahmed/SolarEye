"""2D Frequency-domain transfer-function masks (Milestone 3).

Owner: Member 1 (Tech Lead, Integration & Metrics).
Milestone 3 deliverable — all functions raise `NotImplementedError` until
Phase 2. Required NumPy ops: `ideal_frequency_mask` and
`butterworth_frequency_mask` (plus Gaussian/notch helpers).
"""

from __future__ import annotations

import numpy as np


def ideal_frequency_mask(
    shape: tuple[int, int],
    cutoff: float,
    highpass: bool = False,
) -> np.ndarray:
    """Generate a centered 2D Ideal LP or HP frequency mask in `[0.0, 1.0]`.

    Formula: `D(u, v) = sqrt((u - M/2)^2 + (v - N/2)^2)`.
    LPF: `1.0` if `D <= cutoff` else `0.0`; HPF: `1.0 - LPF`.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Build radial distance grid via np.ogrid/meshgrid, "
        "threshold D <= cutoff, invert if highpass=True, return float64."
    )


def butterworth_frequency_mask(
    shape: tuple[int, int],
    cutoff: float,
    order: int = 2,
    highpass: bool = False,
) -> np.ndarray:
    """Generate a centered 2D Butterworth LP or HP mask in `[0.0, 1.0]`.

    LPF Formula: `H(u, v) = 1 / (1 + (D(u, v) / D0) ** (2 * n))`.
    HPF Formula: `H(u, v) = 1 / (1 + (D0 / max(D, eps)) ** (2 * n))`.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Compute radial distance D(u,v) in float64, apply "
        "Butterworth formula with zero-distance guard, return float64."
    )


def gaussian_frequency_mask(
    shape: tuple[int, int],
    cutoff: float,
    highpass: bool = False,
) -> np.ndarray:
    """Generate a centered 2D Gaussian LP or HP mask in `[0.0, 1.0]`.

    LPF Formula: `H(u, v) = exp(-(D(u, v)^2) / (2 * D0^2))`.
    """
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Compute exp(-D^2 / (2 * cutoff^2)) and invert if HP."
    )


def ideal_lowpass_mask(
    shape: tuple[int, int],
    cutoff: float,
) -> np.ndarray:
    """Convenience wrapper returning centered 2D Ideal Low-Pass mask."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Delegate to ideal_frequency_mask(shape, cutoff, False)."
    )


def ideal_highpass_mask(
    shape: tuple[int, int],
    cutoff: float,
) -> np.ndarray:
    """Convenience wrapper returning centered 2D Ideal High-Pass mask."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Delegate to ideal_frequency_mask(shape, cutoff, True)."
    )


def butterworth_lowpass_mask(
    shape: tuple[int, int],
    cutoff: float,
    order: int = 2,
) -> np.ndarray:
    """Convenience wrapper returning centered 2D Butterworth LP mask."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Delegate to butterworth_frequency_mask(..., False)."
    )


def butterworth_highpass_mask(
    shape: tuple[int, int],
    cutoff: float,
    order: int = 2,
) -> np.ndarray:
    """Convenience wrapper returning centered 2D Butterworth HP mask."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Delegate to butterworth_frequency_mask(..., True)."
    )


def gaussian_bandreject_mask(
    shape: tuple[int, int],
    centers: list[tuple[int, int]],
    bandwidth: float = 5.0,
) -> np.ndarray:
    """Symmetric notch/band-reject mask for periodic EL busbar suppression."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 1. "
        "TODO(M3): Multiply symmetric Gaussian notch rejectors at each "
        "(u_k, v_k) and conjugate mirror (-u_k, -v_k)."
    )
