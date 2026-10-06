import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # без GUI — для сохранения в файл
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import time
import os
import warnings
warnings.filterwarnings("ignore")

# ЭТАП 1 — Сбор данных

BASE_URL = "https://api.openligadb.de"
LEAGUE   = "bl1"          # Bundesliga 1
SEASONS  = [2020, 2021, 2022, 2023]


def fetch_json(url: str) -> list | dict:
    """GET-запрос с обработкой ошибок."""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [ERROR] {url} → {e}")
        return []


def parse_match(raw: dict, season: int) -> dict:
    """Разбираем один матч из ответа API."""
    results   = raw.get("matchResults", [])
    final_res = next((x for x in results if x.get("resultTypeID") == 2), None)
    half_res  = next((x for x in results if x.get("resultTypeID") == 1), None)

    team1   = raw.get("team1")   or {}
    team2   = raw.get("team2")   or {}
    group   = raw.get("group")   or {}
    loc     = raw.get("location") or {}

    h_full  = final_res.get("pointsTeam1") if final_res else None
    a_full  = final_res.get("pointsTeam2") if final_res else None

    if h_full is not None and a_full is not None:
        if h_full > a_full:
            winner = "home"
        elif a_full > h_full:
            winner = "away"
        else:
            winner = "draw"
        total_goals = h_full + a_full
    else:
        winner      = None
        total_goals = None

    dt_str = raw.get("matchDateTimeUTC") or ""
    return {
        "match_id":              raw.get("matchID"),
        "season":                season,
        "match_date":            dt_str[:10]  if dt_str else None,
        "match_time":            dt_str[11:16] if dt_str else None,
        "matchday":              group.get("groupOrderID"),
        "matchday_name":         group.get("groupName", ""),
        "home_team_id":          team1.get("teamId"),
        "home_team":             team1.get("teamName", ""),
        "away_team_id":          team2.get("teamId"),
        "away_team":             team2.get("teamName", ""),
        "home_goals_halftime":   half_res.get("pointsTeam1")  if half_res  else None,
        "away_goals_halftime":   half_res.get("pointsTeam2")  if half_res  else None,
        "home_goals_fulltime":   h_full,
        "away_goals_fulltime":   a_full,
        "total_goals":           total_goals,
        "winner":                winner,
        "venue_stadium":         loc.get("locationStadion", ""),
        "venue_city":            loc.get("locationCity",    ""),
        "match_finished":        raw.get("matchIsFinished", False),
    }


def collect_matches() -> pd.DataFrame:
    all_rows = []
    for season in SEASONS:
        url = f"{BASE_URL}/getmatchdata/{LEAGUE}/{season}"
        print(f"  Загрузка матчей сезона {season}/{season+1}...")
        raw_list = fetch_json(url)
        for raw in raw_list:
            all_rows.append(parse_match(raw, season))
        time.sleep(0.4)
    df = pd.DataFrame(all_rows)
    print(f"  Всего матчей загружено: {len(df)}")
    return df


def collect_teams() -> pd.DataFrame:
    seen, rows = set(), []
    for season in SEASONS:
        url = f"{BASE_URL}/getavailableteams/{LEAGUE}/{season}"
        print(f"  Загрузка команд сезона {season}...")
        for t in fetch_json(url):
            tid = t.get("teamId")
            if tid not in seen:
                seen.add(tid)
                rows.append({
                    "team_id":       tid,
                    "team_name":     t.get("teamName",    ""),
                    "short_name":    t.get("shortName",   ""),
                    "icon_url":      t.get("teamIconUrl", ""),
                })
        time.sleep(0.3)
    df = pd.DataFrame(rows)
    print(f"  Всего уникальных команд: {len(df)}")
    return df


print("=" * 60)
print("ЭТАП 1 — Сбор данных")
print("=" * 60)

matches_df = collect_matches()
teams_df   = collect_teams()

matches_df.to_csv("bundesliga_matches_raw.csv", index=False, encoding="utf-8")
teams_df.to_csv("bundesliga_teams.csv",         index=False, encoding="utf-8")

print("\n✔ Файлы сохранены:")
print(f"  bundesliga_matches_raw.csv  — {len(matches_df)} строк, {len(matches_df.columns)} колонок")
print(f"  bundesliga_teams.csv        — {len(teams_df)} строк, {len(teams_df.columns)} колонок")
print("\nКолонки матчей:", list(matches_df.columns))


# ЭТАП 3 — Предобработка данных
# (выполняем перед визуализацией, чтобы рисовать на чистых данных)

print("\n" + "=" * 60)
print("ЭТАП 3 — Предобработка данных")
print("=" * 60)

df = matches_df.copy()
print(f"\nИсходный размер: {df.shape}")

# 3.1 — Убираем дубликаты
before = len(df)
df.drop_duplicates(subset="match_id", inplace=True)
print(f"Удалено дубликатов по match_id: {before - len(df)}")

