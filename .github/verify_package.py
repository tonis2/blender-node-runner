#!/usr/bin/env python3
"""Check that an extension zip contains exactly the manifest's build paths.

Usage: verify_package.py <package.zip> [manifest.toml]

Exits non-zero and lists the offending entries if the archive contains any
file that is not ``blender_manifest.toml`` or one of the ``[build] paths``
entries, or if an expected file is missing.
"""

import sys
import tomllib
import zipfile
from pathlib import Path

MANIFEST = "blender_manifest.toml"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    package = Path(argv[1])
    manifest_path = Path(argv[2]) if len(argv) > 2 else Path(MANIFEST)

    with open(manifest_path, "rb") as fh:
        manifest = tomllib.load(fh)

    expected = {MANIFEST}
    for entry in manifest["build"]["paths"]:
        expected.add(entry.rstrip("/"))

    with zipfile.ZipFile(package) as zf:
        actual = {name for name in zf.namelist() if not name.endswith("/")}

    # A directory in the allowlist may contain any file underneath it.
    def allowed(name):
        return any(name == e or name.startswith(e + "/") for e in expected)

    unexpected = sorted(n for n in actual if not allowed(n))
    missing = sorted(
        e for e in expected if not any(n == e or n.startswith(e + "/") for n in actual)
    )

    print(f"{package.name}: {len(actual)} files")
    for name in sorted(actual):
        print(f"  {name}")

    ok = True
    if unexpected:
        ok = False
        print("\nERROR: files in the package that are not in the manifest allowlist:")
        for name in unexpected:
            print(f"  {name}")
    if missing:
        ok = False
        print("\nERROR: manifest paths missing from the package:")
        for name in missing:
            print(f"  {name}")

    if ok:
        print("\nOK: package matches blender_manifest.toml [build] paths")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
