
import tkinter as tk
from tkinter import ttk

C = {
    "bg":       "#0d1f0f",
    "panel":    "#122914",
    "widget":   "#1a3a1e",
    "border":   "#2d6a32",
    "accent":   "#4caf50",
    "accent2":  "#81c784",
    "accent3":  "#a5d6a7",
    "fg":       "#e8f5e9",
    "fg_dim":   "#a5d6a7",
    "text_bg":  "#071008",
    "hdr_bg":   "#0a1f0c",
    "cell_hdr": "#0f2a11",
}

CELL_COLORS = {
    "data":    {"bg": C["text_bg"],  "fg": "#c8e6c9"},
    "col_hdr": {"bg": C["cell_hdr"], "fg": "#81c784"},
    "header":  {"bg": C["cell_hdr"], "fg": "#4caf50"},
    "accent":  {"bg": C["text_bg"],  "fg": "#69f0ae"},
    "pivot":   {"bg": "#1a2a00",     "fg": "#ffcc02"},
    "elim":    {"bg": C["text_bg"],  "fg": "#a5d6a7"},
    "answer":  {"bg": C["text_bg"],  "fg": "#69f0ae"},
    "formula": {"bg": C["text_bg"],  "fg": "#81c784"},
}

CELL_FONT  = ("Consolas", 10)
LABEL_FONT = ("Segoe UI", 10, "bold")
HDR_FONT   = ("Segoe UI", 11, "bold")
SEP_W      = 3   # ширина разделителя | в пикселях


