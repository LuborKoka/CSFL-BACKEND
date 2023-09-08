from django.http import (
    HttpResponseNotFound,
    HttpRequest,
)
import json
from django.views.decorators.csrf import csrf_exempt
from ..controllers.scheduleRelated import getSchedule, postSchedule, deleteSchedule
from ..controllers.seasons import getAllSeasons
from ..controllers.credentials import isUserPermitted
from ..controllers.driverLineUp import getTeamDrivers, postTeamDrivers
from ..controllers.authentication import getUserRoles
from ..controllers.rules import getRules, postRules, patchRules

# api/roles/<str:user_id>/
@csrf_exempt
def roles(req: HttpRequest, user_id: str):
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, []
    )

    if permission != True:
        return permission


    if req.method == "GET":
        return getUserRoles(user_id)

    return HttpResponseNotFound()


# api/schedule/<str:season_id>/
@csrf_exempt
def schedule(req: HttpRequest, season_id: str):
    if req.method == "GET":  # preteky v sezone
        return getSchedule(season_id)

    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "POST":  # pridanie pretekov do sezony
        data = json.loads(req.body)
        return postSchedule(data["params"], season_id)

    if req.method == "DELETE":  # vymazanie celej sezony
        return deleteSchedule(season_id)

    return HttpResponseNotFound()


@csrf_exempt
def seasons(req: HttpRequest):
    if req.method == "GET":
        return getAllSeasons()


# edit timovych dvojic na sezonu
# api/admins/season-drivers/<str:season_id>/
@csrf_exempt
def seasonDrivers(req: HttpRequest, season_id: str):
    if req.method == "GET":
        return getTeamDrivers(season_id)

    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission

    if req.method == "POST":
        return postTeamDrivers(season_id, json.loads(req.body)["params"])

    return HttpResponseNotFound()

@csrf_exempt
def rules(req: HttpRequest):
    if req.method == "GET":
        return getRules()
    
    authorization_header = req.META.get("HTTP_AUTHORIZATION", "")

    permission = isUserPermitted(
        authorization_header, ["Sys Admin", "F1 Admin", "F1 Super Admin"]
    )

    if permission != True:
        return permission
    

    if req.method == "POST":
        return postRules(req.FILES.items())
    
    if req.method == "PATCH":
        return patchRules(json.loads(req.body)["params"])