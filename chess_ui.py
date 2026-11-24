"""Настольный интерфейс для игры двух человек за одной доской."""
from math import ceil
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from backend.game import Game, ROYALS
from backend.models import BACK, SETUP_OPTIONS, SETUP_SLOTS

FILES = 'abcdefgh'
NAMES = {item['kind']: item['name'] for item in SETUP_OPTIONS}
NAMES.update(Q='Ферзь', F='Феникс', A='Возрождённый феникс', T='Гусеница', W='Бабочка', S='Росток')
SYMBOLS = dict(zip('KQRBNP', '♚♛♜♝♞♟'))
PIECE_FILES = {'G': 'griffin', 'C': 'camel', 'E': 'elephant',
               'F': 'phoenix', 'A': 'reborn', 'T': 'caterpillar', 'W': 'butterfly', 'S': 'sprout'}
PIECE_DIR = Path(__file__).resolve().parent / 'assets' / 'pieces'
THEMES = {
    'Магический лес': ('#c4d5ac', '#6d947d'),
    'Дерево': ('#ecd9b6', '#b78963'),
    'Синий': ('#dfeaf2', '#819eb5'),
    'Зелёный': ('#e3e9d2', '#90a57f'),
}


class ChessWindow:
    def __init__(self, root):
        self.root = root
        root.title('Шахматы')
        root.minsize(690, 510)
        self.game = Game(forest=True)
        self.selected = None
        self.moves = []
        self.theme = tk.StringVar(value='Магический лес')
        self.status = tk.StringVar()
        self.geometry = None
        self.icons = {
            (kind, color): tk.PhotoImage(master=root, file=str(PIECE_DIR / f'{name}-{color}.gif'))
            for kind, name in PIECE_FILES.items() for color in ('white', 'black')
        }
        self.scaled_icons = {}

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(frame, textvariable=self.status, font=('TkDefaultFont', 15, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 8))
        self.board = tk.Canvas(frame, width=510, height=510, highlightthickness=0, bg='#263332')
        self.board.grid(row=1, column=0, sticky='nsew')
        self.board.bind('<Configure>', self.draw)
        self.board.bind('<Button-1>', self.click)
        ttk.Label(frame, text='Выберите фигуру, затем клетку для хода.').grid(row=2, column=0, sticky='w')

        side = ttk.Frame(frame, padding=(16, 0, 0, 0))
        side.grid(row=0, column=1, rowspan=3, sticky='ns')
        ttk.Button(side, text='Новая партия…', command=self.setup).pack(fill='x')
        ttk.Label(side, text='Оформление доски').pack(anchor='w', pady=(14, 2))
        theme = ttk.Combobox(side, textvariable=self.theme, state='readonly', values=list(THEMES))
        theme.pack(fill='x')
        theme.bind('<<ComboboxSelected>>', self.draw)
        ttk.Label(side, text='Протокол партии').pack(anchor='w', pady=(18, 4))
        table = ttk.Frame(side)
        table.pack(fill='both', expand=True)
        self.history = ttk.Treeview(table, columns=('№', 'Белые', 'Чёрные'), show='headings', height=8)
        for name, width in zip(self.history['columns'], (34, 72, 72)):
            self.history.heading(name, text=name)
            self.history.column(name, width=width, anchor='center')
        scroll = ttk.Scrollbar(table, command=self.history.yview)
        self.history.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.history.pack(fill='both', expand=True)
        self.legend = ttk.Frame(side)
        self.legend.pack(anchor='w', pady=(12, 0))
        self.update_legend()
        self.refresh()

    def update_legend(self):
        for widget in self.legend.winfo_children():
            widget.destroy()
        if self.game.forest:
            rules = (('T', 'после шаха станет бабочкой'), ('W', 'обмен с соседним союзником'),
                     ('F', '1–2 клетки, одно возрождение'), ('S', 'ходит по диагонали, берёт прямо\nПри взятии оставляет мини-росток'))
        else:
            rules = (('G', 'ходит как слон или конь'), ('C', 'прыгает на 3 × 1'),
                     ('E', 'прыгает на две клетки'))
        for row, (kind, rule) in enumerate(rules):
            ttk.Label(self.legend, image=self.icon(kind, 'black', 32)).grid(row=row, column=0)
            ttk.Label(self.legend, text=f'{NAMES[kind]}\n{rule}').grid(row=row, column=1, sticky='w')

    def icon(self, kind, color, size):
        original = self.icons[kind, color]
        factor = max(1, ceil(original.width() / size))
        key = kind, color, factor
        if key not in self.scaled_icons:
            self.scaled_icons[key] = original.subsample(factor)
        return self.scaled_icons[key]

    def draw(self, event=None):
        board = self.board
        board.delete('all')
        w, h = board.winfo_width(), board.winfo_height()
        cell = (min(w, h) - 40) // 8
        if cell < 1:
            self.geometry = None
            return
        left, top = (w - cell * 8) // 2, (h - cell * 8) // 2
        self.geometry = left, top, cell
        colors = THEMES[self.theme.get()]
        forest_theme = self.theme.get() == 'Магический лес'
        board.configure(bg='#203e36' if forest_theme else '#263332')
        checked = self.game.in_check(self.game.turn)
        for index in range(8):
            center = (index + 0.5) * cell
            for y in (top - 10, top + 8 * cell + 10):
                board.create_text(left + center, y, text=FILES[index], fill='white')
            for x in (left - 10, left + 8 * cell + 10):
                board.create_text(x, top + center, text=8-index, fill='white')
        for r, row in enumerate(self.game.board):
            for c, piece in enumerate(row):
                x, y = left + c * cell, top + r * cell
                fill = colors[(r + c) % 2]
                if checked and piece and piece.kind in ROYALS and piece.color == self.game.turn:
                    fill = '#d67566'
                if self.selected == (r, c):
                    fill = '#e0bd54'
                board.create_rectangle(x, y, x + cell, y + cell, fill=fill, outline='')
                cx, cy = x + cell / 2, y + cell / 2
                if forest_theme:
                    # Небольшая веточка в углу клетки оставляет центр свободным.
                    leaf = ('#a8bf98', '#618774')[(r+c) % 2]
                    unit = cell / 64
                    board.create_line(x+2*unit, y+13*unit, x+11*unit, y+3*unit, fill=leaf)
                    for dx, dy in ((4, 6), (8, 2)):
                        board.create_oval(x+dx*unit, y+dy*unit, x+(dx+5)*unit, y+(dy+3)*unit,
                                          fill=leaf, outline='')
                kind = piece.kind if piece else None
                if kind == 'M':
                    board.create_image(cx, cy, image=self.icon('S', piece.color, max(1, cell * 2 // 3)))
                elif kind in PIECE_FILES:
                    board.create_image(cx, cy, image=self.icon(kind, piece.color, cell))
                elif piece:
                    symbol = SYMBOLS[piece.kind]
                    font = ('Arial', -max(8, int(cell * 0.72)))
                    ink = '#242829' if piece.color == 'black' else '#fffaf0'
                    if piece.color == 'white':
                        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                            board.create_text(cx+dx, cy+dy, text=symbol, font=font, fill='#3f4340')
                    board.create_text(cx, cy, text=symbol, font=font, fill=ink)
                if (r, c) in self.moves:
                    radius = cell * (0.43 if piece else 0.11)
                    board.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                                      fill='' if piece else '#395e53', outline='#395e53', width=2)

    def click(self, event):
        if not self.geometry or self.game.pending_promotion or self.game.status.startswith(('Мат', 'Пат')):
            return
        left, top, cell = self.geometry
        r, c = (event.y - top) // cell, (event.x - left) // cell
        if not (0 <= r < 8 and 0 <= c < 8):
            return
        if (r, c) in self.moves:
            self.game.move(self.selected, (r, c))
            self.refresh()
            if self.game.pending_promotion:
                self.promotion()
            return
        piece = self.game.board[r][c]
        self.selected = (r, c) if piece and piece.color == self.game.turn and self.selected != (r, c) else None
        self.moves = self.game.legal(r, c) if self.selected else []
        self.draw()

    def refresh(self):
        self.selected, self.moves = None, []
        status = self.game.status
        if not status.startswith(('Мат', 'Пат')):
            turn = 'белых' if self.game.turn == 'white' else 'чёрных'
            status = f'{status} · ход {turn}'
        if self.game.events:
            status += '\n' + ' · '.join(self.game.events)
        self.status.set(status)
        self.history.delete(*self.history.get_children())
        moves = self.game.history
        for i in range(0, len(moves), 2):
            item = self.history.insert('', 'end', values=(i // 2 + 1, *moves[i:i+2]))
        if moves:
            self.history.see(item)
        self.draw()

    def dialog(self, title):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.transient(self.root)
        window.resizable(False, False)
        window.grab_set()
        return window

    def setup(self):
        window = self.dialog('Новая партия')
        frame = ttk.Frame(window, padding=16)
        frame.pack()
        ttk.Label(frame, text='Стартовый ряд для обеих сторон').grid(columnspan=2, pady=(0, 10))
        kinds = [item['kind'] for item in SETUP_OPTIONS]
        mode = tk.StringVar(value='Лесная' if self.game.forest else 'Обычная')
        ttk.Label(frame, text='Партия').grid(row=1, column=0)
        ttk.Combobox(frame, textvariable=mode, values=('Лесная', 'Обычная'),
                     state='readonly').grid(row=1, column=1)
        choices = {}
        for row, col in enumerate(SETUP_SLOTS, start=2):
            ttk.Label(frame, text=FILES[col]).grid(row=row, column=0, padx=(0, 12))
            choice = ttk.Combobox(frame, values=[NAMES[k] for k in kinds], state='readonly')
            choice.current(kinds.index(self.game.back_rank[col]))
            choice.grid(row=row, column=1, pady=2)
            choices[col] = choice

        def start():
            rank = list(BACK)
            for col, choice in choices.items():
                rank[col] = kinds[choice.current()]
            self.game = Game(rank, forest=mode.get() == 'Лесная')
            self.update_legend()
            window.destroy()
            self.refresh()

        ttk.Button(frame, text='Начать партию', command=start).grid(row=8, columnspan=2, pady=(10, 0))

    def promotion(self):
        pawn = 'росток' if self.game.forest else 'пешку'
        window = self.dialog('Выбор фигуры')

        def choose(kind):
            self.game.promote(kind)
            window.destroy()
            self.refresh()

        window.protocol('WM_DELETE_WINDOW', window.bell)
        frame = ttk.Frame(window, padding=14)
        frame.pack()
        ttk.Label(frame, text=f'В какую фигуру превратить {pawn}?').pack(pady=(0, 6))
        for kind in sorted(self.game.promotion_options, key=lambda k: (k != 'Q', NAMES[k])):
            button = ttk.Button(frame, text=NAMES[kind], command=lambda k=kind: choose(k))
            if kind in PIECE_FILES:
                button.configure(image=self.icon(kind, self.game.turn, 32), compound='left')
            button.pack(fill='x')


def main():
    root = tk.Tk()
    ChessWindow(root)
    root.mainloop()
