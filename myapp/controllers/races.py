from django.http import HttpResponse, HttpResponseBadRequest
from ..models import Races, RacesDrivers
import json


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
