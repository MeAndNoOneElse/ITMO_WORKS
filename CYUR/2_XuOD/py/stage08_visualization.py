import os
import psycopg2
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─── Подключение к БД ────────────────────────────────────────────────────────
DB = dict(
    host="postgrepro.dc-edu.ru",
    port=5432,
    dbname="dbstud",
    user="bk_465029_2026",
    password="bk_465029",
    options="-c search_path=bk_465029_2026",
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "img")
os.makedirs(OUT_DIR, exist_ok=True)


def get_df(query: str) -> pd.DataFrame:
    conn_str = (
        f"host={DB['host']} port={DB['port']} dbname={DB['dbname']} "
        f"user={DB['user']} password={DB['password']} sslmode=require"
    )
    with psycopg2.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO bk_465029_2026")
        return pd.read_sql_query(query, conn)


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Сохранён: {path}")


sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"

print("=" * 60)
print("ЭТАП 8 — Визуализация SQL-запросов")
print("=" * 60)


# ─── ГРАФИК 1 ─────────────────────────────────────────────────────────────────
# Запрос 2 — Турнирная таблица Bundesliga 2023/24
# Тип: горизонтальная гистограмма

print("\n[1/5] Турнирная таблица 2023/24 (Запрос 2)...")

q1 = """
WITH stats AS (
    SELECT t.team_name,
        COUNT(*) FILTER (WHERE mr.winner='home' AND m.home_team_id=t.team_id
                           OR   mr.winner='away' AND m.away_team_id=t.team_id) AS wins,
        COUNT(*) FILTER (WHERE mr.winner='draw')                               AS draws,
        COUNT(*) FILTER (WHERE mr.winner='away' AND m.home_team_id=t.team_id
                           OR   mr.winner='home' AND m.away_team_id=t.team_id) AS losses,
        SUM(CASE WHEN m.home_team_id=t.team_id THEN mr.home_goals ELSE mr.away_goals END) AS gf,
        SUM(CASE WHEN m.home_team_id=t.team_id THEN mr.away_goals ELSE mr.home_goals END) AS ga
    FROM teams t
    JOIN matches m  ON t.team_id=m.home_team_id OR t.team_id=m.away_team_id
    JOIN match_results mr ON m.match_id=mr.match_id
    WHERE m.season=2023
    GROUP BY t.team_name
)
SELECT team_name AS team, wins*3+draws AS points,
       wins, draws, losses, gf, ga, gf-ga AS gd
FROM stats
ORDER BY points DESC, gd DESC, gf DESC
"""
df1 = get_df(q1)
print(f"  Получено: {len(df1)} команд")

fig, ax = plt.subplots(figsize=(12, 7))
palette = (["#f1c40f"] + ["#2ecc71"] * 3 + ["#3498db"] * 2
           + ["#95a5a6"] * (len(df1) - 8) + ["#e74c3c"] * 3)
bars = ax.barh(df1["team"][::-1], df1["points"][::-1],
               color=palette[::-1], edgecolor="white")
