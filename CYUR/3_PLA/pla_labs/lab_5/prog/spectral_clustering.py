"""Задание 1. Спектральная кластеризация социальной сети (мат. Лапласа + k-means).

Строит связный неориентированный граф из 18 вершин с 3 визуально заметными
кластерами, считает матрицу Лапласа, собственные числа/векторы, выполняет
кластеризацию для k in {2,3,4,5,6} и сохраняет данные, графики и рисунки графов.
"""
import json
import csv
import os
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))          # .../lab_5/prog
PROJ = os.path.dirname(BASE)                               # .../lab_5
DATA = os.path.join(PROJ, "data")
GRAPHICS = os.path.join(PROJ, "graphics")
IMAGES = os.path.join(PROJ, "images")
for d in (DATA, GRAPHICS, IMAGES):
    os.makedirs(d, exist_ok=True)

RNG = np.random.default_rng(42)

# ---------------------------социальный граф---------------------------------
N = 18
NAMES = [
    "Аня", "Боря", "Вера", "Гриша", "Даша", "Егор",      # кластер А (0-5)
    "Женя", "Захара", "Ира", "Кира", "Леша", "Маша",     # кластер Б (6-11)
    "Настя", "Олег", "Полина", "Рома", "Саша", "Толя",   # кластер В (12-17)
]
CLUSTER_NAME = {0: "А", 1: "Б", 2: "В"}
CLUSTER_IDX = {"А": 0, "Б": 1, "В": 2}

G = nx.Graph()
G.add_nodes_from(range(N))
for i in range(N):
    G.nodes[i]["name"] = NAMES[i]
    G.nodes[i]["true_cluster"] = CLUSTER_NAME[i // 6]

# рёбра внутри кластера (плотно)
for c in range(3):
    members = list(range(c * 6, c * 6 + 6))
    for ii in range(len(members)):
        for jj in range(ii + 1, len(members)):
            a, b = members[ii], members[jj]
            if RNG.random() < 0.72:
                G.add_edge(a, b)

# несколько межкластеровых рёбер (graf остаётся связным, но кластеры заметны)
INTER_EDGES = [(2, 7), (5, 8), (11, 13), (0, 14), (4, 16),
               (9, 15), (1, 6), (10, 17), (3, 12), (7, 12)]
for a, b in INTER_EDGES:
    G.add_edge(a, b)

# гарантируем связность
if not nx.is_connected(G):
    comps = list(nx.connected_components(G))
    for i in range(len(comps) - 1):
        a = sorted(comps[i])[0]
        b = sorted(comps[i + 1])[0]
        G.add_edge(a, b)

print("Задание 1: вершин =", G.number_of_nodes(), ", рёбер =", G.number_of_edges(),
      ", связан =", nx.is_connected(G))
print("размеры истинных кластеров:",
      {c: sum(1 for v in G.nodes if G.nodes[v]["true_cluster"] == CLUSTER_NAME[c])
       for c in range(3)})

# позиции вершин: три кластера на углах треугольника (визуально разделены)
CENTERS = {0: np.array([-2.0, 1.0]), 1: np.array([2.0, 1.0]), 2: np.array([0.0, -2.0])}
POS = {}
for c in range(3):
    members = [v for v in G.nodes if G.nodes[v]["true_cluster"] == CLUSTER_NAME[c]]
    for k, v in enumerate(members):
        ang = 2 * np.pi * k / len(members)
        POS[v] = CENTERS[c] + 0.75 * np.array([np.cos(ang), np.sin(ang)])

# ----------------------матрица Лапласа и спектр-----------------------------
A = nx.to_numpy_array(G, nodelist=range(N))          # матрица смежности
deg = A.sum(axis=1)
D = np.diag(deg)
L = D - A                                            # комбинаторный Лапласиан
w, U = np.linalg.eigh(L)                             # собственные числа (возр.) и векторы
w = np.real(w)
U = np.real(U)
order = np.argsort(w)
w = w[order]
U = U[:, order]

np.savetxt(os.path.join(DATA, "adjacency.csv"), A, delimiter=",", fmt="%d")
np.savetxt(os.path.join(DATA, "laplacian.csv"), L, delimiter=",", fmt="%.6f")
with open(os.path.join(DATA, "eigenvalues.json"), "w", encoding="utf-8") as f:
    json.dump([float(x) for x in w], f, ensure_ascii=False, indent=2)

print("собственные числа Лапласа:", np.round(w, 4))

# -------------------- отрисовка исходного графа (с истинными кластерами) ---
def draw_graph(G, pos, labels, title, out_pdf, node_color=None, cmap="tab10",
               with_numbers=True):
    plt.figure(figsize=(7.2, 5.6))
    ax = plt.gca()
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.2, alpha=0.55, edge_color="#6b6b6b")
    if node_color is None:
        node_color = "#9ecae1"
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_color,
                                   cmap=plt.get_cmap(cmap), node_size=700,
                                   linewidths=1.0, edgecolors="#1a3a5c")
    if with_numbers:
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                                font_size=9, font_weight="bold",
                                font_family="DejaVu Sans")
    plt.title(title, fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_pdf)
    plt.close()

