"""Настольный интерфейс для шахмат двух игроков за одним компьютером.

Выполнен в современном тёмном стиле (Modern Dark UI) с векторной отрисовкой
всех фигур на Canvas, интерактивными подсказками ходов и протоколом партии.
"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from backend.game import Game, NEW_BACK, NEW_SETUP, ROYALS
from backend.models import SETUP_OPTIONS, SETUP_SLOTS
from pieces_renderer import render_piece
from theme import (
    apply_theme, create_chess_icon,
    BG_MAIN, BG_CARD, BG_HOVER,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT, COLOR_SELECTED, COLOR_LAST_MOVE,
    COLOR_CHECK, COLOR_MOVE_DOT, COLOR_CAPTURE_MARK,
    BOARD_THEMES, FONT_UI, FONT_UI_BOLD, FONT_STATUS, FONT_MONO, FONT_MONO_BOLD
)

CLASSIC = 'Классические шахматы'
NEW = 'Новые шахматы'
FILES = 'abcdefgh'
NAMES = {item['kind']: item['name'] for item in SETUP_OPTIONS}
NAMES.update(Q='Ферзь', F='Феникс', A='Возрождённый феникс', T='Гусеница', W='Бабочка', S='Росток')


class ChessWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title('Шахматы')
        root.minsize(760, 560)

        # Применяем тёмную тему ttk и устанавливаем сгенерированную шахматную иконку окна
        self.style = apply_theme(root)
        self.icon_photo = create_chess_icon()
        root.iconphoto(False, self.icon_photo)

        # Инициализация партии и состояния интерфейса (по умолчанию классические шахматы)
        self.game = Game()
        self.selected = None
        self.moves = []
        self.last_move = None  # Координаты (start, end) для подсветки последнего хода
        self.theme_name = tk.StringVar(value='Дерево')
        self.status = tk.StringVar()
        self.geometry = None

        # Главный контейнер с отступами
        main_container = ttk.Frame(root, padding=16)
        main_container.pack(fill='both', expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Верхняя панель: статус партии и индикатор очереди хода
        header = ttk.Frame(main_container)
        header.grid(row=0, column=0, sticky='w', pady=(0, 10))

        # Круговой индикатор текущего хода (белые/чёрные)
        self.turn_canvas = tk.Canvas(header, width=18, height=18, bg=BG_MAIN, highlightthickness=0)
        self.turn_canvas.pack(side='left', padx=(0, 10))

        # Текст статуса (ход белых, шах, мат и события)
        self.status_label = ttk.Label(header, textvariable=self.status, font=FONT_STATUS)
        self.status_label.pack(side='left')

        # Шахматная доска (холст Canvas)
        self.board = tk.Canvas(main_container, width=510, height=510, highlightthickness=0, bg='#18181b')
        self.board.grid(row=1, column=0, sticky='nsew')
        self.board.bind('<Configure>', self.draw)
        self.board.bind('<Button-1>', self.click)

        # Нижняя подсказка для игрока
        self.hint_label = ttk.Label(
            main_container,
            text='Нажмите на фигуру, чтобы увидеть возможные ходы, затем на подсвеченную клетку.',
            style='Muted.TLabel'
        )
        self.hint_label.grid(row=2, column=0, sticky='w', pady=(10, 0))

        # Правая боковая панель с элементами управления
        side = ttk.Frame(main_container, style='Card.TFrame', padding=16)
        side.grid(row=0, column=1, rowspan=3, sticky='nsew', padx=(16, 0))
        main_container.columnconfigure(1, minsize=260)

        # Кнопка «Новая партия...» с акцентным стилем
        new_game_btn = ttk.Button(side, text='Новая партия…', style='Accent.TButton', command=self.setup)
        new_game_btn.pack(fill='x', pady=(0, 16))

        # Выбор темы оформления доски
        ttk.Label(side, text='Оформление доски', style='CardMuted.TLabel', font=FONT_UI_BOLD).pack(anchor='w', pady=(0, 4))
        theme_combo = ttk.Combobox(side, textvariable=self.theme_name, state='readonly', values=list(BOARD_THEMES.keys()))
        theme_combo.pack(fill='x', pady=(0, 16))
        theme_combo.bind('<<ComboboxSelected>>', self.draw)

        # Протокол ходов партии (таблица Treeview)
        ttk.Label(side, text='Протокол партии', style='CardMuted.TLabel', font=FONT_UI_BOLD).pack(anchor='w', pady=(0, 4))
        table_container = ttk.Frame(side, style='Card.TFrame')
        table_container.pack(fill='both', expand=True)

        self.history = ttk.Treeview(table_container, columns=('№', 'Белые', 'Чёрные'), show='headings', height=8)
        for name, width in zip(self.history['columns'], (38, 85, 85)):
            self.history.heading(name, text=name)
            self.history.column(name, width=width, anchor='center')

        # Зебра-оформление строк таблицы ходов
        self.history.tag_configure('even', background='#27272a')
        self.history.tag_configure('odd', background='#212124')

        scroll = ttk.Scrollbar(table_container, orient='vertical', command=self.history.yview)
        self.history.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.history.pack(side='left', fill='both', expand=True)

        # Панель легенды для авторских фигур
        self.legend = ttk.Frame(side, style='Card.TFrame')
        self.legend.pack(fill='x', pady=(12, 0))

        self.update_legend()
        self.refresh()

    def update_legend(self):
        """Обновляет памятку правил ходов и обозначений фигур в правой панели."""
        for widget in self.legend.winfo_children():
            widget.destroy()

        self.root.title(NEW if self.game.forest else CLASSIC)

        if self.game.forest:
            ttk.Label(self.legend, text='Правила новых фигур:', style='CardMuted.TLabel', font=FONT_UI_BOLD).pack(anchor='w', pady=(0, 6))

            rules = (
                ('G', 'Грифон (G)', 'слон и конь'),
                ('C', 'Верблюд (C)', 'прыжок 3 × 1'),
                ('E', 'Слон (E)', 'прыжок на 2 клетки'),
                ('F', 'Феникс (F)', '1–2 клетки по прямым и косым'),
                ('A', 'Возрождённый (A)', 'может перепрыгивать'),
                ('T', 'Гусеница (T)', 'становится бабочкой при шахе'),
                ('W', 'Бабочка (W)', 'меняется местами с союзником'),
                ('S', 'Росток (S)', 'ходит наискось, бьёт прямо'),
                ('M', 'Мини-росток (M)', 'вырастает после взятия')
            )

            legend_grid = ttk.Frame(self.legend, style='Card.TFrame')
            legend_grid.pack(fill='x')

            for row, (kind, name, rule) in enumerate(rules):
                c = tk.Canvas(legend_grid, width=22, height=22, bg=BG_CARD, highlightthickness=0)
                c.grid(row=row, column=0, padx=(0, 6), pady=1)
                render_piece(c, kind, 'white', 11, 11, 20)
                ttk.Label(legend_grid, text=f'{name} — {rule}', style='Card.TLabel', font=('Segoe UI', 8)).grid(row=row, column=1, sticky='w')
        else:
            ttk.Label(self.legend, text='Обозначения фигур:', style='CardMuted.TLabel', font=FONT_UI_BOLD).pack(anchor='w', pady=(0, 6))

            classic_pieces = (
                ('K', 'Король (K)', 'ход на 1 клетку, рокировка'),
                ('Q', 'Ферзь (Q)', 'по прямым и диагоналям'),
                ('R', 'Ладья (R)', 'по горизонтали и вертикали'),
                ('B', 'Слон (B)', 'по диагоналям'),
                ('N', 'Конь (N)', 'буквой «Г», прыгает через фигуры'),
                ('P', 'Пешка (P)', 'ход вперёд, взятие наискосок')
            )

            legend_grid = ttk.Frame(self.legend, style='Card.TFrame')
            legend_grid.pack(fill='x')

            for row, (kind, name, rule) in enumerate(classic_pieces):
                c = tk.Canvas(legend_grid, width=22, height=22, bg=BG_CARD, highlightthickness=0)
                c.grid(row=row, column=0, padx=(0, 6), pady=1)
                render_piece(c, kind, 'white', 11, 11, 20)
                ttk.Label(legend_grid, text=f'{name} — {rule}', style='Card.TLabel', font=('Segoe UI', 8)).grid(row=row, column=1, sticky='w')

    def draw(self, event=None):
        """Отрисовывает шахматную доску, клетки, координаты, подсказки и фигуры."""
        board = self.board
        board.delete('all')

        w, h = board.winfo_width(), board.winfo_height()
        cell = (min(w, h) - 44) // 8
        if cell < 10:
            self.geometry = None
            return

        left = (w - cell * 8) // 2
        top = (h - cell * 8) // 2
        self.geometry = left, top, cell

        current_theme = BOARD_THEMES.get(self.theme_name.get(), BOARD_THEMES['Магический лес'])
        board.configure(bg=current_theme['board_bg'])

        # Координаты по периметру доски (a-h и 1-8)
        coord_font = FONT_MONO
        for index in range(8):
            center = (index + 0.5) * cell
            # Буквы снизу и сверху
            for y in (top - 14, top + 8 * cell + 14):
                board.create_text(left + center, y, text=FILES[index], fill=TEXT_MUTED, font=coord_font)
            # Цифры слева и справа
            for x in (left - 14, left + 8 * cell + 14):
                board.create_text(x, top + center, text=str(8 - index), fill=TEXT_MUTED, font=coord_font)

        # Определение короля под шахом для подсветки
        king_in_check = self.game.find_royal(self.game.turn) if self.game.in_check(self.game.turn) else None

        # Отрисовка клеток доски
        for r in range(8):
            for c in range(8):
                x = left + c * cell
                y = top + r * cell

                # Базовый цвет клетки из темы
                fill = current_theme['light'] if (r + c) % 2 == 0 else current_theme['dark']

                # Подсветка последнего сделанного хода (откуда и куда пошла фигура)
                if self.last_move and ((r, c) == self.last_move[0] or (r, c) == self.last_move[1]):
                    fill = COLOR_LAST_MOVE

                # Подсветка выбранной игроком клетки
                if self.selected == (r, c):
                    fill = COLOR_SELECTED

                # Подсветка короля красным цветом при шахе
                if king_in_check and (r, c) == king_in_check:
                    fill = COLOR_CHECK

                board.create_rectangle(x, y, x + cell, y + cell, fill=fill, outline='')

                # Декоративные лесные листочки в углу для темы «Магический лес»
                if current_theme.get('decor') == 'forest':
                    leaf_color = '#a8bf98' if (r + c) % 2 == 0 else '#4d725d'
                    unit = cell / 64.0
                    board.create_line(x + 2*unit, y + 13*unit, x + 11*unit, y + 3*unit, fill=leaf_color)
                    for dx, dy in ((4, 6), (8, 2)):
                        board.create_oval(x + dx*unit, y + dy*unit, x + (dx+4)*unit, y + (dy+3)*unit,
                                          fill=leaf_color, outline='')

                # Отрисовка фигуры с помощью чистого векторного рендерера
                piece = self.game.board[r][c]
                if piece:
                    cx = x + cell / 2.0
                    cy = y + cell / 2.0
                    render_piece(board, piece.kind, piece.color, cx, cy, cell)

                # Подсветка доступных ходов для выбранной фигуры
                if (r, c) in self.moves:
                    cx = x + cell / 2.0
                    cy = y + cell / 2.0
                    if piece:
                        # Если клетка занята — это взятие фигуры (рисуем аккуратные уголки по краям клетки)
                        d = cell * 0.22
                        lw = 3
                        # Верхний левый угол
                        board.create_line(x, y + d, x, y, x + d, y, fill=COLOR_CAPTURE_MARK, width=lw)
                        # Верхний правый угол
                        board.create_line(x + cell - d, y, x + cell, y, x + cell, y + d, fill=COLOR_CAPTURE_MARK, width=lw)
                        # Нижний левый угол
                        board.create_line(x, y + cell - d, x, y + cell, x + d, y + cell, fill=COLOR_CAPTURE_MARK, width=lw)
                        # Нижний правый угол
                        board.create_line(x + cell - d, y + cell, x + cell, y + cell, x + cell, y + cell - d, fill=COLOR_CAPTURE_MARK, width=lw)
                    else:
                        # Если клетка пустая — аккуратная округлая точка по центру
                        radius = cell * 0.13
                        board.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                          fill=COLOR_MOVE_DOT, outline='')

    def click(self, event):
        """Обработка клика мыши по шахматной доске."""
        if not self.geometry or self.game.pending_promotion or self.game.status.startswith(('Мат', 'Пат')):
            return

        left, top, cell = self.geometry
        r = int((event.y - top) // cell)
        c = int((event.x - left) // cell)

        if not (0 <= r < 8 and 0 <= c < 8):
            return

        # Если нажали на одну из подсвеченных клеток — делаем ход
        if (r, c) in self.moves:
            start_pos = self.selected
            self.game.move(start_pos, (r, c))
            self.last_move = (start_pos, (r, c))
            self.refresh()
            if self.game.pending_promotion:
                self.promotion()
            return

        # Выбор своей фигуры
        piece = self.game.board[r][c]
        if piece and piece.color == self.game.turn and self.selected != (r, c):
            self.selected = (r, c)
            self.moves = self.game.legal(r, c)
        else:
            self.selected = None
            self.moves = []

        self.draw()

    def refresh(self):
        """Обновляет индикаторы, текстовый статус, протокол партии и перерисовывает поле."""
        self.selected = None
        self.moves = []

        # Обновляем визуальный индикатор очереди хода
        self.turn_canvas.delete('all')
        if self.game.turn == 'white':
            self.turn_canvas.create_oval(2, 2, 16, 16, fill='#ffffff', outline='#71717a', width=2)
        else:
            self.turn_canvas.create_oval(2, 2, 16, 16, fill='#27272a', outline='#f4f4f5', width=2)

        status = self.game.status
        if not status.startswith(('Мат', 'Пат')):
            turn = 'белых' if self.game.turn == 'white' else 'чёрных'
            status = f'{status} · ход {turn}'
        if self.game.events:
            status += '\n' + ' · '.join(self.game.events)
        self.status.set(status)

        # Обновление таблицы ходов
        self.history.delete(*self.history.get_children())
        moves = self.game.history
        last_item = None
        for i in range(0, len(moves), 2):
            tag = 'odd' if (i // 2) % 2 == 1 else 'even'
            row_data = (i // 2 + 1, *moves[i:i+2])
            last_item = self.history.insert('', 'end', values=row_data, tags=(tag,))

        # Автопрокрутка таблицы к последнему сделанному ходу
        if last_item:
            self.history.see(last_item)

        self.draw()

    def dialog(self, title: str) -> tk.Toplevel:
        """Создает модальное окно в едином тёмном стиле."""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.transient(self.root)
        window.resizable(False, False)
        window.configure(bg=BG_MAIN)
        window.grab_set()
        return window

    def setup(self):
        """Диалог настроек и запуска новой партии в едином тёмном стиле."""
        window = self.dialog('Новая партия')
        frame = ttk.Frame(window, padding=20)
        frame.pack()

        mode = tk.StringVar(value=NEW if self.game.forest else CLASSIC)

        settings = ttk.LabelFrame(frame, text='Стартовый ряд для обеих сторон', padding=12)
        settings.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(12, 16))

        kinds = [item['kind'] for item in NEW_SETUP]
        rank = self.game.back_rank if self.game.forest else NEW_BACK
        choices = {}

        def show_settings():
            if mode.get() == NEW:
                settings.grid()
            else:
                settings.grid_remove()

        for col, title in enumerate((CLASSIC, NEW)):
            ttk.Radiobutton(frame, text=title, variable=mode, value=title,
                            command=show_settings).grid(row=0, column=col, padx=8, pady=(0, 4))

        for row, col in enumerate(SETUP_SLOTS):
            ttk.Label(settings, text=f'Линия {FILES[col]}').grid(row=row, column=0, padx=8, pady=3, sticky='w')
            choice = ttk.Combobox(settings, values=[NAMES[k] for k in kinds], state='readonly', width=18)
            choice.current(kinds.index(rank[col]))
            choice.grid(row=row, column=1, pady=3)
            choices[col] = choice

        show_settings()

        def start():
            if mode.get() == NEW:
                new_rank = list(NEW_BACK)
                for col, choice in choices.items():
                    new_rank[col] = kinds[choice.current()]
                self.game = Game(new_rank, forest=True)
            else:
                self.game = Game()
            self.last_move = None
            self.update_legend()
            window.destroy()
            self.refresh()

        ttk.Button(frame, text='Начать партию', style='Accent.TButton', command=start).grid(
            row=8, columnspan=2, sticky='ew', pady=(12, 0))

    def promotion(self):
        """Диалог выбора фигуры при превращении пешки/ростка."""
        pawn_name = 'росток' if self.game.forest else 'пешку'
        window = self.dialog('Превращение фигуры')

        def choose(kind):
            self.game.promote(kind)
            window.destroy()
            self.refresh()

        window.protocol('WM_DELETE_WINDOW', window.bell)
        frame = ttk.Frame(window, padding=20)
        frame.pack()

        ttk.Label(frame, text=f'Выберите, в кого превратить {pawn_name}:', font=FONT_UI_BOLD).pack(pady=(0, 14))

        for kind in sorted(self.game.promotion_options, key=lambda k: (k != 'Q', NAMES[k])):
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill='x', pady=3)

            # Векторная мини-иконка фигуры на кнопке
            preview = tk.Canvas(btn_frame, width=28, height=28, bg=BG_MAIN, highlightthickness=0)
            preview.pack(side='left', padx=(0, 8))
            render_piece(preview, kind, self.game.turn, 14, 14, 26)

            ttk.Button(btn_frame, text=NAMES[kind], command=lambda k=kind: choose(k)).pack(side='left', fill='x', expand=True)


def main():
    root = tk.Tk()
    ChessWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
