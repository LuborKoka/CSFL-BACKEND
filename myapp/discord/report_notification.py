from django.db import connection
from ..models import ReportTargets
import traceback, requests, os, json
from datetime import datetime
from django.http import HttpResponse, HttpResponseServerError

def notify(reportID: str, isDecision: bool):
    webhook_url = os.environ.get('CSFL_FIA_WEBHOOK_URL') if isDecision else os.environ.get('CSFL_REPORT_WEBHOOK_URL')

    c = connection.cursor()

    try:
        c.execute("""
            WITH report_rank AS (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY race_id ORDER BY created_at ASC) AS rank
                FROM reports
                WHERE race_id = (SELECT race_id FROM reports WHERE id = %s)
            )

            SELECT re.created_at, d.name, t.race_name, rr.rank, r.season_id, r.id, da.discord_id, t.emoji
                FROM reports AS re
                JOIN races AS r ON re.race_id = r.id
                JOIN tracks AS t ON r.track_id = t.id
                JOIN drivers AS d ON re.from_driver = d.id
                JOIN users AS u ON d.id = u.driver_id
                LEFT JOIN discord_accounts AS da ON u.id = da.user_id
                JOIN report_rank AS rr ON re.id = rr.id
                WHERE re.id = %s
        """, [reportID, reportID])

        report_data = c.fetchall()[0]

        content = formatContent(reportID, report_data, isDecision)

        message = {
            "content": content,
            "username": 'FIA' if isDecision else report_data[1]
        }

        response = requests.post(webhook_url, json=message)
        response.raise_for_status()

        return HttpResponse(status=204)

        # for attr_name in dir(response):
        #     attr_value = getattr(response, attr_name)
        #     print(f"{attr_name}: {attr_value}")

    
    except Exception:
        traceback.print_exc()
        if isDecision:
            return HttpResponseServerError(json.dumps({
                "error": "Rozhodnutie sme úspešne zaznamenali, ale nepodarilo sa tagnúť dotknuté osoby na Discorde."
            }))

        return HttpResponseServerError(json.dumps({
            "error": "Report sme úspešne zaznamenali, ale nepodarilo sa tagnúť dotknuté osoby na Discorde."
        }))


def formatContent(reportID: str, report_data, isDecision: bool):
    if not isDecision:
        date = datetime.fromtimestamp(report_data[0].timestamp())

        return f"""
## {report_data[7]} {report_data[2]}, Report #{report_data[3]}
*{date.strftime('%d.%m.%y %H:%M:%S')}*

Na koho: 
{tagReportTargets(reportID)}

Viac info [na tomto odkaze](http://192.168.100.22:3000/seasons/{report_data[4]}/race/{report_data[5]}/reports)
        """ 
    
    reporting_driver_name = f'<@{report_data[6]}>' if report_data[6] is not None else report_data[1]

    return f"""   
## {report_data[7]} {report_data[2]}, Report #{report_data[3]}

### Pridané rozhodnutie

Účastníci:
    - {reporting_driver_name}
{tagReportTargets(reportID)}

Viac info [na tomto odkaze](http://192.168.100.22:3000/seasons/{report_data[4]}/race/{report_data[5]}/reports)
    """



def tagReportTargets(reportID: str):
    try:
        report_targets = ReportTargets.objects.select_related(
            'driver',
            'driver__users',
            'driver__users__discord_account'
        ).filter(report_id=reportID)

        result = []

        for t in report_targets:
            if t.driver is None:
                result.append("- Hra")
                continue

            driver_name = t.driver.name
            user_discord_account = t.driver.users.discord_account if (hasattr(t.driver, 'users') and t.driver.users.discord_account) else None

            if user_discord_account:
                result.append(f"- <@{user_discord_account.discord_id}>")
            else:
                result.append(f"- {driver_name}")

        return '\n'.join(result)  
    
    except Exception:
        traceback.print_exc()
        return '- je to dojebkane'