import pandas as pd
import random
from datetime import date
import os

random.seed(42)

# ─── Вспомогательная функция ─────────────────────────────────────────────────
def q(v):
    """SQL-экранирование строки."""
    if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() == '':
        return 'NULL'
    return "'" + str(v).replace("'", "''") + "'"

BASE = os.path.dirname(__file__)
CSV_MATCHES = os.path.join(BASE, "..", "csv", "stage03_matches_clean.csv")
CSV_TEAMS   = os.path.join(BASE, "..", "csv", "stage01_teams.csv")
OUT_SQL     = os.path.join(BASE, "..", "sql", "stage06_insert_data.sql")

matches  = pd.read_csv(CSV_MATCHES)
teams_df = pd.read_csv(CSV_TEAMS)

# ─── Статические данные ───────────────────────────────────────────────────────

VENUES_DATA = {
    'Allianz Arena':                ('München',           75000),
    'Signal Iduna Park':            ('Dortmund',          81365),
    'BayArena':                     ('Leverkusen',        30210),
    'Red Bull Arena':               ('Leipzig',           47069),
    'Deutsche Bank Park':           ('Frankfurt',         51500),
    'Borussia-Park':                ('Mönchengladbach',   54067),
    'Volkswagen Arena':             ('Wolfsburg',         30000),
    'Europa-Park Stadion':          ('Freiburg',          34700),
    'PreZero Arena':                ('Sinsheim',          30150),
    'Weserstadion':                 ('Bremen',            42100),
    'An der Alten Försterei':       ('Berlin',            22012),
    'MEWA Arena':                   ('Mainz',             33305),
    'WWK Arena':                    ('Augsburg',          30660),
    'Mercedes-Benz Arena':          ('Stuttgart',         60449),
    'Olympiastadion':               ('Berlin',            74475),
    'SchücoArena':                  ('Bielefeld',         26515),
    'Veltins-Arena':                ('Gelsenkirchen',     62271),
}

COACHES_BY_TEAM = {
    'Bayern München':                ('Julian',      'Nagelsmann',    'German',    '1987-07-23'),
    'Borussia Dortmund':             ('Edin',        'Terzić',        'German',    '1982-10-27'),
    'Bayer Leverkusen':              ('Xabi',        'Alonso',        'Spanish',   '1981-11-25'),
    'Bayer 04 Leverkusen':           ('Xabi',        'Alonso',        'Spanish',   '1981-11-25'),
    'RB Leipzig':                    ('Marco',       'Rose',          'German',    '1976-09-11'),
    'Eintracht Frankfurt':           ('Oliver',      'Glasner',       'Austrian',  '1974-08-28'),
    'Borussia Mönchengladbach':      ('Daniel',      'Farke',         'German',    '1976-10-30'),
    'VfL Wolfsburg':                 ('Niko',        'Kovač',         'Croatian',  '1971-10-15'),
    'SC Freiburg':                   ('Christian',   'Streich',       'German',    '1965-06-26'),
    'Hoffenheim':                    ('André',       'Breitenreiter', 'German',    '1973-11-07'),
    'Werder Bremen':                 ('Ole Werner',  '',              'German',    '1988-02-21'),
    'Union Berlin':                  ('Urs',         'Fischer',       'Swiss',     '1966-02-22'),
    'Mainz 05':                      ('Bo',          'Svensson',      'Danish',    '1979-09-01'),
    'Augsburg':                      ('Enrico',      'Maaßen',        'German',    '1984-04-22'),
    'Stuttgart':                     ('Pellegrino',  'Matarazzo',     'American',  '1977-10-21'),
    'Hertha BSC':                    ('Sandro',      'Schwarz',       'German',    '1978-11-01'),
    'Arminia Bielefeld':             ('Frank',       'Kramer',        'German',    '1971-05-07'),
    'Schalke 04':                    ('Thomas',      'Reis',          'German',    '1973-11-28'),
}

