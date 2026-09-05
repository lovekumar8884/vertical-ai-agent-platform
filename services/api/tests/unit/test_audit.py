from vsa_api.platform.audit import MAX_DIFF_BYTES, build_diff, cap_diff


def test_build_diff_reports_only_changed_keys():
    diff = build_diff({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4})
    assert diff == {
        "b": {"before": 2, "after": 3},
        "c": {"before": None, "after": 4},
    }


def test_build_diff_is_empty_when_unchanged():
    assert build_diff({"a": 1}, {"a": 1}) == {}


def test_cap_diff_returns_small_diff_unchanged():
    diff = {"x": {"before": "a", "after": "b"}}
    assert cap_diff(diff) == diff


def test_cap_diff_truncates_oversized_diff():
    oversized = {"x": {"before": "", "after": "y" * (MAX_DIFF_BYTES + 100)}}
    capped = cap_diff(oversized)
    assert capped["_truncated"] is True
    assert "x" not in capped
