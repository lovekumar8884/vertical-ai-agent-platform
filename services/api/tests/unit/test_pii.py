from vsa_api.platform.pii import REDACTED, scrub, scrub_text


def test_email_is_redacted():
    out = scrub_text("reach me at jane.doe@example.com please")
    assert "jane.doe@example.com" not in out
    assert REDACTED in out


def test_phone_is_redacted():
    out = scrub_text("call +1 (415) 555-2671 today")
    assert "555" not in out
    assert REDACTED in out


def test_credit_card_is_redacted():
    out = scrub_text("card 4111 1111 1111 1111 on file")
    assert "4111" not in out
    assert REDACTED in out


def test_nested_dict_and_list_are_scrubbed():
    event = {
        "message": "user jane.doe@example.com signed in",
        "breadcrumbs": [{"data": {"contact": "x@y.com"}}],
        "tags": ("+1 (415) 555-2671",),
    }
    scrubbed = scrub(event)
    flat = str(scrubbed)
    assert "jane.doe@example.com" not in flat
    assert "x@y.com" not in flat
    assert "555" not in flat


def test_non_pii_text_is_untouched():
    assert scrub_text("order 12 shipped") == "order 12 shipped"
