from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.db import connection, transaction
from ..models import Races, RacesDrivers, SeasonsDrivers, Teams
import json
from typing import TypedDict, List
from .timeFormatting import gap_to_time, time_to_seconds, time_to_gap
import traceback


class Driver(TypedDict):
    teamID: str
    drivers: List[str]


class RaceDriversParams(TypedDict):
    teams: List[Driver]


class DriverResult(TypedDict):
    id: str
    time: str
    plusLaps: int


class Results(TypedDict):
    leader: DriverResult
    otherDrivers: List[DriverResult]
    fastestLap: str


class PostRaceResultsParams(TypedDict):
    results: Results


def getRaceDrivers(id: str):
    try:
        drivers = (
            RacesDrivers.objects.filter(race=id)
            .select_related("driver", "team")
            .order_by("team_id")
        )

        data = {"drivers": [], "raceName": ""}

        for d in drivers:
            data["drivers"].append(
                {
                    "id": str(d.driver.id),
                    "name": d.driver.name,
                    "teamName": d.team.name,
                    "logo": d.team.logo,
                }
            )

        race = Races.objects.select_related("track").get(id=id)

        data["raceName"] = race.track.race_name

        return HttpResponse(json.dumps(data), status=200)

    except Exception as e:
        print(e)

    return HttpResponseBadRequest()


def getEditRace(raceID: str):
    try:
        teams = Teams.objects.all().order_by("name")

        race = Races.objects.select_related("track").get(id=raceID)

        reservePilot = SeasonsDrivers.objects.filter(
            is_reserve=True, season_id=race.season.id
        ).select_related("driver")

    except Exception as e:
        print(e)
        print("no teams found")
        return HttpResponseServerError()

    # tuna su uz zapisani jazdci na velku cenu

    result = {"raceName": race.track.race_name, "date": str(race.date), "teams": []}

    try:
        drivers = RacesDrivers.objects.filter(race_id=raceID).select_related(
            "driver", "team"
        )

        reserve = []

        if len(drivers) > 0:
            season_drivers = SeasonsDrivers.objects.filter(
                season_id=race.season_id
            ).select_related("driver", "team")

            for t in teams:
                team_drivers = []

                for d in drivers:
                    if d.team.id == t.id:
                        team_drivers.append(str(d.driver.id))

                team = {
                    "teamID": str(t.id),
                    "teamName": t.name,
                    "drivers": [],
                    "color": t.color,
                    "allOptions": [],
                }

                for sd in season_drivers:
                    if sd.is_reserve or sd.team.id == t.id:
                        team["allOptions"].append(
                            {
                                "id": str(sd.driver.id),
                                "name": sd.driver.name,
                                "isReserve": sd.is_reserve,
                            }
                        )

                for d in team["allOptions"]:
                    if d["id"] in team_drivers:
                        team["drivers"].append(d)

                result["teams"].append(team)

            return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        traceback.print_exc()

    # ak neni su ziadni zapisani, fetchnem timove dvojice pre sezonu

    try:
        for rp in reservePilot:
            reserve.append(
                {"id": str(rp.driver.id), "name": rp.driver.name, "isReserve": True}
            )

        for t in teams:
            drivers = SeasonsDrivers.objects.filter(
                season_id=race.season_id, team_id=t.id
            ).select_related("driver")

            team = {
                "teamID": str(t.id),
                "teamName": t.name,
                "drivers": [],
                "color": t.color,
                "allOptions": [],
            }

            for d in drivers:
                team["drivers"].append(
                    {"id": str(d.driver.id), "name": d.driver.name, "isReserve": False}
                )
                team["allOptions"].append(
                    {"id": str(d.driver.id), "name": d.driver.name, "isReserve": False}
                )

            team["allOptions"].extend(reserve)

            result["teams"].append(team)

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postEditRaceDrivers(raceID: str, params: RaceDriversParams):
    if not areDriversUnique(params):
        return HttpResponseBadRequest(
            json.dumps({"error": "Jeden pilot nemôže jazdiť za dva tímy naraz"})
        )

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
        ).order_by('time', 'team__name')

        result = {"drivers": []}

        if len(drivers) > 0:
            leader_time = drivers[0].time

            if leader_time is not None:
                fl_driver = RacesDrivers.objects.select_related('driver').get(race_id = raceID, has_fastest_lap = True)
                result["fastestLap"] = {"driverID": str(fl_driver.driver.id), "driverName": fl_driver.driver.name}

            for d in drivers:
                result["drivers"].append(
                    {"id": str(d.driver.id), "name": d.driver.name, "color": d.team.color, "time": time_to_gap(leader_time, d.time)}
                )

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


# bude treba aj sprinty doriesit
@transaction.atomic
def postEditRaceResults(raceID: str, params: PostRaceResultsParams):
    """
    Saves race results for the specific raceID.

    Returns the appropriate http response.
    """
    # prepocet casu vitaza na sekundy
    leader = {
        "id": params["results"]["leader"]["id"],
        "time": time_to_seconds(params["results"]["leader"]["time"]),
    }

    # zapis vitaza pretekov
    c = connection.cursor()

    try:
         # premaze existujuce najrychlejsie kolo zavodu, pre pripad, ze sa znova zapisuju vysledky
        fl_driver = RacesDrivers.objects.get(race_id=raceID, has_fastest_lap = True)
        fl_driver.has_fastest_lap = False
        fl_driver.save()
    except RacesDrivers.DoesNotExist:
        pass

    try:
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
        data.append(
            [gap_to_time(leader["time"], d["time"]), d["plusLaps"], raceID, d["id"]]
        )
    try:
        c.executemany(
            """
            UPDATE races_drivers
            SET time = %s, plus_laps = %s
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
                    SELECT r.id AS race_id, d.id, d.name, rd.time + COALESCE(tp.time, 0) AS result_time, has_fastest_lap, t.name AS team_name, r.is_sprint, plus_laps, rd.is_dsq
                    FROM races AS r
                    JOIN races_drivers AS rd ON r.id = rd.race_id
                    LEFT JOIN time_penalties AS tp ON tp.driver_id = rd.driver_id
                    JOIN drivers AS d ON d.id = rd.driver_id
                    JOIN teams AS t ON t.id = rd.team_id
                    WHERE r.id = %s
                    ORDER BY result_time
                )

                SELECT id, name, result_time, ROW_NUMBER() OVER (PARTITION BY rt.race_id ORDER BY is_dsq ASC, result_time ASC), has_fastest_lap, team_name, is_sprint, plus_laps, is_dsq
                FROM result_times AS rt
                ORDER BY is_dsq ASC, result_time ASC
            """,
            [raceID, raceID],
        )

        # [0: driver_id, 1: driver_name, 2: result_time, 3: rank, 4: has_fastest_lap, 5: team_name, 6: is_sprint, 7: plus_laps, 8: is_dsq]
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
                    "plusLaps": d[7],
                    "isDSQ": d[8]
                }
            )

        return HttpResponse(json.dumps(results), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def areDriversUnique(params: RaceDriversParams) -> bool:
    all_drivers = []

    for team in params["teams"]:
        for driver in team["drivers"]:
            if driver in all_drivers:
                return False
            all_drivers.append(driver)

    return True
