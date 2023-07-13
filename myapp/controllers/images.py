from django.http import HttpResponse, HttpResponseBadRequest
from ..models import Races, Teams, Tracks


def raceImage(trackID: str):
    try:
        track = Tracks.objects.get(id=trackID)
        image = bytes(track.flag)

        response = HttpResponse(image, content_type="image/svg+xml")
        response["Cache-Control"] = "public, max-age=31536000"
        response["Content-Disposition"] = "inline"
        return response

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
