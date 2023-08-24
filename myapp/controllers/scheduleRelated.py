from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection
from ..models import Tracks, Teams, Drivers, Races, SeasonsDrivers, Seasons
import json, pytz, traceback
from typing import TypedDict, List, Dict
from datetime import datetime
from ..controllers.uuid import is_valid_uuid


class CreateSeasonParams(TypedDict):
    name: str


class SubmitTeamsDriversParams(TypedDict):
    teams: List[Dict[str, List[str]]]
    # teams: {
    # teamID: string,
    # drivers: string[]
    # }[]


class Race(TypedDict):
    trackID: str
    timestamp: str
    hasSprint: bool


class PostScheduleParams(TypedDict):
    races: List[Race]
    seasonID: str
    # races: {
    #    trackID: string,
    #    timestamp: string
    # }[]


class PatchRaceParams(TypedDict):
    trackID: str
    date: str


def getAllAvailableTracks():
    try:
        # pristup k riadkom: tracks[index]["fieldname"]
        tracks = Tracks.objects.all()
        data = {"tracks": []}

        for track in tracks:
            data["tracks"].append({"id": str(track.id), "name": track.race_name})

        return HttpResponse(json.dumps(data), status=200)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


# momentalne nepouzivane, prenechane len pre pripad
def fetchAllTeamsDrivers(seasonID: str):
    try:
        teams = Teams.objects.all()
        drivers = Drivers.objects.all()
        signed = SeasonsDrivers.objects.filter(season_id=seasonID)

        data = {"teams": [], "drivers": []}

        for t in teams:
            team = {"id": str(t.id), "name": t.name, "signed": [], "color": t.color}

            for s in signed:
                if s.team_id == t.id:
                    team["signed"].append(
                        {"id": str(s.driver.id), "name": s.driver.name}
                    )
            data["teams"].append(team)

        for d in drivers:
            data["drivers"].append({"id": str(d.id), "name": d.name})

        return HttpResponse(json.dumps(data), status=200)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


# momentalne nepouzivane, prenechane len pre pripad
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
    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def postSchedule(params: PostScheduleParams, seasonID):
    races = []
    sprints = []

    zone = pytz.timezone("Europe/Budapest")

    for row in params["races"]:
        races.append(
            [
                zone.localize(datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M")),
                row["trackID"],
                seasonID,
            ]
        )

        if row["hasSprint"]:
            sprints.append(
                [
                    zone.localize(
                        datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M")
                    ),
                    row["trackID"],
                    seasonID,
                ]
            )

    c = connection.cursor()

    try:
        c.executemany(
            """
                INSERT INTO races(date, track_id, season_id)
                VALUES(%s, %s, %s)
            """,
            races,
        )

        if len(sprints) > 0:
            c.executemany(
                """
                    INSERT INTO races(date, track_id, season_id, is_sprint)
                    VALUES(%s, %s, %s, true)
                """,
                sprints,
            )

        return HttpResponse(status=204)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def getSchedule(seasonID):
    if not is_valid_uuid(seasonID):
        return HttpResponseNotFound()

    try:
        schedule = (
            Races.objects.filter(season_id=seasonID)
            .select_related("track")
            .order_by("date", "-is_sprint")
        )

        season = Seasons.objects.get(id=seasonID)

        result = {"races": [], "seasonName": season.name}

        for r in schedule:
            result["races"].append(
                {
                    "id": str(r.id),
                    "date": str(r.date),
                    "raceName": r.track.race_name,
                    "trackID": str(r.track.id),
                    "isSprint": r.is_sprint,
                    "image": r.track.image,
                }
            )

        return HttpResponse(json.dumps(result), status=200)
    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def deleteSchedule(seasonID: str):
    try:
        Seasons.objects.get(id=seasonID).delete()

        return HttpResponse(status=204)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def deleteFromSchedule(raceID: str, seasonID: str):
    try:
        Races.objects.get(id=raceID, season_id=seasonID).delete()

        return HttpResponse(status=204)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def patchInSchedule(raceID: str, seasonID: str, params: PatchRaceParams):
    try:
        track = Tracks.objects.get(id=params["trackID"])
        race = Races.objects.get(id=raceID, season_id=seasonID)
        race.track = track
        race.date = params["date"]
        race.save()

        return HttpResponse(status=204)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()
