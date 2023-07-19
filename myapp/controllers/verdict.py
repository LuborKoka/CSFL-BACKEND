from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Prefetch
from django.db import connection
from ..models import Reports, ReportTargets
from typing import TypedDict, List
import json


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
        report = Reports.objects.get(id=reportID)
        report.verdict = params["content"]
        report.save()

        print(params["penalties"])

        if len(params["penalties"]) == 0:
            return HttpResponse(status=200)

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

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
