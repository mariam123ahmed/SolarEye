"""Unit and regression tests for `src/data.py` (Owner: Member 2, M2)."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
from PIL import Image

from src.data import (
    add_gaussian_noise,
    add_poisson_noise,
    add_salt_pepper_noise,
    add_speckle_noise,
    bgr_to_rgb,
    create_dev_test_split,
    load_image,
    load_image_mask_pair,
    load_mask,
)


class TestDataModule(unittest.TestCase):
    """Contract and regression tests for data I/O, splits, and noise."""

    def test_bgr_to_rgb_swaps_outer_channels(self) -> None:
        """Channel 0 and channel 2 must swap without mutating input."""
        bgr = np.zeros((4, 4, 3), dtype=np.uint8)
        bgr[..., 0] = 10
        bgr[..., 1] = 20
        bgr[..., 2] = 30
        rgb = bgr_to_rgb(bgr)
        self.assertTrue(np.array_equal(rgb[..., 0], bgr[..., 2]))
        self.assertTrue(np.array_equal(rgb[..., 2], bgr[..., 0]))

    def test_load_mask_decodes_gray_rgb_palette_and_nearest(self) -> None:
        """Decode {0,255}, color-coded RGB, palette PNG, and resize safely."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            # 1) Grayscale {0, 255} resized with INTER_NEAREST
            p_gray = tmp / "mask_gray.png"
            raw = np.zeros((16, 16), dtype=np.uint8)
            raw[4:12, 4:12] = 255
            Image.fromarray(raw).save(p_gray)
            loaded = load_mask(p_gray, target_size=(8, 8))
            self.assertEqual(loaded.dtype, np.uint8)
            self.assertEqual(loaded.shape, (8, 8))
            self.assertEqual(set(np.unique(loaded).tolist()), {0, 1})

            # 2) Color-coded RGB mask with pure green (0, 255, 0) defect
            p_rgb = tmp / "mask_rgb.png"
            rgb = np.zeros((16, 16, 3), dtype=np.uint8)
            rgb[2:6, 2:6, 1] = 255
            Image.fromarray(rgb).save(p_rgb)
            dec_rgb = load_mask(p_rgb)
            self.assertEqual(int(dec_rgb[3, 3]), 1)
            self.assertEqual(int(dec_rgb[0, 0]), 0)

            # 3) Palette mode ('P') PNG mask
            p_pal = tmp / "mask_pal.png"
            pal_img = Image.fromarray(rgb).convert("P")
            pal_img.save(p_pal)
            dec_pal = load_mask(p_pal)
            self.assertEqual(int(dec_pal[3, 3]), 1)
            self.assertEqual(int(dec_pal[0, 0]), 0)

    def test_invalid_corrupt_and_mismatched_dimensions_raise(self) -> None:
        """Corrupt, missing, or shape-mismatched files must raise errors."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            with self.assertRaises(FileNotFoundError):
                load_image(tmp / "missing.png")

            corrupt_path = tmp / "corrupt.png"
            corrupt_path.write_bytes(b"not_a_valid_image")
            with self.assertRaises(ValueError):
                load_image(corrupt_path)
            with self.assertRaises(ValueError):
                load_mask(corrupt_path)

            img_p = tmp / "img.png"
            msk_p = tmp / "msk.png"
            Image.fromarray(np.zeros((16, 16), dtype=np.uint8)).save(img_p)
            Image.fromarray(np.zeros((12, 16), dtype=np.uint8)).save(msk_p)
            with self.assertRaises(ValueError):
                load_image_mask_pair(img_p, msk_p)

    def test_load_image_grayscale_returns_2d_uint8(self) -> None:
        """Grayscale loader must return shape (H, W), never (H, W, 1)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "img.png"
            Image.fromarray(np.full((12, 16), 180, dtype=np.uint8)).save(path)
            arr = load_image(path, grayscale=True)
            self.assertEqual(arr.shape, (12, 16))
            self.assertEqual(arr.dtype, np.uint8)

    def test_split_preserves_official_and_blocks_sha_leakage(self) -> None:
        """Official split is preserved; duplicate hashes never leak across."""
        df_off = pd.DataFrame(
            {
                "image_id": [f"tr_{i}" for i in range(6)]
                + [f"te_{i}" for i in range(4)],
                "official_split": ["train"] * 6 + ["test"] * 4,
                "image_sha256": [f"h_{i}" for i in range(9)] + ["h_0"],
            }
        )
        dev_o, test_o = create_dev_test_split(df_off, preserve_official_split=True)
        self.assertEqual(len(dev_o), 6)
        self.assertEqual(len(test_o), 3)
        self.assertTrue(
            set(dev_o["image_sha256"]).isdisjoint(set(test_o["image_sha256"]))
        )

        df_rand = pd.DataFrame({"image_id": [f"id_{i}" for i in range(100)]})
        dev_a, test_a = create_dev_test_split(df_rand, test_ratio=0.3, seed=42)
        dev_b, test_b = create_dev_test_split(df_rand, test_ratio=0.3, seed=42)
        self.assertEqual(len(dev_a), 70)
        self.assertEqual(len(test_a), 30)
        self.assertTrue(dev_a["image_id"].equals(dev_b["image_id"]))
        self.assertTrue(
            set(dev_a["image_id"]).isdisjoint(set(test_a["image_id"]))
        )

    def test_noise_generators_are_deterministic_and_bounded(self) -> None:
        """All noise generators must honor seed=42 and uint8 bounds."""
        base = np.full((64, 64), 128, dtype=np.uint8)
        g1 = add_gaussian_noise(base, sigma=15.0, seed=42)
        g2 = add_gaussian_noise(base, sigma=15.0, seed=42)
        self.assertTrue(np.array_equal(g1, g2))
        self.assertEqual(g1.dtype, np.uint8)

        sp = add_salt_pepper_noise(base, density=0.1, salt_ratio=0.5, seed=42)
        self.assertEqual(sp.dtype, np.uint8)
        self.assertGreater(int((sp == 255).sum()), 0)
        self.assertGreater(int((sp == 0).sum()), 0)

        spk = add_speckle_noise(base, variance=0.04, seed=42)
        poi = add_poisson_noise(base, peak=30.0, seed=42)
        self.assertEqual(spk.dtype, np.uint8)
        self.assertEqual(poi.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
