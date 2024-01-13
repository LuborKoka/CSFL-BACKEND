from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.db import connection
from ..models import SeasonsDrivers, Teams, Seasons
from typing import TypedDict, List
import json, traceback
from urllib.parse import unquote


class DriversParams(TypedDict):
    reserves: List[str]
    newDrivers: List[str]


class Team(TypedDict):
    teamID: str
    drivers: DriversParams


# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz
# moze byt jeden driver vo viacerych timoch naraz


def getTeamDrivers(seasonName: str):
    """
    driverLineUp.py
    
    Returns:
        An array of all teams and their drivers.
    """

    name = unquote(seasonName)

    c = connection.cursor()

    result = {"teams": [], "availableDrivers": [], "reserves": []}
    try:
        season = Seasons.objects.get(name=name)

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
            [season.id],
        )

        available = c.fetchall()

        for d in available:
            result["availableDrivers"].append({"id": str(d[0]), "name": d[1]})

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseBadRequest()
    
    isEmptyLineUp = True

    try:
        teams = Teams.objects.all().order_by("name")

        for t in teams:
            drivers = SeasonsDrivers.objects.filter(
                season_id=season.id, team=t
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

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseBadRequest()

    try:
        reserves = SeasonsDrivers.objects.filter(is_reserve=True).select_related(
            "driver"
        )

        for r in reserves:
            result["reserves"].append({"id": str(r.driver.id), "name": r.driver.name})

    except Exception:
        traceback.print_exc()
        c.close()
        return HttpResponseServerError()
    
    c.close()
    return HttpResponse(json.dumps(result), status=200)


def postTeamDrivers(seasonName: str, params: Team):
    try:
        season = Seasons.objects.get(name=unquote(seasonName))
        # ak prichadza o sedacku, nastavim ho ako nahradnika
        for r in params["drivers"]["reserves"]:
            reserve = SeasonsDrivers.objects.get(season_id=season.id, driver_id=r)
            reserve.team = None
            reserve.is_reserve = True
            reserve.save()

    except Exception as e:
        return HttpResponseBadRequest()

    if len(params["drivers"]["newDrivers"]) == 0:
        return HttpResponse(status=204)

    c = connection.cursor()

    data = []

    for d in params["drivers"]["newDrivers"]:
        data.append((d, season.id, params["teamID"]))

    try:

        # povodny zamer bol prepisat nahradnikov do noveho timu on conflict, ale prepise aj tych, ktori uz tim maju
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

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()
