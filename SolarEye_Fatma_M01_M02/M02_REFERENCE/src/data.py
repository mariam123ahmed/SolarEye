"""Dataset loading, BGR->RGB conversion, splitting, and noise synthesis.

Owner: Member 2 (Data, Restoration & Frequency) — Milestone 2 deliverable.
Implements canonical image/mask I/O, color-coded/palette mask decoding,
nearest-neighbor mask resizing, official/deterministic manifest splitting,
and reproducible classical noise synthesis (`seed=42`).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from data.validate_dataset import _discover_pairs


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert a 3-channel `(H, W, 3)` BGR image to RGB channel order."""
    arr = np.asarray(image)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(
            f"bgr_to_rgb expects (H, W, 3) array, got shape {arr.shape}."
        )
    if arr.dtype != np.uint8:
        raise ValueError(
            f"bgr_to_rgb expects np.uint8 dtype, got {arr.dtype}."
        )
    return np.ascontiguousarray(arr[..., ::-1].copy())


def load_image(
    path: str | Path,
    grayscale: bool = True,
    target_size: tuple[int, int] | None = None,
) -> np.ndarray:
    """Load an EL image as `np.uint8` in `[0, 255]`.

    Returns 2D `(H, W)` when `grayscale=True`, or 3D `(H, W, 3)` RGB when
    `grayscale=False`. Uses `cv2.INTER_AREA` / `cv2.INTER_LINEAR` if
    `target_size=(H, W)` is provided.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    raw = cv2.imread(str(file_path), flag)
    if raw is None or raw.size == 0:
        raise ValueError(f"Failed to decode image file: {file_path}")

    if not grayscale:
        if raw.ndim == 2:
            raw = cv2.cvtColor(raw, cv2.COLOR_GRAY2RGB)
        elif raw.ndim == 3 and raw.shape[2] == 3:
            raw = bgr_to_rgb(raw)
        else:
            raise ValueError(f"Unsupported channel shape: {raw.shape}")
    elif raw.ndim == 3:
        raw = raw[..., 0]

    if target_size is not None:
        h_tgt, w_tgt = int(target_size[0]), int(target_size[1])
        if h_tgt <= 0 or w_tgt <= 0:
            raise ValueError(f"target_size must be positive, got {target_size}")
        interp = (
            cv2.INTER_AREA
            if (h_tgt < raw.shape[0] or w_tgt < raw.shape[1])
            else cv2.INTER_LINEAR
        )
        raw = cv2.resize(raw, (w_tgt, h_tgt), interpolation=interp)

    return np.ascontiguousarray(raw.astype(np.uint8))


def load_mask(
    path: str | Path,
    target_size: tuple[int, int] | None = None,
) -> np.ndarray:
    """Load a pixel-level ground-truth defect mask as `np.uint8` in `{0, 1}`.

    Supports grayscale `{0, 1}`, `{0, 255}`, multi-class integer masks,
    palette (`P`) PNGs, and RGB color-coded masks (`any(rgb > 0) -> 1`).
    Resizes strictly with nearest-neighbor interpolation (`INTER_NEAREST`).
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Mask file not found: {file_path}")

    try:
        with Image.open(file_path) as img:
            if img.mode in ("P", "RGBA", "LA"):
                arr = np.asarray(img.convert("RGB"))
            else:
                arr = np.asarray(img)
    except Exception as exc:
        raise ValueError(f"Failed to decode mask file: {file_path}") from exc

    if arr.size == 0:
        raise ValueError(f"Empty mask array: {file_path}")

    if arr.ndim == 3:
        if arr.shape[2] >= 3:
            binary = np.any(arr[..., :3] > 0, axis=2).astype(np.uint8)
        else:
            binary = (arr[..., 0] > 0).astype(np.uint8)
    elif arr.ndim == 2:
        binary = (arr > 0).astype(np.uint8)
    else:
        raise ValueError(f"Unsupported mask ndim={arr.ndim} in {file_path}")

    if target_size is not None:
        h_tgt, w_tgt = int(target_size[0]), int(target_size[1])
        if h_tgt <= 0 or w_tgt <= 0:
            raise ValueError(f"target_size must be positive, got {target_size}")
        binary = cv2.resize(
            binary, (w_tgt, h_tgt), interpolation=cv2.INTER_NEAREST
        )
        binary = (binary > 0).astype(np.uint8)

    return np.ascontiguousarray(binary)


