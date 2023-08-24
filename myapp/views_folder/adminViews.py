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
from ..controllers.users_roles import get_users, add_user_role, delete_user_role
from ..controllers.wife_beater import createDriver

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

    if req.method == "PUT":  # upravenie velkej ceny
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

# api/admins/users-roles/
@csrf_exempt
def userRoles(req: HttpRequest):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission
    
    if req.method == "GET":
        return get_users()
    
    if req.method == "PATCH":
        return add_user_role(json.loads(req.body)['params'])
    

    user_id = req.GET.get('user_id')
    role = req.GET.get('role')

    if req.method == "DELETE":
        return delete_user_role(user_id=user_id, role=role)
    

# api/wife-beater/drivers/
@csrf_exempt
def drivers(req: HttpRequest):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin"]
    )

    if permission != True:
        return permission
    

    if req.method == "POST":
        return createDriver(json.loads(req.body)['params'])
    

# api/wife-beater/roles/
@csrf_exempt
def changeRoles(req: HttpRequest):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin"]
    )

    if permission != True:
        return permission
    

    if req.method == "GET":
        return get_users()
    
    userID = req.GET.get('user_id')
    roleID = req.GET.get('role_id')

    if req.method == "PUT":
        return add_user_role(userID, roleID)
    

    if req.method == "DELETE":
        return delete_user_role(userID, roleID)
    
    return HttpResponseNotFound()