labels_num = {i: str(i + 1) for i in range(N)}
labels_name = {i: NAMES[i] for i in range(N)}
true_colors = [CLUSTER_IDX[G.nodes[v]["true_cluster"]] for v in G.nodes]
draw_graph(G, POS, labels_num,
           "Социальный граф: 18 вершин, 3 сообщества (истинная раскраска)",
           os.path.join(IMAGES, "social_graph_numbered.pdf"),
           node_color=true_colors)

# ---------------------------спектр Лапласа----------------------------------
plt.figure(figsize=(7.0, 4.4))
plt.stem(range(1, N + 1), w, markerfmt="o", linefmt="#1a3a5c", basefmt=" ")
plt.xlabel("номер собственного числа")
plt.ylabel("собственное число")
plt.title("Собственные числа матрицы Лапласа (n=18)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(GRAPHICS, "laplacian_spectrum.pdf"))
plt.close()

# -----------------------------k-means---------------------------------------
def kmeans(X, k, n_init=20, max_iter=500, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(n_init):
        cents = X[rng.choice(len(X), size=k, replace=False)]
        for _ in range(max_iter):
            d = ((X[:, None, :] - cents[None, :, :]) ** 2).sum(axis=2)
            labels = d.argmin(axis=1)
            new_cents = np.array([X[labels == j].mean(axis=0) if np.any(labels == j)
                                  else cents[j] for j in range(k)])
            if np.allclose(new_cents, cents):
                cents = new_cents
                break
            cents = new_cents
        d = ((X[:, None, :] - cents[None, :, :]) ** 2).sum(axis=2)
        inertia = d[np.arange(len(X)), d.argmin(axis=1)].sum()
        if best is None or inertia < best[0]:
            best = (inertia, labels.copy(), cents.copy())
    return best[1]

K_VALUES = [2, 3, 4, 5, 6]
summary_rows = []

for k in K_VALUES:
    V = U[:, :k]                     # n x k: k собственных векторов к k наименьшим λ
    labels = kmeans(V, k)

    # оценка совпадения с истинной кластеризацией (лучшая перестановка меток)
    true = np.array([CLUSTER_IDX[G.nodes[v]["true_cluster"]]
                     for v in range(N)])
    from itertools import permutations
    best_acc = 0.0
    for perm in permutations(range(k)):
        mapped = np.array([perm[x] for x in labels])
        best_acc = max(best_acc, np.mean(mapped == true))

    # цвета для отрисовки
    node_colors = labels
    draw_graph(G, POS, labels_num,
               f"Кластеризация (k={k}), совпадение с истинной: {best_acc:.0%}",
               os.path.join(IMAGES, f"social_graph_k{k}.pdf"),
               node_color=node_colors, cmap="tab10")

    with open(os.path.join(DATA, f"clustering_k{k}.json"), "w", encoding="utf-8") as f:
        json.dump({
            "k": k,
            "labels": [int(x) for x in labels],
            "true_labels": [int(x) for x in true],
            "accuracy_best_perm": float(best_acc),
        }, f, ensure_ascii=False, indent=2)
    summary_rows.append({"k": k, "accuracy_best_perm": best_acc,
                         "clusters": {str(c): int(np.sum(labels == c))
                                      for c in range(k)}})
    print(f"k={k}: точность (лучшая перестановка) = {best_acc:.0%}")

with open(os.path.join(DATA, "clustering_summary.csv"), "w", newline="",
          encoding="utf-8") as f:
    wtr = csv.DictWriter(f, fieldnames=["k", "accuracy_best_perm", "clusters"])
    wtr.writeheader()
    for r in summary_rows:
        wtr.writerow(r)

# собственные векторы для максимального k (приложение)
maxk = max(K_VALUES)
Vmax = U[:, :maxk]
with open(os.path.join(DATA, f"eigenvectors_k{maxk}.json"), "w", encoding="utf-8") as f:
    json.dump({"k": maxk,
               "vectors": [[float(x) for x in row] for row in Vmax],
               "vertex_names": NAMES}, f, ensure_ascii=False, indent=2)

print("Готово. Данные ->", DATA, "; графики ->", GRAPHICS, "; изображения ->", IMAGES)
