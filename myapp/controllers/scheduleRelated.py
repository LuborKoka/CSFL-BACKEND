from django.http import HttpResponse, HttpResponseBadRequest
from django.db import connection
from ..models import Tracks, Teams, Drivers, Races, SeasonsDrivers
import json
from typing import TypedDict, List, Dict


class CreateSeasonParams(TypedDict):
    name: str


class SubmitTeamsDriversParams(TypedDict):
    teams: List[Dict[str, List[str]]]
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


def fetchAllTeamsDrivers(seasonID: str):
    try:
        teams = Teams.objects.all()
        drivers = Drivers.objects.all()
        signed = SeasonsDrivers.objects.filter(season_id=seasonID)

        data = {"teams": [], "drivers": []}

        for t in teams:
            team = {"id": str(t.id), "name": t.name, "signed": []}

            for s in signed:
                if s.team_id == t.id:
                    team["signed"].append(str(s.driver_id))
            data["teams"].append(team)

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


def postSchedule(params: PostScheduleParams, seasonID):
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
                    [row["timestamp"], row["trackID"], seasonID],
                )

                result["races"].append(str(c.fetchone()[0]))

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getSchedule(seasonID):
    try:
        schedule = Races.objects.filter(season_id=seasonID)
        result = {"races": []}

        for r in schedule:
            result["races"].append(
                {"id": str(r.id), "date": str(r.date), "trackID": str(r.track_id)}
            )

        return HttpResponse(json.dumps(result), status=200)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def deleteFromSchedule(raceID: str):
    try:
        Races.objects.get(id=raceID).delete()

        return HttpResponse(status=204)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
