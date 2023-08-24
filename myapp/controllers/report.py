from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from typing import ItemsView
from django.core.files.uploadedfile import InMemoryUploadedFile
from manage import PATH
from django.db import connection, transaction
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
from typing import TypedDict, List
from ..models import Reports, ReportTargets, ReportResponses, Penalties, Races, RacesDrivers, Users
from urllib.parse import urlparse, parse_qs
import imghdr, os, json, traceback
from datetime import datetime, timedelta
from ..discord.discordIntegration import notify_discord_on_report
from uuid import UUID


FILE_PATH = os.path.join(PATH, "media")
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


@transaction.atomic
def reportUpload(
    files: ItemsView[str, InMemoryUploadedFile], form: FormData, raceID: str
):
    # if datum neni medzi zaciatkom koncom,
    race = Races.objects.get(id=raceID)

    form = json.loads(form)

    user = Users.objects.select_related('driver').get(id=form["from_driver"])
    is_allowed = allowReportPost(race.date, False, race.id, user.driver.id)

    if not is_allowed == True:
        return is_allowed
    
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

            report_id = c.fetchone()[0]

            for t in form["targets"]:
                data = [None if t == "hra" else t, report_id]
                c.execute(
                    """
                    INSERT INTO report_targets (driver_id, report_id)
                    VALUES (%s, %s)
                """,
                    data,
                )

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest(json.dumps({
            "error": "Niečo sa pokazilo. Skús report odoslať znova."
        }))

    for v in form["video"]:
        video_paths.append(v)

    for name, file in files:
        video_paths.append(FILE_PATH + "reports/" + str(id) + name)
        with open(FILE_PATH + "/reports/" + str(id) + name, "wb") as dst:
            for chunk in file.chunks():
                dst.write(chunk)

    try:
        report = Reports.objects.get(id=report_id)
        report.video_path = FILE_PATH_DELIM.join(video_paths)
        report.save()

        return notify_discord_on_report(report_id, False)

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest(json.dumps({
            "error": "Niečo sa pokazilo. Skús report odoslať znova."
        }))
    

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

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def postReportResponse(
    files: ItemsView[str, InMemoryUploadedFile], reportID: str, form: ReportResponse
):
    data = [form["from_driver"], form["inchident"], reportID]

    try:
        report = Reports.objects.select_related('race').get(id = reportID)
        user = Users.objects.select_related('driver').get(id=form["from_driver"])

    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    
    except Exception:
        traceback.print_exc()
        HttpResponseServerError()

    is_allowed = allowReportPost(report.race.date, True, reportID, user.driver.id)

    if not is_allowed == True:
        return is_allowed

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

        c.close()

    except Exception:
        c.close()
        traceback.print_exc()
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

    except Exception:
        traceback.print_exc()
        return HttpResponseBadRequest()


def processMediaPath(video_string: str):
    paths = video_string.split(FILE_PATH_DELIM)

    delim = os.sep

    videos = {"local": [], "online": []}

    for p in paths:
        if PATH in p:
            if not os.path.isfile(p):  
                # ked neexistuje file, dam to ako image a zobrazi sa alt file not found hotovo
                videos["local"].append(
                    {"isImage": True, "url": p.replace(FILE_PATH + delim, "")}
                )
                continue

            if imghdr.what(p) is not None:
                videos["local"].append(
                    {"isImage": True, "url": p.replace(FILE_PATH + delim, "")}
                )
                continue
            videos["local"].append({"isImage": False, "url": p.replace(FILE_PATH + delim, "")})
        else:
            videos["online"].append(getEmbedUrl(p))

    return videos



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



def allowReportPost(date: datetime, is_response: bool, subject_id: UUID | str, driver_id: UUID) -> bool | HttpResponseBadRequest | HttpResponseForbidden:
    """
    Params:
        date: race date
        is_response: is it a new report or a response to a report
        subject_id: if is_response then report_id else race_id
        driver_id: from driver (id)

    Returns:
        true if user is permitted or the appropriate http response.
    """
    
    endTime = (date + timedelta(days=1)).replace(hour=23, minute=59, second=59, tzinfo=None)
    now = datetime.now()

    try:
        did_participate = False
        id = Reports.objects.select_related('race').get(id=subject_id).race.id if is_response else subject_id
        drivers = RacesDrivers.objects.select_related('driver').filter(race_id=id)
        for d in drivers:
            if d.driver.id == driver_id:
                did_participate = True
                break

    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()
   
    if not did_participate:
        return HttpResponseForbidden(json.dumps({
            "error": "Nemáš dovolené sa tu vyjadriť. Už to neskúšaj."
        }))

    if now <= date.replace(tzinfo=None):
        return HttpResponseBadRequest(json.dumps({
            "error": "Ešte je na posielanie reportov skoro."
        }))

    if not is_response:
        if now > endTime:
            return HttpResponseForbidden(json.dumps({
                "error": "Čas na posielanie reportov už vypršal."
            }))
                
        return True      
    

    try:
        report = Reports.objects.get(id = subject_id)
        targets = ReportTargets.objects.filter(report_id=subject_id, driver_id=driver_id)
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()


    # ti, na ktorych je poslany
    for t in targets:
        if t.driver.id == driver_id and (now < (report.created_at + timedelta(days=1) ).replace(tzinfo=None) or now < endTime):
            return True
        
    if now < endTime:
        return True
    
    return HttpResponseForbidden(json.dumps({
        "error": "Čas na posielanie reportov už vypršal."
    }))