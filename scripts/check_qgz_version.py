"""Fail if a .qgz project was not saved with the required QGIS version."""

from __future__ import annotations

import re
import sys
import zipfile

REQUIRED = re.compile(r"^3\.40\.")
VERSION_RE = re.compile(rb'<qgis [^>]*?\bversion="([^"]*)"')


def saved_version(path: str) -> str | None:
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".qgs"):
                match = VERSION_RE.search(z.read(name))
                return match.group(1).decode() if match else None
    return None


def main(paths: list[str]) -> int:
    status = 0
    for path in paths:
        version = saved_version(path)
        if version is None or not REQUIRED.match(version):
            print(f"{path}: saved with QGIS {version}, expected 3.40.*. Re-save it in QGIS 3.40.")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
