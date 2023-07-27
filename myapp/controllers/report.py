from django.http import HttpResponse, HttpResponseBadRequest
from typing import ItemsView
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from manage import PATH
from django.db import connection
from django.db.models import Prefetch
from typing import TypedDict, List
import json
from ..models import Reports, ReportTargets, ReportResponses, Penalties
from urllib.parse import urlparse, parse_qs
import imghdr
import os

FILE_PATH = os.path.join(PATH, "media\\")
FILE_PATH_DELIM = "++"


class FormData(TypedDict):
    targets: List[str]
    inchident: str
    from_driver: str
    video: List[str]


class ReportResponse(TypedDict):
    inchident: str
    from_driver: str
    video: List[str]


def reportUpload(
    files: ItemsView[str, InMemoryUploadedFile], form: FormData, raceID: str
):
    # if datum neni medzi zaciatkom koncom,

    form = json.loads(form)
    video_paths = []

    report = [
        form["inchident"],
        form["from_driver"],
        raceID,
    ]
    # kto, popis a race id, videa hned za tym
    try:
        with connection.cursor() as c:
            c.execute(
                """
                INSERT INTO reports(content, from_driver, race_id)
                VALUES (%s, (SELECT driver_id FROM users WHERE id = %s), %s)
                RETURNING id
            """,
                report,
            )

            id = c.fetchone()[0]

            for t in form["targets"]:
                data = [None if t == "hra" else t, id]
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

    for v in form["video"]:
        video_paths.append(v)

    for name, file in files:
        video_paths.append(FILE_PATH + str(id) + name)
        with open(FILE_PATH + str(id) + name, "wb") as dst:
            for chunk in file.chunks():
                dst.write(chunk)

    try:
        report = Reports.objects.get(id=id)
        report.video_path = FILE_PATH_DELIM.join(video_paths)
        report.save()

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getReports(raceID: str):
    result = {"reports": []}
    try:
        reports = (
            Reports.objects.filter(race_id=raceID)
            .select_related("from_driver")
            .prefetch_related(
                Prefetch(
                    "reportresponses_set",
                    queryset=ReportResponses.objects.select_related("from_driver"),
                )
            )
            .order_by("created_at")
        )
        rank = 1
        for r in reports:
            videos = processMediaPath(r.video_path)

            responses = []

            penalties = []

            pents = Penalties.objects.filter(report_id=r.id).select_related("driver")

            for p in pents:
                penalties.append(
                    {
                        "driverID": str(p.driver.id),
                        "driverName": p.driver.name,
                        "time": p.time,
                        "penaltyPoints": p.penalty_points,
                    }
                )

            for re in r.reportresponses_set.all():
                responses.append(
                    {
                        "id": str(re.id),
                        "videos": processMediaPath(re.video_path),
                        "content": re.content,
                        "createdAt": str(re.created_at),
                        "driverID": str(re.from_driver.id),
                        "driverName": re.from_driver.name,
                    }
                )

            target_drivers = ReportTargets.objects.filter(
                report_id=r.id
            ).select_related("driver")

            targets = []

            for t in target_drivers:
                targets.append(
                    {
                        "id": "hra" if t.driver == None else str(t.driver.id),
                        "name": "Hra" if t.driver == None else t.driver.name,
                    }
                )

            result["reports"].append(
                {
                    "reportID": str(r.id),
                    "from": {
                        "id": str(r.from_driver.id),
                        "name": str(r.from_driver.name),
                    },
                    "content": r.content,
                    "videos": videos,
                    "targets": targets,
                    "createdAt": str(r.created_at),
                    "responses": responses,
                    "verdict": r.verdict,
                    "penalties": penalties,
                    "rank": rank,
                }
            )
            rank += 1

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def postReportResponse(
    files: ItemsView[str, InMemoryUploadedFile], reportID: str, form: ReportResponse
):
    data = [form["from_driver"], form["inchident"], reportID]
    c = connection.cursor()
    try:
        c.execute(
            """
                INSERT INTO report_responses(from_driver, content, report_id)
                VALUES ((SELECT driver_id FROM users WHERE id = %s), %s, %s)
                RETURNING id
            """,
            data,
        )

        id = c.fetchone()[0]

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()

    video_path = []

    for v in form["video"]:
        video_path.append(v)

    for name, file in files:
        video_path.append(FILE_PATH + str(id) + name)
        with open(FILE_PATH + str(id) + name, "wb") as dst:
            for chunk in file.chunks():
                dst.write(chunk)

    try:
        res = ReportResponses.objects.get(id=id)
        res.video_path = FILE_PATH_DELIM.join(video_path)
        res.save()

        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def processMediaPath(video_string: str):
    paths = video_string.split(FILE_PATH_DELIM)

    videos = {"local": [], "online": []}

    for p in paths:
        if PATH in p:
            if not os.path.isfile(
                p
            ):  # ked neexistuje file, dam to ako image a zobrazi sa alt file not found hotovo
                videos["local"].append(
                    {"isImage": True, "url": p.replace(FILE_PATH, "")}
                )
                continue

            if imghdr.what(p) is not None:
                videos["local"].append(
                    {"isImage": True, "url": p.replace(FILE_PATH, "")}
                )
                continue
            videos["local"].append({"isImage": False, "url": p.replace(FILE_PATH, "")})
        else:
            videos["online"].append(getEmbedUrl(p))

    return videos


from urllib.parse import urlparse, parse_qs


def getEmbedUrl(url: str):
    parsed_url = urlparse(url)

    if "youtube.com" in parsed_url.netloc:
        # Extract the video id from the 'v' query parameter.
        query = parse_qs(parsed_url.query)
        video_id = query.get("v")

        if video_id:
            # Return the embed link
            return {
                "url": f"https://www.youtube.com/embed/{video_id[0]}",
                "embed": True,
            }

    elif "youtu.be" in parsed_url.netloc:
        # Extract the video id from the URL path.
        video_id = parsed_url.path.lstrip("/")
        if video_id:
            # Return the embed link
            return {"url": f"https://www.youtube.com/embed/{video_id}", "embed": True}

    elif "streamable.com" in parsed_url.netloc:
        video_id = parsed_url.path.lstrip("/")
        if video_id:
            return {"url": f"https://streamable.com/e/{video_id}", "embed": True}

    elif "medal.tv" in parsed_url.netloc:
        embeddable_url = url.replace("clips", "clip")
        return {"url": embeddable_url, "embed": True}

    elif "outplayed.tv" in parsed_url.netloc:
        return {"url": url, "embed": True}

    # If the video id was not found, return the original url
    return {"url": url, "embed": False}
