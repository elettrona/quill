"""Smoke test for the Quillin Hub: routes, API, and real Forge submissions.

Runs against a throwaway SQLite database -- no PostgreSQL required. Needs the
Hub requirements installed plus the main QUILL package (``pip install -e ..``)
so the Forge can shell out to ``quill.tools.artifact_validate``.

Usage::

    python smoke_test.py
"""

import io
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

HUB_DIR = Path(__file__).resolve().parent
REPO = HUB_DIR.parent
sys.path.insert(0, str(HUB_DIR))
os.chdir(HUB_DIR)

tmp = tempfile.mkdtemp(prefix="hub-smoke-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tmp, "hub.db").replace("\\", "/")

from app import create_app, db  # noqa: E402

app = create_app()
app.config["UPLOAD_FOLDER"] = os.path.join(tmp, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

with app.app_context():
    db.create_all()
    from app.models.database import Artifact

    db.session.add(
        Artifact(
            manifest_id="agent:summarizer",
            artifact_type="agent",
            name="Summarizer",
            version="1.0.0",
            description="Summarizes documents.",
            status="Verified",
            download_url="https://example.test/summarizer.md",
            is_gold_standard=True,
        )
    )
    db.session.commit()

client = app.test_client()
checks = []


def check(name, ok, detail=""):
    checks.append((name, ok))
    print(("OK  " if ok else "FAIL") + " " + name + (" -- " + detail if detail and not ok else ""))


r = client.get("/")
check("storefront 200", r.status_code == 200)
check("storefront shows agent", b"Summarizer" in r.data)
check("storefront type filter nav", b"Browse by type" in r.data)

r = client.get("/?type=agent")
check("type filter 200", r.status_code == 200 and b"Summarizer" in r.data)

r = client.get("/?type=quillin")
check("empty type filter", r.status_code == 200 and b"Summarizer" not in r.data)

r = client.get("/artifact/1")
check("detail page 200", r.status_code == 200 and b"Summarizer" in r.data)

r = client.get("/plugin/1")
check("legacy plugin URL", r.status_code == 200)

r = client.get("/search?q=Summar")
check("search 200", r.status_code == 200 and b"Summarizer" in r.data)

r = client.get("/api/v1/types")
check("api types lists all 7", r.status_code == 200 and len(r.get_json()) == 7)

r = client.get("/api/v1/artifacts")
check("api artifacts", r.status_code == 200 and len(r.get_json()) == 1)

r = client.get("/api/v1/artifacts?type=agent")
check("api artifacts type filter", len(r.get_json()) == 1)

r = client.get("/api/v1/artifacts?type=bogus")
check("api artifacts bad type 400", r.status_code == 400)

r = client.get("/api/v1/plugins")
check("api legacy plugins quillin-only", r.status_code == 200 and r.get_json() == [])

r = client.get("/api/v1/artifacts/agent:summarizer/latest")
check("api latest", r.status_code == 200 and r.get_json()["version"] == "1.0.0")

r = client.get("/forge/")
check("forge index 200", r.status_code == 200 and b"What can you share?" in r.data)

r = client.get("/forge/submit")
check("forge submit form 200", r.status_code == 200)

# Real submissions through the Forge.
# 1. A pronunciation dictionary (pass).
pron = json.dumps({"id": "smoke", "name": "Smoke", "entries": [{"term": "QUILL"}]}).encode()
r = client.post(
    "/forge/submit",
    data={"artifact": (io.BytesIO(pron), "smoke-dict.json")},
    content_type="multipart/form-data",
)
check(
    "forge pronunciation pass",
    r.status_code == 200 and b"Passed." in r.data,
    r.data[:300].decode("utf-8", "replace"),
)

# 2. A broken keyboard pack (fail).
bad_kqp = json.dumps({"name": "No version"}).encode()
r = client.post(
    "/forge/submit",
    data={"artifact": (io.BytesIO(bad_kqp), "bad.kqp")},
    content_type="multipart/form-data",
)
check("forge bad kqp fails", r.status_code == 200 and b"Needs work." in r.data)

# 3. A zipped Quillin (a real bundled one).
quillin_dir = REPO / "quill" / "quillins_bundled" / "journal-stamp"
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w") as archive:
    for path in quillin_dir.rglob("*"):
        if path.is_file():
            archive.write(path, str(path.relative_to(quillin_dir.parent)))
buffer.seek(0)
r = client.post(
    "/forge/submit",
    data={"artifact": (buffer, "journal-stamp.zip")},
    content_type="multipart/form-data",
)
check(
    "forge zipped quillin pass",
    r.status_code == 200 and b"Passed." in r.data,
    r.data[:500].decode("utf-8", "replace"),
)

# 4. A disallowed file type.
r = client.post(
    "/forge/submit",
    data={"artifact": (io.BytesIO(b"x"), "evil.exe")},
    content_type="multipart/form-data",
)
check("forge rejects unknown suffix", r.status_code == 400)

with app.app_context():
    from app.models.database import Submission

    count = Submission.query.count()
    check("submissions recorded", count == 3, f"count={count}")

failed = [name for name, ok in checks if not ok]
print()
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
