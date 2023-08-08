from django.http import (
    HttpResponseNotFound,
    HttpRequest,
)
import json
from django.views.decorators.csrf import csrf_exempt
from ..controllers.seasons import (
    createSeason,
    getNonReserveDrivers,
    postNewReserves,
    getFiaCandidates,
    postFIA,
)
from ..controllers.races import (
    postEditRaceDrivers,
    postEditRaceResults,
    getEditRaceResults,
    getEditRace,
)
from ..controllers.scheduleRelated import (
    getAllAvailableTracks,
    patchInSchedule,
    deleteFromSchedule,
)
from ..controllers.credentials import isUserPermitted

# content:
#   seasons or drivers
#   schedule
#   races
#   fia


# api/admins/create-season/
@csrf_exempt
def createSeasonView(req: HttpRequest):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "POST":
        data = json.loads(req.body)
        return createSeason(data["params"])

    return HttpResponseNotFound()



# pridanie nahradnikov k sezone
# api/admins/season-drivers/<str:season_id>/reserves/
@csrf_exempt
def seasonReserves(req: HttpRequest, season_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "GET":
        return getNonReserveDrivers(season_id)

    if req.method == "POST":
        return postNewReserves(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()


# api/admins/all-tracks/
def fetchAllTracks(req: HttpRequest):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "GET":
        return getAllAvailableTracks()

    return HttpResponseNotFound()


# api/schedule/<str:season_id>/<str:race_id>/
@csrf_exempt
def changeSchedule(req: HttpRequest, season_id: str, race_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "PATCH":  # upravenie velkej ceny
        return patchInSchedule(race_id, season_id, json.loads(req.body)["params"])

    if req.method == "DELETE":  # vymazanie velkej ceny z kalendaru
        return deleteFromSchedule(race_id, season_id)

    return HttpResponseNotFound()


#  api/admins/edit-race/results/<str:race_id>/
@csrf_exempt
def editRaceResults(req: HttpRequest, race_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "GET":
        return getEditRaceResults(race_id)
    if req.method == "POST":
        data = json.loads(req.body)
        return postEditRaceResults(race_id, data["params"])

    return HttpResponseNotFound()


# api/admins/edit-race/drivers/<str:race_id>/
@csrf_exempt
def editRaceDrivers(req: HttpRequest, race_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "GET":
        return getEditRace(race_id)

    if req.method == "POST":
        data = json.loads(req.body)
        return postEditRaceDrivers(race_id, data["params"])

    return HttpResponseNotFound()


# ziskanie kandidatov na fiu a zapisanie fie pre sezonu
# api/admins/fia/<str:season_id>/
@csrf_exempt
def seasonFia(req: HttpRequest, season_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "GET":
        return getFiaCandidates(season_id)

    if req.method == "POST":
        return postFIA(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()
