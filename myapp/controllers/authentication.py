from typing import TypedDict
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection
import bcrypt
import jwt
import json
from ..models import Users, Drivers, Seasons
from uuid import UUID
import time
from .seasons import getAllSeasons

# chyba porobit role a ukladanie tokenov do prihlaseni


class signUpParams(TypedDict):
    username: str
    password: str
    passwordConfirm: str
    raceName: str


class logInParmas(TypedDict):
    username: str
    password: str


class User(TypedDict):
    password: bytes
    id: UUID


class changeRoleParams(TypedDict):
    changerID: str
    changed_race_name: str
    targetRole: int


class changePasswordParams(TypedDict):
    username: str
    oldPassword: str
    newPassword: str
    newPasswordConfirm: str


# doplnit pri registracii race name, ak uz existuje, prepojit, ak nie, vytvorit noveho drajvera
# doplnene
def userSignUp(params: signUpParams, SECRET_KEY: str):
    if params["password"] != params["passwordConfirm"]:
        return HttpResponseBadRequest()

    driver = (
        Drivers.objects.values("id").filter(name=params["raceName"]).first()
    )  # hladam, ci race name ma zaznam v tab drivers

    if driver == None:
        try:
            with connection.cursor() as c:
                c.execute(
                    """
                    INSERT INTO drivers(name)
                    VALUES (%s)
                    RETURNING id          
                """,
                    [params["raceName"]],
                )
                driver = {"id": str(c.fetchone()[0])}

        except Exception as e:
            print(e)
            HttpResponseBadRequest()

    hash = bcrypt.hashpw(
        password=params["password"].encode("UTF-8"), salt=bcrypt.gensalt(15)
    )
    userData = [params["username"], hash, driver["id"]]
    user = None
    try:
        with connection.cursor() as c:
            c.execute(
                """
                    INSERT INTO users (username, password, driver_id) VALUES
                    (%s, %s, %s)
                    RETURNING id
                """,
                userData,
            )
            data = c.fetchone()
            if len(data) == 0:
                return HttpResponse(status=409)
            user = data

        payload = {
            "username": params["username"],
            "id": str(user[0]),
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY)
        seasons = getAllSeasons()
        response = json.dumps(
            {
                "token": token,
                "seasons": seasons["seasons"],
            }
        )
        return HttpResponse(response, content_type="application/json", status=201)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)


def userLogIn(params: logInParmas, SECRET_KEY: str):
    user = None
    try:
        user: User = (
            Users.objects.filter(username=params["username"])
            .values("password", "id")
            .first()
        )

        if not user:
            data = json.dumps({"data": "Bad Credentials"})
            time.sleep(0.5)
            return HttpResponseBadRequest(data)

    except Exception as e:
        print(e)
        time.sleep(0.5)
        return HttpResponseBadRequest()

    if bcrypt.checkpw(
        password=params["password"].encode("UTF-8"),
        hashed_password=bytes(user["password"]),
    ):
        payload = {
            "username": params["username"],
            "id": str(user["id"]),
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY)
        seasons = getAllSeasons()   #there is an error right around here
        # 
        response = json.dumps(
            {
                "token": token,
                "seasons": seasons["seasons"],
            }
        )
        return HttpResponse(response, status=200)

    return HttpResponseBadRequest(json.dumps({"data": "Bad Credentials"}))


def changeUserRole(params: changeRoleParams):
    try:
        Users.objects.filter(race_name=params["changed_race_name"]).update(
            role=params["targetRole"]
        )
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def changePassword(params: changePasswordParams):
    try:
        user = Users.objects.filter(username=params["username"]).values().first()

        if not user:
            return HttpResponseNotFound()

        if params["newPassword"] != params["newPasswordConfirm"]:
            return HttpResponseBadRequest(
                json.dumps({"error": "passwords don't match"})
            )

        correctPassword = bcrypt.checkpw(
            password=params["oldPassword"].encode("UTF-8"),
            hashed_password=bytes(user["password"]),
        )

        if not correctPassword:
            return HttpResponseBadRequest(json.dumps({"error": "incorrect password"}))

        if params["newPassword"] != params["newPasswordConfirm"]:
            return HttpResponseBadRequest(
                json.dumps({"error": "passwords don't match"})
            )

        hash = bcrypt.hashpw(
            password=params["newPassword"].encode("UTF-8"), salt=bcrypt.gensalt(15)
        )

        Users.objects.filter(id=str(user["id"])).update(password=hash)

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
