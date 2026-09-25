from django.urls import path

from apps.content.api.views import CategoryDetailView, HomeView, SiteSettingsView

urlpatterns = [
    path("site-settings/", SiteSettingsView.as_view()),
    path("home/", HomeView.as_view()),
    path("categories/<str:slug>/", CategoryDetailView.as_view()),
]
