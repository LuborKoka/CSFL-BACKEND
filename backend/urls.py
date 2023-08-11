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
# from myapp import views
from myapp.views_folder import userViews, sharedViews, adminViews


urlpatterns = [
    path("api/admin/", admin.site.urls),
    # path("api/api/myroute/<str:param>/", views.my_view),
    # path("api/hello", views.hello, name="hello"),
    path("api/signup/", userViews.signup),  # authentication.py
    path("api/login/", userViews.signin),  # authentication.py
    path("api/change-password/", userViews.changePasswordEndpoint),  # authentication.py
    path("api/roles/<str:user_id>/", sharedViews.roles),
    path(
        "api/races/<str:race_id>/drivers/", userViews.fetchRaceDrivers
    ),  # races.py, zoznam jazdcov do reportu
    path("api/races/<str:race_id>/results/", userViews.raceResults),
    path("api/races/<str:race_id>/reports/", userViews.report),  # report.py
    path("api/report/<str:report_id>/response/", userViews.reportResponse),
    path("api/report/<str:report_id>/verdict/", userViews.reportVerdict),
    path("api/media/<str:file_name>/", userViews.reportVideoView),  #
    path("api/media/<str:folder>/<str:file_name>/", userViews.mediaView),
    path(
        "api/images/tracks/<str:track_id>/", userViews.raceImage
    ),  # mozno ked zrusim icon ako bytea v db a ulozim tie svg ako subory vo file systeme, pouzijem endpoint vyssie
    path("api/seasons/<str:season_id>/standings/", userViews.standings),
    path("api/fia/<str:race_id>/drivers/", userViews.raceReportsFIA),
    path("api/seasons/", sharedViews.seasons),  # seasons.py
    path(
        "api/schedule/<str:season_id>/",  # zlucim dokopy s obycajnym endpointom pre pouzivatela a okrem get metody dam autorizaciu
        sharedViews.schedule
        # vytvorenie pretekov sezony, ziskanie jej pretekov, uprava a vymazanie (toto uz plati pre samotnu sezonu, nie jej preteky, na upravu pretekov bude iny endpoint)
    ),  # scheduleRelated.py; zlucene
    path("api/season-drivers/<str:season_id>/", sharedViews.seasonDrivers),
    path("api/rules/", sharedViews.rules),
    path("api/admins/create-season/", adminViews.createSeasonView),  # seasons.py
    path(
        "api/admins/season-drivers/<str:season_id>/reserves/", adminViews.seasonReserves
    ),
    path(
        "api/schedule/<str:season_id>/<str:race_id>/", adminViews.changeSchedule
    ),  # admin route pre mazanie z kalendaru
    path("api/admins/edit-race/<str:race_id>/drivers/", adminViews.editRaceDrivers),
    path("api/admins/edit-race/<str:race_id>/results/", adminViews.editRaceResults),
    path(
        "api/admins/all-tracks/", adminViews.fetchAllTracks
    ),  # scheduleRelated.py, zoznam dostupnych trati pre vytvorenie novej GP
    path(
        "api/admins/fia/<str:season_id>/", adminViews.seasonFia
    ),  # zoznam vsetkych pouzivatelov dostupnych na poziciu a ulozenie fie
]
