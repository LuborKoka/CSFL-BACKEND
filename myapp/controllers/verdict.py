from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Prefetch
from django.db import connection
from ..models import Reports, ReportTargets, UsersRoles, Roles
from typing import TypedDict, List
import json
from ..discord.discordIntegration import notify_discord_on_report


class Penalty(TypedDict):
    driverID: str
    time: int
    penaltyPoints: int


class NewVerdict(TypedDict):
    content: str
    penalties: List[Penalty]


def getConcernedDrivers(reportID):
    try:
        drivers = ReportTargets.objects.filter(report_id=reportID).select_related(
            "report", "driver"
        )

        result = {"drivers": []}

        result["drivers"].append(
            {
                "id": str(drivers[0].report.from_driver.id),
                "name": drivers[0].report.from_driver.name,
            }
        )

        for d in drivers:
            result["drivers"].append({"id": str(d.driver.id), "name": d.driver.name})

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postVerdict(reportID: str, params: NewVerdict):
    try:
        report = Reports.objects.select_related('race').get(id=reportID)

        user_role = UsersRoles.objects.select_related('role').filter(role__name=f'{report.race.season.name}fia')

        if len(user_role) == 0:
            return HttpResponseForbidden(json.dumps({
                "error": "Prístup zamietnutý. Ak si prihlásený, už to neskúšaj."
            }))

        report.verdict = params["content"]
        report.save()

        if len(params["penalties"]) == 0:
            return HttpResponse(status=204)

        data = []

        for p in params["penalties"]:
            data.append((p["penaltyPoints"], p["time"], p["driverID"], reportID))

        with connection.cursor() as c:
            c.executemany(
                """
                    INSERT INTO penalties(penalty_points, time, driver_id, report_id)
                    VALUES (%s, %s, %s, %s)
                """,
                data,
            )

        return notify_discord_on_report(reportID, True)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getRaceReportsFIAVersion(raceID: str):
    try:
        reports = (
            Reports.objects.filter(race_id=raceID)
            .select_related("from_driver", "race")
            .prefetch_related(
                Prefetch(
                    "reporttargets_set",
                    queryset=ReportTargets.objects.select_related("driver"),
                )
            )
            .order_by("created_at")
        )

        result = {
            "reports": [],
            "raceName": reports[0].race.track.race_name,
        }

        rank = 1
        for r in reports:
            drivers = []

            for rt in r.reporttargets_set.all():
                drivers.append(
                    {
                        "driverID": "hra" if rt.driver == None else str(rt.driver.id),
                        "driverName": "Hra" if rt.driver == None else rt.driver.name,
                    }
                )

            if r.verdict == None:
                result["reports"].append(
                    {
                        "reportID": str(r.id),
                        "targets": drivers,
                        "rank": rank,
                        "fromDriver": {
                            "id": str(r.from_driver.id),
                            "name": r.from_driver.name,
                        },
                    }
                )

            rank += 1

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
