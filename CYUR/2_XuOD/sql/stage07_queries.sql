SET search_path TO bk_465029_2026;

-- ЗАПРОС 1 (обязательный): РАСПИСАНИЕ ТУРНИРА
-- «Какая команда, когда, где и с кем играет»
SELECT
    m.season                             AS "Сезон",
    m.matchday                           AS "Тур",
    m.match_date                         AS "Дата",
    m.match_time                         AS "Время",
    ht.team_name                         AS "Хозяева",
    at.team_name                         AS "Гости",
    v.stadium_name                       AS "Стадион",
    v.city                               AS "Город",
    (SELECT status_name FROM match_statuses WHERE status_id = m.status_id) AS "Статус"
FROM   matches      m
JOIN   teams        ht ON m.home_team_id = ht.team_id
JOIN   teams        at ON m.away_team_id = at.team_id
LEFT JOIN venues    v  ON m.venue_id     = v.venue_id
WHERE  m.season = 2023                   -- фильтр по сезону
ORDER BY m.matchday, m.match_date;


-- ЗАПРОС 2 (обязательный): ИТОГОВАЯ СВОДНАЯ ТАБЛИЦА ТУРНИРА
-- Турнирная таблица: очки, разница голов, место
WITH team_stats AS (
    SELECT
        t.team_name,
        COUNT(*) FILTER (WHERE mr.winner = 'home' AND m.home_team_id = t.team_id
                           OR   mr.winner = 'away' AND m.away_team_id = t.team_id)  AS wins,
        COUNT(*) FILTER (WHERE mr.winner = 'draw')                                   AS draws,
        COUNT(*) FILTER (WHERE mr.winner = 'away' AND m.home_team_id = t.team_id
                           OR   mr.winner = 'home' AND m.away_team_id = t.team_id)  AS losses,
        SUM(CASE WHEN m.home_team_id = t.team_id THEN mr.home_goals
                 ELSE mr.away_goals END)                                              AS goals_for,
        SUM(CASE WHEN m.home_team_id = t.team_id THEN mr.away_goals
                 ELSE mr.home_goals END)                                              AS goals_against
    FROM   teams   t
    JOIN   matches m  ON t.team_id = m.home_team_id
                      OR t.team_id = m.away_team_id
    JOIN   match_results mr ON m.match_id = mr.match_id
    WHERE  m.season = 2023
    GROUP BY t.team_name
)
SELECT
    ROW_NUMBER() OVER (ORDER BY wins*3 + draws DESC,
                                goals_for - goals_against DESC,
                                goals_for DESC)          AS "Место",
    team_name                                            AS "Команда",
    wins + draws + losses                                AS "И",
    wins                                                 AS "В",
    draws                                                AS "Н",
    losses                                               AS "П",
    goals_for                                            AS "ГЗ",
    goals_against                                        AS "ГП",
    goals_for - goals_against                            AS "РГ",
    wins * 3 + draws                                     AS "Очки"
FROM   team_stats
ORDER BY "Очки" DESC, "РГ" DESC, "ГЗ" DESC;


-- ЗАПРОС 3: РЕЗУЛЬТАТЫ ВСЕХ МАТЧЕЙ С ПОЛНЫМ СЧЁТОМ
SELECT
    m.season                                      AS "Сезон",
    m.matchday                                    AS "Тур",
    m.match_date                                  AS "Дата",
    ht.team_name                                  AS "Хозяева",
    CONCAT(mr.home_goals, ' : ', mr.away_goals)   AS "Счёт",
    CONCAT(mr.home_goals_ht,' : ',mr.away_goals_ht) AS "Счёт (1 тайм)",
    at.team_name                                  AS "Гости",
    CASE mr.winner
        WHEN 'home' THEN ht.team_name
        WHEN 'away' THEN at.team_name
        ELSE 'Ничья'
    END                                           AS "Победитель"
FROM   matches       m
JOIN   teams         ht ON m.home_team_id = ht.team_id
JOIN   teams         at ON m.away_team_id = at.team_id
JOIN   match_results mr ON m.match_id     = mr.match_id
ORDER  BY m.match_date, m.matchday;


-- ЗАПРОС 4: СТАТИСТИКА МАТЧЕЙ ПО СТАДИОНАМ
SELECT
    v.stadium_name                                AS "Стадион",
    v.city                                        AS "Город",
    v.capacity                                    AS "Вместимость",
    COUNT(m.match_id)                             AS "Матчей сыграно",
    ROUND(AVG(mr.home_goals + mr.away_goals), 2)  AS "Ср. голов/матч",
    MAX(mr.home_goals + mr.away_goals)            AS "Макс голов"
FROM   venues        v
JOIN   matches       m  ON v.venue_id  = m.venue_id
JOIN   match_results mr ON m.match_id  = mr.match_id
GROUP  BY v.venue_id, v.stadium_name, v.city, v.capacity
HAVING COUNT(m.match_id) > 0
ORDER  BY COUNT(m.match_id) DESC;


-- ЗАПРОС 5: КОМАНДЫ С НАИБОЛЬШЕЙ ДОЛЕЙ ПОБЕД ДОМА
SELECT
    ht.team_name                                        AS "Команда",
    COUNT(*)                                            AS "Домашних матчей",
    COUNT(*) FILTER (WHERE mr.winner = 'home')          AS "Побед дома",
    COUNT(*) FILTER (WHERE mr.winner = 'draw')          AS "Ничьих дома",
    COUNT(*) FILTER (WHERE mr.winner = 'away')          AS "Поражений дома",
    ROUND(100.0 * COUNT(*) FILTER (WHERE mr.winner = 'home')
          / COUNT(*), 1)                                AS "% побед дома"
