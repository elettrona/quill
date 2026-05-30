from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

_SIGNATURE_SALT = "quill-manifest-signature-v1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a signed Quill update feed file.")
    parser.add_argument("--version", required=True, help="Release version (example: 0.2 or 1.0.0)")
    parser.add_argument("--download-url", required=True, help="URL users should open to download")
    parser.add_argument("--notes", default="", help="Short release notes shown in update prompt")
    parser.add_argument(
        "--published-at",
        default=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        help="ISO-8601 release time (UTC)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "site" / "updates" / ".quill-update-feed-v1.json",
        help="Target feed file path",
    )
    args = parser.parse_args()

    payload = {
        "version": args.version.strip(),
        "download_url": args.download_url.strip(),
        "published_at": args.published_at.strip(),
        "notes": args.notes.strip(),
    }
    signature = _signature_for(payload)
    payload["signature"] = signature
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote signed update feed to {args.output}")
    return 0


def _signature_for(payload: dict[str, str]) -> str:
    canonical = json.dumps(
        {
            "download_url": payload["download_url"],
            "notes": payload["notes"],
            "published_at": payload["published_at"],
            "version": payload["version"],
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(f"{canonical}|{_SIGNATURE_SALT}".encode()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
