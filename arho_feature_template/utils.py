from __future__ import annotations

from pathlib import Path


def get_icon_file_path(
    icon_file: str, icons_directory: Path = Path(__file__).parent / "resources/template_libraries/icons"
) -> Path | None:
    icon_full_fp = icons_directory / icon_file
    if icon_full_fp.exists():
        return icon_full_fp.resolve()
    return None
