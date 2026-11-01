#!/usr/bin/env python3
"""Task 2. Latent Semantic Analysis (LSA) via SVD.

Corpus: data/corpus.txt (each line is a document; own Russian corpus, see
WORKLOG assumptions). Steps: remove punctuation, tokenize, lemmatize (own
dictionary, assumption: pymorphy2 not installed), remove stop-words (own list,
assumption: nltk not installed), term-document matrix, SVD, topic analysis,
two word clouds (matplotlib, assumption: wordcloud not installed).
Outputs: data/corpus_preprocessed.txt, data/terms.csv, data/lsa_top_words.csv,
graphics/lsa_*.png. Run: python3 prog/lsa.py (from lab_6 root).
"""

import os
import re
import string
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GRAPHICS = os.path.join(ROOT, "graphics")

CORPUS = os.path.join(DATA, "corpus.txt")
PREPROCESSED = os.path.join(DATA, "corpus_preprocessed.txt")
TERMS_CSV = os.path.join(DATA, "terms.csv")
TOP_WORDS_CSV = os.path.join(DATA, "lsa_top_words.csv")

STOP_WORDS = {
    "и", "в", "на", "с", "для", "по", "а", "или", "как", "не", "это", "из",
    "у", "от", "к", "о", "за", "под", "над", "при", "без", "между", "во",
    "без", "через", "но", "да", "же", "бы", "быть", "он",
    "она", "они", "мы", "вы", "я", "его", "ее", "их", "им", "них", "от",
    "то", "тоже", "уже", "только", "еще", "ли", "если", "тогда",
}

LEMMA_MAP = {}
_VARIANTS_TO_LEMMA = {
    "язык": "язык", "языки": "язык",
    "программирование": "программирование",
    "используется": "использовать", "применяются": "применять", "реализуются": "реализовать",
    "разработка": "разработка", "разработке": "разработка", "разработки": "разработка",
    "программ": "программа", "программы": "программа", "программа": "программа",
    "питон": "питон", "python": "питон",
    "джава": "джава", "java": "джава",
    "с++": "с плюс плюс", "с плюс плюс": "с плюс плюс",
    "код": "код", "коды": "код",
    "алгоритм": "алгоритм", "алгоритмы": "алгоритм",
    "сортировка": "сортировка",
    "поиск": "поиск",
    "футбол": "футбол", "футболу": "футбол",
    "команда": "команда", "команды": "команда", "команду": "команда",
    "чемпионат": "чемпионат",
    "спортсмен": "спортсмен", "спортсменов": "спортсмен",
    "баскетбол": "баскетбол", "баскетбольный": "баскетбол",
    "матч": "матч", "матче": "матч", "матча": "матч",
    "теннис": "теннис", "теннисный": "теннис",
    "турнир": "турнир",
    "хоккей": "хоккей", "хоккейная": "хоккей", "хоккею": "хоккей",
    "стадион": "стадион",
    "рецепт": "рецепт",
    "пицца": "пицца",
    "томат": "томат", "томаты": "томат",
    "сыр": "сыр",
    "кухня": "кухня", "кухне": "кухня",
    "выпечка": "выпечка",
    "хлеб": "хлеб",
    "торт": "торт",
    "мука": "мука",
    "сахар": "сахар",
    "готовится": "готовить",
    "выполняется": "выполнять",
    "прошли": "проходить",
    "играла": "играть",
    "выиграла": "выиграть",
}
for _form, _lemma in _VARIANTS_TO_LEMMA.items():
    LEMMA_MAP[_form] = _lemma


def lemmatize(word):
    return LEMMA_MAP.get(word, word)


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [lemmatize(t) for t in text.split() if len(t) >= 2]
    return [t for t in tokens if t not in STOP_WORDS]


def build_term_document_matrix(doc_tokens):
    vocab = sorted({t for doc in doc_tokens for t in doc})
    index = {t: i for i, t in enumerate(vocab)}
    M = np.zeros((len(vocab), len(doc_tokens)), dtype=np.float64)
    for j, doc in enumerate(doc_tokens):
        for t in doc:
            M[index[t], j] += 1.0
    return vocab, M


