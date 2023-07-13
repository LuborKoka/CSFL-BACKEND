V `standings.py` prva query pre poradie jazdcov

```sql
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
```

Bude sem treba doplnit sprinty a penalizacie of FIA. Niekde do CTE results snad.  
Stlpec time by mal znamenat nasledovne:

> null -> DNS  
> 0 -> DNF  
> -N -> N kol pozadu  
> Predbezne. Bude to mierne jebat vypocet poradia a bodov, prinajhorsom si dorobim dalsi stlpec.

Druha query pre poradie v pohari konstrukterov

```sql
WITH ranks AS (
	SELECT team_id, t.name, t.color, has_fastest_lap, RANK() OVER (PARTITION BY race_id ORDER BY time ASC)
	FROM races_drivers AS rd
	JOIN races AS r ON rd.race_id = r.id
	JOIN teams AS t ON rd.team_id = t.id
	WHERE r.season_id = %s
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

```

Mozno do buducna by bolo fajn vypocitat do poradia aj pocet vitazstiev, keby nahodou
