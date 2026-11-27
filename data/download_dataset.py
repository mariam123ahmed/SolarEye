"""Download and MD5-verify the SolarEye primary MSPS EL dataset.

Supports live download from Zenodo record 21549573 (CC BY 4.0), MD5 checksum
verification (`25d8fdaa8c9f2f7cf114d9c1f44c0bce`), safe ZIP extraction with
path-traversal protection, and `--dry_run` inspection.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import urllib.request
import zipfile

MSPS_ZENODO_URL = (
    "https://zenodo.org/records/21549573/files/MSPS.zip?download=1"
)
MSPS_EXPECTED_BYTES = 360_415_905
MSPS_EXPECTED_MD5 = "25d8fdaa8c9f2f7cf114d9c1f44c0bce"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for dataset acquisition."""
    parser = argparse.ArgumentParser(
        description="Download and extract SolarEye benchmark datasets."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="msps",
        choices=["msps"],
        help="Dataset identifier (default: msps).",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("data/raw/msps"),
        help="Destination directory for extracted dataset files.",
    )
    parser.add_argument(
        "--zip_path",
        type=Path,
        default=Path("data/raw/MSPS.zip"),
        help="Local path to save or read the MSPS.zip archive.",
    )
    parser.add_argument(
        "--skip_extract",
        action="store_true",
        help="Download archive only without extracting.",
    )
    parser.add_argument(
        "--skip_md5",
        action="store_true",
        help="Skip MD5 checksum verification after download.",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Print planned URLs and paths without downloading.",
    )
    return parser.parse_args(argv)


def compute_md5(path: Path) -> str:
    """Compute MD5 hex digest for archive integrity verification."""
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, dest_path: Path) -> Path:
    """Download a remote archive to `dest_path` using stdlib urllib."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "SolarEye-Dataset-Fetcher/1.0"}
    )
    with urllib.request.urlopen(request) as response, open(
        dest_path, "wb"
    ) as out_file:
        shutil.copyfileobj(response, out_file, length=1024 * 1024)
    return dest_path


def extract_zip(zip_path: Path, out_dir: Path) -> None:
    """Safely extract `zip_path` into `out_dir` with path traversal guard."""
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved_root = out_dir.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = (resolved_root / member.filename).resolve()
            try:
                target.relative_to(resolved_root)
            except ValueError as exc:
                raise ValueError(
                    f"Unsafe zip member path detected: {member.filename}"
                ) from exc
        zf.extractall(resolved_root)


def main(argv: list[str] | None = None) -> int:
    """Execute dataset download, MD5 verification, and ZIP extraction."""
    args = parse_args(argv)
    if args.dry_run:
        print(f"[DRY RUN] Dataset      : {args.dataset}")
        print(f"[DRY RUN] URL          : {MSPS_ZENODO_URL}")
        print(f"[DRY RUN] Archive      : {args.zip_path}")
        print(f"[DRY RUN] Extract      : {args.out_dir}")
        print(f"[DRY RUN] Exact Bytes  : {MSPS_EXPECTED_BYTES}")
        print(f"[DRY RUN] Expected MD5 : {MSPS_EXPECTED_MD5}")
        return 0

    if not args.zip_path.exists():
        print(f"Downloading {args.dataset} from {MSPS_ZENODO_URL}...")
        download_file(MSPS_ZENODO_URL, args.zip_path)
    else:
        print(f"Using existing archive: {args.zip_path}")

    size_bytes = args.zip_path.stat().st_size
    print(f"Archive size: {size_bytes} bytes ({size_bytes / 1e6:.2f} MB)")

    if not args.skip_md5:
        actual_md5 = compute_md5(args.zip_path)
        print(f"Archive MD5 : {actual_md5}")
        if actual_md5 != MSPS_EXPECTED_MD5:
            raise ValueError(
                f"MD5 mismatch: expected {MSPS_EXPECTED_MD5}, got {actual_md5}"
            )

    if not args.skip_extract:
        print(f"Extracting archive to {args.out_dir}...")
        extract_zip(args.zip_path, args.out_dir)
        print("Extraction complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
