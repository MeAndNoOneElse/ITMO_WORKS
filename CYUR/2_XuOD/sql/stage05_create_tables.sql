SET search_path TO bk_465029_2026;

-- Позиции игроков
CREATE TABLE IF NOT EXISTS positions (
    position_id   INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    position_name VARCHAR(30)  NOT NULL UNIQUE
);

-- Национальности (общий справочник для игроков, тренеров, судей)
CREATE TABLE IF NOT EXISTS nationalities (
    nationality_id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nationality_name VARCHAR(80) NOT NULL UNIQUE
);

-- Категории судей
CREATE TABLE IF NOT EXISTS referee_categories (
    category_id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(20) NOT NULL UNIQUE  -- FIFA | national | regional
);

-- Роли судей в матче
CREATE TABLE IF NOT EXISTS referee_roles (
    role_id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE  -- main | assistant_1 | assistant_2 | fourth_official | VAR
);

-- Статусы матча
CREATE TABLE IF NOT EXISTS match_statuses (
    status_id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status_name VARCHAR(20) NOT NULL UNIQUE  -- scheduled | in_progress | finished | cancelled
);

-- ============================================================
--  РАЗДЕЛ 2: Основные таблицы
-- ============================================================

-- Стадионы
CREATE TABLE IF NOT EXISTS venues (
    venue_id     INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stadium_name VARCHAR(150) NOT NULL,
    city         VARCHAR(100) NOT NULL,
    country      VARCHAR(100) NOT NULL DEFAULT 'Germany',
    capacity     INTEGER      CHECK (capacity > 0),
    surface      VARCHAR(50)  NOT NULL DEFAULT 'grass'
);

-- Тренеры
CREATE TABLE IF NOT EXISTS coaches (
    coach_id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name     VARCHAR(80) NOT NULL,
    last_name      VARCHAR(80) NOT NULL,
    nationality_id INTEGER     NULL REFERENCES nationalities(nationality_id),
    birth_date     DATE
);

-- Команды
CREATE TABLE IF NOT EXISTS teams (
    team_id      INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name    VARCHAR(150) NOT NULL UNIQUE,
    short_name   VARCHAR(30),
    city         VARCHAR(100),
    founded_year INTEGER      CHECK (
                     founded_year > 1800
                     AND founded_year <= EXTRACT(YEAR FROM CURRENT_DATE)
                 ),
    -- NULL допустим: команда может временно не иметь стадиона или тренера
    venue_id     INTEGER      NULL REFERENCES venues(venue_id)  ON DELETE SET NULL,
    coach_id     INTEGER      NULL REFERENCES coaches(coach_id) ON DELETE SET NULL
);

-- Игроки
CREATE TABLE IF NOT EXISTS players (
    player_id      INTEGER  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id        INTEGER  NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    first_name     VARCHAR(80) NOT NULL,
    last_name      VARCHAR(80) NOT NULL,
    position_id    INTEGER  NULL REFERENCES positions(position_id),
    jersey_number  SMALLINT CHECK (jersey_number BETWEEN 1 AND 99),
    nationality_id INTEGER  NULL REFERENCES nationalities(nationality_id),
    birth_date     DATE,
    UNIQUE (team_id, jersey_number)
);

-- Судьи
CREATE TABLE IF NOT EXISTS referees (
    referee_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name     VARCHAR(80) NOT NULL,
    last_name      VARCHAR(80) NOT NULL,
    nationality_id INTEGER NULL REFERENCES nationalities(nationality_id),
    category_id    INTEGER NOT NULL
                           REFERENCES referee_categories(category_id)
);

-- Матчи
CREATE TABLE IF NOT EXISTS matches (
    match_id     INTEGER  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    season       SMALLINT NOT NULL CHECK (season BETWEEN 2000 AND 2100),
    matchday     SMALLINT NOT NULL CHECK (matchday BETWEEN 1 AND 38),
    match_date   DATE     NOT NULL,
    match_time   TIME     DEFAULT '15:30:00',
    home_team_id INTEGER  NOT NULL REFERENCES teams(team_id),
    away_team_id INTEGER  NOT NULL REFERENCES teams(team_id),
    -- NULL допустим: место проведения может быть неизвестно
    venue_id     INTEGER  NULL REFERENCES venues(venue_id) ON DELETE SET NULL,
    status_id    INTEGER  NOT NULL REFERENCES match_statuses(status_id),
    CONSTRAINT chk_different_teams CHECK (home_team_id <> away_team_id)
);

-- Результаты матчей
-- winner — производное поле, вычисляется как GENERATED ALWAYS (stored computed column)
CREATE TABLE IF NOT EXISTS match_results (
    result_id      INTEGER  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- UNIQUE + NOT NULL: один матч — один результат; NULL недопустим (если матч не сыгран — записи нет)
    match_id       INTEGER  NOT NULL UNIQUE REFERENCES matches(match_id) ON DELETE CASCADE,
    home_goals     SMALLINT NOT NULL DEFAULT 0 CHECK (home_goals     >= 0),
    away_goals     SMALLINT NOT NULL DEFAULT 0 CHECK (away_goals     >= 0),
    home_goals_ht  SMALLINT NOT NULL DEFAULT 0 CHECK (home_goals_ht  >= 0),
    away_goals_ht  SMALLINT NOT NULL DEFAULT 0 CHECK (away_goals_ht  >= 0),
    -- Вычисляемый столбец: не хранится вручную, исключает рассинхронизацию данных
    winner         VARCHAR(10) GENERATED ALWAYS AS (
                       CASE
                           WHEN home_goals > away_goals THEN 'home'
                           WHEN away_goals > home_goals THEN 'away'
                           ELSE 'draw'
                       END
                   ) STORED
);

-- Судьи матчей (связь M:N между matches и referees)
CREATE TABLE IF NOT EXISTS match_referees (
    match_id    INTEGER NOT NULL REFERENCES matches(match_id)   ON DELETE CASCADE,
    referee_id  INTEGER NOT NULL REFERENCES referees(referee_id),
    role_id     INTEGER NOT NULL REFERENCES referee_roles(role_id),
    PRIMARY KEY (match_id, referee_id)
);

-- ============================================================
--  РАЗДЕЛ 3: Наполнение справочников (статические значения)
-- ============================================================

INSERT INTO positions (position_name) VALUES
    ('goalkeeper'), ('defender'), ('midfielder'), ('forward')
ON CONFLICT (position_name) DO NOTHING;

INSERT INTO referee_categories (category_name) VALUES
    ('FIFA'), ('national'), ('regional')
ON CONFLICT (category_name) DO NOTHING;

INSERT INTO referee_roles (role_name) VALUES
    ('main'), ('assistant_1'), ('assistant_2'), ('fourth_official'), ('VAR')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO match_statuses (status_name) VALUES
    ('scheduled'), ('in_progress'), ('finished'), ('cancelled')
ON CONFLICT (status_name) DO NOTHING;
