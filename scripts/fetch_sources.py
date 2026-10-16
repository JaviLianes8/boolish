"""Fetch the specifications the ground-truth tests read, and record them in a manifest.

    python scripts/fetch_sources.py

The copies land in ``tests/sources/`` (git-ignored: third-party text is never committed
or shipped). ``tests/sources/MANIFEST.json`` is tracked and records, for each file, the
URL, the fetch date, size, SHA-256 and licence. Tests that read a copy skip when it is
missing. Pass ``--check`` to fail when a fetched file no longer matches the manifest.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "tests" / "sources"
CPYTHON = (
    "https://raw.githubusercontent.com/python/cpython/59d1bd5f0beb95f26771a96fe11eac1653d69ffa"
)
CLDR = (
    "https://raw.githubusercontent.com/unicode-org/cldr-json/"
    "91c267402229a59e3ef2774544f001bf959e8809/cldr-json/cldr-misc-full/main"
)
YAML_LICENCE = "may be freely copied provided it is not modified (stated on the page)"
SOURCES = {
    "yaml-1.1-bool.html": ("https://yaml.org/type/bool.html", YAML_LICENCE),
    "yaml-1.2.2.html": ("https://yaml.org/spec/1.2.2/", YAML_LICENCE),
    "distutils-util-3.11.py": (f"{CPYTHON}/Lib/distutils/util.py", "PSF-2.0"),
    "pep-0632.html": (
        "https://peps.python.org/pep-0632/",
        "public domain or CC0-1.0 (stated in the PEP)",
    ),
    **{
        f"cldr-posix-{lang}.json": (f"{CLDR}/{lang}/posix.json", "Unicode-3.0")
        for lang in ("en", "es", "fr", "de", "it", "pt")
    },
}


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "boolish-sources"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return bytes(response.read())


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "MANIFEST.json"
    check = "--check" in sys.argv
    old = json.loads(manifest_path.read_text("utf-8")) if manifest_path.is_file() else {}
    manifest = {}
    for name, (url, licence) in SOURCES.items():
        data = _fetch(url)
        digest = hashlib.sha256(data).hexdigest()
        if check and old.get(name, {}).get("sha256") != digest:
            print(f"{name}: changed since the manifest was written")
            return 1
        (ROOT / name).write_bytes(data)
        manifest[name] = {
            "url": url,
            "fetched": datetime.date.today().isoformat(),
            "size": len(data),
            "sha256": digest,
            "licence": licence,
        }
        print(f"{name}: {len(data)} bytes")
    if not check:
        text = json.dumps(manifest, indent=1, sort_keys=True) + "\n"
        manifest_path.write_text(text, "utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
