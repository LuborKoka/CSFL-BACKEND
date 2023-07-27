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
    path(
        "api/races/", views.fetchRaces
    ),  # races.py; v races.py mam este nejake upravy na plane po zmene db -- ale keby si sem dopisem, ze ako do pitchi
    path("api/races/<str:race_id>/drivers/", views.fetchRaceDrivers),  # races.py
    path("api/races/<str:race_id>/results/", views.raceResults),
    path("api/races/<str:race_id>/reports/", views.report),  # report.py
    path("api/report/<str:report_id>/response/", views.reportResponse),
    path("api/report/<str:report_id>/verdict/", views.reportVerdict),
    path("api/fia/<str:race_id>/drivers/", views.raceReportsFIA),
    path("api/media/<str:name>/", views.reportVideoView),
    path("api/seasons/", views.seasons),  # seasons.py
    path(
        "api/season-schedule/<str:season_id>/",
        views.season,  # mal by uz byt nahradeny a moze sa zrejme vymazat, get metoda urcite
    ),  # seasons.py; toto a "api/admins/schedule/<str:season_id>/" vyzeraju rovnako
    path("api/admins/create-season/", views.createSeasonView),  # seasons.py
    path(
        "api/admins/all-tracks/", views.fetchAllTracks
    ),  # scheduleRelated.py, zoznam dostupnych trati pre vytvorenie novej GP
    path(
        "api/schedule/<str:season_id>/",  # zlucim dokopy s obycajnym endpointom pre pouzivatela a okrem get metody dam autorizaciu
        views.schedule
        # vytvorenie pretekov sezony, ziskanie jej pretekov, uprava a vymazanie (toto uz plati pre samotnu sezonu, nie jej preteky, na upravu pretekov bude iny endpoint)
    ),  # scheduleRelated.py
    path("api/admins/season-drivers/<str:season_id>/", views.seasonDrivers),
    path("api/admins/season-drivers/<str:season_id>/reserves/", views.seasonReserves),
    path("api/admins/schedule/<str:season_id>/<str:race_id>/", views.changeSchedule),
    path("api/admins/edit-race/<str:race_id>/drivers/", views.editRaceDrivers),
    path("api/admins/edit-race/<str:race_id>/results/", views.editRaceResults),
    path("api/seasons/<str:season_id>/standings/", views.standings),
    path("api/images/tracks/<str:track_id>/", views.raceImage),
]
