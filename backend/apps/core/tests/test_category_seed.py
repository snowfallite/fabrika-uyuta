"""S2-16 AC2: categories are seeded once, then the content manager owns them."""

import pytest
from django.core.management import call_command

from apps.content.models import Category

pytestmark = pytest.mark.django_db


def test_ac2_empty_table_gets_six_categories_with_other() -> None:
    call_command("sync_reference_data")
    assert Category.objects.count() == 6
    assert Category.objects.get(slug="other").title == "Другое"


def test_ac2_second_run_keeps_the_same_rows() -> None:
    call_command("sync_reference_data")
    call_command("sync_reference_data")
    assert Category.objects.count() == 6


def test_ac2_deleted_category_does_not_come_back() -> None:
    call_command("sync_reference_data")
    Category.objects.filter(slug="office").delete()
    call_command("sync_reference_data")
    assert Category.objects.count() == 5
    assert not Category.objects.filter(slug="office").exists()


def test_ac2_own_category_survives_the_next_run() -> None:
    call_command("sync_reference_data")
    Category.objects.create(slug="kids", title="Детская мебель", position=9)
    call_command("sync_reference_data")
    assert Category.objects.filter(slug="kids").exists()
    assert Category.objects.count() == 7
