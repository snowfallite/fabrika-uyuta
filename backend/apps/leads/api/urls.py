from django.urls import path

from apps.leads.api.fake_sheet import FakeSheetView
from apps.leads.api.views import LeadCreateView

urlpatterns = [
    path("leads/", LeadCreateView.as_view()),
    path("test/fake-sheet/", FakeSheetView.as_view()),
]