def save_wordcloud(weights, terms, path, title, top_n=40):
    order = np.argsort(np.abs(weights))[::-1][:top_n]
    sel_terms = [terms[i] for i in order]
    sel_weights = np.abs(weights[order])
    if sel_weights.max() > 0:
        sel_weights = sel_weights / sel_weights.max()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    ax.set_title(title, fontsize=12, pad=12)
    rng = np.random.default_rng(7)
    for i, (term, w) in enumerate(zip(sel_terms, sel_weights)):
        x = rng.uniform(5, 95)
        y = rng.uniform(5, 55)
        size = 10 + 40 * w
        ax.text(x, y, term, fontsize=size, ha="center", va="center",
                color=(0.2, 0.4, 0.8 + 0.2 * w), alpha=0.85)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(GRAPHICS, exist_ok=True)

    with open(CORPUS, encoding="utf-8") as f:
        raw_docs = [line.strip() for line in f if line.strip()]

    print(f"Documents in corpus: {len(raw_docs)}")

    doc_tokens = [preprocess(d) for d in raw_docs]
    with open(PREPROCESSED, "w", encoding="utf-8") as f:
        for i, toks in enumerate(doc_tokens, 1):
            f.write(f"Document {i}: {' '.join(toks)}\n")

    vocab, M = build_term_document_matrix(doc_tokens)
    print(f"Dictionary size: {len(vocab)} terms; matrix {M.shape[0]}x{M.shape[1]}")

    with open(TERMS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["term"] + [f"doc{d+1}" for d in range(M.shape[1])])
        for i, term in enumerate(vocab):
            w.writerow([term] + [f"{v:.4f}" for v in M[i, :]])

    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    total_energy = float(np.sum(s ** 2))

    print("\nSingular numbers:")
    for i, sv in enumerate(s[:8], 1):
        print(f"  sigma_{i} = {sv:.4f}  energy = {np.sum(s[:i] ** 2) / total_energy:.4f}")

    rows = []
    for comp in (1, 2):
        u = U[:, comp - 1]
        top_idx = np.argsort(np.abs(u))[::-1][:5]
        top_words = [(vocab[i], float(u[i])) for i in top_idx]
        v = Vt[comp - 1, :]
        top_docs_idx = np.argsort(np.abs(v))[::-1][:3]
        top_docs = [(int(d) + 1, float(v[d])) for d in top_docs_idx]
        rows.append({"component": comp, "sigma": float(s[comp - 1]),
                     "words": "; ".join(f"{w} ({val:+.3f})" for w, val in top_words),
                     "documents": "; ".join(f"doc{d} ({val:+.3f})" for d, val in top_docs)})
        print(f"\nTheme {comp} (left singular vector, sigma={s[comp-1]:.4f}):")
        for w, val in top_words:
            print(f"   {w}: {val:+.4f}")
        print("   Top documents:", top_docs)

    with open(TOP_WORDS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["component", "sigma", "top_5_words", "top_documents"])
        for r in rows:
            w.writerow([r["component"], r["sigma"], r["words"], r["documents"]])

    plt.figure(figsize=(7, 4))
    plt.semilogy(s, marker="o", markersize=4, lw=1.4)
    plt.xlabel("Index of singular number")
    plt.ylabel("Singular number (log scale)")
    plt.title("Singular numbers of term-document matrix (LSA)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "lsa_singular_values.png"), dpi=300)
    plt.close()

    save_wordcloud(U[:, 0], vocab,
                   os.path.join(GRAPHICS, "lsa_wordcloud_theme1.png"),
                   "Theme 1 — word cloud (left singular vector #1)")
    save_wordcloud(U[:, 1], vocab,
                   os.path.join(GRAPHICS, "lsa_wordcloud_theme2.png"),
                   "Theme 2 — word cloud (left singular vector #2)")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), sharey=True)
    for ax, comp in zip(axes, (1, 2)):
        v = Vt[comp - 1, :]
        docs = [f"Doc {d+1}" for d in range(M.shape[1])]
        colors = ["tab:red" if val > 0 else "tab:blue" for val in v]
        ax.bar(docs, v, color=colors, alpha=0.7)
        ax.set_title(f"Theme {comp} by documents (row {comp} of V^T)")
        ax.set_ylabel("Document weight in theme")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    plt.savefig(os.path.join(GRAPHICS, "lsa_document_topics.png"), dpi=300)
    plt.close()

    print("Done.")


if __name__ == "__main__":
    main()
