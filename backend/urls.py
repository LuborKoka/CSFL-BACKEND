"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/api/myroute/<str:param>/", views.my_view),
    path("api/hello", views.hello, name="hello"),
    path("api/signup/", views.signup),  # authentication.py
    path("api/login/", views.signin),  # authentication.py
    path("api/change-password/", views.changePasswordEndpoint),  # authentication.py
    path("api/upload-report/", views.uploadReport),  # report.py
    path(
        "api/races/", views.fetchRaces
    ),  # races.py; v races.py mam este nejake upravy na plane po zmene db
    path("api/races/<str:race_id>/drivers/", views.fetchRaceDrivers),  # races.py
    path("api/seasons/", views.seasons),  # seasons.py
    path("api/season-schedule/<str:season_id>/", views.season),  # seasons.py
    path("api/admins/create-season/", views.createSeasonView),  # seasons.py
    path("api/admins/all-tracks/", views.fetchAllTracks),  # scheduleRelated.py
    path(
        "api/admins/all-teams-and-drivers/<str:season_id>/",
        views.fetchAllTeamsDriversView,
    ),  # scheduleRelated.py
    path(
        "api/admins/schedule/<str:object_id>/",
        views.schedule
        # vytvorenie pretekov sezony, ziskanie jej pretekov, uprava a vymazanie
    ),  # scheduleRelated.py; object_id je season_id, pre delete metodu je to race.id, ktora bude vymazana
    path("api/admins/edit-race/<str:race_id>/drivers/", views.editRaceDrivers),
    path("api/admins/edit-race/<str:race_id>/results/", views.editRaceResults),
]
