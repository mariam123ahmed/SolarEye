"""AI-assisted reference scaffold for downloading the MSPS EL dataset.

Review the upstream record and checksum before use. The archive is kept under
data/raw/, which is ignored by Git.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import urllib.request
import zipfile

MSPS_URL = "https://zenodo.org/records/21549573/files/MSPS.zip?download=1"
EXPECTED_BYTES = 360_415_905
EXPECTED_MD5 = "25d8fdaa8c9f2f7cf114d9c1f44c0bce"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse dataset download options."""
    parser = argparse.ArgumentParser(
        description="Download and extract the SolarEye MSPS dataset."
    )
    parser.add_argument("--dataset", choices=["msps"], default="msps")
    parser.add_argument("--out_dir", type=Path, default=Path("data/raw/msps"))
    parser.add_argument("--zip_path", type=Path, default=Path("data/raw/MSPS.zip"))
    parser.add_argument("--skip_extract", action="store_true")
    parser.add_argument("--skip_md5", action="store_true")
    parser.add_argument("--dry_run", action="store_true")
    return parser.parse_args(argv)


def compute_md5(path: Path) -> str:
    """Return the MD5 digest used for matching the published archive checksum."""
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, destination: Path) -> Path:
    """Download a URL to a local file, writing to a temporary sibling first."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(
        url, headers={"User-Agent": "SolarEye-Dataset-Fetcher/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def extract_zip_safely(archive: Path, destination: Path) -> None:
    """Extract a ZIP only when every member remains inside destination."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            target = (root / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise ValueError(
                    f"Unsafe ZIP member path: {member.filename}"
                ) from exc
        zipped.extractall(root)


def main(argv: list[str] | None = None) -> int:
    """Run the requested MSPS download and extraction workflow."""
    args = parse_args(argv)
    if args.dry_run:
        print(f"[DRY RUN] Dataset: {args.dataset}")
        print(f"[DRY RUN] URL: {MSPS_URL}")
        print(f"[DRY RUN] Archive: {args.zip_path}")
        print(f"[DRY RUN] Extract to: {args.out_dir}")
        print(f"[DRY RUN] Expected bytes: {EXPECTED_BYTES}")
        print(f"[DRY RUN] Expected MD5: {EXPECTED_MD5}")
        return 0

    if not args.zip_path.exists():
        print(f"Downloading {args.dataset} from Zenodo...")
        download_file(MSPS_URL, args.zip_path)
    else:
        print(f"Using existing archive: {args.zip_path}")

    actual_bytes = args.zip_path.stat().st_size
    print(f"Archive size: {actual_bytes} bytes")
    if actual_bytes != EXPECTED_BYTES:
        raise ValueError(
            f"Archive size mismatch: expected {EXPECTED_BYTES}, got {actual_bytes}"
        )

    if not args.skip_md5:
        actual_md5 = compute_md5(args.zip_path)
        print(f"Archive MD5: {actual_md5}")
        if actual_md5 != EXPECTED_MD5:
            raise ValueError(
                f"MD5 mismatch: expected {EXPECTED_MD5}, got {actual_md5}"
            )

    if not args.skip_extract:
        print(f"Extracting to {args.out_dir}...")
        extract_zip_safely(args.zip_path, args.out_dir)
        print("Extraction complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
