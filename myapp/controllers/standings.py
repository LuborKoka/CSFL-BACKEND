from django.http import HttpResponse, HttpResponseBadRequest
from django.db import connection
from typing import List, TypedDict
import json
import base64


def getStandings(seasonID: str):
    try:
        with connection.cursor() as c:
            # pohar jazdcov
            c.execute(
                """
                    WITH results AS (
                        SELECT rd.driver_id, rd.race_id, RANK() OVER (PARTITION BY race_id ORDER BY time asc) AS rank
                        FROM races_drivers AS rd
                        JOIN races AS r ON rd.race_id = r.id
                        WHERE season_id = %s
                        ORDER BY r.date
                    ),
                    res_with_points AS (
                        SELECT d.id AS driver_id, d.name AS driver_name, sd.is_reserve, tr.flag, t.name AS team_name, rd.time, rd.has_fastest_lap, re.rank, r.date,
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
                            END +
                            CASE
                                WHEN rd.has_fastest_lap = TRUE AND re.rank <= 10 THEN 1
                                ELSE 0
                            END AS points, r.id AS race_id, tr.id AS track_id
                        FROM seasons_drivers AS sd
                        JOIN races AS r ON r.season_id = sd.season_id
                        JOIN tracks AS tr ON tr.id = r.track_id
                        JOIN drivers AS d ON d.id = sd.driver_id
                        LEFT JOIN races_drivers AS rd ON r.id = rd.race_id AND sd.driver_id = rd.driver_id
                        LEFT JOIN teams AS t ON rd.team_id = t.id
                        LEFT JOIN results AS re ON rd.driver_id = re.driver_id AND rd.race_id = re.race_id
                        WHERE sd.season_id = %s
                    )

                    SELECT *, SUM(points) OVER (PARTITION BY driver_name) AS points_total, COUNT(race_id) OVER (PARTITION BY driver_id) AS race_count
                    FROM res_with_points
                    ORDER BY points_total DESC, driver_name, date
                """,
                [seasonID, seasonID],
            )

            result = {"drivers": [], "races": [], "teams": []}

            # team_name a race_name by mali byt neskor nahradene ikonkou (tim mozno, race urcite)
            data = c.fetchall()
            raceCount = data[0][13]

            # [0: driver_id, 1: driver_name, 2: is_reserve, 3: flag, 4: team_name, 5: time, 6: has_fastest_lap,
            # 7: rank, 8: date, 9: points, 10: race_id, 11: track_id, 12: points_total, 13: race_count]

            for i in range(raceCount):
                result["races"].append(
                    {"id": str(data[i][10]), "trackID": str(data[i][11])}
                )  # bude nahradene svg obrazkom a uz aj by malo byt

            for i in range(len(data) // raceCount):
                driver = {
                    "driverID": str(data[i * raceCount][0]),
                    "driverName": data[i * raceCount][1],
                    "isReserve": data[i * raceCount][2],
                    "totalPoints": data[i * raceCount][12],
                    "races": [],
                }

                for ii in range(raceCount):
                    driver["races"].append(
                        {
                            "teamName": data[i * raceCount + ii][4],
                            "hasFastestLap": data[i * raceCount + ii][6],
                            "rank": data[i * raceCount + ii][7],
                            "points": data[i * raceCount + ii][9],
                        }
                    )

                result["drivers"].append(driver)

            # pohar konstrukterov
            c.execute(
                """
                    WITH ranks AS (
                        SELECT team_id, t.name, t.color, has_fastest_lap, RANK() OVER (PARTITION BY race_id ORDER BY time ASC)
                        FROM races_drivers AS rd
                        JOIN races AS r ON rd.race_id = r.id
                        JOIN teams AS t ON rd.team_id = t.id
                        WHERE r.season_id = '8e7881cb-4284-4af9-b5e4-66ea822a77e0'
                        ORDER BY date, time
                    ),
                    points AS (
                        SELECT *, 
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
                            END +
                            CASE
                                WHEN has_fastest_lap = TRUE AND rank <= 10 THEN 1
                                ELSE 0
                            END AS points
                        FROM ranks 
                    ),
                    team_points AS (
                        SELECT DISTINCT ON(team_id) *, SUM(points) OVER (PARTITION BY team_id)
                        FROM points
                    )
                    SELECT team_id, color, sum AS points, name, ROW_NUMBER() OVER (ORDER BY sum DESC) AS rank
                    FROM team_points
                    ORDER BY sum DESC

                """
            )
            teams = c.fetchall()

            # row: [0: team_id, 1: color, 2: points, 3: name, 4: rank]
            for t in teams:
                result["teams"].append(
                    {"id": str(t[0]), "color": t[1], "points": t[2], "name": t[3]}
                )

        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
