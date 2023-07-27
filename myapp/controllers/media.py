from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from ..models import Tracks
from .report import FILE_PATH


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


def media(name: str):
    video_path = FILE_PATH + name  # Replace with the actual video path

    response = FileResponse(open(video_path, "rb"))
    response["Cache-Control"] = "public, max-age=259200"
    return response
