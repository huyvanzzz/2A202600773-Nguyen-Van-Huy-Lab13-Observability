from app.pii import scrub_text


def test_scrub_common_sensitive_values() -> None:
    text = (
        "student@vinuni.edu.vn 090 123 4567 012345678901 "
        "4111 1111 1111 1111 B12345678 duong Nguyen Trai"
    )

    out = scrub_text(text)

    assert "student@" not in out
    assert "090 123" not in out
    assert "012345678901" not in out
    assert "4111" not in out
    assert "B12345678" not in out
    assert "Nguyen Trai" not in out
    assert "REDACTED_EMAIL" in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "REDACTED_PASSPORT" in out
    assert "REDACTED_ADDRESS_VN" in out
