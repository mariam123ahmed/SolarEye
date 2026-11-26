"""AI-assisted reference scaffold for inspecting the MSPS dataset locally.

Scans image and mask files, reports pairing/dimension issues, raw mask encoding,
dark-defect polarity, and exact duplicate image files. Does not download data.
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
MASK_DIR_NAMES = {"mask", "masks", "label", "labels", "labels01", "gt", "annotation"}
MASK_SUFFIXES = ("_mask", "-mask", "_gt", "-gt", "_label", "-label")
IGNORED_PAIR_DIRS = {
    "image", "images", "img", "imgs", "mask", "masks",
    "label", "labels", "labels01", "gt", "annotation", "annotations",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse dataset directory and report output options."""
    parser = argparse.ArgumentParser(
        description="Validate image/mask pairing and metadata for SolarEye."
    )
    parser.add_argument("--data_dir", type=Path, default=Path("data/raw/msps"))
    parser.add_argument("--images_subdir", default="")
    parser.add_argument("--masks_subdir", default="")
    parser.add_argument(
        "--out_report", type=Path, default=Path("data/validation_report.json")
    )
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str:
    """Calculate SHA-256 over a file in bounded-size chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pair_key(path: Path, root: Path, is_mask: bool) -> str:
    """Normalize relative paths so image and annotation stems can be paired."""
    relative = path.relative_to(root)
    parents = [
        part for part in relative.parts[:-1]
        if part.lower() not in IGNORED_PAIR_DIRS
    ]
    stem = path.stem
    if is_mask:
        for suffix in MASK_SUFFIXES:
            if stem.lower().endswith(suffix):
                stem = stem[:-len(suffix)]
                break
    return "/".join([*parents, stem]) if parents else stem


def discover_pairs(
    root: Path, images_subdir: str = "", masks_subdir: str = ""
) -> tuple[dict[str, Path], dict[str, Path], list[str]]:
    """Discover image and mask paths, returning maps and duplicate-key warnings."""
    if bool(images_subdir) != bool(masks_subdir):
        raise ValueError("Provide both --images_subdir and --masks_subdir, or neither.")

    if images_subdir:
        image_root = root / images_subdir
        mask_root = root / masks_subdir
        if not image_root.is_dir():
            raise FileNotFoundError(f"Images directory not found: {image_root}")
        if not mask_root.is_dir():
            raise FileNotFoundError(f"Masks directory not found: {mask_root}")
        image_paths = sorted(
            p for p in image_root.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        mask_paths = sorted(
            p for p in mask_root.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        images = {
            p.relative_to(image_root).with_suffix("").as_posix(): p
            for p in image_paths
        }
        masks = {
            p.relative_to(mask_root).with_suffix("").as_posix(): p
            for p in mask_paths
        }
        collisions = []
        if len(images) != len(image_paths):
            collisions.append("duplicate image relative path")
        if len(masks) != len(mask_paths):
            collisions.append("duplicate mask relative path")
        return images, masks, collisions

    images: dict[str, Path] = {}
    masks: dict[str, Path] = {}
    collisions: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        relative = path.relative_to(root)
        parent_names = {part.lower() for part in relative.parts[:-1]}
        is_mask = bool(parent_names & MASK_DIR_NAMES) or any(
            path.stem.lower().endswith(suffix) for suffix in MASK_SUFFIXES
        )
        mapping = masks if is_mask else images
        key = pair_key(path, root, is_mask)
        if key in mapping:
            collisions.append(f"duplicate {'mask' if is_mask else 'image'} key: {key}")
        mapping[key] = path
    return images, masks, collisions


def read_mask(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    """Read a mask, converting palette/RGBA formats to RGB for color inspection."""
    with Image.open(path) as image:
        mode = image.mode
        raw = np.asarray(image)
        decoded = np.asarray(image.convert("RGB")) if mode in {"P", "RGBA", "LA"} else raw
    if decoded.size == 0:
        raise ValueError("empty mask")
    return decoded, raw, mode


def validate_dataset(
    data_dir: Path, images_subdir: str = "", masks_subdir: str = ""
) -> dict[str, Any]:
    """Return a structured report about the dataset files and their consistency."""
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory does not exist: {data_dir}")

    image_map, mask_map, collisions = discover_pairs(
        data_dir, images_subdir, masks_subdir
    )
    image_keys, mask_keys = set(image_map), set(mask_map)
    matched = sorted(image_keys & mask_keys)
    unmatched_images = sorted(image_keys - mask_keys)
    unmatched_masks = sorted(mask_keys - image_keys)

    image_shapes: Counter[str] = Counter()
    mask_shapes: Counter[str] = Counter()
    image_dtypes: Counter[str] = Counter()
    mask_modes: Counter[str] = Counter()
    mask_values: set[int] = set()
    mask_colors: set[tuple[int, int, int]] = set()
    corrupt: list[str] = []
    dimension_mismatches: list[str] = []
    polarity_differences: list[float] = []
    image_hashes: dict[str, list[str]] = {}
    empty_masks = 0
    rgb_identical: list[bool] = []

    for key in matched:
        image_path, mask_path = image_map[key], mask_map[key]
        try:
            with Image.open(image_path) as source:
                image = np.asarray(source)
            decoded_mask, raw_mask, mask_mode = read_mask(mask_path)
        except Exception as exc:
            corrupt.append(f"{key}: {exc}")
            continue

        if image.size == 0:
            corrupt.append(f"{key}: empty image")
            continue
        image_shapes[str(image.shape)] += 1
        mask_shapes[str(raw_mask.shape)] += 1
        image_dtypes[str(image.dtype)] += 1
        mask_modes[mask_mode] += 1

        if image.shape[:2] != decoded_mask.shape[:2]:
            dimension_mismatches.append(
                f"{key}: image={image.shape[:2]}, mask={decoded_mask.shape[:2]}"
            )
            continue

        gray = image[..., :3].mean(axis=2) if image.ndim == 3 else image.astype(float)
        if image.ndim == 3 and image.shape[2] >= 3:
            rgb_identical.append(bool(
                np.array_equal(image[..., 0], image[..., 1])
                and np.array_equal(image[..., 1], image[..., 2])
            ))

        if decoded_mask.ndim == 3 and decoded_mask.shape[2] >= 3:
            rgb = decoded_mask[..., :3]
            foreground = np.any(rgb > 0, axis=2)
            colors = np.unique(rgb.reshape(-1, 3), axis=0)
            mask_colors.update(tuple(map(int, row)) for row in colors)
            mask_values.update(map(int, np.unique(raw_mask)))
        else:
            foreground = decoded_mask > 0
            mask_values.update(map(int, np.unique(decoded_mask)))

        if not np.any(foreground):
            empty_masks += 1
        elif np.any(~foreground):
            fg_mean = float(gray[foreground].mean())
            bg_mean = float(gray[~foreground].mean())
            polarity_differences.append(bg_mean - fg_mean)

        digest = sha256_file(image_path)
        image_hashes.setdefault(digest, []).append(key)

    duplicate_groups = [group for group in image_hashes.values() if len(group) > 1]
    polarity_fraction = (
        float(np.mean([diff > 0 for diff in polarity_differences]))
        if polarity_differences else None
    )
    passed = bool(matched) and not any((
        unmatched_images, unmatched_masks, collisions,
        dimension_mismatches, corrupt
    ))

    return {
        "data_dir": data_dir.as_posix(),
        "status": "PASSED" if passed else "FAILED",
        "counts": {
            "images_found": len(image_map),
            "masks_found": len(mask_map),
            "matched_pairs": len(matched),
            "unmatched_images": len(unmatched_images),
            "unmatched_masks": len(unmatched_masks),
            "pairing_collisions": len(collisions),
            "dimension_mismatches": len(dimension_mismatches),
            "empty_masks": empty_masks,
            "corrupt_files": len(corrupt),
            "duplicate_sha256_groups": len(duplicate_groups),
        },
        "image_shapes": dict(image_shapes),
        "mask_shapes": dict(mask_shapes),
        "image_dtypes": dict(image_dtypes),
        "mask_pil_modes": dict(mask_modes),
        "rgb_channels_identical_all": all(rgb_identical) if rgb_identical else None,
        "mask_unique_values": sorted(mask_values),
        "mask_unique_rgb_colors": [list(color) for color in sorted(mask_colors)],
        "dark_defect_polarity_fraction": polarity_fraction,
        "unmatched_image_samples": unmatched_images[:10],
        "unmatched_mask_samples": unmatched_masks[:10],
        "pairing_collision_samples": collisions[:10],
        "dimension_mismatch_samples": dimension_mismatches[:10],
        "corrupt_samples": corrupt[:10],
        "duplicate_samples": duplicate_groups[:10],
    }


def main(argv: list[str] | None = None) -> int:
    """Run validation and write the JSON report."""
    args = parse_args(argv)
    report = validate_dataset(args.data_dir, args.images_subdir, args.masks_subdir)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    counts = report["counts"]
    print(f"Validation status   : {report['status']}")
    print(f"Matched pairs       : {counts['matched_pairs']}")
    print(f"Unmatched images    : {counts['unmatched_images']}")
    print(f"Unmatched masks     : {counts['unmatched_masks']}")
    print(f"Dimension mismatches: {counts['dimension_mismatches']}")
    print(f"Mask unique values  : {report['mask_unique_values']}")
    print(f"Mask RGB colors     : {report['mask_unique_rgb_colors']}")
    print(f"Image shapes        : {report['image_shapes']}")
    print(f"Report written      : {args.out_report}")
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