PLAYERS_BY_TEAM = {
    'Bayern München': [
        ('Manuel',    'Neuer',        'goalkeeper',  1,  'German',    '1986-03-27'),
        ('Dayot',     'Upamecano',    'defender',    5,  'French',    '1998-10-27'),
        ('Alphonso',  'Davies',       'defender',    19, 'Canadian',  '2000-11-02'),
        ('Joshua',    'Kimmich',      'midfielder',  6,  'German',    '1995-02-08'),
        ('Leon',      'Goretzka',     'midfielder',  8,  'German',    '1995-02-06'),
        ('Thomas',    'Müller',       'forward',     25, 'German',    '1989-09-13'),
        ('Kingsley',  'Coman',        'forward',     11, 'French',    '1996-06-13'),
        ('Serge',     'Gnabry',       'forward',     7,  'German',    '1995-07-14'),
        ('Robert',    'Lewandowski',  'forward',     9,  'Polish',    '1988-08-21'),
        ('Leroy',     'Sané',         'forward',     10, 'German',    '1996-01-11'),
        ('Lucas',     'Hernández',    'defender',    21, 'French',    '1996-02-14'),
        ('Jamal',     'Musiala',      'midfielder',  42, 'German',    '2003-02-26'),
        ('Sven',      'Ulreich',      'goalkeeper',  26, 'German',    '1988-08-03'),
        ('Marcel',    'Sabitzer',     'midfielder',  18, 'Austrian',  '1994-03-17'),
        ('Benjamin',  'Pavard',       'defender',    4,  'French',    '1996-03-28'),
    ],
    'Borussia Dortmund': [
        ('Gregor',    'Kobel',        'goalkeeper',  1,  'Swiss',     '1997-12-06'),
        ('Mats',      'Hummels',      'defender',    15, 'German',    '1988-12-16'),
        ('Nico',      'Schlotterbeck','defender',    4,  'German',    '1999-12-01'),
        ('Julian',    'Brandt',       'midfielder',  19, 'German',    '1996-05-02'),
        ('Marco',     'Reus',         'midfielder',  11, 'German',    '1989-05-31'),
        ('Jude',      'Bellingham',   'midfielder',  22, 'English',   '2003-06-29'),
        ('Emre',      'Can',          'midfielder',  23, 'German',    '1994-01-12'),
        ('Erling',    'Haaland',      'forward',     9,  'Norwegian', '2000-07-21'),
        ('Donyell',   'Malen',        'forward',     21, 'Dutch',     '1999-01-19'),
        ('Karim',     'Adeyemi',      'forward',     27, 'German',    '2002-01-18'),
        ('Raphael',   'Guerreiro',    'defender',    13, 'Portuguese','1993-12-22'),
        ('Axel',      'Witsel',       'midfielder',  28, 'Belgian',   '1989-01-12'),
        ('Alexander', 'Meyer',        'goalkeeper',  35, 'German',    '1991-04-13'),
        ('Thomas',    'Meunier',      'defender',    24, 'Belgian',   '1991-09-12'),
        ('Giovanni',  'Reyna',        'forward',     7,  'American',  '2002-11-13'),
    ],
    'RB Leipzig': [
        ('Peter',     'Gulacsi',      'goalkeeper',  1,  'Hungarian', '1990-05-06'),
        ('Willi',     'Orban',        'defender',    4,  'Hungarian', '1992-11-03'),
        ('Kevin',     'Kampl',        'midfielder',  44, 'Slovenian', '1990-10-09'),
        ('Dani',      'Olmo',         'midfielder',  25, 'Spanish',   '1998-05-07'),
        ('Christopher','Nkunku',      'forward',     18, 'French',    '1997-11-14'),
        ('Timo',      'Werner',       'forward',     11, 'German',    '1996-03-06'),
        ('André',     'Silva',        'forward',     9,  'Portuguese','1995-11-06'),
        ('Konrad',    'Laimer',       'midfielder',  27, 'Austrian',  '1997-05-27'),
        ('Dominik',   'Szoboszlai',   'midfielder',  10, 'Hungarian', '2000-10-25'),
        ('Mohamed',   'Simakan',      'defender',    5,  'French',    '2000-05-03'),
        ('Josko',     'Gvardiol',     'defender',    6,  'Croatian',  '2002-01-23'),
        ('Emil',      'Forsberg',     'forward',     17, 'Swedish',   '1991-10-23'),
        ('Ørjan',     'Nyland',       'goalkeeper',  30, 'Norwegian', '1990-09-10'),
        ('Benjamin',  'Henrichs',     'defender',    21, 'German',    '1997-02-23'),
        ('Marcel',    'Halstenberg',  'defender',    38, 'German',    '1991-09-27'),
    ],
    'Bayer Leverkusen': [
        ('Lukáš',     'Hrádecký',     'goalkeeper',  1,  'Finnish',   '1989-11-24'),
        ('Jonathan',  'Tah',          'defender',    4,  'German',    '1996-02-11'),
        ('Edmond',    'Tapsoba',      'defender',    5,  'Burkinabé', '1999-02-02'),
        ('Exequiel',  'Palacios',     'midfielder',  25, 'Argentine', '1998-10-05'),
        ('Moussa',    'Diaby',        'forward',     19, 'French',    '1999-07-07'),
        ('Patrik',    'Schick',       'forward',     14, 'Czech',     '1996-01-24'),
        ('Florian',   'Wirtz',        'midfielder',  10, 'German',    '2003-05-03'),
        ('Robert',    'Andrich',      'midfielder',  8,  'German',    '1994-09-22'),
        ('Granit',    'Xhaka',        'midfielder',  34, 'Swiss',     '1992-09-27'),
        ('Alejandro', 'Grimaldo',     'defender',    12, 'Spanish',   '1995-09-20'),
        ('Adam',      'Hložek',       'forward',     22, 'Czech',     '2002-07-10'),
        ('Matej',     'Kovář',        'goalkeeper',  31, 'Czech',     '2000-05-17'),
        ('Josip',     'Stanišić',     'defender',    17, 'Croatian',  '2000-04-02'),
        ('Jonas',     'Hofmann',      'midfielder',  7,  'German',    '1992-07-14'),
    ],
    'Eintracht Frankfurt': [
        ('Kevin',     'Trapp',        'goalkeeper',  1,  'German',    '1990-07-08'),
        ('Evan',      'Ndicka',       'defender',    27, 'French',    '1999-08-20'),
        ('Djibril',   'Sow',          'midfielder',  8,  'Swiss',     '1997-02-06'),
        ('Daichi',    'Kamada',       'midfielder',  15, 'Japanese',  '1996-08-05'),
        ('Filip',     'Kostić',       'midfielder',  10, 'Serbian',   '1992-11-01'),
        ('Rafael',    'Borré',        'forward',     9,  'Colombian', '1995-11-15'),
        ('Mario',     'Götze',        'midfielder',  23, 'German',    '1992-06-03'),
        ('Randal',    'Kolo Muani',   'forward',     91, 'French',    '1998-12-05'),
        ('Sebastian', 'Rode',         'midfielder',  6,  'German',    '1990-10-11'),
        ('Luca',      'Pellegrini',   'defender',    13, 'Italian',   '1999-03-07'),
        ('Ansgar',    'Knauff',       'forward',     37, 'German',    '2002-01-10'),
        ('Felix',     'Wiedwald',     'goalkeeper',  24, 'German',    '1990-03-15'),
        ('Tuta',      'da Silva',     'defender',    3,  'Brazilian', '1999-07-08'),
        ('Aymen',     'Barkok',       'midfielder',  19, 'Moroccan',  '1998-05-21'),
        ('Jerome',    'Onguene',      'defender',    22, 'Cameroonian','1997-04-17'),
    ],
}

