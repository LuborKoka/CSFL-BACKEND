from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Races, Seasons
from typing import TypedDict, List


class PostReservesParams(TypedDict):
    drivers: List[str]


# raw query pri insertoch preto, aby id generovala db a nie django (aspon myslim)
def createSeason(params):
    try:
        data = {"seasonID": None}
        with connection.cursor() as c:
            c.execute(
                """
                INSERT INTO seasons (name)
                VALUES (%s)
                RETURNING id
            """,
                [params["name"]],
            )

            data["seasonID"] = str(c.fetchone()[0])

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)

        return HttpResponseBadRequest()


def getSeasonSchedule(seasonID: str):
    try:
        races = (
            Races.objects.filter(season_id=seasonID)
            .select_related("track")
            .order_by("date")
        )

        season = Seasons.objects.get(id=seasonID)
        result = {"races": [], "seasonName": season.name}

        for race in races:
            result["races"].append(
                {
                    "raceID": str(race.id),
                    "date": str(race.date),
                    "raceName": race.track.race_name,
                    "name": race.track.name,
                }
            )

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getAllSeasons():
    result = {"seasons": []}
    try:
        seasons = Seasons.objects.all()
        for s in seasons:
            result["seasons"].append({"id": str(s.id), "name": s.name})

    except Exception as e:
        print(e)

    return HttpResponse(json.dumps(result), status=200)


def getNonReserveDrivers(seasonID: str):
    c = connection.cursor()
    try:
        result = {"drivers": []}
        c.execute(
            """
                WITH excluded AS (
                    SELECT DISTINCT ON (d.id) d.id, d.name
                    FROM drivers AS d
                    JOIN seasons_drivers AS sd ON d.id = sd.driver_id
                    WHERE season_id = %s
                    ORDER BY d.id
                )
                SELECT d.id, d.name
                FROM drivers AS d
                LEFT JOIN excluded AS e ON d.id = e.id
                WHERE e.id IS NULL
            """,
            [seasonID],
        )

        drivers = c.fetchall()

        for d in drivers:
            result["drivers"].append({"driverID": str(d[0]), "driverName": d[1]})

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postNewReserves(seasonID: str, params: PostReservesParams):
    c = connection.cursor()

    data = []

    for d in params["drivers"]:
        data.append((d, seasonID))

    try:
        c.executemany(
            """
                INSERT INTO seasons_drivers (is_reserve, driver_id, season_id)
                VALUES (true, %s, %s)
            """,
            data,
        )

        return HttpResponse(status=204)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
