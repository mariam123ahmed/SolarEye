"""Milestone 2 orchestration of the two required classical baselines."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from src.morphology import connected_component_stats
from src.segmentation import (
    baseline0_fixed_threshold,
    baseline1_otsu_opening,
)


def run_baseline_0(
    image: np.ndarray,
    threshold: int = 127,
    dark_defects: bool = True,
) -> dict[str, Any]:
    """Execute strictly pure Baseline 0 (`raw < 127`, no pre/post-processing).

    Returns standardized dict:
    `{"mask": uint8 {0,1}, "stages": {...}, "runtime_s": float,
    "metadata": {...}}`.
    """
    t0 = time.perf_counter()
    mask = baseline0_fixed_threshold(
        image, thresh=threshold, dark_defects=dark_defects
    )
    stats = connected_component_stats(mask, connectivity=8)
    elapsed = float(time.perf_counter() - t0)
    return {
        "mask": mask,
        "stages": {
            "01_raw_gray": image,
            "02_fixed_threshold_127": (mask * 255).astype(np.uint8),
        },
        "stage_timings_s": {"threshold": elapsed},
        "runtime_s": elapsed,
        "stats": stats,
        "metadata": {
            "pipeline": "baseline_0",
            "threshold": int(threshold),
            "dark_defects": bool(dark_defects),
        },
    }


def run_baseline_1(
    image: np.ndarray,
    opening_size: int = 3,
    opening_shape: str = "rect",
    dark_defects: bool = True,
) -> dict[str, Any]:
    """Execute Baseline 1 (Otsu polarity inversion + single `3x3` opening)."""
    t0 = time.perf_counter()
    otsu_thresh, opened = baseline1_otsu_opening(
        image,
        opening_size=opening_size,
        opening_shape=opening_shape,
        dark_defects=dark_defects,
    )
    stats = connected_component_stats(opened, connectivity=8)
    elapsed = float(time.perf_counter() - t0)
    return {
        "mask": opened,
        "stages": {
            "01_raw_gray": image,
            "02_otsu_plus_opening": (opened * 255).astype(np.uint8),
        },
        "stage_timings_s": {"otsu_and_opening": elapsed},
        "runtime_s": elapsed,
        "stats": stats,
        "metadata": {
            "pipeline": "baseline_1",
            "otsu_threshold": int(otsu_thresh),
            "opening_size": int(opening_size),
            "opening_shape": opening_shape,
            "dark_defects": bool(dark_defects),
        },
    }


def run_single_image(
    image: np.ndarray,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Dispatch `image` to the pipeline named in `cfg['pipeline']`."""
    name = str(cfg.get("pipeline", "")).strip()
    dark = bool(cfg.get("dark_defects", True))
    if name == "baseline_0":
        thresh = int(cfg.get("segmentation", {}).get("threshold", 127))
        return run_baseline_0(image, threshold=thresh, dark_defects=dark)
    if name == "baseline_1":
        morph = cfg.get("morphology", {})
        ksize = int(morph.get("opening_ksize", 3))
        shape = str(morph.get("opening_shape", "rect"))
        return run_baseline_1(
            image, opening_size=ksize, opening_shape=shape, dark_defects=dark
        )
    raise ValueError(f"Unsupported pipeline name in config: '{name}'.")
