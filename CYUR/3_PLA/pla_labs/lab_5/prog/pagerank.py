"""Задание 2. Google PageRank (ориентированный граф, столбцово-нормированная M).

Строит связный ориентированный граф из 12 вершин и 43 дуг, составляет матрицу M,
находит собственный вектор к наибольшему собственному числу, считает PageRank при
d=1 и при других d, сохраняет данные, графики и рисунок графа.
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

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BASE)
DATA = os.path.join(PROJ, "data")
GRAPHICS = os.path.join(PROJ, "graphics")
IMAGES = os.path.join(PROJ, "images")
for d in (DATA, GRAPHICS, IMAGES):
    os.makedirs(d, exist_ok=True)

# -----------------------ориентированный веб-граф--------------------------
PAGES = ["главная", "новости", "контакты", "каталог", "товар 1", "товар 2",
         "товар 3", "блог", "о нас", "поиск", "корзина", "вопросы"]
N = len(PAGES)

# дуги (источник, цель); из каждой вершины >= 1 исходящей
EDGES = [
    (0, 1), (0, 3), (0, 7), (0, 8), (0, 9),            # главная
    (1, 0), (1, 7), (1, 4),                            # новости
    (2, 0), (2, 8),                                    # контакты
    (3, 0), (3, 4), (3, 5), (3, 6),                    # каталог
    (4, 0), (4, 3), (4, 10), (4, 11),                  # товар 1
    (5, 0), (5, 3), (5, 10),                           # товар 2
    (6, 0), (6, 3), (6, 10), (6, 11),                  # товар 3
    (7, 0), (7, 1), (7, 4), (7, 5),                    # блог
    (8, 0), (8, 2), (8, 11),                           # о нас
    (9, 0), (9, 4), (9, 5), (9, 6),                    # поиск
    (10, 0), (10, 4), (10, 5), (10, 6), (10, 11),      # корзина
    (11, 0), (11, 2),                                  # вопросы
]

G = nx.DiGraph()
G.add_nodes_from(range(N))
for i in range(N):
    G.nodes[i]["name"] = PAGES[i]
G.add_edges_from(EDGES)

out_deg = np.array([G.out_degree(i) for i in range(N)])
assert np.all(out_deg >= 1), "каждая вершина должна иметь исходящую дугу"
print("Задание 2: вершин =", G.number_of_nodes(), ", дуг =", G.number_of_edges(),
      ", связан (неор.) =", nx.is_connected(nx.Graph(G)))

# матрица M: M[i, j] = (# дуг j->i) / (исходящих из j)
A = np.zeros((N, N), dtype=float)  # A[i, j] = число дуг j -> i
for s, t in EDGES:
    A[t, s] += 1
M = A / out_deg[None, :]           # нормируем столбцы
assert np.allclose(M.sum(axis=0), 1.0), "столбцы M должны суммироваться в 1"

np.savetxt(os.path.join(DATA, "pagerank_edges.csv"), EDGES, delimiter=",",
           fmt="%d", header="source,target", comments="")
np.savetxt(os.path.join(DATA, "pagerank_M.csv"), M, delimiter=",", fmt="%.6f")

# собственные числа/векторы M
vals, vecs = np.linalg.eig(M)
vals = np.real(vals)
vecs = np.real(vecs)
order = np.argsort(-np.abs(vals))
vals = vals[order]
vecs = vecs[:, order]
lam_max = vals[0]
v_max = np.real(vecs[:, 0])
v_max = v_max / v_max.sum()        # нормируем сумма = 1
if v_max.sum() < 0:
    v_max = -v_max

np.savetxt(os.path.join(DATA, "pagerank_eigenvalues.csv"), vals,
           delimiter=",", fmt="%.10f")
with open(os.path.join(DATA, "pagerank_eigenvector_max.json"), "w",
          encoding="utf-8") as f:
    json.dump({
        "lambda_max": float(lam_max),
        "vector": [float(x) for x in v_max],
        "pages": PAGES,
    }, f, ensure_ascii=False, indent=2)

print("lambda_max =", lam_max)
print("собственный вектор (страница: ранг):")
for name, val in sorted(zip(PAGES, v_max), key=lambda x: -x[1]):
    print(f"  {name:10s} {val:.4f}")

# ---------------------------PageRank при d------------------------------
def pagerank(M, d, n_iter=10000, tol=1e-12):
    n = M.shape[0]
    r = np.ones(n) / n
    teleport = np.ones(n) / n
    for _ in range(n_iter):
        r_new = d * (M @ r) + (1 - d) * teleport
        if np.linalg.norm(r_new - r, 1) < tol:
            return r_new
        r = r_new
    return r

D_VALUES = [1.0, 0.85, 0.5, 0.15]
pr_results = {}
for d in D_VALUES:
    r = pagerank(M, d)
    pr_results[str(d)] = [float(x) for x in r]
    order_pr = np.argsort(-r)
    print(f"d={d}:", " > ".join(f"{PAGES[i]} ({r[i]:.3f})" for i in order_pr))

with open(os.path.join(DATA, "pagerank_results.json"), "w", encoding="utf-8") as f:
    json.dump({"d_values": D_VALUES, "pages": PAGES, "results": pr_results},
              f, ensure_ascii=False, indent=2)

# ---------------------------отрисовка графа-----------------------------
pos = nx.circular_layout(G)
plt.figure(figsize=(8, 6))
ax = plt.gca()
nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#9ecae1", node_size=900,
                       linewidths=1.0, edgecolors="#1a3a5c")
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, arrowstyle="-|>",
                       arrowsize=14, width=1.4, edge_color="#6b6b6b",
                       connectionstyle="arc3,rad=0.12")
nx.draw_networkx_labels(G, pos, labels={i: f"{i+1}\n{PAGES[i]}" for i in range(N)},
                        ax=ax, font_size=8, font_weight="bold")
plt.title("Ориентированный веб-граф PageRank: 12 страниц, 43 ссылки",
          fontsize=11)
plt.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(IMAGES, "web_graph_numbered.pdf"))
plt.close()

# ---------------------------графики-------------------------------------
# PageRank при разных d (столбчатая диаграмма)
x = np.arange(N)
width = 0.2
plt.figure(figsize=(9, 4.2))
for i, d in enumerate(D_VALUES):
    r = np.array(pr_results[str(d)])
    plt.bar(x + (i - 1.5) * width, r, width, label=f"d={d}")
plt.xticks(x, [f"{i+1}\n{PAGES[i]}" for i in range(N)], fontsize=7)
plt.ylabel("PageRank")
plt.title("PageRank страниц при разных значениях d")
plt.legend(fontsize=9)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(GRAPHICS, "pagerank.pdf"))
plt.close()

# модули собственных чисел M (спектр)
plt.figure(figsize=(7, 4.2))
plt.stem(range(1, N + 1), np.abs(vals), markerfmt="o",
         linefmt="#1a3a5c", basefmt=" ")
plt.axhline(1.0, color="#c0392b", linestyle="--", linewidth=1, label="|λ|=1")
plt.xlabel("номер собственного числа")
plt.ylabel("|собственное число|")
plt.title("Спектр матрицы M PageRank (n=12)")
plt.grid(alpha=0.3)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GRAPHICS, "pagerank_spectrum.pdf"))
plt.close()

print("Готово. Данные ->", DATA, "; графики ->", GRAPHICS, "; изображения ->", IMAGES)
