from django.db import connection, transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
import json, traceback
from ..models import Seasons
from typing import TypedDict, List
from urllib.parse import unquote


class PostReservesParams(TypedDict):
    drivers: List[str]


class PostFiaParams(TypedDict):
    users: List[str]


# raw query pri insertoch preto, aby id generovala db a nie django (aspon myslim)
def createSeason(params):
    c = connection.cursor()
    roleName = params["name"] + "fia"

    try:
        data = {"seasonID": None}
        c.execute(
            """
            INSERT INTO seasons (name)
            VALUES (%s)
            RETURNING id
        """,
            [params["name"]],
        )

        seasonID = str(c.fetchone()[0])

        c.execute(
            """
                INSERT INTO roles(name)
                VALUES (%s)
                RETURNING id
            """,
            [roleName],
        )

        roleID = str(c.fetchone()[0])

        c.execute(
            """
                UPDATE seasons
                SET fia_role_id = %s
                WHERE id = %s
            """,
            [roleID, seasonID],
        )

        data["seasonID"] = seasonID

        c.close()
        return HttpResponse(json.dumps(data), status=201)

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseBadRequest()


def getAllSeasons():
    result = {"seasons": []}
    try:
        seasons = Seasons.objects.all()
        for s in seasons:
            result["seasons"].append({"id": str(s.id), "name": s.name})

    except Exception:
        traceback.print_exc()

    return HttpResponse(json.dumps(result), status=200)


def getNonReserveDrivers(seasonName: str):
    c = connection.cursor()
    
    name = unquote(seasonName)

    try:
        result = {"drivers": []}
        c.execute(
            """
                WITH excluded AS (
                    SELECT DISTINCT ON (d.id) d.id, d.name
                    FROM drivers AS d
                    JOIN seasons_drivers AS sd ON d.id = sd.driver_id
                    WHERE season_id = (SELECT id FROM seasons WHERE name = %s)
                    ORDER BY d.id
                )
                SELECT d.id, d.name
                FROM drivers AS d
                LEFT JOIN excluded AS e ON d.id = e.id
                WHERE e.id IS NULL
            """,
            [name],
        )

        drivers = c.fetchall()

        for d in drivers:
            result["drivers"].append({"driverID": str(d[0]), "driverName": d[1]})

        c.close()
        return HttpResponse(json.dumps(result), status=200)

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseBadRequest()


@transaction.atomic
def postNewReserves(seasonName: str, params: PostReservesParams):
    c = connection.cursor()

    name = unquote(seasonName)

    data = []

    for d in params["drivers"]:
        data.append((d, name))

    try:
        c.executemany(
            """
                INSERT INTO seasons_drivers (is_reserve, driver_id, season_id)
                VALUES (true, %s, (SELECT id FROM seasons WHERE name = %s))
            """,
            data,
        )

        c.close()
        return HttpResponse(status=204)

    except Exception as e:
        traceback.print_exc()
        c.close()
        if 'duplicate key value violates unique constraint "unique_season_driver"' in str(e):
            return HttpResponseBadRequest(json.dump({
                "error": "Jeden z týchto jazdcov už na túto sezónu zapísaný je."
            }))
        
        return HttpResponseBadRequest()


def getFiaCandidates(seasonName: str):
    c = connection.cursor()

    name = unquote(seasonName)

    try:
        # vyberie aj current fiu, ALE
        # ta potrebuje byt tiez medzi options, takze je to dobre
        result = {"users": [], "currentFIA": []}
        c.execute(
            """
                WITH excluded AS (
                    SELECT u.id AS user_id, d.name
                    FROM users AS u
                    JOIN drivers AS d ON u.driver_id = d.id
                    JOIN seasons_drivers AS sd ON sd.driver_id = d.id
                    WHERE sd.season_id = (SELECT id FROM seasons WHERE name = %s)
                )
                SELECT u.id, d.name
                FROM users AS u
                JOIN drivers AS d ON d.id = u.driver_id
                LEFT JOIN excluded AS e ON u.id = e.user_id
                WHERE user_id IS NULL

            """,
            [name],
        )

        users = c.fetchall()

        for u in users:
            result["users"].append({"userID": str(u[0]), "driverName": u[1]})

        # current fia
        c.execute(
            """
                SELECT u.id, d.name
                FROM users AS u
                JOIN drivers AS d ON d.id = u.driver_id
                JOIN users_roles AS ur ON ur.user_id = u.id
                JOIN seasons AS s ON ur.role_id = s.fia_role_id
                WHERE s.id = (SELECT id FROM seasons WHERE name = %s)
            """,
            [name],
        )

        current = c.fetchall()

        for curr in current:
            result["currentFIA"].append({"userID": str(curr[0]), "driverName": curr[1]})

        c.close()
        return HttpResponse(json.dumps(result), status=200)

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseServerError()


def postFIA(seasonName: str, params: PostFiaParams):
    c = connection.cursor()

    name = unquote(seasonName)

    data = []

    try:
        c.execute(
            """
                DELETE FROM users_roles WHERE role_id = (SELECT fia_role_id FROM seasons WHERE id = (SELECT id FROM seasons WHERE name = %s))
            """,
            [name],
        )

    except Exception:
        c.close()
        traceback.print_exc()
        return HttpResponseServerError()

    if len(params["users"]) == 0:
        return HttpResponse(status=204)

    for u in params["users"]:
        data.append((u, name))

    try:
        c.executemany(
            """
                INSERT INTO users_roles(user_id, role_id)
                VALUES (%s, (SELECT fia_role_id FROM seasons WHERE id = (SELECT id FROM seasons WHERE name = %s)))
            """,
            data,
        )

        c.close()
        return HttpResponse(status=204)

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseServerError()