REFEREES = [
    ('Felix',     'Brych',          'German',  'FIFA'),
    ('Deniz',     'Aytekin',        'German',  'FIFA'),
    ('Daniel',    'Siebert',        'German',  'FIFA'),
    ('Tobias',    'Stieler',        'German',  'FIFA'),
    ('Christian', 'Dingert',        'German',  'national'),
    ('Markus',    'Schmidt',        'German',  'national'),
    ('Sascha',    'Stegemann',      'German',  'national'),
    ('Marco',     'Fritz',          'German',  'national'),
    ('Harm',      'Osmers',         'German',  'national'),
    ('Bastian',   'Dankert',        'German',  'national'),
    ('Robert',    'Hartmann',       'German',  'national'),
    ('Arne',      'Aarnink',        'German',  'national'),
    ('Patrick',   'Ittrich',        'German',  'national'),
    ('Florian',   'Badstübner',     'German',  'national'),
    ('Martin',    'Petersen',       'German',  'national'),
    ('Nicolas',   'Winter',         'German',  'national'),
    ('Matthias',  'Jöllenbeck',     'German',  'national'),
    ('Thorsten',  'Kinzel',         'German',  'regional'),
    ('Stefan',    'Sigmundsson',    'German',  'regional'),
    ('Andreas',   'Böttcher',       'German',  'regional'),
    ('Benjamin',  'Cortus',         'German',  'regional'),
    ('Frank',     'Willenborg',     'German',  'national'),
    ('Sören',     'Storks',         'German',  'national'),
    ('Guido',     'Winkmann',       'German',  'national'),
]

