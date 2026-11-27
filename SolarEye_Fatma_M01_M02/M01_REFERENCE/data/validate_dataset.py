"""Reproducible dataset validation script for SolarEye (Milestone 1/2).

Audits downloaded EL images and pixel masks for directory layout, unambiguous
1-to-1 stem pairing, spatial dimension alignment, channel layout, dtypes,
color-coded/palette/binary mask decoding, dark-defect polarity, empty masks,
and SHA-256 duplicates, writing a JSON summary report.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
IGNORED_DIR_TOKENS = {
    "image",
    "images",
    "img",
    "imgs",
    "mask",
    "masks",
    "label",
    "labels",
    "labels01",
    "gt",
    "annotation",
    "annotations",
}
MASK_DIR_TOKENS = ("mask", "label", "gt", "ann")
MASK_SUFFIXES = ("_mask", "-mask", "_gt", "-gt", "_label", "-label")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for dataset validation."""
    parser = argparse.ArgumentParser(
        description="Validate PV EL images and pixel masks for SolarEye."
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("data/raw/msps"),
        help="Root directory of extracted dataset.",
    )
    parser.add_argument(
        "--images_subdir",
        type=str,
        default="",
        help="Optional explicit relative subpath to image files.",
    )
    parser.add_argument(
        "--masks_subdir",
        type=str,
        default="",
        help="Optional explicit relative subpath to mask files.",
    )
    parser.add_argument(
        "--out_report",
        type=Path,
        default=Path("data/validation_report.json"),
        help="Output JSON report path.",
    )
    return parser.parse_args(argv)


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest for exact duplicate detection."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_image_raw(path: Path) -> tuple[np.ndarray, str]:
    """Load an image file via PIL returning `(array, pil_mode)`."""
    with Image.open(path) as img:
        return np.asarray(img), img.mode


