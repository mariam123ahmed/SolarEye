"""Runnable Milestone 1/2 contract, validation, and regression tests."""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

from app.streamlit_app import (
    apply_controlled_degradation,
    build_inspection_report_md,
    compute_centered_log_fft,
    render_overlay_with_boxes,
    run_ui_pipeline_hook,
)
from data.validate_dataset import validate_dataset
from src import EXPERIMENT_LOG_COLUMNS
from src.config import (
    build_pipeline_config,
    get_project_root,
    load_config,
    validate_config,
)
from src.enhancement import convolve2d_numpy
from src.frequency import compute_fft_spectrum
from src.pipeline import run_pipeline_a, run_pipeline_c


class TestRepositoryContracts(unittest.TestCase):
    """Verify M1/M2 configuration, schema, dataset validator, and M3 stubs."""

    def setUp(self) -> None:
        """Locate repository root."""
        self.root = get_project_root()

    def test_all_yaml_configs_load_and_honor_contracts(self) -> None:
        """All YAML configs must satisfy seed=42 and dark-defect invariants."""
        config_names = [
            "dataset.yaml",
            "baseline_0.yaml",
            "baseline_1.yaml",
            "pipeline_a.yaml",
            "pipeline_b.yaml",
            "pipeline_c.yaml",
        ]
        for name in config_names:
            cfg = load_config(self.root / "configs" / name)
            self.assertEqual(cfg["random_seed"], 42, msg=name)
            self.assertTrue(cfg["dark_defects"], msg=name)
            self.assertEqual(cfg["mask_values"], [0, 1], msg=name)
            self.assertEqual(cfg["border_mode"], "reflect", msg=name)
            if "pipeline" in cfg:
                typed = build_pipeline_config(cfg)
                self.assertEqual(typed.random_seed, 42)

    def test_invalid_config_values_raise_value_error(self) -> None:
        """Invalid seed, polarity, mask_values, border, or pipeline fail."""
        base = {
            "run_id": "X",
            "pipeline": "baseline_0",
            "random_seed": 42,
            "dark_defects": True,
            "mask_values": [0, 1],
            "border_mode": "reflect",
        }
        for key, bad_val in (
            ("random_seed", 7),
            ("dark_defects", False),
            ("mask_values", [0, 255]),
            ("border_mode", "constant"),
            ("pipeline", "unknown_pipe"),
        ):
            mutated = {**base, key: bad_val}
            with self.assertRaises(ValueError):
                validate_config(mutated)

    def test_experiment_log_header_schema(self) -> None:
        """Experiment log CSV must match the canonical 16-column header."""
        log_path = self.root / "experiments" / "experiment_log.csv"
        self.assertTrue(log_path.exists())
        with open(log_path, "r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
        self.assertEqual(header, EXPERIMENT_LOG_COLUMNS)
        self.assertEqual(len(header), 16)

    def test_validate_dataset_on_synthetic_el_samples(self) -> None:
        """Dataset validator must pass paired synthetic EL images and masks."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            img_dir = root / "images"
            msk_dir = root / "masks"
            img_dir.mkdir(parents=True)
            msk_dir.mkdir(parents=True)

            for idx in range(2):
                img = np.full((32, 32), 200, dtype=np.uint8)
                img[10:14, 8:24] = 40
                msk = np.zeros((32, 32), dtype=np.uint8)
                msk[10:14, 8:24] = 255
                Image.fromarray(img).save(img_dir / f"cell_{idx}.png")
                Image.fromarray(msk).save(msk_dir / f"cell_{idx}.png")

            report = validate_dataset(root)
            self.assertEqual(report["status"], "PASSED")
            self.assertEqual(report["counts"]["matched_pairs"], 2)
            self.assertEqual(report["counts"]["dimension_mismatches"], 0)
            self.assertEqual(report["mask_unique_values"], [0, 255])
            self.assertEqual(report["dark_defect_polarity_fraction"], 1.0)

    def test_validate_dataset_catches_mismatch_missing_and_rgb_masks(self) -> None:
        """Validator must catch missing masks, shape mismatches, and RGB."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "images").mkdir()
            (root / "masks").mkdir()

            img = np.full((32, 32), 200, dtype=np.uint8)
            img[8:16, 8:16] = 30
            Image.fromarray(img).save(root / "images" / "a.png")
            # Green-channel color-coded RGB mask with matching shape
            rgb_msk = np.zeros((32, 32, 3), dtype=np.uint8)
            rgb_msk[8:16, 8:16, 1] = 255
            Image.fromarray(rgb_msk).save(root / "masks" / "a.png")

            rep_rgb = validate_dataset(root)
            self.assertEqual(rep_rgb["status"], "PASSED")
            self.assertEqual(rep_rgb["dark_defect_polarity_fraction"], 1.0)
            self.assertIn([0, 255, 0], rep_rgb["mask_unique_rgb_colors"])

            # Add mismatched mask dimension and orphan image
            Image.fromarray(img).save(root / "images" / "b.png")
            Image.fromarray(np.zeros((16, 16), dtype=np.uint8)).save(
                root / "masks" / "b.png"
            )
            Image.fromarray(img).save(root / "images" / "orphan.png")
            rep_bad = validate_dataset(root)
            self.assertEqual(rep_bad["status"], "FAILED")
            self.assertEqual(rep_bad["counts"]["dimension_mismatches"], 1)
            self.assertEqual(rep_bad["counts"]["unmatched_images"], 1)

    def test_future_m3_stubs_remain_unimplemented(self) -> None:
        """Future Milestone 3 functions must still raise NotImplementedError."""
        dummy = np.zeros((8, 8), dtype=np.uint8)
        with self.assertRaises(NotImplementedError):
            convolve2d_numpy(dummy, np.ones((3, 3)))
        with self.assertRaises(NotImplementedError):
            compute_fft_spectrum(dummy)
        with self.assertRaises(NotImplementedError):
            run_pipeline_a(dummy, {})
        with self.assertRaises(NotImplementedError):
            run_pipeline_c(dummy, {})

    def test_streamlit_app_helpers_smoke(self) -> None:
        """App helpers must run cleanly on verified Baselines 0 and 1."""
        img = np.full((32, 32), 200, dtype=np.uint8)
        img[10:18, 10:18] = 35
        deg = apply_controlled_degradation(
            img,
            gauss_sigma=5.0,
            sp_density=0.02,
            contrast_alpha=1.1,
            illum_strength=0.2,
            blur_ksize=3,
            seed=42,
        )
        self.assertEqual(deg.shape, img.shape)
        self.assertEqual(deg.dtype, np.uint8)
        res = run_ui_pipeline_hook(deg, "baseline_1")
        fft_disp = compute_centered_log_fft(deg)
        self.assertEqual(fft_disp.shape, img.shape)
        overlay = render_overlay_with_boxes(
            deg, res["mask"], res["stats"]["components"]
        )
        self.assertEqual(overlay.shape, (32, 32, 3))
        md = build_inspection_report_md("test.png", "baseline_1", res, None)
        self.assertIn("baseline_1", md)
        with self.assertRaises(ValueError):
            run_ui_pipeline_hook(img, "pipeline_c")


if __name__ == "__main__":
    unittest.main()
