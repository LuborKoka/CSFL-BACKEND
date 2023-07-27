from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.db import connection
from ..models import Races, RacesDrivers, SeasonsDrivers, Drivers, Tracks, Teams
import json
from typing import TypedDict, List
from ..controllers.time import gap_to_time, time_to_seconds


class Driver(TypedDict):
    teamID: str
    drivers: List[str]


class RaceDriversParams(TypedDict):
    teams: List[Driver]


class DriverResult(TypedDict):
    id: str
    time: str


class Results(TypedDict):
    leader: DriverResult
    otherDrivers: List[DriverResult]
    fastestLap: str


class PostRaceResultsParams(TypedDict):
    results: Results


# race name bude treba joinovat s tracks a vytiahnut race_name z tej tabulky, az dropnem name z races
def getRaces():
    try:
        races = Races.objects.values("name", "id")

        data = {"races": []}

        for r in races:
            data["races"].append({"name": r["name"], "id": str(r["id"])})

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)

    return HttpResponseBadRequest()


def getRaceDrivers(id: str):
    try:
        drivers = RacesDrivers.objects.filter(race=id).select_related("driver")

        data = {"drivers": [], "raceName": ""}

        for d in drivers:
            data["drivers"].append({"id": str(d.driver.id), "name": d.driver.name})

        race = Races.objects.select_related("track").get(id=id)

        data["raceName"] = race.track.race_name

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)

    return HttpResponseBadRequest()


def getEditRace(raceID: str):
    try:
        race = Races.objects.select_related("track").get(id=raceID)

        teams = Teams.objects.all()

        reservePilot = SeasonsDrivers.objects.filter(
            is_reserve=True, season_id=race.season.id
        ).select_related("driver")

        altTeams = []

        reserve = []

        for rp in reservePilot:
            reserve.append({"id": str(rp.driver.id), "name": rp.driver.name})

        for t in teams:
            drivers = SeasonsDrivers.objects.filter(
                season_id=race.season_id, team_id=t.id
            ).select_related("driver")

            team = {
                "teamID": str(t.id),
                "teamName": t.name,
                "drivers": [],
                "color": t.color,
            }

            for d in drivers:
                team["drivers"].append({"id": str(d.driver.id), "name": d.driver.name})

            altTeams.append(team)

        result = {
            "raceName": race.track.race_name,
            "date": str(race.date),
            "teams": altTeams,
            "reserves": reserve,
        }

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postEditRaceDrivers(raceID: str, params: RaceDriversParams):
    try:
        raceDrivers = RacesDrivers.objects.filter(race_id=raceID)
        raceDrivers.delete()

    except Exception as e:
        print(e)
        return HttpResponseServerError()

    data = []

    for t in params["teams"]:
        for d in t["drivers"]:
            data.append([t["teamID"], raceID, d])

    try:
        with connection.cursor() as c:
            c.executemany(
                """
                    INSERT INTO races_drivers(team_id, race_id, driver_id)
                    VALUES (%s, %s, %s)
                """,
                data,
            )

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getEditRaceResults(raceID: str):
    try:
        drivers = RacesDrivers.objects.filter(race_id=raceID).select_related(
            "driver", "team"
        )

        result = {"drivers": []}

        for d in drivers:
            result["drivers"].append(
                {"id": str(d.driver.id), "name": d.driver.name, "color": d.team.color}
            )

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


# bude treba aj sprinty doriesit
def postEditRaceResults(raceID: str, params: PostRaceResultsParams):
    # prepocet casu vitaza na sekundy
    leader = {
        "id": params["results"]["leader"]["id"],
        "time": time_to_seconds(params["results"]["leader"]["time"]),
    }

    # zapis vitaza pretekov
    try:
        with connection.cursor() as c:
            c.execute(
                """
                UPDATE races_drivers 
                SET time = %s
                WHERE driver_id = %s AND race_id = %s
                RETURNING driver_id
                """,
                [leader["time"], leader["id"], raceID],
            )

            c.fetchone()[0]
    except Exception as e:
        print(e)
        return HttpResponseNotFound()

    data = []
    for d in params["results"]["otherDrivers"]:
        data.append([gap_to_time(leader["time"], d["time"]), raceID, d["id"]])
    try:
        with connection.cursor() as c:
            c.executemany(
                """
                UPDATE races_drivers
                SET time = %s
                WHERE race_id = %s AND driver_id = %s
                """,
                data,
            )

        driver = RacesDrivers.objects.get(
            driver_id=params["results"]["fastestLap"], race_id=raceID
        )
        driver.has_fastest_lap = True
        driver.save()

        return HttpResponse(status=204)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getRaceResults(raceID: str):
    # doriesit preteky, ktore maju supisku ale nemaju este zapisane vysledky, kazdemu jebne vitazsvo

    c = connection.cursor()
    try:
        c.execute(
            """
                WITH time_penalties AS (
                    SELECT DISTINCT ON (driver_id) SUM(time) OVER (PARTITION BY driver_id) AS time, driver_id, report_id, race_id
                    FROM races AS r 
                    JOIN reports AS re ON r.id = re.race_id
                    JOIN penalties AS p ON p.report_id = re.id
                    WHERE r.id = %s
					ORDER BY driver_id
                ),
                result_times AS (
                    SELECT r.id AS race_id, d.id, d.name, rd.time + COALESCE(tp.time, 0) AS result_time, has_fastest_lap, t.name AS team_name, r.is_sprint
                    FROM races AS r
                    JOIN races_drivers AS rd ON r.id = rd.race_id
                    LEFT JOIN time_penalties AS tp ON tp.driver_id = rd.driver_id
                    JOIN drivers AS d ON d.id = rd.driver_id
                    JOIN teams AS t ON t.id = rd.team_id
                    WHERE r.id = %s
                    ORDER BY result_time
                )

                SELECT id, name, result_time, ROW_NUMBER() OVER (PARTITION BY rt.race_id ORDER BY result_time ASC), has_fastest_lap, team_name, is_sprint
                FROM result_times AS rt
                ORDER BY result_time ASC
            """,
            [raceID, raceID],
        )

        # [0: driver_id, 1: driver_name, 2: result_time, 3: rank, 4: has_fastest_lap, 5: team_name, 6: is_sprint]
        drivers = c.fetchall()

        results = {"results": []}

        for d in drivers:
            results["results"].append(
                {
                    "driverID": str(d[0]),
                    "driverName": d[1],
                    "time": d[2],
                    "teamName": d[5],
                    "rank": d[3],
                    "hasFastestLap": d[4],
                    "isSprint": d[6],
                }
            )

        return HttpResponse(json.dumps(results), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
