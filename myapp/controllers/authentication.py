from typing import TypedDict
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.db import connection, IntegrityError, transaction
import bcrypt
import jwt
import json
from ..models import Users, Drivers, UsersRoles, Roles
from uuid import UUID
import time
from datetime import datetime, timedelta

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
# doplnit, aby nejebalo existujuci link driver-user


@transaction.atomic
def userSignUp(params: signUpParams, SECRET_KEY: str):
    if params["password"] != params["passwordConfirm"]:
        return HttpResponseBadRequest(
            json.dumps({"error": "Heslá sa nezhodujú."}),
        )

    driver = (
        Drivers.objects.values("id").filter(name=params["raceName"]).first()
    )  # hladam, ci race name ma zaznam v tab drivers

    c = connection.cursor()
    if driver == None:
        try:
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
            if "value too long for type character varying" in str(e):
                return HttpResponseBadRequest(
                    json.dumps({"error": "Meno musí mať najviac 50 znakov."})
                )
            print(e)
            return HttpResponseServerError()

    hash = bcrypt.hashpw(
        password=params["password"].encode("UTF-8"), salt=bcrypt.gensalt(15)
    )

    try:
        c.execute(
            """
                INSERT INTO users (username, password, driver_id) VALUES
                (%s, %s, %s)
                RETURNING id
            """,
            [params["username"], hash, driver["id"]],
        )
        user = c.fetchone()

        payload = {
            "username": params["username"],
            "id": str(user[0]),
            "exp": datetime.utcnow() + timedelta(days=7),
        }

        token = jwt.encode(payload=payload, key=SECRET_KEY)

        responseData = json.dumps({"token": token})
        return HttpResponse(responseData, status=201)
    except IntegrityError as e:
        if 'duplicate key value violates unique constraint "unique_driver_id"' in str(
            e
        ):
            return HttpResponse(
                json.dumps({"error": "Takéto verejné meno už existuje."}), status=409
            )

        if (
            'duplicate key value violates unique constraint "users_username_key"'
            in str(e)
        ):
            return HttpResponse(
                json.dumps({"error": "Takéto používateľské meno už existuje."}),
                status=409,
            )

    except Exception as e:
        if "value too long for type character varying" in str(e):
            return HttpResponseBadRequest(
                json.dumps({"error": "Meno musí mať najviac 50 znakov."})
            )
        print(e)
        return HttpResponseServerError()


def userLogIn(params: logInParmas, SECRET_KEY: str):
    user = None
    try:
        user: User = (
            Users.objects.filter(username=params["username"])
            .values("password", "id")
            .first()
        )

        if not user:
            data = json.dumps({"error": "Nesprávne meno alebo heslo"})
            time.sleep(1.5)
            return HttpResponse(data, status=401)

    except Exception as e:
        print(e)
        time.sleep(1.5)
        return HttpResponseServerError()

    if bcrypt.checkpw(
        password=params["password"].encode("UTF-8"),
        hashed_password=bytes(user["password"]),
    ):
        payload = {
            "username": params["username"],
            "id": str(user["id"]),
            "exp": datetime.utcnow() + timedelta(days=7),
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY)

        result = {"token": token, "roles": []}
        roles = UsersRoles.objects.filter(user_id=user["id"]).select_related("role")
        for r in roles:
            result["roles"].append(r.role.name)

        return HttpResponse(json.dumps(result), status=200)

    return HttpResponse(json.dumps({"error": "Nesprávne meno alebo heslo"}), status=401)


def changeUserRole(params: changeRoleParams):
    try:
        Users.objects.filter(race_name=params["changed_race_name"]).update(
            role=params["targetRole"]
        )
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getUserRoles(userID: str):
    try:
        result = {"roles": []}
        roles = UsersRoles.objects.filter(user_id=userID).select_related("role")

        for r in roles:
            result["roles"].append(r.role.name)

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        return HttpResponseBadRequest()


def changePassword(params: changePasswordParams):
    try:
        user = Users.objects.filter(username=params["username"]).first()

        if not user:
            return HttpResponseNotFound()

        if params["newPassword"] != params["newPasswordConfirm"]:
            return HttpResponseBadRequest(json.dumps({"error": "Heslá sa nezhodujú"}))

        correctPassword = bcrypt.checkpw(
            password=params["oldPassword"].encode("UTF-8"),
            hashed_password=bytes(user["password"]),
        )

        if not correctPassword:
            return HttpResponseBadRequest(json.dumps({"error": "Nesprávne heslo."}))

        hash = bcrypt.hashpw(
            password=params["newPassword"].encode("UTF-8"), salt=bcrypt.gensalt(15)
        )

        user.password = hash
        user.save()

        return HttpResponse(status=204)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
