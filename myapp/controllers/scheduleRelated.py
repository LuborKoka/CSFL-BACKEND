from django.http import HttpResponse, HttpResponseBadRequest
from django.db import connection
from ..models import Tracks, Teams, Drivers
import json
from typing import TypedDict, List, Dict


class CreateSeasonParams(TypedDict):
    name: str


class SubmitTeamsDriversParams(TypedDict):
    teams: List[Dict[str, List[str]]]
    seasonID: str
    # teams: {
    # teamID: string,
    # drivers: string[]
    # }[]


class PostScheduleParams(TypedDict):
    races: List[Dict[str, str]]
    seasonID: str
    # races: {
    #    trackID: string,
    #    timestamp: string
    # }[]


def getAllAvailableTracks():
    try:
        # pristup k riadkom: tracks[index]["fieldname"]
        tracks = Tracks.objects.values("id", "name").all()
        data = {"tracks": []}

        for track in tracks:
            data["tracks"].append({"id": str(track["id"]), "name": track["name"]})

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


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


def fetchAllTeamsDrivers():
    try:
        teams = Teams.objects.all()
        drivers = Drivers.objects.all()

        data = {"teams": [], "drivers": []}

        for t in teams:
            data["teams"].append({"id": str(t.id), "name": t.name})

        for d in drivers:
            data["drivers"].append({"id": str(d.id), "name": d.name})

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def submitTeamsDrivers(data: SubmitTeamsDriversParams):
    for row in data["teams"]:
        print(row["drivers"])
    try:
        rows = []
        for row in data["teams"]:
            rows.append([row["drivers"][0], data["seasonID"], row["teamID"]])
            rows.append([row["drivers"][1], data["seasonID"], row["teamID"]])

        for a in rows:
            print(a)
        with connection.cursor() as c:
            c.executemany(
                """
                INSERT INTO seasons_drivers(driver_id, season_id, team_id)
                VALUES (%s, %s, %s)     
            """,
                rows,
            )

        return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postSchedule(params: PostScheduleParams):
    try:
        result = {"races": []}

        for row in params["races"]:
            with connection.cursor() as c:
                c.execute(
                    """
                    INSERT INTO races(date, track_id, season_id, name)
                    VALUES (%s, %s, %s, 'random name')
                    RETURNING id
                    """,
                    [row["timestamp"], row["trackID"], params["seasonID"]],
                )

                result["races"].append(str(c.fetchone()[0]))

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
