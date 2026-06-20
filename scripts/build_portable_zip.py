"""Build the portable distribution ZIP for a release.

The portable bundle is the runnable QUILL distribution with embedded
Python and all bundled tools (Pandoc, DECtalk, eSpeak-NG, Piper,
Kokoro). It is published as a release asset so users who don't want
the installer can extract the zip and run run-quill.cmd.

Usage::

    python scripts/build_portable_zip.py \\
        --source-dir windows-distribution/portable \\
        --output Quill-Portable-v0.7.0-beta.1.zip
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("windows-distribution") / "portable",
        help="The portable bundle directory to zip.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="The output zip path (e.g. Quill-Portable-v0.7.0-beta.1.zip).",
    )
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"ERROR: {args.source_dir} is not a directory", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    file_count = 0
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(args.source_dir.rglob("*")):
            if path.is_file():
                arcname = path.relative_to(args.source_dir.parent)
                zf.write(path, arcname)
                file_count += 1
    print(f"Wrote {args.output} ({file_count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