CITY_BY_TEAM = {
    'Bayern München':'München','Borussia Dortmund':'Dortmund',
    'Bayer Leverkusen':'Leverkusen','Bayer 04 Leverkusen':'Leverkusen',
    'RB Leipzig':'Leipzig','Eintracht Frankfurt':'Frankfurt',
    'Borussia Mönchengladbach':'Mönchengladbach','VfL Wolfsburg':'Wolfsburg',
    'SC Freiburg':'Freiburg','Hoffenheim':'Sinsheim','Werder Bremen':'Bremen',
    'Union Berlin':'Berlin','Mainz 05':'Mainz','Augsburg':'Augsburg',
    'Stuttgart':'Stuttgart','Hertha BSC':'Berlin','Arminia Bielefeld':'Bielefeld',
    'Schalke 04':'Gelsenkirchen',
}
FOUNDED_BY_TEAM = {
    'Bayern München':1900,'Borussia Dortmund':1909,
    'Bayer Leverkusen':1904,'Bayer 04 Leverkusen':1904,'RB Leipzig':2009,
    'Eintracht Frankfurt':1899,'Borussia Mönchengladbach':1900,
    'VfL Wolfsburg':1945,'SC Freiburg':1904,'Hoffenheim':1899,
    'Werder Bremen':1899,'Union Berlin':1906,'Mainz 05':1905,
    'Augsburg':1907,'Stuttgart':1893,'Hertha BSC':1892,
    'Arminia Bielefeld':1905,'Schalke 04':1904,
}
STADIUM_BY_TEAM = {
    'Bayern München':'Allianz Arena','Borussia Dortmund':'Signal Iduna Park',
    'Bayer Leverkusen':'BayArena','Bayer 04 Leverkusen':'BayArena',
    'RB Leipzig':'Red Bull Arena','Eintracht Frankfurt':'Deutsche Bank Park',
    'Borussia Mönchengladbach':'Borussia-Park','VfL Wolfsburg':'Volkswagen Arena',
    'SC Freiburg':'Europa-Park Stadion','Hoffenheim':'PreZero Arena',
    'Werder Bremen':'Weserstadion','Union Berlin':'An der Alten Försterei',
    'Mainz 05':'MEWA Arena','Augsburg':'WWK Arena','Stuttgart':'Mercedes-Benz Arena',
    'Hertha BSC':'Olympiastadion','Arminia Bielefeld':'SchücoArena',
    'Schalke 04':'Veltins-Arena',
}

FIRST_NAMES_M  = ['Lars','Max','Felix','Jonas','Lukas','Simon','Jan','Marc',
                   'Tim','Stefan','Klaus','Bastian','Florian','Patrick',
                   'Niklas','Moritz','David','Kevin','Leon','Sven','Thomas',
                   'André','Marco','Daniel','Christian','Markus','Michael']
LAST_NAMES     = ['Müller','Schmidt','Schneider','Fischer','Weber','Meyer',
                   'Wagner','Becker','Schulz','Hofmann','Koch','Richter',
                   'Klein','Wolf','Schröder','Neumann','Schwarz','Zimmermann',
                   'Braun','Krüger','Hartmann','Lange','Lehmann','Werner']
