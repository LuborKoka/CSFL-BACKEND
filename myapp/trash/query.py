from django.db import connection


def insertRacesDrivers():
    with connection.cursor() as c:
        try:
            c.execute(
                """
                SELECT driver_id, league_id, team_id, d.name as driver, t.name as team 
                FROM leagues_drivers AS ld
                JOIN drivers as d ON ld.driver_id = d.id
                JOIN teams AS t ON ld.team_id = t.id
            """
            )

            data = c.fetchall()

            for row in data:
                raceData = [
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                    str(row[0]),
                    str(row[2]),
                ]
                c.execute(
                    """
                    INSERT INTO races_drivers(driver_id, race_id, team_id)
                    VALUES
                        (%s, 'ad944a7e-6abc-4da7-979c-7e728ef07182', %s),
                        (%s, '3a39e9ae-3d6d-4213-81a3-b6e908d7aad9', %s),
                        (%s, 'a59a6172-9969-481b-bebe-3325a4506111', %s),
                        (%s, '62188063-d192-4b67-b23c-62984e2093f5', %s),
                        (%s, '31f2276f-8b91-4934-93ec-38090587217d', %s),
                        (%s, 'a361a77b-7d07-462d-bb74-95a4aa8410b0', %s),
                        (%s, '0cac9339-7c64-4721-b47e-b6851b5fd805', %s),
                        (%s, 'dc7e1720-7291-4ef8-a45c-daab762e5486', %s),
                        (%s, 'd014fd0a-d068-4c90-9ab0-1d27b55f559c', %s),
                        (%s, 'b045d536-95d1-4d6f-ab69-8d884c5f1b78', %s),
                        (%s, 'acc63562-8e27-441c-a067-0e63fd081575', %s),
                        (%s, '76666658-b6fe-4af4-b918-6d66c77f5b3a', %s),
                        (%s, 'b61ebd16-aa21-43f9-952b-c917e0d4e2c4', %s),
                        (%s, '88550d62-e429-4ec7-9817-c112efa75e7c', %s),
                        (%s, '9fbdb23f-7183-4604-b64f-3a9d70344484', %s),
                        (%s, 'a6a8a31b-8d3c-4e6f-93a6-aaf18b01c0f1', %s),
                        (%s, '0f267d4b-c178-4d91-954d-56120ff05aa0', %s),
                        (%s, '3ab39292-b845-402e-a64c-c0aad7229dd2', %s),
                        (%s, '3f86fb46-6792-4387-9452-01b11ba9e675', %s),
                        (%s, '2fa962dc-6e95-4ede-86af-62ed295206d1', %s),
                        (%s, '6718f4b4-1186-42b1-b418-814efea2e9e5', %s),
                        (%s, 'a4c2849f-b6ed-4373-bdd0-9947c78e082b', %s),
                        (%s, 'c94f04dc-d17a-44b9-8876-9ceec83ad417', %s)
                """,
                    raceData,
                )
                print(raceData)
        except Exception as e:
            print(e)