for bar, pts in zip(bars, df1["points"][::-1]):
    ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
            str(int(pts)), va="center", fontsize=9, fontweight="bold")

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#f1c40f", label="Чемпион"),
    Patch(facecolor="#2ecc71", label="Лига чемпионов (2–4)"),
    Patch(facecolor="#3498db", label="Лига Европы (5–6)"),
    Patch(facecolor="#95a5a6", label="Середина таблицы"),
    Patch(facecolor="#e74c3c", label="Вылет (16–18)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)
ax.set_title("Турнирная таблица — Bundesliga 2023/24\n(Запрос 2: итоговая сводная таблица)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Очки", fontsize=11)
ax.set_xlim(0, df1["points"].max() * 1.12)
ax.grid(axis="x", alpha=0.35)
plt.tight_layout()
save(fig, "stage08_viz1_standings.png")


# ─── ГРАФИК 2 ─────────────────────────────────────────────────────────────────
# Запрос 4 — Средние голы за матч по командам (хозяева + гости, все сезоны)
# Тип: горизонтальная гистограмма с цветовым градиентом

print("\n[2/5] Средние голы по командам (Запрос 4)...")

q2 = """
SELECT t.team_name AS team,
       ROUND(AVG(CASE WHEN m.home_team_id=t.team_id
                      THEN mr.home_goals + mr.away_goals
                      ELSE mr.home_goals + mr.away_goals END)::numeric, 2) AS avg_goals_in_match,
       ROUND(AVG(CASE WHEN m.home_team_id=t.team_id THEN mr.home_goals
                      ELSE mr.away_goals END)::numeric, 2)                 AS avg_scored,
       ROUND(AVG(CASE WHEN m.home_team_id=t.team_id THEN mr.away_goals
                      ELSE mr.home_goals END)::numeric, 2)                 AS avg_conceded,
       COUNT(*) AS games
FROM teams t
JOIN matches m  ON t.team_id=m.home_team_id OR t.team_id=m.away_team_id
JOIN match_results mr ON m.match_id=mr.match_id
GROUP BY t.team_name
HAVING COUNT(*) >= 10
ORDER BY avg_scored DESC
"""
df2 = get_df(q2)
print(f"  Получено: {len(df2)} команд")

fig, ax = plt.subplots(figsize=(12, 7))
pal = sns.color_palette("RdYlGn", len(df2))
bars = ax.barh(df2["team"][::-1], df2["avg_scored"][::-1],
               color=pal, edgecolor="white")
for bar, v in zip(bars, df2["avg_scored"][::-1]):
    ax.text(bar.get_width() + 0.03, bar.get_y() + bar.get_height() / 2,
            f"{v:.2f}", va="center", fontsize=8.5)
ax.set_title("Среднее забитых голов за матч по командам (2020–2023)\n(Запрос 4: статистика матчей по командам)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Среднее забитых голов за матч", fontsize=11)
ax.set_xlim(0, df2["avg_scored"].max() * 1.18)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
save(fig, "stage08_viz2_team_goals.png")


# ─── ГРАФИК 3 ─────────────────────────────────────────────────────────────────
# Запрос 5 — Доля домашних побед/ничьих/поражений по командам
# Тип: составная (stacked) горизонтальная гистограмма

print("\n[3/5] Домашняя статистика команд (Запрос 5)...")

q3 = """
SELECT ht.team_name AS team,
       COUNT(*) AS home_games,
       COUNT(*) FILTER (WHERE mr.winner='home') AS home_wins,
       COUNT(*) FILTER (WHERE mr.winner='draw') AS home_draws,
       COUNT(*) FILTER (WHERE mr.winner='away') AS home_losses
FROM matches m
JOIN teams ht ON m.home_team_id=ht.team_id
JOIN match_results mr ON m.match_id=mr.match_id
GROUP BY ht.team_name
ORDER BY COUNT(*) FILTER (WHERE mr.winner='home')::float / NULLIF(COUNT(*), 0) DESC
"""
df3 = get_df(q3)
df3["win_pct"]  = df3["home_wins"]   / df3["home_games"] * 100
df3["draw_pct"] = df3["home_draws"]  / df3["home_games"] * 100
df3["loss_pct"] = df3["home_losses"] / df3["home_games"] * 100
df3 = df3.sort_values("win_pct", ascending=True)
print(f"  Получено: {len(df3)} команд")

fig, ax = plt.subplots(figsize=(12, 7))
ax.barh(df3["team"], df3["win_pct"],  color="#27ae60", label="Победы",    edgecolor="white")
ax.barh(df3["team"], df3["draw_pct"], left=df3["win_pct"],
        color="#f39c12", label="Ничьи", edgecolor="white")
ax.barh(df3["team"], df3["loss_pct"],
        left=df3["win_pct"] + df3["draw_pct"],
        color="#e74c3c", label="Поражения", edgecolor="white")
ax.set_title("Результаты домашних матчей по командам\n(Запрос 5: доля домашних побед)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Доля матчей, %", fontsize=11)
ax.legend(loc="lower right", fontsize=9)
ax.set_xlim(0, 105)
plt.tight_layout()
save(fig, "stage08_viz3_home_wins.png")


# ─── ГРАФИК 4 ─────────────────────────────────────────────────────────────────
# Запрос 9 — Среднее голов по турам и сезонам
# Тип: линейный график (multi-line)

print("\n[4/5] Динамика голов по турам и сезонам (Запрос 9)...")

q4 = """
SELECT m.season, m.matchday,
       ROUND(AVG(mr.home_goals + mr.away_goals)::numeric, 2) AS avg_goals
FROM matches m
JOIN match_results mr ON m.match_id=mr.match_id
GROUP BY m.season, m.matchday
ORDER BY m.season, m.matchday
"""
df4 = get_df(q4)
print(f"  Получено: {len(df4)} строк")

fig, ax = plt.subplots(figsize=(14, 5))
palette4 = sns.color_palette("tab10", df4["season"].nunique())
for i, (season, grp) in enumerate(df4.groupby("season")):
    ax.plot(grp["matchday"], grp["avg_goals"],
            label=f"{season}/{str(int(season)+1)[-2:]}",
            linewidth=1.8, marker="o", markersize=3,
            color=palette4[i % len(palette4)])
overall = df4["avg_goals"].mean()
ax.axhline(overall, color="grey", linestyle="--", linewidth=1.2,
           label=f"Общее среднее: {overall:.2f}")
ax.set_title("Среднее голов за матч по турам\n(Запрос 9: динамика по сезонам)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Игровой тур", fontsize=11)
ax.set_ylabel("Среднее голов", fontsize=11)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.legend(fontsize=9, ncol=2)
ax.grid(alpha=0.3)
plt.tight_layout()
save(fig, "stage08_viz4_goals_by_matchday.png")


# ─── ГРАФИК 5 ─────────────────────────────────────────────────────────────────
# Запрос 7 — Нагрузка на судей
# Тип: сгруппированная гистограмма

print("\n[5/5] Нагрузка на судей (Запрос 7)...")

q5 = """
SELECT r.last_name || ' ' || r.first_name AS referee,
       (SELECT category_name FROM referee_categories WHERE category_id = r.category_id) AS category,
       COUNT(*) FILTER (WHERE mref.role_id=(SELECT role_id FROM referee_roles WHERE role_name='main'))            AS main_games,
       COUNT(*) FILTER (WHERE mref.role_id IN (SELECT role_id FROM referee_roles WHERE role_name LIKE 'assistant%')) AS asst_games
FROM referees r
JOIN match_referees mref ON r.referee_id=mref.referee_id
GROUP BY r.referee_id, r.first_name, r.last_name, r.category_id
ORDER BY main_games DESC
LIMIT 15
"""
df5 = get_df(q5)
print(f"  Получено: {len(df5)} судей")

fig, ax = plt.subplots(figsize=(12, 6))
x = range(len(df5))
width = 0.38
ax.bar([i - width / 2 for i in x], df5["main_games"],
       width=width, color="#2980b9", label="Главный судья", edgecolor="white")
ax.bar([i + width / 2 for i in x], df5["asst_games"],
       width=width, color="#e67e22", label="Ассистент",     edgecolor="white")
ax.set_xticks(list(x))
ax.set_xticklabels(df5["referee"], rotation=45, ha="right", fontsize=8.5)
ax.set_title("Количество матчей по судьям\n(Запрос 7: нагрузка на судей)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_ylabel("Количество матчей", fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save(fig, "stage08_viz5_referees.png")


print("\n" + "=" * 60)
print("Все графики сохранены в папку img/")
print("=" * 60)
for i, name in enumerate([
    "stage08_viz1_standings.png",
    "stage08_viz2_team_goals.png",
    "stage08_viz3_home_wins.png",
    "stage08_viz4_goals_by_matchday.png",
    "stage08_viz5_referees.png",
], 1):
    p = os.path.join(OUT_DIR, name)
    status = "✔" if os.path.exists(p) else "✘"
    size = f"{os.path.getsize(p)//1024} KB" if os.path.exists(p) else "—"
    print(f"  {status} [{i}] {name} ({size})")
