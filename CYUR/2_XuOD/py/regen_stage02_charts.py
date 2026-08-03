import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

BASE = os.path.dirname(__file__)
CSV  = os.path.join(BASE, "..", "csv", "stage03_matches_clean.csv")
OUT  = os.path.join(BASE, "..", "img")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(CSV)
df["match_date"]  = pd.to_datetime(df["match_date"], errors="coerce")
df["season"]      = df["season"].astype(str)
df["total_goals"] = df["home_goals_fulltime"] + df["away_goals_fulltime"]

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    kb = os.path.getsize(path) // 1024
    print(f"  ✔ {name}  ({kb} KB)")


# ── График 1: Распределение голов за матч (без изменений) ──────────────────
fig, ax = plt.subplots(figsize=(10, 5))
goal_counts = df["total_goals"].value_counts().sort_index()
bars = ax.bar(goal_counts.index, goal_counts.values,
              color="#1f77b4", edgecolor="white", linewidth=0.8)
for bar in bars:
    h = bar.get_height()
    if h > 0:
        ax.text(bar.get_x() + bar.get_width() / 2, h + 5,
                str(int(h)), ha="center", va="bottom", fontsize=8)
ax.set_title("Распределение голов за матч — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Количество голов в матче", fontsize=11)
ax.set_ylabel("Количество матчей", fontsize=11)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_xlim(-0.5, goal_counts.index.max() + 0.5)
plt.tight_layout()
save(fig, "stage02_chart1_goals_distribution.png")


# ── График 2: Исходы матчей по сезонам — ИСПРАВЛЕНО ────────────────────────
# Ось X: «Сезон», подписи: «45% (135)» — процент и абсолютное значение

outcome_abs = (df.groupby(["season", "winner"])
                 .size()
                 .unstack(fill_value=0)
                 .reindex(columns=["home", "draw", "away"]))
outcome_pct = outcome_abs.div(outcome_abs.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(10, 5))
outcome_pct.plot(
    kind="bar", ax=ax, stacked=True,
    color=["#2ecc71", "#95a5a6", "#e74c3c"],
    edgecolor="white", linewidth=0.6
)
ax.set_title("Соотношение исходов матчей по сезонам — Bundesliga",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Сезон", fontsize=11)            # исправлено
ax.set_ylabel("Доля матчей, %", fontsize=11)
ax.set_ylim(0, 108)
ax.legend(["Победа хозяев", "Ничья", "Победа гостей"],
          loc="upper right", fontsize=9)
ax.set_xticklabels(outcome_pct.index, rotation=0)

# Подписи: «45% (135)»
bottoms = {col: pd.Series([0.0] * len(outcome_pct), index=outcome_pct.index)
           for col in outcome_pct.columns}
cumul = pd.Series([0.0] * len(outcome_pct), index=outcome_pct.index)
for i, col in enumerate(["home", "draw", "away"]):
    for season in outcome_pct.index:
        pct = outcome_pct.loc[season, col]
        cnt = int(outcome_abs.loc[season, col])
        if pct > 4:
            y = cumul[season] + pct / 2
            ax.text(list(outcome_pct.index).index(season),
                    y, f"{pct:.0f}%\n({cnt})",
                    ha="center", va="center",
                    fontsize=7.5, color="white", fontweight="bold")
    cumul += outcome_pct[col]

plt.tight_layout()
save(fig, "stage02_chart2_outcomes_by_season.png")


# ── График 3: Топ-15 команд по голам — ИСПРАВЛЕНО ──────────────────────────
# Один цвет; топ-3 выделены другим оттенком

goals_home = df.groupby("home_team")["home_goals_fulltime"].sum()
goals_away = df.groupby("away_team")["away_goals_fulltime"].sum()
total_scored = (goals_home.add(goals_away, fill_value=0)
                          .sort_values(ascending=False)
                          .head(15))

colors_bar = ["#e74c3c" if i < 3 else "#4a90d9"
              for i in range(len(total_scored))][::-1]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(total_scored.index[::-1], total_scored.values[::-1],
               color=colors_bar, edgecolor="white")
for bar in bars:
    w = bar.get_width()
    ax.text(w + 3, bar.get_y() + bar.get_height() / 2,
            str(int(w)), va="center", fontsize=9)

from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor="#e74c3c", label="Топ-3"),
    Patch(facecolor="#4a90d9", label="Остальные"),
], loc="lower right", fontsize=9)
ax.set_title("Топ-15 команд по забитым голам — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Сумма забитых голов", fontsize=11)
ax.set_xlim(0, total_scored.max() * 1.12)
ax.grid(axis="x", alpha=0.4)
plt.tight_layout()
save(fig, "stage02_chart3_top_scorers.png")


# ── График 4: Средние голы по туру (без изменений) ─────────────────────────
avg_by_md = (df.groupby("matchday")["total_goals"]
               .mean()
               .reset_index()
               .rename(columns={"total_goals": "avg_goals"}))

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(avg_by_md["matchday"], avg_by_md["avg_goals"],
        color="#e74c3c", linewidth=2, marker="o", markersize=4)
mean_val = df["total_goals"].mean()
ax.axhline(mean_val, color="#7f8c8d", linestyle="--", linewidth=1.2,
           label=f"Среднее за все туры: {mean_val:.2f}")
ax.fill_between(avg_by_md["matchday"], avg_by_md["avg_goals"], mean_val,
                alpha=0.15, color="#e74c3c")
ax.set_title("Среднее количество голов за матч по игровым турам — Bundesliga 2020–2023",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Игровой тур", fontsize=11)
ax.set_ylabel("Среднее голов за матч", fontsize=11)
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
ax.legend(fontsize=10)
ax.set_xlim(avg_by_md["matchday"].min(), avg_by_md["matchday"].max())
plt.tight_layout()
save(fig, "stage02_chart4_goals_by_matchday.png")


# ── График 5 (НОВЫЙ): Ящик с усами — распределение голов по сезонам ─────────
# Тип: box plot (новый тип диаграммы)

fig, ax = plt.subplots(figsize=(10, 6))
seasons_order = sorted(df["season"].unique())
data_by_season = [df[df["season"] == s]["total_goals"].values for s in seasons_order]
labels = [f"{s}/{str(int(s)+1)[-2:]}" for s in seasons_order]

bp = ax.boxplot(data_by_season, labels=labels, patch_artist=True,
                medianprops=dict(color="white", linewidth=2),
                flierprops=dict(marker="o", markerfacecolor="#e74c3c",
                                markersize=4, alpha=0.5))

palette = sns.color_palette("Blues", len(seasons_order))
for patch, color in zip(bp["boxes"], palette):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

# Нанести медианы значениями
for i, (season_data, label) in enumerate(zip(data_by_season, labels), 1):
    med = pd.Series(season_data).median()
    ax.text(i, med + 0.15, f"{med:.1f}", ha="center", fontsize=8.5,
            fontweight="bold", color="#333333")

ax.set_title("Распределение голов за матч по сезонам — Bundesliga",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Сезон", fontsize=11)
ax.set_ylabel("Голов за матч", fontsize=11)
ax.grid(axis="y", alpha=0.4)
plt.tight_layout()
save(fig, "stage02_chart5_goals_boxplot.png")

print("\nВсе графики этапа 2 сохранены в img/")
