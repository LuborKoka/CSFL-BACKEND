from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
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
        drivers = (
            RacesDrivers.objects.filter(race=id)
            .select_related("driver")
            .values("driver", "driver__name")
        )

        data = {"drivers": []}

        for d in drivers:
            data["drivers"].append({"id": str(d["driver"]), "name": d["driver__name"]})

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)

    return HttpResponseBadRequest()


def getEditRace(raceID: str):
    try:
        race = Races.objects.select_related("track").get(id=raceID)

        teams = Teams.objects.all()

        reservePilot = SeasonsDrivers.objects.filter(is_reserve=True).select_related(
            "driver"
        )

        altTeams = []

        reserve = []

        for rp in reservePilot:
            reserve.append({"id": str(rp.driver.id), "name": rp.driver.name})

        for t in teams:
            drivers = SeasonsDrivers.objects.filter(
                season_id=race.season_id, team_id=t.id
            ).select_related("driver")

            team = {"teamID": str(t.id), "teamName": t.name, "drivers": []}

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


# bude treba aj sprinty doriesit pravdepodobne
def postEditRaceResults(raceID: str, params: PostRaceResultsParams):
    leader = {
        "id": params["results"]["leader"]["id"],
        "time": time_to_seconds(params["results"]["leader"]["time"]),
    }
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

        1
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

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getRaceResults(raceID: str):
    try:
        drivers = (
            RacesDrivers.objects.filter(race_id=raceID)
            .select_related("driver", "team")
            .order_by("time")
        )

        results = {"results": []}

        rank = 1
        for d in drivers:
            results["results"].append(
                {
                    "driverID": str(d.driver.id),
                    "driverName": d.driver.name,
                    "time": d.time,
                    "teamName": d.team.name,
                    "rank": rank,
                }
            )
            rank += 1

        return HttpResponse(json.dumps(results), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
