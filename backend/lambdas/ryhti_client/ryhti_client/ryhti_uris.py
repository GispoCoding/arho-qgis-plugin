"""Ryhti reference uris.

Ryhti refers to the objects of another plan by uri, not by key:
https://uri.rakennetunymparistontietojarjestelma.fi/{class}/{key}, with the
class name in lower case. The keys of this database are the Ryhti keys, so a
uri is built from a row id and read back into one.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal
from uuid import UUID

if TYPE_CHECKING:
    from database.base import DbId

LOGGER = logging.getLogger(__name__)

RYHTI_URI_BASE = "https://uri.rakennetunymparistontietojarjestelma.fi"

type RyhtiClass = Literal[
    "plan", "planobject", "planregulationgroup", "generalregulationgroup"
]


def ryhti_uri(ryhti_class: RyhtiClass, key: DbId | UUID) -> str:
    return f"{RYHTI_URI_BASE}/{ryhti_class}/{key}"


def key_of_ryhti_uri(uri: str) -> UUID | None:
    """The key a Ryhti uri ends with, or None when the uri holds no key.

    Only the last part of the uri is read, so the class name is not checked.
    """
    try:
        return UUID(uri.rstrip("/").rsplit("/", 1)[-1])
    except ValueError:
        LOGGER.warning("Uri %s does not end with a key.", uri)
        return None
