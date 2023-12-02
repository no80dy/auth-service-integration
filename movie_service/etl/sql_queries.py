sql_genres = """
    SELECT DISTINCT g.id, g.name, g.description
    FROM content.genre AS g
    RIGHT JOIN content.genre_film_work AS gfw ON gfw.genre_id = g.id
    WHERE g.modified > '{}';
"""


sql_persons = """
    WITH tmp AS (   
        SELECT pfw.person_id, pfw.film_work_id,
        ARRAY_AGG(DISTINCT pfw.role) AS roles
        FROM content.person_film_work AS pfw
        GROUP BY pfw.person_id, pfw.film_work_id
        )
    SELECT  p.id,
            p.full_name,
            json_agg(json_build_object('film_work_id',tmp.film_work_id,'roles',tmp.roles)) as films
    FROM tmp
    LEFT JOIN content.person AS p ON p.id = tmp.person_id
    WHERE p.modified > '{}'
    GROUP BY p.id, p.full_name;
"""