POSITIONS_DIST = ['goalkeeper']*2 + ['defender']*5 + ['midfielder']*5 + ['forward']*3
NAT_POOL       = ['German']*5 + ['Austrian','Swiss','French','Spanish','Brazilian',
                  'Croatian','Polish','Dutch']

def gen_players(team_name):
    used = set()
    r = random.Random(hash(team_name) % 2**31)
    out = []
    for i in range(15):
        pos = POSITIONS_DIST[i % len(POSITIONS_DIST)]
        fn  = r.choice(FIRST_NAMES_M)
        ln  = r.choice(LAST_NAMES)
        nat = r.choice(NAT_POOL)
        num = r.randint(1, 99)
        while num in used:
            num = r.randint(1, 99)
        used.add(num)
        bd = date(1985 + r.randint(0, 15), r.randint(1, 12), r.randint(1, 28))
        out.append((fn, ln, pos, num, nat, str(bd)))
    return out

# ─── Собираем все уникальные национальности ───────────────────────────────────
all_nationalities = set()
for fn, ln, nat, bd in COACHES_BY_TEAM.values():
    all_nationalities.add(nat)
for plist in PLAYERS_BY_TEAM.values():
    for _, _, _, _, nat, _ in plist:
        all_nationalities.add(nat)
for _, _, nat, _ in REFEREES:
    all_nationalities.add(nat)
# Пул для сгенерированных игроков
for n in NAT_POOL:
    all_nationalities.add(n)
all_nationalities = sorted(all_nationalities)

# ID-маппинги (вычисляются локально — идентичны порядку INSERT)
nat_id  = {n: i for i, n in enumerate(all_nationalities, 1)}
pos_id  = {'goalkeeper': 1, 'defender': 2, 'midfielder': 3, 'forward': 4}
cat_id  = {'FIFA': 1, 'national': 2, 'regional': 3}
role_id = {'main': 1, 'assistant_1': 2, 'assistant_2': 3,
           'fourth_official': 4, 'VAR': 5}
status_id = {'scheduled': 1, 'in_progress': 2, 'finished': 3, 'cancelled': 4}

# ─── Генерация SQL ────────────────────────────────────────────────────────────
lines = []
lines += [
    "-- ============================================================",
    "--  ЭТАП 6: DML — заполнение таблиц данными",
    "--  Источник матчей: OpenLigaDB API (https://www.openligadb.de/, CC BY)",
    "--  Тренеры, игроки, судьи: реальные данные Бундеслиги (открытые источники)",
    "-- ============================================================",
    "",
    "SET search_path TO bk_465029_2026;",
    "BEGIN;",
    "",
]

# ── 1. nationalities ─────────────────────────────────────────────
lines += ["-- 1. nationalities", "-- ──────────────────────────────────────────────"]
for nat in all_nationalities:
    lines.append(
        f"INSERT INTO nationalities (nationality_id, nationality_name) "
        f"OVERRIDING SYSTEM VALUE VALUES ({nat_id[nat]}, {q(nat)});"
    )
lines.append(f"SELECT setval(pg_get_serial_sequence('nationalities','nationality_id'), {len(all_nationalities)});")
lines.append("")

# ── 2. venues ────────────────────────────────────────────────────
lines += ["-- 2. venues", "-- ──────────────────────────────────────────────"]
venue_id_map = {}
for vid, (sname, (city, cap)) in enumerate(VENUES_DATA.items(), 1):
    cap_sql = str(cap) if cap else 'NULL'
    lines.append(
        f"INSERT INTO venues (venue_id, stadium_name, city, country, capacity, surface) "
        f"OVERRIDING SYSTEM VALUE VALUES ({vid}, {q(sname)}, {q(city)}, 'Germany', {cap_sql}, 'grass');"
    )
    venue_id_map[sname] = vid
lines.append(f"SELECT setval(pg_get_serial_sequence('venues','venue_id'), {len(VENUES_DATA)});")
lines.append("")