def _read_mask_raw(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    """Load a mask file via PIL, decoding palette (`P`) and RGB masks.

    Returns `(decoded_rgb_or_gray_array, raw_array, pil_mode)`.
    """
    with Image.open(path) as img:
        mode = img.mode
        raw = np.asarray(img)
        if mode == "P":
            decoded = np.asarray(img.convert("RGB"))
            return decoded, raw, mode
        if mode in ("RGBA", "LA"):
            decoded = np.asarray(img.convert("RGB"))
            return decoded, raw, mode
        return raw, raw, mode


def _normalized_pair_key(path: Path, root: Path) -> str:
    """Build an unambiguous split-preserving stem key for pairing."""
    rel = path.relative_to(root)
    kept_parts = [
        part for part in rel.parts[:-1] if part.lower() not in IGNORED_DIR_TOKENS
    ]
    stem = path.stem
    for suffix in MASK_SUFFIXES:
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return "/".join([*kept_parts, stem]) if kept_parts else stem


def _is_mask_path(path: Path, root: Path) -> bool:
    """Determine if `path` belongs to mask annotations by folder or stem."""
    rel = path.relative_to(root)
    parent_parts = [part.lower() for part in rel.parts[:-1]]
    if any(tok in part for part in parent_parts for tok in MASK_DIR_TOKENS):
        return True
    stem_low = path.stem.lower()
    return any(stem_low.endswith(sfx) for sfx in MASK_SUFFIXES)


def _discover_pairs(
    data_dir: Path,
    images_subdir: str = "",
    masks_subdir: str = "",
) -> tuple[dict[str, Path], dict[str, Path], list[str]]:
    """Discover image and mask files and detect pairing key collisions."""
    collisions: list[str] = []
    img_map: dict[str, Path] = {}
    msk_map: dict[str, Path] = {}

    if images_subdir and masks_subdir:
        img_root = data_dir / images_subdir
        msk_root = data_dir / masks_subdir
        img_files = sorted(
            p for p in img_root.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        msk_files = sorted(
            p for p in msk_root.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        for path in img_files:
            key = path.relative_to(img_root).with_suffix("").as_posix()
            if key in img_map:
                collisions.append(f"image:{key}")
            img_map[key] = path
        for path in msk_files:
            key = _normalized_pair_key(path, msk_root)
            if key in msk_map:
                collisions.append(f"mask:{key}")
            msk_map[key] = path
        return img_map, msk_map, collisions

    all_files = sorted(
        p for p in data_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    for path in all_files:
        # When both labels/ and labels01/ exist side-by-side (as in MSPS),
        # prefer labels01/ and skip the redundant labels/ mirror folder.
        if (
            "labels" in [pt.lower() for pt in path.parts]
            and (path.parent.parent / "labels01").is_dir()
        ):
            continue
        key = _normalized_pair_key(path, data_dir)
        if _is_mask_path(path, data_dir):
            if key in msk_map:
                collisions.append(f"mask:{key}")
            msk_map[key] = path
        else:
            if key in img_map:
                collisions.append(f"image:{key}")
            img_map[key] = path
    return img_map, msk_map, collisions


def _decode_foreground_and_colors(
    decoded: np.ndarray,
    raw: np.ndarray,
) -> tuple[np.ndarray, set[int], set[tuple[int, int, int]]]:
    """Extract binary foreground mask, scalar values, and RGB color tuples."""
    if decoded.ndim == 3 and decoded.shape[2] >= 3:
        rgb = decoded[..., :3]
        fg = np.any(rgb > 0, axis=2)
        flat = rgb.reshape(-1, 3)
        uniq_rows = np.unique(flat, axis=0)
        colors = {(int(r), int(g), int(b)) for r, g, b in uniq_rows}
        vals = {int(v) for v in np.unique(raw)}
        return fg, vals, colors
    fg = decoded > 0
    vals = {int(v) for v in np.unique(decoded)}
    return fg, vals, set()


def validate_dataset(
    data_dir: Path,
    images_subdir: str = "",
    masks_subdir: str = "",
) -> dict[str, Any]:
    """Validate dataset files and return a structured audit dictionary."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {data_dir}")

    img_map, msk_map, collisions = _discover_pairs(
        data_dir, images_subdir, masks_subdir
    )
    img_keys = set(img_map.keys())
    msk_keys = set(msk_map.keys())
    matched_keys = sorted(img_keys & msk_keys)
    unmatched_images = sorted(img_keys - msk_keys)
    unmatched_masks = sorted(msk_keys - img_keys)

    shape_counts: Counter[str] = Counter()
    mask_shape_counts: Counter[str] = Counter()
    dtype_counts: Counter[str] = Counter()
    mask_modes: Counter[str] = Counter()
    mask_values: set[int] = set()
    mask_colors: set[tuple[int, int, int]] = set()
    corrupt_files: list[str] = []
    dim_mismatches: list[str] = []
    rgb_identical_flags: list[bool] = []
    polarity_diffs: list[float] = []
    empty_mask_count = 0
    hash_map: dict[str, list[str]] = {}

    for key in matched_keys:
        img_path = img_map[key]
        msk_path = msk_map[key]
        try:
            img_arr, _ = _read_image_raw(img_path)
            msk_dec, msk_raw, msk_mode = _read_mask_raw(msk_path)
        except Exception as exc:  # pragma: no cover - corrupt file guard
            corrupt_files.append(f"{key}: {exc}")
            continue

        if img_arr.size == 0 or msk_dec.size == 0:
            corrupt_files.append(f"{key}: zero-sized array")
            continue

        shape_counts[str(img_arr.shape)] += 1
        mask_shape_counts[str(msk_raw.shape)] += 1
        dtype_counts[str(img_arr.dtype)] += 1
        mask_modes[msk_mode] += 1

        if img_arr.shape[:2] != msk_dec.shape[:2]:
            dim_mismatches.append(
                f"{key}: img={img_arr.shape[:2]} vs mask={msk_dec.shape[:2]}"
            )
            continue

        if img_arr.ndim == 3 and img_arr.shape[2] >= 3:
            c0, c1, c2 = img_arr[..., 0], img_arr[..., 1], img_arr[..., 2]
            identical = bool(
                np.array_equal(c0, c1) and np.array_equal(c1, c2)
            )
            rgb_identical_flags.append(identical)
            gray = img_arr[..., :3].mean(axis=2)
        else:
            gray = img_arr.astype(np.float64)

        fg, vals, colors = _decode_foreground_and_colors(msk_dec, msk_raw)
        mask_values.update(vals)
        mask_colors.update(colors)

        if not np.any(fg):
            empty_mask_count += 1
        elif np.any(~fg):
            fg_mean = float(gray[fg].mean())
            bg_mean = float(gray[~fg].mean())
            polarity_diffs.append(bg_mean - fg_mean)

        digest = _sha256_file(img_path)
        hash_map.setdefault(digest, []).append(key)

    duplicate_groups = [keys for keys in hash_map.values() if len(keys) > 1]
    dark_defect_ratio = (
        float(np.mean([diff > 0 for diff in polarity_diffs]))
        if polarity_diffs
        else None
    )
    passed = (
        len(matched_keys) > 0
        and len(unmatched_images) == 0
        and len(unmatched_masks) == 0
        and len(collisions) == 0
        and len(dim_mismatches) == 0
        and len(corrupt_files) == 0
    )

    return {
        "data_dir": data_dir.as_posix(),
        "status": "PASSED" if passed else "FAILED",
        "counts": {
            "images_found": len(img_map),
            "masks_found": len(msk_map),
            "matched_pairs": len(matched_keys),
            "unmatched_images": len(unmatched_images),
            "unmatched_masks": len(unmatched_masks),
            "pairing_collisions": len(collisions),
            "dimension_mismatches": len(dim_mismatches),
            "empty_masks": empty_mask_count,
            "corrupt_files": len(corrupt_files),
            "duplicate_sha256_groups": len(duplicate_groups),
        },
        "image_shapes": dict(shape_counts),
        "mask_shapes": dict(mask_shape_counts),
        "image_dtypes": dict(dtype_counts),
        "mask_pil_modes": dict(mask_modes),
        "rgb_channels_identical_all": (
            all(rgb_identical_flags) if rgb_identical_flags else None
        ),
        "mask_unique_values": sorted(mask_values),
        "mask_unique_rgb_colors": [list(c) for c in sorted(mask_colors)],
        "dark_defect_polarity_fraction": dark_defect_ratio,
        "unmatched_image_samples": unmatched_images[:10],
        "unmatched_mask_samples": unmatched_masks[:10],
        "pairing_collision_samples": collisions[:10],
        "dimension_mismatch_samples": dim_mismatches[:10],
        "corrupt_samples": corrupt_files[:10],
        "duplicate_samples": duplicate_groups[:10],
    }


def main(argv: list[str] | None = None) -> int:
    """Run dataset validation and write the JSON audit report."""
    args = parse_args(argv)
    report = validate_dataset(
        data_dir=args.data_dir,
        images_subdir=args.images_subdir,
        masks_subdir=args.masks_subdir,
    )
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_report, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    counts = report["counts"]
    print(f"Validation status   : {report['status']}")
    print(f"Matched pairs       : {counts['matched_pairs']}")
    print(f"Unmatched images    : {counts['unmatched_images']}")
    print(f"Unmatched masks     : {counts['unmatched_masks']}")
    print(f"Dimension mismatches: {counts['dimension_mismatches']}")
    print(f"Mask unique vals    : {report['mask_unique_values']}")
    print(f"Mask unique colors  : {report['mask_unique_rgb_colors']}")
    print(f"Image shapes        : {report['image_shapes']}")
    print(f"Report written      : {args.out_report}")
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
