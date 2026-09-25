"""S1-04 AC4: SiteSettings stays a singleton at the database level."""

import pytest
from django.db import IntegrityError

from apps.content.models import SiteSettings

pytestmark = pytest.mark.django_db


def test_ac4_second_site_settings_row_is_rejected() -> None:
    SiteSettings.objects.create(id=1)
    with pytest.raises(IntegrityError):
        SiteSettings.objects.create(id=2)
