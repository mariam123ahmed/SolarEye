"""Binary morphological refinement & defect quantification (M2/M3).

Owner: Member 4 (Segmentation, Morphology & Measurement).
All mask inputs and outputs are strictly 2D `np.uint8` in `{0, 1}`.
Milestone 2 implements pure NumPy erosion, dilation, opening, and
connected-component statistics needed by Baseline 1 and evaluation.
Milestone 3 operations remain clearly marked future stubs.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy import ndimage


def _validate_binary_mask(mask: np.ndarray) -> np.ndarray:
    """Validate 2D binary mask with values strictly in `{0, 1}`."""
    arr = np.asarray(mask)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError(f"Expected non-empty 2D mask, got {arr.shape}.")
    vals = set(np.unique(arr).tolist())
    if not vals.issubset({0, 1}):
        raise ValueError(f"Mask values must be in {{0, 1}}, got {vals}.")
    return arr.astype(np.uint8)


def build_structuring_element(
    ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Construct a binary `{0, 1}` structuring element (`rect`/`cross`/`ellipse`)."""
    if ksize < 3 or ksize % 2 == 0:
        raise ValueError(f"ksize must be an odd integer >= 3, got {ksize}.")
    if shape == "rect":
        return np.ones((ksize, ksize), dtype=bool)
    r = ksize // 2
    yy, xx = np.ogrid[-r : r + 1, -r : r + 1]
    if shape == "cross":
        return (yy == 0) | (xx == 0)
    if shape == "ellipse":
        return ((xx / float(r)) ** 2 + (yy / float(r)) ** 2) <= 1.0
    raise ValueError(
        f"Unsupported structuring element shape '{shape}'. "
        "Choose from 'rect', 'cross', or 'ellipse'."
    )


def binary_erosion_numpy(
    mask: np.ndarray,
    ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Pure NumPy binary erosion on `uint8` `{0, 1}` mask.

    Pads borders with constant `1` (matching OpenCV `cv2.erode` default
    `BORDER_CONSTANT` max-value semantics so foreground touching image
    edges is not artificially eroded).
    """
    arr = _validate_binary_mask(mask)
    se = build_structuring_element(ksize=ksize, shape=shape)
    pad = ksize // 2
    padded = np.pad(arr, pad_width=pad, mode="constant", constant_values=1)
    windows = sliding_window_view(padded, (ksize, ksize))
    eroded = np.all(windows[:, :, se] == 1, axis=2)
    return eroded.astype(np.uint8)


def binary_dilation_numpy(
    mask: np.ndarray,
    ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Pure NumPy binary dilation on `uint8` `{0, 1}` mask.

    Pads borders with constant `0` (matching OpenCV `cv2.dilate` default
    `BORDER_CONSTANT` zero-padding semantics).
    """
    arr = _validate_binary_mask(mask)
    se = build_structuring_element(ksize=ksize, shape=shape)
    pad = ksize // 2
    padded = np.pad(arr, pad_width=pad, mode="constant", constant_values=0)
    windows = sliding_window_view(padded, (ksize, ksize))
    dilated = np.any(windows[:, :, se] == 1, axis=2)
    return dilated.astype(np.uint8)


def erode_binary_numpy(mask: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Contract alias for `binary_erosion_numpy(mask, ksize=ksize)`."""
    return binary_erosion_numpy(mask, ksize=ksize, shape="rect")


def dilate_binary_numpy(mask: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Contract alias for `binary_dilation_numpy(mask, ksize=ksize)`."""
    return binary_dilation_numpy(mask, ksize=ksize, shape="rect")


def morph_opening(
    mask: np.ndarray,
    ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Morphological opening (erosion followed by dilation) -> `uint8 {0, 1}`."""
    eroded = binary_erosion_numpy(mask, ksize=ksize, shape=shape)
    return binary_dilation_numpy(eroded, ksize=ksize, shape=shape)


def connected_component_stats(
    mask: np.ndarray,
    connectivity: int = 8,
) -> dict[str, Any]:
    """Compute connected-component defect count, areas, and bounding boxes."""
    if connectivity not in (4, 8):
        raise ValueError(f"connectivity must be 4 or 8, got {connectivity}.")
    arr = _validate_binary_mask(mask)
    struct = (
        np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        if connectivity == 4
        else np.ones((3, 3), dtype=np.uint8)
    )
    labeled, n_comp = ndimage.label(arr > 0, structure=struct)
    total_area_px = int(arr.sum())
    area_pct = 100.0 * float(total_area_px) / float(arr.size)

    components: list[dict[str, Any]] = []
    slices = ndimage.find_objects(labeled)
    for comp_id, slc in enumerate(slices, start=1):
        if slc is None:
            continue
        r_slc, c_slc = slc
        sub = labeled[slc] == comp_id
        area_px = int(sub.sum())
        h_box = int(r_slc.stop - r_slc.start)
        w_box = int(c_slc.stop - c_slc.start)
        aspect = float(max(h_box, w_box) / max(1, min(h_box, w_box)))
        components.append(
            {
                "id": comp_id,
                "area_px": area_px,
                "bbox_xywh": [
                    int(c_slc.start),
                    int(r_slc.start),
                    w_box,
                    h_box,
                ],
                "aspect_ratio": round(aspect, 3),
            }
        )

    return {
        "defect_count": int(n_comp),
        "total_area_px": total_area_px,
        "area_pct": float(area_pct),
        "components": components,
    }


def morph_closing(
    mask: np.ndarray,
    ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Morphological closing (dilation followed by erosion) -> `uint8 {0, 1}`."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Apply binary_dilation_numpy then binary_erosion_numpy."
    )


def morphological_open_close(
    mask: np.ndarray,
    open_ksize: int = 3,
    close_ksize: int = 3,
    shape: str = "rect",
) -> np.ndarray:
    """Sequential opening (noise removal) + closing (crack bridging)."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Apply morph_opening followed by morph_closing."
    )


def fill_holes(mask: np.ndarray) -> np.ndarray:
    """Fill interior background holes enclosed inside defect regions."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Flood-fill background from border or scipy binary_fill_holes."
    )


def remove_small_components(
    mask: np.ndarray,
    min_area_px: int = 15,
    connectivity: int = 8,
) -> np.ndarray:
    """Remove connected defect components smaller than `min_area_px`."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Label connected components and zero out small regions."
    )


def connect_broken_cracks(
    mask: np.ndarray,
    ksize: int = 5,
    shape: str = "ellipse",
) -> np.ndarray:
    """Bridge fragmented micro-crack segments via directional/disk closing."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Apply morph_closing tuned for crack continuity."
    )


def quantify_defects(
    mask: np.ndarray,
    cell_area_px: int | None = None,
    connectivity: int = 8,
) -> dict[str, Any]:
    """Return `defect_count`, `total_area_px`, `area_ratio`, and boxes."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Aggregate connected_component_stats using cell_area_px."
    )


def classify_cell_status(
    quantification: dict[str, Any],
    area_warning_pct: float = 2.0,
    count_warning: int = 3,
) -> str:
    """Experimental image-based defect severity triage label."""
    raise NotImplementedError(
        "Planned for Milestone 3 — assigned to Member 4. "
        "TODO(M3): Return experimental morphological triage label."
    )
