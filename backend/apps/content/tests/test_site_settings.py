"""S2-10: contacts in the API and the singleton admin."""

import re
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from hypothesis import given
from hypothesis import strategies as st

from apps.content.models import SiteSettings
from apps.core.phone import format_phone_display

pytestmark = pytest.mark.django_db
MaxQueries = Callable[[int], AbstractContextManager[Any]]


@given(st.from_regex(r"9[0-9]{9}", fullmatch=True))
def test_russian_numbers_display_in_the_mask_with_digits_kept(national: str) -> None:
    shown = format_phone_display(f"+7{national}")
    assert re.fullmatch(r"\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}", shown)
    assert re.sub(r"\D", "", shown) == f"7{national}"


def test_format_phone_display_keeps_other_countries_international() -> None:
    assert format_phone_display("+375291234567") == "+375 29 123-45-67"
    assert format_phone_display("") == ""


@pytest.fixture(autouse=True)
def reference_rows() -> None:
    call_command("sync_reference_data")


def api(client: Client, settings: Any) -> dict[str, Any]:
    response = client.get(
        "/api/v1/site-settings/", headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN}
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    return data


def test_site_settings_api_returns_contacts_and_links(
    client: Client, settings: Any, django_assert_max_num_queries: MaxQueries
) -> None:
    row = SiteSettings.objects.get(id=1)
    row.phone = "+78172000000"
    row.max_phone = "+79990000001"
    row.vk_url = "https://vk.com/fabrikauyuta"
    row.email = "info@example.ru"
    row.save()
    row.social_links.create(label="Второй", url="https://example.com/2", position=2)
    row.social_links.create(label="Первый", url="https://example.com/1", position=1)

    with django_assert_max_num_queries(2):
        data = api(client, settings)

    assert data == {
        "phone": "+78172000000",
        "phone_display": "+7 (817) 200-00-00",
        "max_phone": "+79990000001",
        "max_phone_display": "+7 (999) 000-00-01",
        "vk_url": "https://vk.com/fabrikauyuta",
        "email": "info@example.ru",
        "address": "",
        "work_hours": "",
        "map_url": "",
        "social_links": [
            {"label": "Первый", "url": "https://example.com/1"},
            {"label": "Второй", "url": "https://example.com/2"},
        ],
    }


def test_empty_settings_give_empty_strings(client: Client, settings: Any) -> None:
    data = api(client, settings)
    assert data["phone"] == data["phone_display"] == ""
    assert data["max_phone"] == data["max_phone_display"] == ""
    assert data["vk_url"] == ""
    assert data["social_links"] == []


def owner() -> Client:
    client = Client()
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    return client


def form_data(**overrides: str) -> dict[str, str]:
    data = {
        "phone": "",
        "max_phone": "",
        "vk_url": "",
        "email": "",
        "address": "",
        "work_hours": "",
        "map_url": "",
        "notify_emails": "",
        "max_chat_id": "",
        "social_links-TOTAL_FORMS": "0",
        "social_links-INITIAL_FORMS": "0",
    }
    return data | overrides


def test_ac4_menu_opens_the_single_settings_form() -> None:
    client = owner()
    response = client.get(reverse("admin:content_sitesettings_changelist"))
    assert response.status_code == 302
    assert response["Location"] == reverse("admin:content_sitesettings_change", args=[1])
    assert client.get(reverse("admin:content_sitesettings_add")).status_code == 403
    delete = reverse("admin:content_sitesettings_delete", args=[1])
    assert client.get(delete).status_code == 403
    assert SiteSettings.objects.count() == 1


def test_ac4_phone_is_normalized_on_save() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])
    response = owner().post(url, form_data(phone="8 (817) 200-00-00"))
    assert response.status_code == 302
    assert SiteSettings.objects.get(id=1).phone == "+78172000000"


def test_ac4_invalid_phone_is_not_saved() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])
    response = owner().post(url, form_data(phone="12345"))
    assert response.status_code == 200
    assert "Проверьте номер телефона" in response.content.decode()
    assert SiteSettings.objects.get(id=1).phone == ""


def test_max_phone_is_normalized_on_save() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])
    response = owner().post(url, form_data(max_phone="8 999 000 00 01"))
    assert response.status_code == 302
    assert SiteSettings.objects.get(id=1).max_phone == "+79990000001"


def test_invalid_max_phone_is_not_saved() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])
    response = owner().post(url, form_data(max_phone="12345"))
    assert response.status_code == 200
    assert "Проверьте номер телефона" in response.content.decode()
    assert SiteSettings.objects.get(id=1).max_phone == ""


def test_ac8_recipients_are_cleaned_up_on_save() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])

    raw = " b@example.ru;a@example.ru\nb@example.ru "

    response = owner().post(url, form_data(notify_emails=raw))

    assert response.status_code == 302
    assert SiteSettings.objects.get(id=1).notify_emails == "b@example.ru, a@example.ru"


def test_ac8_broken_recipient_is_not_saved() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])

    response = owner().post(url, form_data(notify_emails="manager@example.ru, сломанный"))

    assert response.status_code == 200
    assert "Проверьте адрес: сломанный" in response.content.decode()
    assert SiteSettings.objects.get(id=1).notify_emails == ""


def test_ac8_recipients_stay_out_of_the_api(client: Client, settings: Any) -> None:
    SiteSettings.objects.filter(id=1).update(notify_emails="manager@example.ru")

    assert "notify_emails" not in api(client, settings)


def test_the_chat_id_is_saved_from_the_admin() -> None:
    url = reverse("admin:content_sitesettings_change", args=[1])

    response = owner().post(url, form_data(max_chat_id="-12307927"))

    assert response.status_code == 302
    assert SiteSettings.objects.get(id=1).max_chat_id == -12307927


def test_ac8_the_chat_stays_out_of_the_api(client: Client, settings: Any) -> None:
    SiteSettings.objects.filter(id=1).update(max_chat_id=-12307927)

    assert "max_chat_id" not in api(client, settings)
