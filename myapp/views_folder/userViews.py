from django.db import connection
from django.http import HttpResponseNotFound, HttpRequest
import json
from django.views.decorators.csrf import csrf_exempt
from ..controllers.standings import getStandings
from ..controllers.media import media, raceImage as getRaceImage
from ..controllers.races import getRaceResults, getRaceDrivers
from ..controllers.verdict import (
    getRaceReportsFIAVersion,
    getConcernedDrivers,
    postVerdict,
)
from ..controllers.report import postReportResponse, getReports, reportUpload
from ..controllers.authentication import userSignUp, userLogIn, changePassword
from ..discord.discordIntegration import saveUserDiscord, getUserDiscord, deleteUserDiscord
from ..controllers.authentication import csrf_token
import os, binascii, base64

SECRET_KEY = base64.b64encode(binascii.b2a_hex(os.urandom(31))).decode("UTF-8")

def getCSRFToken(req: HttpRequest):
    if req.method == "GET":
        return csrf_token(req)


@csrf_exempt  # api/signup/
def signup(req: HttpRequest):
    if req.method == "POST":
        data = json.loads(req.body)
        return userSignUp(data["params"], SECRET_KEY)
    
    if req.method == "PUT":
        return saveUserDiscord(json.loads(req.body)["params"])


    return HttpResponseNotFound()

# api/user-discord/<str:user_id>/
@csrf_exempt
def userDiscord(req: HttpRequest, user_id: str):
    if req.method == "GET":
        return getUserDiscord(user_id)

    if req.method == "POST":
        return saveUserDiscord(json.loads(req.body)["params"])
    
    if req.method == "DELETE":
        return deleteUserDiscord(user_id)


@csrf_exempt  # api/login/
def signin(req: HttpRequest):
    print("signin request recieved")
    if req.method == "POST":
        # for attr_name in dir(req):
        #     attr_value = getattr(req, attr_name)
        #     print(f"{attr_name}: {attr_value}\n\n\n")
        data = json.loads(req.body)
        return userLogIn(data["params"], SECRET_KEY)

    return HttpResponseNotFound()


@csrf_exempt  # api/change-password/
def changePasswordEndpoint(req: HttpRequest):
    if req.method == "PATCH":
        data = json.loads(req.body)
        return changePassword(data["params"])
    return HttpResponseNotFound()


# api/seasons/<str:season_id>/standings/
@csrf_exempt
def standings(req: HttpRequest, season_id: str):
    if req.method == "GET":
        return getStandings(season_id)

    return HttpResponseNotFound()


# api/races/<str:race_id>/results/
@csrf_exempt
def raceResults(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceResults(race_id)

    return HttpResponseNotFound()


# api/races/<str:race_id>/drivers/
@csrf_exempt
def fetchRaceDrivers(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceDrivers(race_id)
    return HttpResponseNotFound()


# api/media/<str:name>/
@csrf_exempt
def reportVideoView(req: HttpRequest, file_name: str):
    if req.method == "GET":
        return media(name=file_name)  # name je actually path

    return HttpResponseNotFound()


def mediaView(req: HttpRequest, folder: str, file_name: str):
    if req.method == "GET":
        return media(name=file_name, folder=folder)

    return HttpResponseNotFound()


# api/images/tracks/<str:track_id>/
@csrf_exempt
def raceImage(req: HttpRequest, track_id: str):
    if req.method == "GET":
        return getRaceImage(track_id)
    # kandidat na rework a zlucenie s inym endpointom, ked sa presunu ikonky z db do file systemu
    return HttpResponseNotFound()


# api/fia/<str:race_id>/drivers/
@csrf_exempt
def raceReportsFIA(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceReportsFIAVersion(race_id)

    return HttpResponseNotFound()


# api/report/<str:report_id>/verdict/
@csrf_exempt
def reportVerdict(req: HttpRequest, report_id: str):
    if req.method == "GET":
        return getConcernedDrivers(report_id)

    if req.method == "POST":
        data = json.loads(req.body)["params"]
        return postVerdict(report_id, data)

    return HttpResponseNotFound()


# kandidat na zlucenie s endpointom vyssie, pouzit PUT metodu zrejme
# api/report/<str:report_id>/response/
@csrf_exempt
def reportResponse(req: HttpRequest, report_id: str):
    if req.method == "POST":
        return postReportResponse(
            req.FILES.items(), report_id, json.loads(dict(req.POST.items())["data"])
        )

    return HttpResponseNotFound()


@csrf_exempt  # api/races/<str:race_id>/report/
def report(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getReports(race_id)

    if req.method == "POST":
        return reportUpload(
            req.FILES.items(), dict(req.POST.items())["report"], race_id
        )

    return HttpResponseNotFound()
