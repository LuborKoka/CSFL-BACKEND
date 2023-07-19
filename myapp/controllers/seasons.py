from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Races, Seasons


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
        result = {"races": []}

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