# 3.2 — Оставляем только сыгранные матчи (для анализа результатов)
df_finished = df[df["match_finished"] == True].copy()
print(f"Сыгранных матчей: {len(df_finished)}  (незавершённых/будущих: {len(df) - len(df_finished)})")

# 3.3 — Проверяем пропуски в ключевых колонках
key_cols = ["home_goals_fulltime", "away_goals_fulltime", "total_goals",
            "winner", "matchday", "match_date"]
print("\nПропуски в ключевых колонках (df_finished):")
print(df_finished[key_cols].isnull().sum().to_string())

# 3.4 — Заполняем пропуски в голах для сыгранных матчей нулями (если API не вернул результат)
df_finished["home_goals_fulltime"]  = df_finished["home_goals_fulltime"].fillna(0).astype(int)
df_finished["away_goals_fulltime"]  = df_finished["away_goals_fulltime"].fillna(0).astype(int)
df_finished["home_goals_halftime"]  = df_finished["home_goals_halftime"].fillna(0).astype(int)
df_finished["away_goals_halftime"]  = df_finished["away_goals_halftime"].fillna(0).astype(int)
df_finished["total_goals"]          = (df_finished["home_goals_fulltime"]
                                        + df_finished["away_goals_fulltime"])

# 3.5 — Преобразование типов
df_finished["match_date"] = pd.to_datetime(df_finished["match_date"], errors="coerce")
df_finished["season"]     = df_finished["season"].astype(str)