def load_image_mask_pair(
    image_path: str | Path,
    mask_path: str | Path,
    grayscale: bool = True,
    target_size: tuple[int, int] | None = None,
    resize_mask_to_image: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Load an aligned `(image, mask)` pair with strict dimension validation."""
    image = load_image(image_path, grayscale=grayscale, target_size=target_size)
    mask_target = target_size
    mask = load_mask(mask_path, target_size=mask_target)
    if image.shape[:2] != mask.shape[:2]:
        if resize_mask_to_image:
            mask = load_mask(mask_path, target_size=image.shape[:2])
        else:
            raise ValueError(
                f"Image-mask dimension mismatch: image={image.shape[:2]} "
                f"vs mask={mask.shape[:2]} for {image_path} / {mask_path}."
            )
    return image, mask


def _file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest for leakage detection across splits."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_dataset_manifest(
    data_dir: str | Path,
    project_root: str | Path | None = None,
) -> pd.DataFrame:
    """Scan `data_dir` and build a paired manifest DataFrame with SHA-256."""
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory not found: {root}")
    base = Path(project_root).resolve() if project_root else Path.cwd().resolve()
    img_map, msk_map, collisions = _discover_pairs(root)
    if collisions:
        raise ValueError(f"Pairing key collisions detected: {collisions[:5]}")
    keys = sorted(set(img_map.keys()) & set(msk_map.keys()))
    if not keys:
        raise ValueError(f"No matched image-mask pairs found under {root}")

    rows: list[dict[str, Any]] = []
    for key in keys:
        img_p = img_map[key].resolve()
        msk_p = msk_map[key].resolve()
        parts_low = [p.lower() for p in img_p.parts]
        if "train" in parts_low or "training" in parts_low or "dev" in parts_low:
            official_split = "train"
        elif "test" in parts_low or "testing" in parts_low or "val" in parts_low:
            official_split = "test"
        else:
            official_split = "unspecified"
        try:
            rel_img = img_p.relative_to(base).as_posix()
        except ValueError:
            rel_img = img_p.as_posix()
        try:
            rel_msk = msk_p.relative_to(base).as_posix()
        except ValueError:
            rel_msk = msk_p.as_posix()
        rows.append(
            {
                "image_id": key,
                "image_path": rel_img,
                "mask_path": rel_msk,
                "official_split": official_split,
                "image_sha256": _file_sha256(img_p),
            }
        )
    return pd.DataFrame(rows)


def create_dev_test_split(
    manifest_df: pd.DataFrame,
    test_ratio: float = 0.3,
    seed: int = 42,
    group_col: str | None = None,
    preserve_official_split: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create deterministic, leakage-free `dev` and `test` DataFrames.

    Preserves official `"train"` / `"test"` splits when present and
    `preserve_official_split=True`. Otherwise performs deterministic
    `seed=42` group-aware splitting by `test_ratio` and removes/rejects
    cross-split duplicate SHA-256 hashes if present.
    """
    if manifest_df.empty:
        raise ValueError("manifest_df must not be empty.")
    if not (0.0 < test_ratio < 1.0):
        raise ValueError(f"test_ratio must be in (0, 1), got {test_ratio}.")

    df = manifest_df.copy().reset_index(drop=True)

    if (
        preserve_official_split
        and "official_split" in df.columns
        and set(df["official_split"]).issuperset({"train", "test"})
    ):
        dev_df = df[df["official_split"] == "train"].reset_index(drop=True)
        test_df = df[df["official_split"] == "test"].reset_index(drop=True)
    else:
        rng = np.random.default_rng(seed)
        if group_col and group_col in df.columns:
            groups = np.array(sorted(df[group_col].astype(str).unique()))
            perm = rng.permutation(len(groups))
            n_test_grp = max(1, int(round(len(groups) * test_ratio)))
            test_groups = set(groups[perm[:n_test_grp]])
            is_test = df[group_col].astype(str).isin(test_groups)
            test_df = df[is_test].reset_index(drop=True)
            dev_df = df[~is_test].reset_index(drop=True)
        else:
            perm = rng.permutation(len(df))
            n_test = max(1, int(round(len(df) * test_ratio)))
            test_idx = perm[:n_test]
            dev_idx = perm[n_test:]
            dev_df = df.iloc[dev_idx].reset_index(drop=True)
            test_df = df.iloc[test_idx].reset_index(drop=True)

    if "image_id" in df.columns:
        overlap = set(dev_df["image_id"]) & set(test_df["image_id"])
        if overlap:
            raise ValueError(f"Data leakage on image_id: {sorted(overlap)[:5]}")
    if "image_sha256" in df.columns:
        dev_hashes = set(dev_df["image_sha256"])
        test_hashes = set(test_df["image_sha256"])
        dup_cross = dev_hashes & test_hashes
        if dup_cross:
            test_df = test_df[
                ~test_df["image_sha256"].isin(dup_cross)
            ].reset_index(drop=True)

    return dev_df, test_df


def add_gaussian_noise(
    image: np.ndarray,
    mean: float = 0.0,
    sigma: float = 15.0,
    seed: int = 42,
) -> np.ndarray:
    """Add deterministic additive Gaussian noise (`uint8` -> `uint8`)."""
    if sigma < 0.0:
        raise ValueError(f"sigma must be >= 0, got {sigma}.")
    arr = np.asarray(image, dtype=np.float64)
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=mean, scale=sigma, size=arr.shape)
    noisy = np.clip(np.rint(arr + noise), 0.0, 255.0)
    return noisy.astype(np.uint8)


