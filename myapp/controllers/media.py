from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from ..models import Tracks
from .report import FILE_PATH
import os

print(FILE_PATH)


# potrebny rework na path namiesto track a team id, usetrim endpoint
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


def media(name: str, folder: str):
    delim = os.sep
    video_path = (
        FILE_PATH + delim + name if folder is None else FILE_PATH + delim + folder + delim + name
    )

    response = FileResponse(open(video_path, "rb"))
    response["Cache-Control"] = "public, max-age=31536000"
    return response
