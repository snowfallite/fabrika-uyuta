from django.urls import path

from apps.leads.api.views import LeadCreateView

urlpatterns = [
    path("leads/", LeadCreateView.as_view()),
]