def add_salt_pepper_noise(
    image: np.ndarray,
    density: float = 0.05,
    salt_ratio: float = 0.5,
    seed: int = 42,
) -> np.ndarray:
    """Add deterministic Salt (`255`) and Pepper (`0`) impulse noise."""
    if not (0.0 <= density <= 1.0):
        raise ValueError(f"density must be in [0, 1], got {density}.")
    if not (0.0 <= salt_ratio <= 1.0):
        raise ValueError(f"salt_ratio must be in [0, 1], got {salt_ratio}.")
    out = np.asarray(image, dtype=np.uint8).copy()
    rng = np.random.default_rng(seed)
    probs = rng.random(out.shape[:2])
    salt_thresh = density * salt_ratio
    pepper_thresh = density
    out[probs < salt_thresh] = 255
    out[(probs >= salt_thresh) & (probs < pepper_thresh)] = 0
    return out


def add_speckle_noise(
    image: np.ndarray,
    variance: float = 0.04,
    seed: int = 42,
) -> np.ndarray:
    """Add deterministic multiplicative speckle noise: `I + I * N(0, var)`."""
    if variance < 0.0:
        raise ValueError(f"variance must be >= 0, got {variance}.")
    arr = np.asarray(image, dtype=np.float64)
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=np.sqrt(variance), size=arr.shape)
    noisy = np.clip(np.rint(arr + arr * noise), 0.0, 255.0)
    return noisy.astype(np.uint8)


def add_poisson_noise(
    image: np.ndarray,
    peak: float = 30.0,
    seed: int = 42,
) -> np.ndarray:
    """Add deterministic signal-dependent Poisson shot noise."""
    if peak <= 0.0:
        raise ValueError(f"peak must be > 0, got {peak}.")
    arr = np.asarray(image, dtype=np.float64)
    rng = np.random.default_rng(seed)
    lam = np.clip(arr / 255.0, 0.0, 1.0) * peak
    sampled = rng.poisson(lam=lam).astype(np.float64) / peak
    noisy = np.clip(np.rint(sampled * 255.0), 0.0, 255.0)
    return noisy.astype(np.uint8)
