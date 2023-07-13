from django.http import HttpResponse, HttpResponseBadRequest
from typing import ItemsView
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from manage import PATH
from django.db import connection
from typing import TypedDict, List
import json

FILE_PATH = os.path.join(PATH, "media\\")
FILE_PATH_DELIM = "++"


class FormData(TypedDict):
    race: str
    targets: List[str]
    inchident: str
    from_driver: str


def reportUpload(files: ItemsView[str, InMemoryUploadedFile], form: FormData):
    form = json.loads(form)
    video_paths = []

    for name, file in files:
        video_paths.append(FILE_PATH + name + ".mp4")
        with open(FILE_PATH + name + ".mp4", "wb") as dst:
            for chunk in file.chunks():
                dst.write(chunk)

    report = [
        form["inchident"],
        FILE_PATH_DELIM.join(video_paths),
        form["from_driver"],
        form["race"],
    ]

    try:
        with connection.cursor() as c:
            c.execute(
                """
                INSERT INTO reports(content, video_path, from_driver, race_id)
                VALUES (%s, %s, (SELECT driver_id FROM users WHERE id = %s), %s)
                RETURNING id
            """,
                report,
            )

            id = c.fetchone()[0]

            for t in form["targets"]:
                data = [t, id]
                c.execute(
                    """
                    INSERT INTO report_targets (driver_id, report_id)
                    VALUES (%s, %s)
                """,
                    data,
                )

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()

    return HttpResponse(status=200)
