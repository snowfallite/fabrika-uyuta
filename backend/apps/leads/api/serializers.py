"""Lead DTOs of tech.md, section 7; error texts of section 12.1."""

from typing import Any

from django.core.validators import ProhibitNullCharactersValidator
from rest_framework import serializers
from rest_framework.validators import ProhibitSurrogateCharactersValidator

from apps.core.enums import ProductKind

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
    return {"required": default, "blank": default, "null": default, "invalid": default} | overrides


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
    name = RawCharField(
        max_length=120, error_messages=_messages(NAME_REQUIRED, max_length=NAME_TOO_LONG)
    )
    phone = RawCharField(
        max_length=32, error_messages=_messages(PHONE_REQUIRED, max_length=PHONE_INVALID)
    )
    product = serializers.ChoiceField(
        choices=ProductKind.choices,
        error_messages=_messages(PRODUCT_REQUIRED, invalid_choice=PRODUCT_REQUIRED),
    )
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
