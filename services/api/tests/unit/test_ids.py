import uuid

import pytest
from vsa_api.platform.ids import IdType, from_uuid, new_id, parse_id, to_uuid


def test_new_id_has_prefix_and_26_char_ulid():
    for id_type in IdType:
        value = new_id(id_type)
        assert value.startswith(f"{id_type.value}_")
        parsed_type, ulid = parse_id(value)
        assert parsed_type is id_type
        assert len(str(ulid)) == 26


def test_uuid_round_trip_for_every_prefix():
    for id_type in IdType:
        original = new_id(id_type)
        as_uuid = to_uuid(original)
        assert isinstance(as_uuid, uuid.UUID)
        assert from_uuid(id_type, as_uuid) == original


def test_parse_rejects_unknown_prefix():
    with pytest.raises(ValueError):
        parse_id("zzz_01M1RQKWSV3Y02W4ZS4XJDAC3P")


def test_parse_rejects_missing_separator():
    with pytest.raises(ValueError):
        parse_id("noseparator")
