from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseNotFound
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users
from .controllers.authentication import (
    userSignUp,
    userLogIn,
    changeUserRole,
    changePassword,
)
from .controllers.report import reportUpload
from .controllers.races import getRaces, getRaceDrivers
from .controllers.scheduleRelated import getAllAvailableTracks
import os, binascii, base64

SECRET_KEY = base64.b64encode(binascii.b2a_hex(os.urandom(31))).decode("UTF-8")


def my_view(request, param):
    if request.method == "POST":
        body_param = request.POST.get("body_param")
        # Handle the request body parameter

    # Handle the URL parameter
    response_data = {"url_param": param, "message": "Hello, Django!"}
    return JsonResponse(response_data)


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


@csrf_exempt  # api/signup/
def signup(req: HttpRequest):
    if req.method == "POST":
        data = json.loads(req.body)
        return userSignUp(data["params"], SECRET_KEY)

    return HttpResponseNotFound()


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


@csrf_exempt
def changeRole(req: HttpRequest):
    if req.method == "PATCH":
        data = json.loads(req.body)
        return changeUserRole(data["params"])
    return HttpResponseNotFound()


@csrf_exempt  # api/change-password/
def changePasswordEndpoint(req: HttpRequest):
    if req.method == "PATCH":
        data = json.loads(req.body)
        return changePassword(data["params"])
    return HttpResponseNotFound()


@csrf_exempt  # api/upload-report/
def uploadReport(req: HttpRequest):
    if req.method == "POST":
        reportUpload(req.FILES.items(), dict(req.POST.items())["report"])

    return HttpResponse(status=200)


@csrf_exempt  # api/races/
def fetchRaces(req: HttpRequest):
    if req.method == "GET":
        return getRaces()
    return HttpResponseNotFound()


@csrf_exempt  # api/races/<str:race_id>/drivers/
def fetchRaceDrivers(req: HttpRequest, race_id: str):
    if req.method == "GET":
        return getRaceDrivers(race_id)
    return HttpResponseNotFound()


@csrf_exempt  # api/admins/all-tracks/
def fetchAllTracks(req: HttpRequest):
    if req.method == "GET":
        return getAllAvailableTracks()

    return HttpResponseNotFound()
