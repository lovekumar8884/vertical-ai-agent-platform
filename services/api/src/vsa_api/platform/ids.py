"""ULID/UUID identifier helpers (ADR-042, ADR-043).

IDs are stored on-disk as ``UUID`` and presented in the API as a ULID string
with a frozen type prefix, e.g. ``agn_01HN...``. All conversion between the two
representations goes through this module.
"""

from __future__ import annotations

import uuid
from enum import Enum

from ulid import ULID

_SEP = "_"


class IdType(str, Enum):
    """Frozen entity -> prefix table (ADR-043). The value is the prefix."""

    ORG = "org"
    USER = "usr"
    MEMBERSHIP = "mem"
    API_KEY = "key"
    AUDIT_LOG = "aud"
    AGENT = "agn"
    AGENT_VERSION = "agv"
    CORPUS = "cor"
    DOCUMENT = "doc"
    CHUNK = "chk"
    TOOL_BINDING = "bnd"
    TOOL = "tol"
    SESSION = "ses"
    TURN = "tur"
    CONNECTION = "con"
    SUBSCRIPTION = "sub"
    INVOICE = "inv"
    USAGE_RECORD = "usg"
    EVAL_RUN = "evr"
    EVENT = "evt"


def format_id(id_type: IdType, ulid: ULID) -> str:
    return f"{id_type.value}{_SEP}{ulid}"


def parse_id(prefixed: str) -> tuple[IdType, ULID]:
    prefix, sep, rest = prefixed.partition(_SEP)
    if not sep or not rest:
        raise ValueError(f"Malformed id: {prefixed!r}")
    return IdType(prefix), ULID.from_str(rest)


def new_id(id_type: IdType) -> str:
    """Mint a new prefixed ULID string for the API surface."""
    return format_id(id_type, ULID())


def to_uuid(prefixed: str) -> uuid.UUID:
    """Convert an API ULID string to the on-disk UUID."""
    _, ulid = parse_id(prefixed)
    return ulid.to_uuid()


def from_uuid(id_type: IdType, value: uuid.UUID) -> str:
    """Present an on-disk UUID as a prefixed ULID string."""
    return format_id(id_type, ULID.from_uuid(value))