# 3.6 — Обработка выбросов в total_goals (IQR)
Q1 = df_finished["total_goals"].quantile(0.25)
Q3 = df_finished["total_goals"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 3 * IQR
upper = Q3 + 3 * IQR
outliers = df_finished[(df_finished["total_goals"] < lower) |
                        (df_finished["total_goals"] > upper)]
print(f"\nВыбросы в total_goals (метод 3*IQR): {len(outliers)} матч(ей)")
print(f"  Граница: [{lower:.1f}, {upper:.1f}]")
if len(outliers) > 0:
    print("  Матчи с выбросами:\n", outliers[["match_id","home_team","away_team",
                                                "total_goals","season"]].to_string())
# Не удаляем выбросы — они реальные матчи, просто отмечаем
df_finished["is_outlier_goals"] = (
    (df_finished["total_goals"] < lower) |
    (df_finished["total_goals"] > upper)
)

# 3.7 — Итоговый чистый датасет
df_clean = df_finished.copy()
df_clean.to_csv("bundesliga_matches_clean.csv", index=False, encoding="utf-8")
print(f"\n✔ Чистый датасет: {df_clean.shape[0]} строк, {df_clean.shape[1]} колонок")
print("  Сохранён: bundesliga_matches_clean.csv")

# 3.8 — Описательные статистики числовых атрибутов
num_cols = ["home_goals_fulltime", "away_goals_fulltime",
            "home_goals_halftime", "away_goals_halftime",
            "total_goals", "matchday"]

stats = df_clean[num_cols].describe().round(3)
print("\n── Описательные статистики ──────────────────────────────")
print(stats.to_string())
stats.to_csv("descriptive_statistics.csv", encoding="utf-8")
print("  Сохранены: descriptive_statistics.csv")

# Дополнительные статистики
print("\n── Дополнительно ──────────────────────────────────────")
print(f"  Медиана голов за матч :  {df_clean['total_goals'].median()}")
print(f"  Мода голов за матч    :  {int(df_clean['total_goals'].mode()[0])}")
print(f"  % побед хозяев        :  {(df_clean['winner']=='home').mean()*100:.1f}%")
print(f"  % побед гостей        :  {(df_clean['winner']=='away').mean()*100:.1f}%")
print(f"  % ничьих              :  {(df_clean['winner']=='draw').mean()*100:.1f}%")
print(f"  Матчей без голов      :  {(df_clean['total_goals']==0).sum()}")
print(f"  Макс. голов в матче   :  {df_clean['total_goals'].max()}")


# ЭТАП 2 — Визуализация данных

print("\n" + "=" * 60)
print("ЭТАП 2 — Визуализация данных")
print("=" * 60)

sns.set_theme(style="whitegrid", palette="muted")
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

# ── График 1: Распределение голов за матч ────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
goal_counts = df_clean["total_goals"].value_counts().sort_index()
bars = ax.bar(goal_counts.index, goal_counts.values,
              color="#1f77b4", edgecolor="white", linewidth=0.8)
for bar in bars:
    h = bar.get_height()
    if h > 0:
        ax.text(bar.get_x() + bar.get_width()/2, h + 5,
                str(int(h)), ha="center", va="bottom", fontsize=8)
ax.set_title("Распределение голов за матч — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Количество голов в матче", fontsize=11)
ax.set_ylabel("Количество матчей",        fontsize=11)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_xlim(-0.5, goal_counts.index.max() + 0.5)
plt.tight_layout()
plt.savefig("chart1_goals_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ chart1_goals_distribution.png")


# ── График 2: Соотношение исходов матчей по сезонам ─────────────────────────
outcome_by_season = (df_clean.groupby(["season", "winner"])
                              .size()
                              .unstack(fill_value=0)
                              .reindex(columns=["home", "draw", "away"]))
outcome_pct = outcome_by_season.div(outcome_by_season.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(10, 5))
outcome_pct.plot(
    kind="bar", ax=ax, stacked=True,
    color=["#2ecc71", "#95a5a6", "#e74c3c"],
    edgecolor="white", linewidth=0.6
)
ax.set_title("Соотношение исходов матчей по сезонам — Bundesliga",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Сезон (начало)", fontsize=11)
ax.set_ylabel("Доля матчей, %", fontsize=11)
ax.set_ylim(0, 105)
ax.legend(["Победа хозяев", "Ничья", "Победа гостей"],
          loc="upper right", fontsize=9)
ax.set_xticklabels(outcome_pct.index, rotation=0)
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f%%", label_type="center",
                 fontsize=8, color="white", fontweight="bold")
plt.tight_layout()
plt.savefig("chart2_outcomes_by_season.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ chart2_outcomes_by_season.png")


# ── График 3: Топ-15 команд по забитым голам (за все сезоны) ─────────────────
goals_home = df_clean.groupby("home_team")["home_goals_fulltime"].sum()
goals_away = df_clean.groupby("away_team")["away_goals_fulltime"].sum()
total_scored = (goals_home.add(goals_away, fill_value=0)
                           .sort_values(ascending=False)
                           .head(15))

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(total_scored.index[::-1], total_scored.values[::-1],
               color=sns.color_palette("Blues_d", len(total_scored))[::-1],
               edgecolor="white")
for bar in bars:
    w = bar.get_width()
    ax.text(w + 3, bar.get_y() + bar.get_height()/2,
            str(int(w)), va="center", fontsize=9)
ax.set_title("Топ-15 команд по забитым голам — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Сумма забитых голов", fontsize=11)
ax.set_ylabel("")
ax.set_xlim(0, total_scored.max() * 1.12)
ax.grid(axis="x", alpha=0.4)
plt.tight_layout()
plt.savefig("chart3_top_scorers.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ chart3_top_scorers.png")


# ── График 4: Средние голы за матч по туру (по всем сезонам) ─────────────────
avg_by_md = (df_clean.groupby("matchday")["total_goals"]
                      .mean()
                      .reset_index()
                      .rename(columns={"total_goals": "avg_goals"}))

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(avg_by_md["matchday"], avg_by_md["avg_goals"],
        color="#e74c3c", linewidth=2, marker="o", markersize=4)
ax.axhline(df_clean["total_goals"].mean(), color="#7f8c8d",
           linestyle="--", linewidth=1.2, label=f"Среднее за все туры: {df_clean['total_goals'].mean():.2f}")
ax.fill_between(avg_by_md["matchday"], avg_by_md["avg_goals"],
                df_clean["total_goals"].mean(), alpha=0.15, color="#e74c3c")
ax.set_title("Среднее количество голов за матч по игровым турам — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Игровой тур", fontsize=11)
ax.set_ylabel("Среднее голов за матч", fontsize=11)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.legend(fontsize=10)
ax.set_xlim(avg_by_md["matchday"].min(), avg_by_md["matchday"].max())
plt.tight_layout()
plt.savefig("chart4_avg_goals_by_matchday.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ chart4_avg_goals_by_matchday.png")


# ИТОГ

print("\n" + "=" * 60)
print("ИТОГО — созданные файлы")
print("=" * 60)
files = [
    ("bundesliga_matches_raw.csv",   "Сырой датасет матчей (Этап 1)"),
    ("bundesliga_teams.csv",          "Датасет команд (Этап 1)"),
    ("bundesliga_matches_clean.csv",  "Чистый датасет матчей (Этап 3)"),
    ("descriptive_statistics.csv",    "Описательные статистики (Этап 3)"),
    ("chart1_goals_distribution.png", "График 1 — распределение голов (Этап 2)"),
    ("chart2_outcomes_by_season.png", "График 2 — исходы по сезонам (Этап 2)"),
    ("chart3_top_scorers.png",        "График 3 — топ команд по голам (Этап 2)"),
    ("chart4_avg_goals_by_matchday.png","График 4 — голы по турам (Этап 2)"),
]
for fname, desc in files:
    exists = "✔" if os.path.exists(fname) else "✘"
    print(f"  {exists}  {fname:45s} — {desc}")

print("\nИсточник данных: OpenLigaDB API — https://www.openligadb.de/")
print("Лицензия: Creative Commons (CC BY)")
print("Данные: Bundesliga (Германия), сезоны 2020/21 – 2023/24")