"""Command-line entry point for SolarEye single-image and split runs.

Owner: Member 1 (Tech Lead, Integration & Metrics).
Supports `--config`, `--input` (unseen-image inference without ground truth),
`--manifest` + `--evaluate` (batch evaluation), and `--output_dir`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from src.config import load_config
from src.data import load_image
from src.evaluate import evaluate_manifest
from src.pipeline import run_single_image


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for SolarEye pipeline runs."""
    parser = argparse.ArgumentParser(
        description="Run SolarEye classical DIP defect inspection pipeline."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to YAML/JSON configuration file (e.g., configs/baseline_0.yaml).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to a single unseen EL image for inference (no GT needed).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to split manifest CSV (e.g., data/splits/dev_manifest.csv).",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run batch evaluation against ground-truth masks in --manifest.",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="Optional cap on number of manifest samples during quick checks.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("experiments/results/demo"),
        help="Directory for output masks, metrics CSVs, and overlays.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, load config, and execute requested pipeline mode."""
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config(args.config)

    if args.input is not None:
        img = load_image(args.input, grayscale=True)
        res = run_single_image(img, cfg)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stem = args.input.stem
        mask_out = args.output_dir / f"{stem}_{cfg['pipeline']}_mask.png"
        Image.fromarray((res["mask"] * 255).astype("uint8")).save(mask_out)
        report = {
            "input": str(args.input),
            "pipeline": cfg["pipeline"],
            "runtime_s": res["runtime_s"],
            "stats": res["stats"],
            "metadata": res["metadata"],
            "mask_path": str(mask_out),
        }
        report_out = args.output_dir / f"{stem}_{cfg['pipeline']}_summary.json"
        report_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    if args.evaluate:
        manifest_path = args.manifest or Path(
            cfg.get("dataset", {}).get(
                "manifest", "data/splits/dev_manifest.csv"
            )
        )
        summary = evaluate_manifest(
            manifest_csv=manifest_path,
            cfg=cfg,
            out_dir=args.output_dir,
            config_file=args.config.as_posix(),
            max_samples=args.max_samples,
        )
        print(json.dumps(summary, indent=2))
        return 0

    parser.error("Provide either --input <image_path> or --evaluate.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