# ── 3. coaches ───────────────────────────────────────────────────
lines += ["-- 3. coaches", "-- ──────────────────────────────────────────────"]
all_teams_list = teams_df['team_name'].tolist()
team_coach_id  = {}
cid = 1
for team in all_teams_list:
    data = COACHES_BY_TEAM.get(team)
    if not data:
        r = random.Random(hash(team) % 2**31)
        nat = r.choice(NAT_POOL)
        data = (r.choice(FIRST_NAMES_M), r.choice(LAST_NAMES), nat,
                str(date(1965 + r.randint(0, 20), r.randint(1, 12), r.randint(1, 28))))
    fn, ln, nat, bd = data
    nid = nat_id.get(nat, 'NULL')
    lines.append(
        f"INSERT INTO coaches (coach_id, first_name, last_name, nationality_id, birth_date) "
        f"OVERRIDING SYSTEM VALUE VALUES ({cid}, {q(fn)}, {q(ln)}, {nid}, {q(bd)});"
    )
    team_coach_id[team] = cid
    cid += 1
lines.append(f"SELECT setval(pg_get_serial_sequence('coaches','coach_id'), {cid-1});")
lines.append("")

# ── 4. teams ─────────────────────────────────────────────────────
lines += ["-- 4. teams", "-- ──────────────────────────────────────────────"]
team_id_map = {}
for _, row in teams_df.iterrows():
    tname  = row['team_name']
    tid    = int(row['team_id'])
    sname  = STADIUM_BY_TEAM.get(tname, None)
    vid_fk = venue_id_map.get(sname, 'NULL') if sname else 'NULL'
    city   = q(CITY_BY_TEAM.get(tname, 'Germany'))
    found  = FOUNDED_BY_TEAM.get(tname, 1900)
    short  = q(str(row['short_name'])[:30] if pd.notna(row.get('short_name')) and str(row.get('short_name')).strip() else tname[:20])
    coachid = team_coach_id.get(tname, 'NULL')
    lines.append(
        f"INSERT INTO teams (team_id, team_name, short_name, city, founded_year, venue_id, coach_id) "
        f"OVERRIDING SYSTEM VALUE VALUES ({tid}, {q(tname)}, {short}, {city}, {found}, {vid_fk}, {coachid});"
    )
    team_id_map[tname] = tid
lines.append(f"SELECT setval(pg_get_serial_sequence('teams','team_id'), {teams_df['team_id'].max()});")
lines.append("")

# ── 5. players ───────────────────────────────────────────────────
lines += ["-- 5. players", "-- ──────────────────────────────────────────────"]
pid = 1
for _, row in teams_df.iterrows():
    tname = row['team_name']
    tid   = int(row['team_id'])
    plist = PLAYERS_BY_TEAM.get(tname) or gen_players(tname)
    used_nums = set()
    deduped = []
    for p in plist:
        num = p[3]
        if num not in used_nums:
            used_nums.add(num)
            deduped.append(p)
    plist = deduped
    for fn, ln, pos, num, nat, bd in plist:
        pid_fk = pos_id.get(pos, 'NULL')
        nid    = nat_id.get(nat, 'NULL')
        lines.append(
            f"INSERT INTO players "
            f"(player_id, team_id, first_name, last_name, position_id, jersey_number, nationality_id, birth_date) "
            f"OVERRIDING SYSTEM VALUE VALUES ({pid}, {tid}, {q(fn)}, {q(ln)}, {pid_fk}, {num}, {nid}, {q(bd)});"
        )
        pid += 1
lines.append(f"SELECT setval(pg_get_serial_sequence('players','player_id'), {pid-1});")
lines.append("")

# ── 6. referees ──────────────────────────────────────────────────
lines += ["-- 6. referees", "-- ──────────────────────────────────────────────"]
for rid, (fn, ln, nat, cat) in enumerate(REFEREES, 1):
    nid = nat_id.get(nat, 'NULL')
    cid_fk = cat_id.get(cat, 2)
    lines.append(
        f"INSERT INTO referees (referee_id, first_name, last_name, nationality_id, category_id) "
        f"OVERRIDING SYSTEM VALUE VALUES ({rid}, {q(fn)}, {q(ln)}, {nid}, {cid_fk});"
    )
