import json

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike


def read_json(json_path: str | PathLike) -> dict:
    with open(json_path) as f:
        return json.load(f)