FROM   matches       m
JOIN   teams         ht ON m.home_team_id = ht.team_id
JOIN   match_results mr ON m.match_id     = mr.match_id
GROUP  BY ht.team_name
ORDER  BY "% побед дома" DESC;


-- ЗАПРОС 6: ТОП МАТЧЕЙ ПО КОЛИЧЕСТВУ ГОЛОВ
SELECT
    m.season                                      AS "Сезон",
    m.matchday                                    AS "Тур",
    m.match_date                                  AS "Дата",
    ht.team_name                                  AS "Хозяева",
    CONCAT(mr.home_goals,' : ',mr.away_goals)     AS "Счёт",
    at.team_name                                  AS "Гости",
    mr.home_goals + mr.away_goals                 AS "Всего голов",
    v.stadium_name                                AS "Стадион"
FROM   matches       m
JOIN   teams         ht ON m.home_team_id = ht.team_id
JOIN   teams         at ON m.away_team_id = at.team_id
JOIN   match_results mr ON m.match_id     = mr.match_id
LEFT JOIN venues     v  ON m.venue_id     = v.venue_id
ORDER  BY mr.home_goals + mr.away_goals DESC
LIMIT  20;


-- ЗАПРОС 7: НАГРУЗКА НА СУДЕЙ
-- Судьи с наибольшим количеством обслуженных матчей
SELECT
    r.last_name || ' ' || r.first_name            AS "Судья",
    (SELECT nationality_name FROM nationalities WHERE nationality_id = r.nationality_id) AS "Национальность",
    (SELECT category_name FROM referee_categories WHERE category_id = r.category_id)   AS "Категория",
    COUNT(*) FILTER (WHERE mref.role_id = (SELECT role_id FROM referee_roles WHERE role_name = 'main'))    AS "Гл. судья",
    COUNT(*) FILTER (WHERE mref.role_id IN (SELECT role_id FROM referee_roles WHERE role_name LIKE 'assistant%')) AS "Ассистент",
    COUNT(*)                                      AS "Всего матчей"
FROM   referees      r
JOIN   match_referees mref ON r.referee_id = mref.referee_id
GROUP  BY r.referee_id, r.first_name, r.last_name, r.nationality_id, r.category_id
ORDER  BY "Всего матчей" DESC;


-- ЗАПРОС 8: СОСТАВ КОМАНД С ТРЕНЕРАМИ И СТАДИОНАМИ
SELECT
    t.team_name                                   AS "Команда",
    t.city                                        AS "Город",
    t.founded_year                                AS "Год основания",
    c.first_name || ' ' || c.last_name            AS "Тренер",
    c.nationality                                 AS "Нац. тренера",
    v.stadium_name                                AS "Стадион",
    v.capacity                                    AS "Вместимость",
    COUNT(p.player_id)                            AS "Игроков в составе"
FROM   teams   t
LEFT JOIN coaches c ON t.coach_id  = c.coach_id
LEFT JOIN venues  v ON t.venue_id  = v.venue_id
LEFT JOIN players p ON t.team_id   = p.team_id
GROUP  BY t.team_id, t.team_name, t.city, t.founded_year,
          c.first_name, c.last_name, c.nationality,
          v.stadium_name, v.capacity
ORDER  BY t.team_name;


-- ЗАПРОС 9: СРЕДНЕЕ КОЛИЧЕСТВО ГОЛОВ ПО СЕЗОНАМ И ТУРАМ
SELECT
    m.season                                                   AS "Сезон",
    m.matchday                                                 AS "Тур",
    COUNT(*)                                                   AS "Матчей",
    ROUND(AVG(mr.home_goals + mr.away_goals), 2)               AS "Ср. голов/матч",
    SUM(mr.home_goals + mr.away_goals)                         AS "Всего голов",
    COUNT(*) FILTER (WHERE mr.winner = 'home')                 AS "Побед хозяев",
    COUNT(*) FILTER (WHERE mr.winner = 'away')                 AS "Побед гостей",
    COUNT(*) FILTER (WHERE mr.winner = 'draw')                 AS "Ничьих"
FROM   matches       m
JOIN   match_results mr ON m.match_id = mr.match_id
GROUP  BY m.season, m.matchday
ORDER  BY m.season, m.matchday;


-- ЗАПРОС 10: ПРЯМЫЕ ОЧНЫЕ ВСТРЕЧИ ДВУХ КОМАНД (H2H)
SELECT
    m.season                                      AS "Сезон",
    m.match_date                                  AS "Дата",
    ht.team_name                                  AS "Хозяева",
    CONCAT(mr.home_goals,' : ',mr.away_goals)     AS "Счёт",
    at.team_name                                  AS "Гости",
    CASE mr.winner
        WHEN 'home' THEN ht.team_name || ' победили'
        WHEN 'away' THEN at.team_name || ' победили'
        ELSE 'Ничья'
    END                                           AS "Итог"
FROM   matches       m
JOIN   teams         ht ON m.home_team_id = ht.team_id
JOIN   teams         at ON m.away_team_id = at.team_id
JOIN   match_results mr ON m.match_id     = mr.match_id
WHERE  (ht.team_name = 'FC Bayern München' AND at.team_name = 'Borussia Dortmund')
    OR (ht.team_name = 'Borussia Dortmund' AND at.team_name = 'FC Bayern München')
ORDER  BY m.match_date;
