import tkinter as tk
from tkinter import ttk, messagebox

from solver import gauss_solve_with_steps
from loader import read_from_keyboard, read_from_file, browse_file
from results import display_solution, display_forward, display_backward, display_comparison
from table_widget import ReportTab

# ── Палитра тёмно-зелёной темы ──────────────────────────────────────────── #
C = {
    "bg":          "#0d1f0f",   # фон окна (очень тёмный зелёный)
    "panel":       "#122914",   # фон панелей
    "widget":      "#1a3a1e",   # фон виджетов (Entry, Text)
    "border":      "#2d6a32",   # рамки и разделители
    "accent":      "#4caf50",   # основной акцент (яркий зелёный)
    "accent2":     "#81c784",   # второй акцент (светло-зелёный)
    "accent3":     "#a5d6a7",   # третий акцент (бледно-зелёный)
    "fg":          "#e8f5e9",   # основной текст (почти белый с зелёным оттенком)
    "fg_dim":      "#a5d6a7",   # приглушённый текст
    "btn":         "#1b5e20",   # фон кнопок
    "btn_active":  "#2e7d32",   # фон кнопок при hover
    "btn_accent":  "#388e3c",   # акцентная кнопка «Решить»
    "text_bg":     "#071008",   # фон текстовых областей
    "scrollbar":   "#2d6a32",
}

GAUSS_CODE = """def gauss_solve_with_steps(A, b):
    n = len(A)
    forward_steps  = []
    backward_steps = []
    _store_matrix = (n <= 9)

    # Счётчик перестановок для знака определителя
    swap_count = 0

    aug = mat_hstack(A, b)
    forward_steps.append(("initial", "Начальная расширенная матрица [A|b]", mat_copy(aug)))

    for i in range(n):
        # ── Partial pivoting: ищем строку с макс. |элементом| в столбце i ──
        max_row = i
        max_val = abs(aug[i][i])
        for r in range(i + 1, n):
            if abs(aug[r][i]) > max_val:
                max_val = abs(aug[r][i])
                max_row = r

        if max_val < 1e-15:
            raise ValueError(
                f"Все элементы столбца {i+1} ниже строки {i+1} равны нулю — "
                f"матрица вырождена (система несовместна или имеет бесконечно много решений)"
            )

        if max_row != i:
            aug[i], aug[max_row] = aug[max_row], aug[i]
            swap_count += 1
            forward_steps.append((
                "swap",
                f"Итерация {i+1}: перестановка строк {i+1} <-> {max_row+1}"
                f"  (ведущий элемент |{aug[i][i]:.6f}|)",
                mat_copy(aug) if _store_matrix else None
            ))

        pivot = aug[i][i]

        forward_steps.append((
            "pivot",
            f"Итерация {i+1}: ведущий элемент  a[{i+1},{i+1}] = {pivot:.6f}",
            mat_copy(aug) if _store_matrix else None
        ))

        for j in range(i + 1, n):
            factor = aug[j][i] / pivot
            if abs(factor) > 1e-15:
                forward_steps.append((
                    "eliminate",
                    f"Строка {j+1}  −  ({factor:.6f}) · Строка {i+1}"
                    f"   [обнуляем a[{j+1},{i+1}]]",
                    None          # матрицу не копируем — она будет в result
                ))
                for k in range(i, n + 1):
                    aug[j][k] -= factor * aug[i][k]
                forward_steps.append((
                    "result",
                    f"Результат после исключения x{i+1} из строки {j+1}",
                    # При большой матрице храним только изменённую строку: (j, row_copy)
                    mat_copy(aug) if _store_matrix else ("row", j, aug[j][:])
                ))

    forward_steps.append((
        "final",
        "Верхняя треугольная матрица после прямого хода",
        mat_copy(aug)
    ))

    det_product = 1.0
    for i in range(n):
        det_product *= aug[i][i]
    # Каждая перестановка строк меняет знак определителя
    if swap_count % 2 == 1:
        det_product = -det_product

    x = [0.0] * n

    for i in range(n - 1, -1, -1):
        diag  = aug[i][i]
        rhs   = aug[i][n]
        sub_terms = [(aug[i][k], k) for k in range(i + 1, n)]

        if not sub_terms:
            formula = (f"x{i+1} = b'[{i+1}] / a'[{i+1},{i+1}]"
                       f" = {rhs:.6f} / {diag:.6f}")
        else:
            parts = "  +  ".join(
                f"({c:+.6f})·x{k+1}" for c, k in sub_terms
            )
            formula = (f"x{i+1} = ( {rhs:.6f}  −  [ {parts} ] )"
                       f" / {diag:.6f}")

        val = rhs
        for coef, k in sub_terms:
            val -= coef * x[k]
        x[i] = val / diag

        if sub_terms:
            num_parts = "  +  ".join(
                f"({c:+.6f})·({x[k]:.6f})" for c, k in sub_terms
            )
            numeric = (f"         = ( {rhs:.6f}  −  [ {num_parts} ] )"
                       f" / {diag:.6f}")
        else:
            numeric = f"         = {rhs:.6f} / {diag:.6f}"

        backward_steps.append((
            i,
            x[i],
            formula,
            numeric,
            [c for c, _ in sub_terms]
        ))

    return x, aug, forward_steps, backward_steps, det_product"""


class GaussMethodGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Метод Гаусса - Решение СЛАУ")
        self.root.attributes('-fullscreen', False)
        self.root.resizable(True, True)

        # Данные
        self.A = None
        self.b = None
        self.n = 0

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_widgets()

    # ------------------------------------------------------------------ #
    #  Стили                                                               #
    # ------------------------------------------------------------------ #

    def _setup_styles(self):
        """Настройка тёмно-зелёной темы для всех виджетов"""
        style = ttk.Style()
        style.theme_use('clam')

        # ── Базовые цвета ───────────────────────────────────────────── #
        self.root.configure(bg=C["bg"])

        # Frame / LabelFrame
        style.configure("TFrame",       background=C["panel"])
        style.configure("TLabelframe",  background=C["panel"],
                        foreground=C["accent2"], relief="flat")
        style.configure("TLabelframe.Label",
                        background=C["panel"], foreground=C["accent"],
                        font=("Segoe UI", 9, "bold"))

        # Label
        style.configure("TLabel",
                        background=C["panel"], foreground=C["fg"],
                        font=("Segoe UI", 10))

        # Entry
        style.configure("TEntry",
                        fieldbackground=C["widget"],
                        foreground=C["accent3"],
                        insertcolor=C["accent"],
                        bordercolor=C["border"],
                        lightcolor=C["border"],
                        darkcolor=C["border"],
                        font=("Consolas", 10))
        style.map("TEntry", bordercolor=[("focus", C["accent"])])

        # Button
        style.configure("TButton",
                        background=C["btn"], foreground=C["fg"],
                        font=("Segoe UI", 9, "bold"),
                        bordercolor=C["border"],
                        focuscolor=C["accent"],
                        relief="flat", padding=(8, 4))
        style.map("TButton",
                  background=[("active", C["btn_active"]),
                              ("pressed", C["border"])],
                  foreground=[("active", C["accent"])])

        # Accent Button (для «РЕШИТЬ СИСТЕМУ»)
        style.configure("Accent.TButton",
                        background=C["btn_accent"], foreground=C["fg"],
                        font=("Segoe UI", 11, "bold"),
                        bordercolor=C["accent"],
                        relief="flat", padding=(10, 6))
        style.map("Accent.TButton",
                  background=[("active", C["accent"]),
                              ("pressed", C["accent2"])],
                  foreground=[("active", "#ffffff")])

        # Radiobutton
        style.configure("TRadiobutton",
                        background=C["panel"], foreground=C["fg_dim"],
                        font=("Segoe UI", 9),
                        focuscolor=C["panel"])
        style.map("TRadiobutton",
                  foreground=[("selected", C["accent"]),
                              ("active", C["accent2"])],
                  background=[("active", C["panel"])])

        # Notebook (вкладки)
        style.configure("TNotebook",
                        background=C["bg"], bordercolor=C["border"],
                        tabmargins=[2, 4, 0, 0])
        style.configure("TNotebook.Tab",
                        background=C["panel"], foreground=C["fg_dim"],
                        font=("Segoe UI", 9, "bold"),
                        padding=[14, 6],
                        bordercolor=C["border"])
        style.map("TNotebook.Tab",
                  background=[("selected", C["widget"]),
                              ("active", C["btn_active"])],
                  foreground=[("selected", C["accent"]),
                              ("active", C["accent2"])])

        # Scrollbar
        style.configure("TScrollbar",
                        background=C["panel"], troughcolor=C["bg"],
                        bordercolor=C["border"],
                        arrowcolor=C["accent2"], relief="flat")
        style.map("TScrollbar",
                  background=[("active", C["border"])])

    # ------------------------------------------------------------------ #
    #  Компоновка главного окна                                           #
    # ------------------------------------------------------------------ #

    def _create_widgets(self):
        """Создание всех элементов интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        left_panel = ttk.Frame(main_frame, width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 4))
        left_panel.pack_propagate(False)

        # Тонкий вертикальный разделитель
        sep = tk.Frame(main_frame, width=2, bg=C["border"])
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_input_panel(left_panel)
        self._create_results_panel(right_panel)

    # ------------------------------------------------------------------ #
    #  Левая панель — ввод данных                                         #
    # ------------------------------------------------------------------ #

    def _create_input_panel(self, parent):
        """Панель ввода данных"""
        # Заголовок
        hdr = tk.Label(parent, text="⬡  ВВОД ДАННЫХ",
                       bg=C["panel"], fg=C["accent"],
                       font=("Segoe UI", 13, "bold"), anchor="w")
        hdr.pack(fill=tk.X, padx=8, pady=(10, 2))
        tk.Frame(parent, height=2, bg=C["accent"]).pack(fill=tk.X, padx=8, pady=(0, 8))

        # Размерность
        size_frame = ttk.Frame(parent)
        size_frame.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(size_frame, text="Размерность n (≤ 20):").pack(side=tk.LEFT, padx=(0, 6))
        self.n_entry = ttk.Entry(size_frame, width=6)
        self.n_entry.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(size_frame, text="Задать", command=self._set_dimension).pack(side=tk.LEFT)

        # Способ ввода
        input_type_frame = ttk.LabelFrame(parent, text="Способ ввода", padding=(8, 6))
        input_type_frame.pack(fill=tk.X, padx=8, pady=8)

        self.input_var = tk.StringVar(value="keyboard")
        ttk.Radiobutton(input_type_frame, text="С клавиатуры",
                        variable=self.input_var, value="keyboard",
                        command=self._toggle_input_method).pack(anchor=tk.W)
        ttk.Radiobutton(input_type_frame, text="Из файла",
                        variable=self.input_var, value="file",
                        command=self._toggle_input_method).pack(anchor=tk.W, pady=(4, 0))

        # ---- Фрейм для клавиатурного ввода ----
        self.keyboard_frame = ttk.Frame(parent)

        ttk.Label(self.keyboard_frame, text="Матрица A:").pack(anchor=tk.W, padx=8, pady=(8, 4))

        # ── Canvas + горизонтальный скроллбар для матрицы ──
        matrix_scroll_area = ttk.Frame(self.keyboard_frame)
        matrix_scroll_area.pack(fill=tk.BOTH, padx=8, pady=2)

        self.matrix_canvas = tk.Canvas(matrix_scroll_area,
                                       bg=C["panel"], highlightthickness=0,
                                       height=1)          # высота подстроится позже
        mat_hbar = ttk.Scrollbar(matrix_scroll_area, orient=tk.HORIZONTAL,
                                 command=self.matrix_canvas.xview)
        self.matrix_canvas.configure(xscrollcommand=mat_hbar.set)

        self.matrix_canvas.pack(side=tk.TOP, fill=tk.X, expand=False)
        mat_hbar.pack(side=tk.TOP, fill=tk.X)

        self.matrix_frame = ttk.Frame(self.matrix_canvas)
        self._matrix_win = self.matrix_canvas.create_window(
            (0, 0), window=self.matrix_frame, anchor="nw")
        self.matrix_frame.bind("<Configure>", self._on_matrix_configure)
        self.matrix_entries = []

        ttk.Label(self.keyboard_frame, text="Вектор правых частей b:").pack(anchor=tk.W, padx=8, pady=(10, 4))

        # ── Canvas + горизонтальный скроллбар для вектора b ──
        vector_scroll_area = ttk.Frame(self.keyboard_frame)
        vector_scroll_area.pack(fill=tk.BOTH, padx=8, pady=2)

        self.vector_canvas = tk.Canvas(vector_scroll_area,
                                       bg=C["panel"], highlightthickness=0,
                                       height=30)
        vec_hbar = ttk.Scrollbar(vector_scroll_area, orient=tk.HORIZONTAL,
                                 command=self.vector_canvas.xview)
        self.vector_canvas.configure(xscrollcommand=vec_hbar.set)

        self.vector_canvas.pack(side=tk.TOP, fill=tk.X, expand=False)
        vec_hbar.pack(side=tk.TOP, fill=tk.X)

        self.vector_frame = ttk.Frame(self.vector_canvas)
        self._vector_win = self.vector_canvas.create_window(
            (0, 0), window=self.vector_frame, anchor="nw")
        self.vector_frame.bind("<Configure>", self._on_vector_configure)
        self.vector_entries = []

        ttk.Button(self.keyboard_frame, text="✔  Ввести данные",
                   command=self._on_read_keyboard).pack(pady=10)

        # ---- Фрейм для ввода из файла ----
        self.file_frame = ttk.Frame(parent)

        ttk.Label(self.file_frame, text="Выберите файл с данными:").pack(padx=8, pady=(8, 4), anchor=tk.W)

        file_entry_frame = ttk.Frame(self.file_frame)
        file_entry_frame.pack(fill=tk.X, padx=8, pady=4)

        self.file_path = ttk.Entry(file_entry_frame)
        self.file_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(file_entry_frame, text="Обзор", command=self._on_browse_file).pack(side=tk.RIGHT)
        ttk.Button(self.file_frame, text="⬇  Загрузить", command=self._on_read_file).pack(pady=8)

        # ---- Разделитель ----
        tk.Frame(parent, height=1, bg=C["border"]).pack(fill=tk.X, padx=8, pady=6)

        # ---- Акцентная кнопка расчёта ----
        self.calc_button = ttk.Button(parent, text="▶  РЕШИТЬ СИСТЕМУ",
                                      style="Accent.TButton",
                                      command=self._calculate, state=tk.DISABLED)
        self.calc_button.pack(fill=tk.X, padx=16, pady=(8, 4))

        ttk.Button(parent, text="↺  Сбросить всё", command=self._reset_all).pack(padx=16, pady=4, fill=tk.X)

        # По умолчанию показываем клавиатурный ввод
        self.keyboard_frame.pack(fill=tk.X)
        self.file_frame.pack_forget()

    # ------------------------------------------------------------------ #
    #  Правая панель — вкладки результатов                                #
    # ------------------------------------------------------------------ #

    def _create_results_panel(self, parent):
        """Панель результатов с вкладками"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.solution_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.solution_frame, text="Решение")

        self.code_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.code_frame, text="Код метода")

        self.forward_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forward_frame, text="Прямой ход")

        self.backward_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backward_frame, text="Обратный ход")

        self.compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_frame, text="Сравнение с NumPy")

        self._create_solution_tab()
        self._create_code_tab()
        self._create_forward_tab()
        self._create_backward_tab()
        self._create_compare_tab()

    def _create_solution_tab(self):
        self.solution_tab = ReportTab(self.solution_frame, n_cols=5)

    def _create_code_tab(self):
        code_text = tk.Text(self.code_frame, wrap=tk.WORD,
                            bg=C["text_bg"], fg=C["accent3"],
                            font=("Consolas", 11),
                            insertbackground=C["accent"],
                            selectbackground=C["border"],
                            relief="flat", padx=10, pady=8)
        code_text.insert(tk.END, GAUSS_CODE)
        code_text.config(state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(self.code_frame, command=code_text.yview)
        code_text.configure(yscrollcommand=scrollbar.set)
        code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_forward_tab(self):
        self.forward_tab = ReportTab(self.forward_frame, n_cols=5)

    def _create_backward_tab(self):
        self.backward_tab = ReportTab(self.backward_frame, n_cols=5)

    def _create_compare_tab(self):
        self.compare_tab = ReportTab(self.compare_frame, n_cols=3)

    def _on_matrix_configure(self, event=None):
        """Обновляет scrollregion и высоту canvas при изменении размера матрицы."""
        self.matrix_frame.update_idletasks()
        w = self.matrix_frame.winfo_reqwidth()
        h = self.matrix_frame.winfo_reqheight()
        self.matrix_canvas.configure(scrollregion=(0, 0, w, h), height=h)

    def _on_vector_configure(self, event=None):
        """Обновляет scrollregion и высоту canvas вектора b."""
        self.vector_frame.update_idletasks()
        w = self.vector_frame.winfo_reqwidth()
        h = self.vector_frame.winfo_reqheight()
        self.vector_canvas.configure(scrollregion=(0, 0, w, h), height=h)

    # ------------------------------------------------------------------ #
    #  Управление размерностью и полями ввода                             #
    # ------------------------------------------------------------------ #

    def _toggle_input_method(self):
        """Переключение между способами ввода"""
        if self.input_var.get() == "keyboard":
            # Не даём переключиться на ручной ввод если n > 9
            if self.n > 9:
                messagebox.showinfo(
                    "Ограничение",
                    "Ручной ввод доступен только для матриц до 9×9.\n"
                    "Используйте загрузку из файла."
                )
                self.input_var.set("file")
                return
            self.keyboard_frame.pack(fill=tk.X, pady=10)
            self.file_frame.pack_forget()
        else:
            self.keyboard_frame.pack_forget()
            self.file_frame.pack(fill=tk.X, pady=10)

    def _set_dimension(self):
        """Установка размерности системы"""
        try:
            n = int(self.n_entry.get())
            if n <= 0 or n > 20:
                messagebox.showerror("Ошибка", "Размерность должна быть от 1 до 20")
                return

            # Ручной ввод ограничен матрицей 9×9
            if n > 9 and self.input_var.get() == "keyboard":
                messagebox.showinfo(
                    "Ограничение",
                    f"Ручной ввод доступен только для матриц размером до 9×9.\n"
                    f"Для n = {n} используйте загрузку из файла."
                )
                # Принудительно переключаем на файловый ввод
                self.input_var.set("file")
                self._toggle_input_method()
                self.n = n
                return

            self.n = n
            self._create_matrix_input()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число")

    def _create_matrix_input(self):
        """Создание полей для ввода матрицы и вектора"""
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        for widget in self.vector_frame.winfo_children():
            widget.destroy()

        self.matrix_entries = []
        self.vector_entries = []

        cell_w = 6 if self.n > 10 else 7   # уже при большой матрице

        for i in range(self.n):
            row_entries = []
            for j in range(self.n):
                entry = ttk.Entry(self.matrix_frame, width=cell_w, justify='center')
                entry.grid(row=i, column=j, padx=1, pady=1)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

        for i in range(self.n):
            entry = ttk.Entry(self.vector_frame, width=cell_w, justify='center')
            entry.grid(row=0, column=i, padx=1, pady=1)
            self.vector_entries.append(entry)

        # Обновляем scrollregion после добавления виджетов
        self.matrix_frame.update_idletasks()
        self._on_matrix_configure()
        self._on_vector_configure()

        # Прокрутка колёсиком мыши (горизонтально — Shift+колёсо или просто колёсо)
        for canvas in (self.matrix_canvas, self.vector_canvas):
            canvas.bind("<MouseWheel>",
                lambda e, c=canvas: c.xview_scroll(-1 * (e.delta // 120), "units"))
            canvas.bind("<Shift-MouseWheel>",
                lambda e, c=canvas: c.xview_scroll(-1 * (e.delta // 120), "units"))

    # ------------------------------------------------------------------ #
    #  Обработчики кнопок — делегируют логику в loader / solver / results #
    # ------------------------------------------------------------------ #

    def _on_browse_file(self):
        path = browse_file()
        if path:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, path)

    def _on_read_keyboard(self):
        if not self.n:
            messagebox.showerror("Ошибка", "Сначала задайте размерность")
            return
        A, b = read_from_keyboard(self.n, self.matrix_entries, self.vector_entries)
        if A is not None:
            self.A, self.b = A, b
            self.calc_button.config(state=tk.NORMAL)
            messagebox.showinfo("Успех", "Данные успешно загружены")

    def _on_read_file(self):
        filename = self.file_path.get().strip()
        n, A, b = read_from_file(filename)
        if A is not None:
            self.n, self.A, self.b = n, A, b

            # Обновляем поле размерности и поля ввода
            self.n_entry.delete(0, tk.END)
            self.n_entry.insert(0, str(n))
            self._create_matrix_input()

            for i in range(n):
                for j in range(n):
                    self.matrix_entries[i][j].delete(0, tk.END)
                    self.matrix_entries[i][j].insert(0, str(A[i][j]))
            for i in range(n):
                self.vector_entries[i].delete(0, tk.END)
                self.vector_entries[i].insert(0, str(b[i]))

            self.calc_button.config(state=tk.NORMAL)
            messagebox.showinfo("Успех", "Данные успешно загружены из файла")

    def _calculate(self):
        """Запуск расчёта и отображение результатов"""
        if self.A is None or self.b is None:
            messagebox.showerror("Ошибка", "Сначала загрузите данные")
            return

        try:
            x, aug, forward_steps, backward_steps, det = gauss_solve_with_steps(self.A, self.b)

            display_solution(self.solution_tab, self.A, self.b, self.n, x, det, aug)
            display_forward(self.forward_tab, forward_steps)
            display_backward(self.backward_tab, backward_steps, aug, self.n)
            display_comparison(self.compare_tab, self.A, self.b, self.n, x, det)

            self.notebook.select(0)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при вычислениях: {str(e)}")

    def _reset_all(self):
        """Сброс всех данных"""
        self.A = None
        self.b = None
        self.n = 0

        self.n_entry.delete(0, tk.END)

        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        for widget in self.vector_frame.winfo_children():
            widget.destroy()

        self.solution_tab.clear()
        self.forward_tab.clear()
        self.backward_tab.clear()
        self.compare_tab.clear()

        self.calc_button.config(state=tk.DISABLED)
        self.file_path.delete(0, tk.END)

        messagebox.showinfo("Сброс", "Все данные очищены")