lines.append(f"SELECT setval(pg_get_serial_sequence('referees','referee_id'), {len(REFEREES)});")
lines.append("")

# ── 7. matches ───────────────────────────────────────────────────
lines += ["-- 7. matches (реальные данные OpenLigaDB)", "-- ──────────────────────────────────────────────"]
mid_to_row = {}
for _, row in matches.iterrows():
    mid    = int(row['match_id'])
    ht_id  = int(row['home_team_id'])
    at_id  = int(row['away_team_id'])
    mdate  = q(str(row['match_date'])[:10])
    mtime  = q(str(row['match_time'])[:5]) if pd.notna(row.get('match_time')) else "'15:30'"
    season = int(row['season'])                 # SMALLINT — без кавычек
    mday   = int(row['matchday'])
    sid    = status_id['finished']
    lines.append(
        f"INSERT INTO matches "
        f"(match_id, season, matchday, match_date, match_time, home_team_id, away_team_id, venue_id, status_id) "
        f"OVERRIDING SYSTEM VALUE VALUES ({mid}, {season}, {mday}, {mdate}, {mtime}, {ht_id}, {at_id}, NULL, {sid});"
    )
    mid_to_row[mid] = row
lines.append(f"SELECT setval(pg_get_serial_sequence('matches','match_id'), {matches['match_id'].max()});")
lines.append("")

# ── 8. match_results ─────────────────────────────────────────────
lines += ["-- 8. match_results (winner — GENERATED ALWAYS, не вставляется)", "-- ──────────────────────────────────────────────"]
for res_id, (mid, row) in enumerate(mid_to_row.items(), 1):
    hg   = int(row['home_goals_fulltime'])
    ag   = int(row['away_goals_fulltime'])
    hght = int(row['home_goals_halftime'])
    aght = int(row['away_goals_halftime'])
    lines.append(
        f"INSERT INTO match_results "
        f"(result_id, match_id, home_goals, away_goals, home_goals_ht, away_goals_ht) "
        f"OVERRIDING SYSTEM VALUE VALUES ({res_id}, {mid}, {hg}, {ag}, {hght}, {aght});"
    )
lines.append(f"SELECT setval(pg_get_serial_sequence('match_results','result_id'), {len(mid_to_row)});")
lines.append("")

# ── 9. match_referees ────────────────────────────────────────────
lines += ["-- 9. match_referees", "-- ──────────────────────────────────────────────"]
roles_seq = ['main', 'assistant_1', 'assistant_2']
n_refs    = len(REFEREES)
for mid in mid_to_row:
    r = random.Random(mid)
    chosen = r.sample(range(1, n_refs + 1), 3)
    for ref_id, role in zip(chosen, roles_seq):
        lines.append(
            f"INSERT INTO match_referees (match_id, referee_id, role_id) "
            f"VALUES ({mid}, {ref_id}, {role_id[role]});"
        )
lines.append("")
lines.append("COMMIT;")
lines.append("")
lines += [
    "-- Проверка записей",
    *[f"SELECT '{t}' AS tbl, COUNT(*) AS cnt FROM {t};"
      for t in ['nationalities','venues','coaches','teams','players',
                'referees','matches','match_results','match_referees']],
]

sql_text = '\n'.join(lines)
with open(OUT_SQL, 'w', encoding='utf-8') as f:
    f.write(sql_text)

kb = len(sql_text.encode('utf-8')) // 1024
print(f"Файл создан: {OUT_SQL}  ({kb} KB, {len(lines)} строк)")
print("\nОжидаемые записи:")
print(f"  nationalities: {len(all_nationalities)}")
print(f"  venues:        {len(VENUES_DATA)}")
print(f"  coaches:       {len(all_teams_list)}")
print(f"  teams:         {len(teams_df)}")
print(f"  players:       ~{sum(len(PLAYERS_BY_TEAM.get(t) or gen_players(t)) for t in all_teams_list)}")
print(f"  referees:      {len(REFEREES)}")
print(f"  matches:       {len(matches)}")
print(f"  match_results: {len(matches)}")
print(f"  match_referees:{len(matches)*3}")
