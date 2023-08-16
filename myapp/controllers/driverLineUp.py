from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.db import connection
from ..models import Drivers, SeasonsDrivers, Teams
from typing import TypedDict, List
import json


class Drivers(TypedDict):
    reserves: List[str]
    newDrivers: List[str]


class Team(TypedDict):
    teamID: str
    drivers: Drivers


# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz


def getTeamDrivers(seasonID: str):
    """
    driverLineUp.py
    
    Returns:
        An array of all teams and their drivers.
    """
    c = connection.cursor()

    result = {"teams": [], "availableDrivers": [], "reserves": []}
    try:
        c.execute(
            """
                WITH excluded AS (
                    SELECT d.id, d.name
                    FROM drivers AS d
                    JOIN seasons_drivers AS sd ON sd.driver_id = d.id
                    WHERE sd.season_id = %s AND is_reserve = false
                )
                SELECT d.id, d.name
                FROM drivers AS d
                LEFT JOIN excluded AS e ON d.id = e.id
                WHERE e.id IS NULL
            """,
            [seasonID],
        )

        available = c.fetchall()

        for d in available:
            result["availableDrivers"].append({"id": str(d[0]), "name": d[1]})

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
    
    isEmptyLineUp = True

    try:
        teams = Teams.objects.all().order_by("name")

        for t in teams:
            drivers = SeasonsDrivers.objects.filter(
                season_id=seasonID, team=t
            ).select_related("driver")
            teamDrivers = []
            for d in drivers:
                teamDrivers.append({"id": str(d.driver.id), "name": d.driver.name})
                isEmptyLineUp = False

            result["teams"].append(
                {
                    "id": str(t.id),
                    "name": t.name,
                    "drivers": teamDrivers,
                    "color": t.color,
                    "image": t.logo,
                }
            )

        if isEmptyLineUp:
            result['isEmptyLineUp'] = True

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()

    try:
        reserves = SeasonsDrivers.objects.filter(is_reserve=True).select_related(
            "driver"
        )

        for r in reserves:
            result["reserves"].append({"id": str(r.driver.id), "name": r.driver.name})

    except Exception as e:
        print(e)
        return HttpResponseServerError()

    return HttpResponse(json.dumps(result), status=200)


def postTeamDrivers(seasonID: str, params: Team):
    try:
        for r in params["drivers"]["reserves"]:
            reserve = SeasonsDrivers.objects.get(season_id=seasonID, driver_id=r)
            reserve.team = None
            reserve.is_reserve = True
            reserve.save()

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()

    if len(params["drivers"]["newDrivers"]) == 0:
        return HttpResponse(status=204)

    c = connection.cursor()

    data = []

    for d in params["drivers"]["newDrivers"]:
        data.append((d, seasonID, params["teamID"]))

    try:
        c.executemany(
            """
                INSERT INTO seasons_drivers(driver_id, season_id, team_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (driver_id, season_id)
                DO UPDATE SET is_reserve = FALSE, team_id = EXCLUDED.team_id
            """,
            data,
        )

        return HttpResponse(status=204)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