class ReportTab:
    def __init__(self, parent, n_cols: int = 5):
        self.parent = parent
        self.n_cols = n_cols
        self._batch = False

        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0, bd=0)
        vbar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._inner = tk.Frame(self._canvas, bg=C["bg"])
        self._win   = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

    # ── canvas callbacks ────────────────────────────────────────────────── #

    def _on_inner_configure(self, _=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, _=None):
        self._canvas.itemconfig(self._win, width=self._canvas.winfo_width())
        if not self._batch:
            self._on_inner_configure()

    # ── batch ────────────────────────────────────────────────────────────── #

    def begin_batch(self):
        self._batch = True
        self._inner.unbind("<Configure>")
        self._canvas.unbind("<Configure>")

    def end_batch(self):
        self._batch = False
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._inner.update_idletasks()
        self._on_canvas_configure()
        self._on_inner_configure()

    # ── public API ───────────────────────────────────────────────────────── #

    def set_n(self, n: int):
        self.n_cols = n

    def clear(self):
        for w in self._inner.winfo_children():
            w.destroy()

    # ── helpers ──────────────────────────────────────────────────────────── #

    def _scroll_bind(self, widget):
        widget.bind("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

    def _make_cell(self, parent, text, colors, col, row=0, colspan=1):
        """Создаёт tk.Text-ячейку в grid parent'а и возвращает её."""
        cell = tk.Text(parent,
                       height=1, width=1,          # width=1 + weight=1 → растягивается
                       bg=colors["bg"], fg=colors["fg"],
                       font=CELL_FONT,
                       relief="flat", bd=1,
                       padx=4, pady=2,
                       wrap=tk.NONE,
                       selectbackground=C["border"],
                       insertbackground=colors["fg"])
        cell.insert("1.0", str(text))
        cell.configure(state=tk.DISABLED)
        cell.grid(row=row, column=col, columnspan=colspan,
                  padx=1, pady=1, sticky="nsew")
        parent.columnconfigure(col, weight=1, minsize=0)
        self._scroll_bind(cell)
        return cell

    def _make_sep(self, parent, col, row=0):
        """Тонкая колонка-разделитель между ячейками и перед b."""
        lbl = tk.Label(parent, text="│", bg=C["bg"], fg=C["border"],
                       font=CELL_FONT, padx=0)
        lbl.grid(row=row, column=col, padx=0, pady=0, sticky="ns")
        parent.columnconfigure(col, weight=0, minsize=SEP_W)

    # ── layout methods ───────────────────────────────────────────────────── #

    def add_heading(self, text: str, level: int = 1):
        fg   = "#4caf50" if level == 1 else "#81c784"
        font = HDR_FONT  if level == 1 else LABEL_FONT
        lbl  = tk.Label(self._inner, text=text,
                        bg=C["hdr_bg"], fg=fg, font=font,
                        anchor="w", pady=4, padx=8)
        lbl.pack(fill=tk.X, pady=(6 if level == 1 else 2, 1))

    def add_separator(self, color: str = C["border"], height: int = 2):
        tk.Frame(self._inner, bg=color, height=height).pack(
            fill=tk.X, padx=4, pady=2)

    def add_info(self, text: str):
        lbl = tk.Label(self._inner, text=text,
                       bg=C["hdr_bg"], fg="#81c784",
                       font=("Segoe UI", 9), anchor="w",
                       justify=tk.LEFT, padx=12, pady=3)
        lbl.pack(fill=tk.X, pady=1)

    def add_text_line(self, text: str, color: str = "#c8e6c9",
                      bold: bool = False, indent: int = 0):
        font = ("Segoe UI", 9, "bold") if bold else ("Segoe UI", 9)
        lbl  = tk.Label(self._inner, text=text,
                        bg=C["bg"], fg=color, font=font,
                        anchor="w", padx=8 + indent*8, pady=1)
        lbl.pack(fill=tk.X)

    def add_matrix_row(self, values: list, kind: str = "data"):
        """
        Строка таблицы из len(values) ячеек.
        Последняя ячейка отделяется разделителем │ (кроме col_hdr).

        Схема колонок grid:
          0     1     2     3   …   2k    2k+1
          cell  cell  cell  cell    sep   cell_last
        """
        colors    = CELL_COLORS.get(kind, CELL_COLORS["data"])
        row_frame = tk.Frame(self._inner, bg=C["bg"])
        row_frame.pack(fill=tk.X, pady=1)

        n = len(values)
        has_sep = (kind != "col_hdr") and n > 1   # разделитель перед последней

        for j, val in enumerate(values):
            is_last = (j == n - 1)
            if is_last and has_sep:
                col = (n - 1) * 2          # sep на чётной позиции
                self._make_sep(row_frame, col)
                self._make_cell(row_frame, val, colors, col + 1)
            else:
                self._make_cell(row_frame, val, colors, j)

    def add_compact_row(self, row_label: str, values: list,
                        kind: str = "data", label_color: str = "#ffcc02"):
        """Строка с меткой слева + ячейки значений."""
        colors    = CELL_COLORS.get(kind, CELL_COLORS["data"])
        row_frame = tk.Frame(self._inner, bg=C["bg"])
        row_frame.pack(fill=tk.X, pady=1)

        # Метка (фиксированная ширина, weight=0)
        lbl = tk.Label(row_frame, text=row_label,
                       bg=C["bg"], fg=label_color,
                       font=("Consolas", 9, "bold"),
                       anchor="e", width=6)
        lbl.grid(row=0, column=0, padx=(2, 1), sticky="ns")
        row_frame.columnconfigure(0, weight=0, minsize=50)

        n = len(values)
        for j, val in enumerate(values):
            is_last = (j == n - 1)
            col = j + 1          # +1 из-за метки
            if is_last and n > 1:
                self._make_sep(row_frame, col)
                self._make_cell(row_frame, val, colors, col + 1)
            else:
                self._make_cell(row_frame, val, colors, col)

    def add_kv_row(self, key: str, value: str,
                   key_color: str = "#81c784",
                   val_color: str = "#69f0ae"):
        """Строка ключ — значение."""
        row_frame = tk.Frame(self._inner, bg=C["bg"])
        row_frame.pack(fill=tk.X, pady=1)

        tk.Label(row_frame, text=key,
                 bg=C["bg"], fg=key_color,
                 font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=8, width=20).pack(side=tk.LEFT)

        cell = tk.Text(row_frame, height=1, width=1,
                       bg=C["text_bg"], fg=val_color,
                       font=CELL_FONT, relief="flat", bd=0,
                       padx=6, pady=2, wrap=tk.NONE,
                       selectbackground=C["border"])
        cell.insert("1.0", value)
        cell.configure(state=tk.DISABLED)
        cell.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._scroll_bind(cell)

    def add_formula_row(self, step_label: str, formula: str,
                        numeric: str = "", result: str = ""):
        """Блок формулы обратного хода."""
        wrap = tk.Frame(self._inner, bg=C["bg"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        wrap.pack(fill=tk.X, padx=4, pady=2)
        wrap.columnconfigure(1, weight=1)

        tk.Label(wrap, text=step_label,
                 bg=C["bg"], fg="#ffcc02",
                 font=("Consolas", 10, "bold"),
                 anchor="nw", padx=8, width=10).grid(
            row=0, column=0, rowspan=3, sticky="nw")

        def _cell(text, fg, row):
            c = tk.Text(wrap, height=1, width=1,
                        bg=C["text_bg"], fg=fg,
                        font=CELL_FONT, relief="flat", bd=0,
                        padx=4, pady=1, wrap=tk.NONE,
                        selectbackground=C["border"])
            c.insert("1.0", text)
            c.configure(state=tk.DISABLED)
            c.grid(row=row, column=1, sticky="ew", padx=4, pady=1)
            self._scroll_bind(c)

        _cell(formula, "#81c784", 0)
        if numeric:
            _cell(numeric, "#a5d6a7", 1)
        if result:
            _cell(f"➜  {result}", "#69f0ae", 2)
