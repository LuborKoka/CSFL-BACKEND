from django.http import HttpResponse, HttpResponseBadRequest
from django.db import connection
from typing import List, TypedDict
import json


def getStandings(seasonID: str):
    # treba pridat penalizacie
    # pridane

    try:
        with connection.cursor() as c:
            # pohar jazdcov
            c.execute(
                """ 
                    WITH total_pents AS (
                        SELECT DISTINCT ON(pents.driver_id, pents.race_id) driver_id, race_id, SUM(time) OVER (PARTITION BY driver_id, race_id)
                            FROM (
                                SELECT *
                                FROM penalties AS p
                                JOIN reports AS r ON p.report_id = r.id
                            ) AS pents
                            ORDER BY driver_id, race_id
                    ),
                    results AS (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY race_id ORDER BY is_dsq ASC, time ASC) AS rank
                        FROM (
                            SELECT rd.driver_id, rd.race_id, rd.time + COALESCE(tp.sum, 0) AS time, r.is_sprint, rd.is_dsq
                            FROM races_drivers AS rd
                            JOIN races AS r ON rd.race_id = r.id
                            LEFT JOIN total_pents AS tp ON tp.race_id = rd.race_id AND rd.driver_id = tp.driver_id
                            WHERE season_id = %s
                            ORDER BY r.date
                        ) AS results_with_pents
                    ),
                    res_with_points AS (
                        SELECT d.id AS driver_id, d.name AS driver_name, sd.is_reserve, tr.flag, t.name AS team_name, rd.time, rd.has_fastest_lap, re.rank, r.date,
                            CASE
                                WHEN rd.time IS NULL OR re.is_dsq = TRUE THEN 0
                                ELSE
                                    CASE
                                        WHEN r.is_sprint = TRUE   THEN 
                                            CASE
                                                WHEN re.rank = 1 THEN 8
                                                WHEN re.rank = 2 THEN 7
                                                WHEN re.rank = 3 THEN 6
                                                WHEN re.rank = 4 THEN 5
                                                WHEN re.rank = 5 THEN 4
                                                WHEN re.rank = 6 THEN 3
                                                WHEN re.rank = 7 THEN 2
                                                WHEN re.rank = 8 THEN 1
                                                ELSE 0
                                            END
                                        ELSE 
                                            CASE
                                                WHEN re.rank = 1 THEN 25
                                                WHEN re.rank = 2 THEN 18
                                                WHEN re.rank = 3 THEN 15
                                                WHEN re.rank = 4 THEN 12
                                                WHEN re.rank = 5 THEN 10
                                                WHEN re.rank = 6 THEN 8
                                                WHEN re.rank = 7 THEN 6
                                                WHEN re.rank = 8 THEN 4
                                                WHEN re.rank = 9 THEN 2
                                                WHEN re.rank = 10 THEN 1
                                                ELSE 0
                                            END
                                    END +
                                    CASE
                                        WHEN rd.has_fastest_lap = TRUE AND re.rank <= 10 AND r.is_sprint = FALSE THEN 1
                                        ELSE 0
                                    END
                            END AS points, r.id AS race_id, tr.id AS track_id, t.color, re.is_dsq
                        FROM seasons_drivers AS sd
                        JOIN races AS r ON r.season_id = sd.season_id
                        JOIN tracks AS tr ON tr.id = r.track_id
                        JOIN drivers AS d ON d.id = sd.driver_id
                        LEFT JOIN races_drivers AS rd ON r.id = rd.race_id AND sd.driver_id = rd.driver_id
                        LEFT JOIN teams AS t ON rd.team_id = t.id
                        LEFT JOIN results AS re ON rd.driver_id = re.driver_id AND rd.race_id = re.race_id
                        WHERE sd.season_id = %s
                    )


                    SELECT rwp.*, SUM(points) OVER (PARTITION BY driver_name) AS points_total, COUNT(race_id) OVER (PARTITION BY driver_id) AS race_count,
                        NOW() > (rwp.date + INTERVAL '3 hours') AS has_been_raced, r.is_sprint
                    FROM res_with_points AS rwp
                    JOIN races AS r ON rwp.race_id = r.id
                    ORDER BY points_total DESC, driver_name, rwp.date, r.is_sprint DESC
                """,
                [seasonID, seasonID],
            )

            result = {"drivers": [], "races": [], "teams": [], "penaltyPoints": []}

            # team_name a race_name by mali byt neskor nahradene ikonkou (tim mozno, race urcite)
            data = c.fetchall()

            if len(data) == 0:
                return HttpResponse(status=204)

            raceCount = data[0][15]

            # [0: driver_id, 1: driver_name, 2: is_reserve, 3: flag, 4: team_name, 5: time, 6: has_fastest_lap, 7: rank,
            # 8: date, 9: points, 10: race_id, 11: track_id, 12: color, 13: is_dsq, 14: points_total, 15: race_count, 16: has_been_raced, 17: is_sprint]

            for i in range(raceCount):
                result["races"].append(
                    {
                        "id": str(data[i][10]),
                        "trackID": str(data[i][11]),
                        "flag": data[i][3],
                    }
                )  # bude nahradene svg obrazkom a uz aj by malo byt

            for i in range(len(data) // raceCount):
                driver = {
                    "driverID": str(data[i * raceCount][0]),
                    "driverName": data[i * raceCount][1],
                    "isReserve": data[i * raceCount][2],
                    "totalPoints": data[i * raceCount][14],
                    "color": data[i * raceCount][12],
                    "races": [],
                }

                for ii in range(raceCount):
                    driver["races"].append(
                        {
                            "teamName": data[i * raceCount + ii][4],
                            "hasFastestLap": data[i * raceCount + ii][6],
                            "rank": 'DSQ' if data[i * raceCount + ii][13] else getDnsDnfRank(
                                data[i * raceCount + ii][2],
                                data[i * raceCount + ii][5],
                                data[i * raceCount + ii][4],
                                data[i * raceCount + ii][7],
                            ),
                            "points": data[i * raceCount + ii][9],
                            "hasBeenRaced": data[i * raceCount + ii][16],
                        }
                    )

                result["drivers"].append(driver)

            # pohar konstrukterov
            c.execute(
                """
                    WITH total_pents AS (
                        SELECT DISTINCT ON(pents.driver_id, pents.race_id) driver_id, race_id, SUM(time) OVER (PARTITION BY driver_id, race_id)
                            FROM (
                                SELECT *
                                FROM penalties AS p
                                JOIN reports AS r ON p.report_id = r.id
                            ) AS pents
                            ORDER BY driver_id, race_id
                    ),
                    ranks AS (
                        SELECT team_id, name, color, has_fastest_lap, RANK() OVER (PARTITION BY race_id ORDER BY is_dsq ASC, time ASC), race_id, is_sprint, time, icon, is_dsq
                        FROM (
                            SELECT team_id, t.name, t.color, has_fastest_lap, rd.time + COALESCE(tp.sum, 0) AS time, rd.race_id, r.is_sprint, icon, rd.is_dsq
                            FROM races_drivers AS rd
                            JOIN races AS r ON rd.race_id = r.id
                            JOIN teams AS t ON rd.team_id = t.id
                            LEFT JOIN total_pents AS tp ON rd.driver_id = tp.driver_id AND rd.race_id = tp.race_id
                            WHERE r.season_id = %s
                            ORDER BY date, time
                        ) ranks_with_pents
                    ),
                    points AS (
                        SELECT *,
                            CASE
                                WHEN time IS NULL OR is_dsq = TRUE THEN 0
                                ELSE
                                    CASE
                                        WHEN is_sprint = TRUE THEN 
                                            CASE
                                                WHEN rank = 1 THEN 8
                                                WHEN rank = 2 THEN 7
                                                WHEN rank = 3 THEN 6
                                                WHEN rank = 4 THEN 5
                                                WHEN rank = 5 THEN 4
                                                WHEN rank = 6 THEN 3
                                                WHEN rank = 7 THEN 2
                                                WHEN rank = 8 THEN 1
                                                ELSE 0
                                            END
                                        ELSE 
                                            CASE
                                                WHEN rank = 1 THEN 25
                                                WHEN rank = 2 THEN 18
                                                WHEN rank = 3 THEN 15
                                                WHEN rank = 4 THEN 12
                                                WHEN rank = 5 THEN 10
                                                WHEN rank = 6 THEN 8
                                                WHEN rank = 7 THEN 6
                                                WHEN rank = 8 THEN 4
                                                WHEN rank = 9 THEN 2
                                                WHEN rank = 10 THEN 1
                                                ELSE 0
                                            END
                                    END +
                                    CASE
                                        WHEN has_fastest_lap = TRUE AND rank <= 10 AND is_sprint = FALSE THEN 1
                                        ELSE 0
                                    END
                            END AS points
                        FROM ranks
                    ),
                    team_points AS (
                        SELECT DISTINCT ON(team_id) *, SUM(points) OVER (PARTITION BY team_id)
                        FROM points
                    )
                    SELECT team_id, color, sum AS points, name, ROW_NUMBER() OVER (ORDER BY sum DESC) AS rank, icon
                    FROM team_points
                    ORDER BY sum DESC
                """,
                [seasonID],
            )
            teams = c.fetchall()

            # row: [0: team_id, 1: color, 2: points, 3: name, 4: rank, 5: icon]
            for t in teams:
                result["teams"].append(
                    {
                        "id": str(t[0]),
                        "color": t[1],
                        "points": t[2],
                        "name": t[3],
                        "icon": t[5],
                    }
                )

            # trestne body

            c.execute(
                """
                    WITH penalty_points AS (
                        SELECT  driver_id, r.race_id, report_id, points
                        FROM (
                            SELECT penalty_points, p.driver_id, r.race_id, report_id, SUM(penalty_points) OVER (PARTITION BY r.race_id, driver_id) AS points,
								ROW_NUMBER() OVER (PARTITION BY r.race_id, driver_id) AS rank
                            FROM penalties AS p
                            JOIN reports AS r ON r.id = p.report_id
                            JOIN drivers AS d ON d.id = p.driver_id
                            WHERE penalty_points > 0
                        ) AS p
                        JOIN reports AS r ON r.id = p.report_id
						WHERE p.rank = 1
                        ORDER BY driver_id
                    )

                    SELECT d.id, d.name, points, COALESCE(SUM(points) OVER (PARTITION BY d.id), 0) AS points_total, t.icon
                    FROM seasons_drivers AS sd
                    JOIN races AS r ON r.season_id = sd.season_id
                    JOIN tracks AS tr ON tr.id = r.track_id
                    JOIN drivers AS d ON d.id = sd.driver_id
                    LEFT JOIN races_drivers AS rd ON r.id = rd.race_id AND sd.driver_id = rd.driver_id
                    LEFT JOIN penalty_points AS p ON sd.driver_id = p.driver_id AND r.id = p.race_id
                    LEFT JOIN teams AS t ON sd.team_id = t.id
                    WHERE sd.season_id = %s
                    ORDER BY d.id, r.date
                """,
                [seasonID],
            )

            # [0: driver_id, 1: driver_name, 2: points, 3: points_total, 4: team_icon]

            penData = c.fetchall()

            for i in range(len(penData) // raceCount):
                penDriver = {
                    "id": str(penData[i * raceCount][0]),
                    "name": penData[i * raceCount][1],
                    "totalPoints": int(penData[i * raceCount][3]),
                    "teamIcon": penData[i * raceCount][4],
                    "races": [],
                }

                for ii in range(raceCount):
                    penDriver["races"].append(
                        0
                        if penData[i * raceCount + ii][2] == None
                        else int(penData[i * raceCount + ii][2])
                    )

                result["penaltyPoints"].append(penDriver)

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()


def getDnsDnfRank(isReserve: bool, time: float | None, teamName: str | None, rank: int):
    """
    A function to determine the displayed rank of a driver in the standings table. 

    Returns:

        if is reserve and did not race then ''

        if is not reserve and did not race then 'DNS'

        if didnt finish then 'DNS'

        else returns finish position
    """

    if isReserve and teamName == None:
        return ""

    if teamName == None:
        return "DNS"

    if time == None:
        return "DNF"

    return rank
