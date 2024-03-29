V `standings.py` prva query pre poradie jazdcov

```sql
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
        WHERE season_id = (SELECT id FROM seasons WHERE name = %s)
        ORDER BY r.date
    ) AS results_with_pents
),
race_wins AS (
    SELECT COUNT(*) AS wins_count, driver_id
    FROM results
    WHERE rank = 1
    GROUP BY driver_id
),
res_with_points AS (
    SELECT d.id AS driver_id, d.name AS driver_name, sd.is_reserve, tr.flag, t.name AS team_name, rd.time, rd.has_fastest_lap, re.rank, r.date,
        CASE
            WHEN rd.time IS NULL OR re.is_dsq = TRUE THEN 0
            ELSE
                CASE
                    WHEN r.is_sprint = TRUE THEN 
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
        END AS points, r.id AS race_id, tr.id AS track_id, t.color, re.is_dsq, COALESCE(rw.wins_count, 0) AS wins_count
    FROM seasons_drivers AS sd
    JOIN races AS r ON r.season_id = sd.season_id
    JOIN tracks AS tr ON tr.id = r.track_id
    JOIN drivers AS d ON d.id = sd.driver_id
    LEFT JOIN races_drivers AS rd ON r.id = rd.race_id AND sd.driver_id = rd.driver_id
    LEFT JOIN teams AS t ON rd.team_id = t.id
    LEFT JOIN results AS re ON sd.driver_id = re.driver_id AND rd.race_id = re.race_id
    LEFT JOIN race_wins AS rw ON sd.driver_id = rw.driver_id
    WHERE sd.season_id = (SELECT id FROM seasons WHERE name = %s)
),
team_colors AS (
    SELECT driver_id, color
    FROM seasons_drivers AS sd
    LEFT JOIN teams AS t ON sd.team_id = t.id
    WHERE sd.season_id = (SELECT id FROM seasons WHERE name = %s)
),
avg_finish_position AS (
    SELECT DISTINCT ON (rwp.driver_id) AVG(rank) OVER (PARTITION BY rwp.driver_id), rwp.driver_id, sd.is_reserve
    FROM res_with_points AS rwp
    JOIN seasons_drivers AS sd ON sd.driver_id = rwp.driver_id
    ORDER BY driver_id
)
SELECT rwp.*, SUM(points) OVER (PARTITION BY driver_name) AS points_total, COUNT(race_id) OVER (PARTITION BY rwp.driver_id) AS race_count,
    NOW() > (rwp.date + INTERVAL '3 hours') AS has_been_raced, r.is_sprint, tc.color
FROM res_with_points AS rwp
JOIN races AS r ON rwp.race_id = r.id
JOIN team_colors AS tc ON rwp.driver_id = tc.driver_id
JOIN avg_finish_position AS avgfp ON avgfp.driver_id = rwp.driver_id
ORDER BY points_total DESC, wins_count DESC, avgfp.avg ASC, avgfp.is_reserve, driver_name, rwp.date, r.is_sprint DESC
```

Bude sem treba doplnit sprinty a penalizacie of FIA. Niekde do CTE results snad.  
Stlpec time by mal znamenat nasledovne:

> null -> DNS  
> 0 -> DNF  
> -N -> N kol pozadu  
> Predbezne. Bude to mierne jebat vypocet poradia a bodov, prinajhorsom si dorobim dalsi stlpec.

Druha query pre poradie v pohari konstrukterov

```sql
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
        WHERE r.season_id = (SELECT id FROM seasons WHERE name = %s)
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
SELECT t.id, t.color, COALESCE(sum, 0) AS points , t.name, ROW_NUMBER() OVER (ORDER BY sum DESC) AS rank, t.icon
FROM team_points
FULL JOIN teams AS t ON t.id = team_id
ORDER BY sum DESC, t.name
```

Mozno do buducna by bolo fajn vypocitat do poradia aj pocet vitazstiev, keby nahodou

Query pre trestne body:

```sql
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
WHERE sd.season_id = (SELECT id FROM seasons WHERE name = %s)
ORDER BY t.name, d.id, r.date
```

V `races.py` getRaceResults:

```sql
WITH time_penalties AS (
	SELECT time, driver_id, report_id, race_id
	FROM races AS r
	JOIN reports AS re ON r.id = re.race_id
	JOIN penalties AS p ON p.report_id = re.id
	WHERE r.id = %s
),
result_times AS (
	SELECT r.id AS race_id, d.id, d.name, rd.time + COALESCE(tp.time, 0) AS result_time, has_fastest_lap, t.name AS team_name
	FROM races AS r
	JOIN races_drivers AS rd ON r.id = rd.race_id
	LEFT JOIN time_penalties AS tp ON tp.driver_id = rd.driver_id
	JOIN drivers AS d ON d.id = rd.driver_id
	JOIN teams AS t ON t.id = rd.team_id
	WHERE r.id = %s
	ORDER BY result_time
)

SELECT id, name, result_time, RANK() OVER (PARTITION BY rt.race_id ORDER BY result_time ASC), has_fastest_lap, team_name
FROM result_times AS rt
ORDER BY result_time ASC
```

# Sprinty

Uz vyriesene presne tak, ako je popisane
Je moznost odstranit tabulku sprints. Do races_drivers pridat stlpec is_sprint, tym padom by kazdy sprint
bol povazovany za samostatne preteky, len s inym bodovanim. Treba potom doriesit zobrazovanie a reporty k tomu.
