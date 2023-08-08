from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseNotFound
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json
from .controllers.authentication import (
    userSignUp,
    userLogIn,
    changeUserRole,
    changePassword,
)
from .controllers.report import reportUpload, getReports, postReportResponse
from .controllers.races import (
    getRaceDrivers,
    getEditRace,
    postEditRaceDrivers,
    getEditRaceResults,
    postEditRaceResults,
    getRaceResults,
)
from .controllers.scheduleRelated import (
    getAllAvailableTracks,
    postSchedule,
    getSchedule,
    deleteSchedule,
    patchInSchedule,
    deleteFromSchedule,
)
from .controllers.verdict import (
    postVerdict,
    getConcernedDrivers,
    getRaceReportsFIAVersion,
)
from .controllers.seasons import (
    createSeason,
    getAllSeasons,
    getNonReserveDrivers,
    postNewReserves,
    getFiaCandidates,
    postFIA,
)
from .controllers.standings import getStandings
from .controllers.media import raceImage as getRaceImage, media
from .controllers.driverLineUp import postTeamDrivers, getTeamDrivers
from .views_folder.userViews import SECRET_KEY
from .controllers.credentials import isUserPermitted


def hello(request: HttpRequest):
    with connection.cursor() as c:
        c.execute(
            """
                SELECT VERSION()
            """
        )
        results = c.fetchall()
        for row in results:
            print(row[0])

    return HttpResponse("<h1>Hello Word</h1>")


# done
@csrf_exempt  # api/signup/
def signup(req: HttpRequest):
    if req.method == "POST":
        data = json.loads(req.body)
        return userSignUp(data["params"], SECRET_KEY)

    return HttpResponseNotFound()


# done
@csrf_exempt  # api/login/
def signin(req: HttpRequest):
    if req.method == "POST":
        # for attr_name in dir(req):
        #     attr_value = getattr(req, attr_name)
        #     print(f"{attr_name}: {attr_value}\n\n\n")
        data = json.loads(req.body)
        return userLogIn(data["params"], SECRET_KEY)

    return HttpResponseNotFound()


# aint even used
@csrf_exempt
def changeRole(req: HttpRequest):
    if req.method == "PATCH":
        data = json.loads(req.body)
        return changeUserRole(data["params"])
    return HttpResponseNotFound()


# done
@csrf_exempt  # api/change-password/
def changePasswordEndpoint(req: HttpRequest):
    if req.method == "PATCH":
        data = json.loads(req.body)
        return changePassword(data["params"])
    return HttpResponseNotFound()


# done
@csrf_exempt  # api/races/<str:race_id>/report/
def report(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getReports(race_id)

    if req.method == "POST":
        return reportUpload(
            req.FILES.items(), dict(req.POST.items())["report"], race_id
        )

    return HttpResponseNotFound()


# done
@csrf_exempt
def reportResponse(req: HttpRequest, report_id: str):
    if req.method == "POST":
        return postReportResponse(
            req.FILES.items(), report_id, json.loads(dict(req.POST.items())["data"])
        )

    return HttpResponseNotFound()


# done
# api/report/<str:report_id>/verdict/
@csrf_exempt
def reportVerdict(req: HttpRequest, report_id: str):
    if req.method == "GET":
        return getConcernedDrivers(report_id)

    if req.method == "POST":
        data = json.loads(req.body)["params"]
        return postVerdict(report_id, data)

    return HttpResponseNotFound()


# done
def raceReportsFIA(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceReportsFIAVersion(race_id)

    return HttpResponseNotFound()


# done
@csrf_exempt  # api/races/<str:race_id>/drivers/
def fetchRaceDrivers(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceDrivers(race_id)
    return HttpResponseNotFound()


# done
@csrf_exempt  # api/admins/all-tracks/
def fetchAllTracks(req: HttpRequest):
    if req.method == "GET":
        return getAllAvailableTracks()

    return HttpResponseNotFound()


# done
# api/seasons/
@csrf_exempt
def seasons(req: HttpRequest):
    if req.method == "GET":
        return getAllSeasons()


# done
# api/admins/create-season/
@csrf_exempt
def createSeasonView(req: HttpRequest):
    if req.method == "POST":
        data = json.loads(req.body)
        return createSeason(data["params"])

    return HttpResponseNotFound()


# done
# api/races/<str:race_id>/results/
@csrf_exempt
def raceResults(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceResults(race_id)

    return HttpResponseNotFound()


# done
# api/admins/edit-race/drivers/<str:race_id>/
@csrf_exempt
def editRaceDrivers(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getEditRace(race_id)

    if req.method == "POST":
        data = json.loads(req.body)
        return postEditRaceDrivers(race_id, data["params"])

    return HttpResponseNotFound()


# done
# api/admins/edit-race/results/<str:race_id>/
@csrf_exempt
def editRaceResults(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getEditRaceResults(race_id)
    if req.method == "POST":
        data = json.loads(req.body)
        return postEditRaceResults(race_id, data["params"])

    return HttpResponseNotFound()


# sorted
@csrf_exempt
def schedule(req: HttpRequest, season_id: str):
    if req.method == "GET":  # preteky v sezone
        return getSchedule(season_id)

    if req.method == "POST":  # pridanie pretekov do sezony
        data = json.loads(req.body)
        return postSchedule(data["params"], season_id)

    if req.method == "DELETE":  # vymazanie celej sezony
        return deleteSchedule(season_id)

    return HttpResponseNotFound()


# done
@csrf_exempt
def changeSchedule(req: HttpRequest, season_id: str, race_id: str):
    if req.method == "PATCH":
        return patchInSchedule(race_id, season_id, json.loads(req.body)["params"])

    if req.method == "DELETE":
        return deleteFromSchedule(race_id, season_id)

    return HttpResponseNotFound()


# done
# api/seasons/<str:season_id>/standings/
def standings(req: HttpRequest, season_id: str):
    if req.method == "GET":
        return getStandings(season_id)

    return HttpResponseNotFound()


# done
# api/images/race/<str:track_id>/
@csrf_exempt
def raceImage(req: HttpRequest, track_id: str):
    if req.method == "GET":
        return getRaceImage(track_id)

    return HttpResponseNotFound()


# done
# api/videos/report/<str:name>/
@csrf_exempt
def reportVideoView(req: HttpRequest, name: str):
    if req.method == "GET":
        return media(name)

    return HttpResponseNotFound()


# admin views
# admin views
# admin views
# admin views
# admin views
# admin views
# admin views
# admin views
# admin views
# admin views
# admin views


# done
@csrf_exempt
def seasonDrivers(req: HttpRequest, season_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(authorization_header, ["Sys Admin"])

    if permission != True:
        return permission

    if req.method == "GET":
        return getTeamDrivers(season_id)

    if req.method == "POST":
        return postTeamDrivers(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()


# done
@csrf_exempt
def seasonReserves(req: HttpRequest, season_id: str):
    if req.method == "GET":
        return getNonReserveDrivers(season_id)

    if req.method == "POST":
        return postNewReserves(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()


# done
@csrf_exempt
def seasonFia(req: HttpRequest, season_id: str):
    if req.method == "GET":
        return getFiaCandidates(season_id)

    if req.method == "POST":
        return postFIA(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()
