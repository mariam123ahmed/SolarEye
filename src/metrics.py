"""Quantitative image restoration and segmentation metrics (Milestone 2).

Owner: Member 1 (Tech Lead, Integration & Metrics).
Enforces SolarEye's binary `{0, 1}` mask contract, `float64` subtraction
(preventing `uint8` wraparound), and explicit edge-case guards for empty
masks, mismatched shapes, and zero MSE.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage


def _validate_binary_pair(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate two 2D masks have equal non-empty shape and values in {0,1}."""
    pred = np.asarray(pred_mask)
    gt = np.asarray(gt_mask)
    if pred.ndim != 2 or gt.ndim != 2:
        raise ValueError(
            f"Binary masks must be 2D, got shapes {pred.shape} and {gt.shape}."
        )
    if pred.shape != gt.shape:
        raise ValueError(
            f"Mask shape mismatch: pred={pred.shape} vs gt={gt.shape}."
        )
    if pred.size == 0:
        raise ValueError("Masks must not be empty.")
    pred_vals = set(np.unique(pred).tolist())
    gt_vals = set(np.unique(gt).tolist())
    if not pred_vals.issubset({0, 1}) or not gt_vals.issubset({0, 1}):
        raise ValueError(
            f"Masks must strictly contain {{0, 1}}, got pred={pred_vals}, "
            f"gt={gt_vals}."
        )
    return pred.astype(bool), gt.astype(bool)


def compute_mse(ref: np.ndarray, target: np.ndarray) -> float:
    """Compute Mean Squared Error between `ref` and `target` in `float64`."""
    arr_ref = np.asarray(ref)
    arr_tgt = np.asarray(target)
    if arr_ref.shape != arr_tgt.shape:
        raise ValueError(
            f"Shape mismatch: ref={arr_ref.shape} vs target={arr_tgt.shape}."
        )
    if arr_ref.size == 0:
        raise ValueError("Input arrays must not be empty.")
    diff = arr_ref.astype(np.float64) - arr_tgt.astype(np.float64)
    return float(np.mean(diff * diff))


def compute_psnr(
    ref: np.ndarray,
    target: np.ndarray,
    max_val: float = 255.0,
) -> float:
    """Compute Peak Signal-to-Noise Ratio (dB); `MSE == 0` -> `inf`."""
    if max_val <= 0.0:
        raise ValueError(f"max_val must be > 0, got {max_val}.")
    mse = compute_mse(ref, target)
    if mse == 0.0:
        return float("inf")
    return float(10.0 * math.log10((max_val ** 2) / mse))


def compute_iou(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Compute Intersection-over-Union on `{0, 1}` masks.

    Returns `1.0` if both masks are empty, and `0.0` if intersection is zero.
    """
    pred_b, gt_b = _validate_binary_pair(pred_mask, gt_mask)
    inter = int(np.logical_and(pred_b, gt_b).sum())
    union = int(np.logical_or(pred_b, gt_b).sum())
    if union == 0:
        return 1.0
    return float(inter / union)


def compute_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Compute Dice Similarity Coefficient on `{0, 1}` masks.

    Returns `1.0` if both masks are empty.
    """
    pred_b, gt_b = _validate_binary_pair(pred_mask, gt_mask)
    inter = int(np.logical_and(pred_b, gt_b).sum())
    denom = int(pred_b.sum()) + int(gt_b.sum())
    if denom == 0:
        return 1.0
    return float((2.0 * inter) / denom)


def compute_precision_recall(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
) -> tuple[float, float]:
    """Compute `(precision, recall)` on binary `{0, 1}` defect masks."""
    pred_b, gt_b = _validate_binary_pair(pred_mask, gt_mask)
    tp = int(np.logical_and(pred_b, gt_b).sum())
    fp = int(np.logical_and(pred_b, ~gt_b).sum())
    fn = int(np.logical_and(~pred_b, gt_b).sum())

    if tp + fp == 0 and tp + fn == 0:
        return 1.0, 1.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    return precision, recall


def compute_area_error(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Compute absolute defective area percentage-point error `|pct_p - pct_g|`."""
    pred_b, gt_b = _validate_binary_pair(pred_mask, gt_mask)
    total_px = float(pred_b.size)
    pred_pct = 100.0 * float(pred_b.sum()) / total_px
    gt_pct = 100.0 * float(gt_b.sum()) / total_px
    return float(abs(pred_pct - gt_pct))


def compute_count_error(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    connectivity: int = 8,
) -> int:
    """Compute absolute connected-component defect count error `|N_p - N_g|`."""
    if connectivity not in (4, 8):
        raise ValueError(
            f"connectivity must be 4 or 8, got {connectivity}."
        )
    pred_b, gt_b = _validate_binary_pair(pred_mask, gt_mask)
    if connectivity == 4:
        struct = np.array(
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8
        )
    else:
        struct = np.ones((3, 3), dtype=np.uint8)
    _, n_pred = ndimage.label(pred_b, structure=struct)
    _, n_gt = ndimage.label(gt_b, structure=struct)
    return int(abs(int(n_pred) - int(n_gt)))
