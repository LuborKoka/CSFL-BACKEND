from django.http import HttpResponse, HttpResponseBadRequest
from ..models import Tracks
import json


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
