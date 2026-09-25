"""Phone normalization shared with the frontend mask (tech.md, 12.3)."""

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


def normalize_phone(raw: str) -> str | None:
    """Return E.164 for a valid number, RU as the default region; never raise."""
    try:
        number = phonenumbers.parse(raw, "RU")
    except NumberParseException:
        return None
    if not phonenumbers.is_valid_number(number):
        return None
    return phonenumbers.format_number(number, PhoneNumberFormat.E164)


def format_phone_display(e164: str) -> str:
    """'+79991234567' -> '+7 (999) 123-45-67'; other countries in INTERNATIONAL format."""
    if not e164:
        return ""
    number = phonenumbers.parse(e164, None)
    if number.country_code == 7:
        digits = f"{number.national_number:010d}"
        return f"+7 ({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:]}"
    return phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
