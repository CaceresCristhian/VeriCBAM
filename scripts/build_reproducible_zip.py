"""
Script to build a 100% self-contained, reproducible Capstone.zip archive.
Ensures that all processed data (data/02_processed/), satellite cache (data/03_satellite_cache/),
experiments, source code, and tests are bundled.
"""

import os
import zipfile
from pathlib import Path

WORKSPACE = Path(__file__).parents[1]
ZIP_PATH = WORKSPACE / "Capstone.zip"

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "archive",
    "csv_tables",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".zip",
    ".log",
}


def build_zip():
    print(f"Building self-contained reproducible package: {ZIP_PATH}")
    # Remove existing zip if present
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    included_count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORKSPACE):
            # Modify dirs in-place to prevent recursion into excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(WORKSPACE)

                # Skip excluded extensions
                if file_path.suffix in EXCLUDE_EXTENSIONS:
                    continue
                # Skip temporary files
                if file.startswith("~$") or file.endswith(".tmp"):
                    continue

                zipf.write(file_path, arcname=str(rel_path).replace("\\", "/"))
                included_count += 1

    zip_size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Successfully packaged {included_count} files into Capstone.zip ({zip_size_mb:.2f} MB)")

    # Verify contents
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()
        has_processed = any("data/02_processed" in n for n in names)
        has_sat = any("data/03_satellite_cache" in n for n in names)
        has_tests = any("tests/" in n for n in names)
        has_docs = any("docs/" in n for n in names)
        print("Verification:")
        print(f"  - data/02_processed included: {has_processed}")
        print(f"  - data/03_satellite_cache included: {has_sat}")
        print(f"  - tests included: {has_tests}")
        print(f"  - docs included: {has_docs}")


if __name__ == "__main__":
    build_zip()
