"""Lead DTOs of tech.md, section 7; error texts of section 12.1."""

from typing import Any
from urllib.parse import urlsplit

from django.core.validators import ProhibitNullCharactersValidator
from rest_framework import serializers
from rest_framework.validators import ProhibitSurrogateCharactersValidator

from apps.content.selectors import category_label
from apps.core.phone import normalize_phone
from apps.core.text import clean_name, clean_text

NAME_REQUIRED = "Укажите ФИО"
NAME_TOO_SHORT = "Слишком короткое имя"
NAME_TOO_LONG = "Не больше 120 символов"
PHONE_REQUIRED = "Укажите телефон"
PHONE_INVALID = "Проверьте номер телефона"
PRODUCT_REQUIRED = "Выберите, что хотите заказать"
DIMENSIONS_TOO_LONG = "Не больше 300 символов"
COMMENT_TOO_LONG = "Не больше 2000 символов"
CONSENT_REQUIRED = "Нужно согласие на обработку персональных данных"


def _messages(default: str, **overrides: str) -> dict[str, Any]:
    keys = ("required", "blank", "null", "invalid", "max_length")
    return dict.fromkeys(keys, default) | overrides


class RawCharField(serializers.CharField):
    """Strings only, as the schema says (DRF would coerce numbers). Drops DRF's null and
    surrogate validators: their default texts would leak into responses, and lead cleanup
    strips such characters anyway."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        prohibited = (ProhibitNullCharactersValidator, ProhibitSurrogateCharactersValidator)
        self.validators = [v for v in self.validators if not isinstance(v, prohibited)]

    def to_internal_value(self, data: Any) -> str:
        if not isinstance(data, str):
            self.fail("invalid")
        return super().to_internal_value(data)


class StrictBooleanField(serializers.BooleanField):
    """JSON true or false only; DRF would also take "yes", "1" and 1."""

    def to_internal_value(self, data: Any) -> bool:
        if not isinstance(data, bool):
            self.fail("invalid")
        return data


class LeadCreateSerializer(serializers.Serializer):
    # Title of the chosen category, taken while validating it and stored as a snapshot.
    _product_label: str = ""

    name = RawCharField(
        max_length=120, error_messages=_messages(NAME_REQUIRED, max_length=NAME_TOO_LONG)
    )
    phone = RawCharField(
        max_length=32, error_messages=_messages(PHONE_REQUIRED, max_length=PHONE_INVALID)
    )
    # v15: the kind is a category slug, so the schema has no enum and the check hits the table.
    product = RawCharField(max_length=32, error_messages=_messages(PRODUCT_REQUIRED))
    dimensions = RawCharField(
        required=False,
        allow_blank=True,
        max_length=300,
        error_messages=_messages(DIMENSIONS_TOO_LONG),
    )
    comment = RawCharField(
        required=False,
        allow_blank=True,
        max_length=2000,
        error_messages=_messages(COMMENT_TOO_LONG),
    )
    consent = StrictBooleanField(error_messages=_messages(CONSENT_REQUIRED))
    website = RawCharField(required=False, allow_blank=True)
    source_url = RawCharField(required=False, allow_blank=True, max_length=2000)

    def validate_name(self, value: str) -> str:
        name = clean_name(value)
        if not any(ch.isalpha() for ch in name):
            raise serializers.ValidationError(NAME_REQUIRED)
        if len(name) < 2:
            raise serializers.ValidationError(NAME_TOO_SHORT)
        if len(name) > 120:
            raise serializers.ValidationError(NAME_TOO_LONG)
        return name

    def validate_phone(self, value: str) -> str:
        phone = normalize_phone(value)
        if phone is None:
            raise serializers.ValidationError(PHONE_INVALID)
        return phone

    def validate_dimensions(self, value: str) -> str:
        return clean_text(value)

    def validate_comment(self, value: str) -> str:
        return clean_text(value)

    def validate_consent(self, value: bool) -> bool:
        if value is not True:
            raise serializers.ValidationError(CONSENT_REQUIRED)
        return value

    def validate_product(self, value: str) -> str:
        """Match the kind to a category and keep its title (tech.md, section 7, v15).

        The check sits on the field, not in validate(), so a bad kind comes back together with
        the other field errors instead of waiting for the next submit. A hidden category still
        passes: the content manager may uncheck the box while a visitor fills the form, and the
        lead matters more than the list being current.
        """
        label = category_label(value)
        if label is None:
            raise serializers.ValidationError(PRODUCT_REQUIRED)
        self._product_label = label
        return value

    def validate_source_url(self, value: str) -> str:
        """Path and query only, no host, at most 500 characters (tech.md, section 7)."""
        parts = urlsplit(clean_text(value))
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        return path[:500]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        return attrs | {"product_label": self._product_label}


class LeadCreatedSerializer(serializers.Serializer):
    id = serializers.UUIDField()


def _error_list() -> serializers.ListField:
    return serializers.ListField(child=serializers.CharField(), required=False)


class LeadCreateErrorSerializer(serializers.Serializer):
    """400 body: field -> messages from 12.1."""

    name = _error_list()
    phone = _error_list()
    product = _error_list()
    dimensions = _error_list()
    comment = _error_list()
    consent = _error_list()
    non_field_errors = _error_list()
