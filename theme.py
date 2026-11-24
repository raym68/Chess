"""Модуль тёмной темы оформления интерфейса шахмат.

Содержит цветовую палитру Modern Dark, темы шахматной доски
и настройки стилей ttk для виджетов (кнопки, списки, таблица ходов).
"""
import tkinter as tk
from tkinter import ttk

# Базовая палитра тёмной темы (Modern Dark / Zinc)
BG_MAIN = '#18181b'        # Основной фон окна
BG_CARD = '#27272a'        # Фон карточек, боковой панели и таблиц
BG_HOVER = '#3f3f46'       # Цвет при наведении и разделители
BG_ACTIVE = '#52525b'      # Цвет нажатия

TEXT_PRIMARY = '#f4f4f5'   # Основной белый/светлый текст
TEXT_MUTED = '#a1a1aa'     # Второстепенный серый текст
TEXT_INACTIVE = '#71717a'  # Неактивный текст

ACCENT = '#16a34a'         # Зелёный акцент для кнопок и активных элементов
ACCENT_HOVER = '#15803d'   # Зелёный при наведении
ACCENT_ACTIVE = '#166534'  # Зелёный при клике

# Цвета для интерактивных подсветок на доске
COLOR_SELECTED = '#eab308'      # Подсветка выбранной клетки (мягкий тёплый жёлтый)
COLOR_LAST_MOVE = '#38bdf8'     # Клетки последнего хода (мягкий голубой оттенок)
COLOR_CHECK = '#ef4444'         # Клетка короля под шахом (красный)
COLOR_MOVE_DOT = '#22c55e'      # Маркер свободного хода (зелёная точка)
COLOR_CAPTURE_MARK = '#f97316'   # Маркер клетки с возможностью взятия (оранжевый)

# Темы оформления самой шахматной доски (светлые и тёмные клетки)
BOARD_THEMES = {
    'Дерево': {
        'light': '#ecd9b6',
        'dark': '#b78963',
        'board_bg': '#1e1b18',
        'decor': None,
    },
    'Изумруд': {
        'light': '#d1e7dd',
        'dark': '#4a7c59',
        'board_bg': '#13231a',
        'decor': None,
    },
    'Графит': {
        'light': '#e4e4e7',
        'dark': '#71717a',
        'board_bg': '#202023',
        'decor': None,
    },
    'Магический лес': {
        'light': '#c4d5ac',
        'dark': '#5b826b',
        'board_bg': '#192b23',
        'decor': 'forest',  # флаг для отрисовки деликатных листочков в углу
    },
}

# Шрифты приложения
FONT_UI = ('Segoe UI', 10)
FONT_UI_BOLD = ('Segoe UI', 10, 'bold')
FONT_TITLE = ('Segoe UI', 14, 'bold')
FONT_STATUS = ('Segoe UI', 12, 'bold')
FONT_MONO = ('Consolas', 10)
FONT_MONO_BOLD = ('Consolas', 10, 'bold')


def apply_theme(root: tk.Tk) -> ttk.Style:
    """Применяет тёмную тему ко всем виджетам ttk."""
    style = ttk.Style(root)

    # Используем тему 'clam' — она лучше всего поддерживает кастомные цвета на Windows
    available = style.theme_names()
    if 'clam' in available:
        style.theme_use('clam')

    # Настройка окна
    root.configure(bg=BG_MAIN)

    # Стили общих фреймов
    style.configure('TFrame', background=BG_MAIN)
    style.configure('Card.TFrame', background=BG_CARD)

    # Лейблы
    style.configure('TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=FONT_UI)
    style.configure('Card.TLabel', background=BG_CARD, foreground=TEXT_PRIMARY, font=FONT_UI)
    style.configure('Muted.TLabel', background=BG_MAIN, foreground=TEXT_MUTED, font=FONT_UI)
    style.configure('CardMuted.TLabel', background=BG_CARD, foreground=TEXT_MUTED, font=FONT_UI)
    style.configure('Title.TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=FONT_TITLE)
    style.configure('Status.TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=FONT_STATUS)

    # Акцентная главная кнопка («Новая партия...»)
    style.configure('Accent.TButton',
                    background=ACCENT,
                    foreground='#ffffff',
                    font=FONT_UI_BOLD,
                    borderwidth=0,
                    focusthickness=0,
                    focuscolor='',
                    padding=(12, 8))
    style.map('Accent.TButton',
              background=[('pressed', ACCENT_ACTIVE), ('active', ACCENT_HOVER)],
              foreground=[('pressed', '#ffffff'), ('active', '#ffffff')])

    # Обычные кнопки диалогов
    style.configure('TButton',
                    background=BG_HOVER,
                    foreground=TEXT_PRIMARY,
                    font=FONT_UI,
                    borderwidth=0,
                    focusthickness=0,
                    focuscolor='',
                    padding=(10, 6))
    style.map('TButton',
              background=[('pressed', BG_ACTIVE), ('active', '#4f4f58')],
              foreground=[('pressed', TEXT_PRIMARY), ('active', TEXT_PRIMARY)])

    # Выпадающий список (Combobox)
    style.configure('TCombobox',
                    background=BG_CARD,
                    fieldbackground=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_MUTED,
                    darkcolor=BG_HOVER,
                    lightcolor=BG_HOVER,
                    bordercolor=BG_HOVER,
                    selectbackground=BG_HOVER,
                    selectforeground=TEXT_PRIMARY,
                    padding=6)
    style.map('TCombobox',
              fieldbackground=[('readonly', BG_CARD)],
              foreground=[('readonly', TEXT_PRIMARY)],
              selectbackground=[('readonly', BG_HOVER)],
              selectforeground=[('readonly', TEXT_PRIMARY)])

    # Радиокнопки
    style.configure('TRadiobutton',
                    background=BG_MAIN,
                    foreground=TEXT_PRIMARY,
                    font=FONT_UI,
                    focuscolor='')
    style.map('TRadiobutton',
              background=[('active', BG_MAIN)],
              foreground=[('active', TEXT_PRIMARY)])

    # LabelFrame (контейнеры настроек)
    style.configure('TLabelframe',
                    background=BG_MAIN,
                    bordercolor=BG_HOVER,
                    darkcolor=BG_HOVER,
                    lightcolor=BG_HOVER)
    style.configure('TLabelframe.Label',
                    background=BG_MAIN,
                    foreground=TEXT_MUTED,
                    font=FONT_UI_BOLD)

    # Таблица протокола ходов (Treeview)
    style.configure('Treeview',
                    background=BG_CARD,
                    fieldbackground=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_MONO,
                    rowheight=28,
                    borderwidth=0,
                    highlightthickness=0)
    style.map('Treeview',
              background=[('selected', BG_HOVER)],
              foreground=[('selected', '#ffffff')])

    # Заголовки таблицы Treeview
    style.configure('Treeview.Heading',
                    background='#1f1f23',
                    foreground=TEXT_MUTED,
                    font=FONT_UI_BOLD,
                    borderwidth=0,
                    padding=4)
    style.map('Treeview.Heading',
              background=[('active', '#2d2d32')],
              foreground=[('active', TEXT_PRIMARY)])

    # Тёмный скроллбар
    style.configure('Vertical.TScrollbar',
                    background=BG_CARD,
                    troughcolor=BG_MAIN,
                    bordercolor=BG_MAIN,
                    arrowcolor=TEXT_MUTED,
                    borderwidth=0,
                    relief='flat')
    style.map('Vertical.TScrollbar',
              background=[('pressed', BG_ACTIVE), ('active', BG_HOVER)])

    # Настройка всплывающих списков для Tk (Listbox внутри Combobox)
    root.option_add('*TCombobox*Listbox.background', BG_CARD)
    root.option_add('*TCombobox*Listbox.foreground', TEXT_PRIMARY)
    root.option_add('*TCombobox*Listbox.selectBackground', ACCENT)
    root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
    root.option_add('*TCombobox*Listbox.font', FONT_UI)
    root.option_add('*TCombobox*Listbox.borderWidth', '0')

    return style


def create_chess_icon() -> tk.PhotoImage:
    """Генерирует аккуратную 32x32 шахматную иконку (ладья) для заголовка окна."""
    # 32x32 пикселей в формате PPM (Portable Pixmap)
    width, height = 32, 32
    # Шахматная ладья (силуэт)
    matrix = [
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "      XXXX   XXXX   XXXX        ",
        "      XXXX   XXXX   XXXX        ",
        "      XXXXXXXXXXXXXXXXXX        ",
        "      XXXXXXXXXXXXXXXXXX        ",
        "       XXXXXXXXXXXXXXXX         ",
        "       XXXXXXXXXXXXXXXX         ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "        XXXXXXXXXXXXXX          ",
        "       XXXXXXXXXXXXXXXX         ",
        "       XXXXXXXXXXXXXXXX         ",
        "      XXXXXXXXXXXXXXXXXX        ",
        "      XXXXXXXXXXXXXXXXXX        ",
        "     XXXXXXXXXXXXXXXXXXXX       ",
        "     XXXXXXXXXXXXXXXXXXXX       ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                "
    ]
    # Зелёная акцентная иконка на тёмном фоне
    bg_rgb = (24, 24, 27)
    fg_rgb = (22, 163, 74)
    ppm_header = f"P6\n{width} {height}\n255\n"
    raw_bytes = bytearray()
    for row in matrix:
        for char in row:
            raw_bytes.extend(fg_rgb if char == 'X' else bg_rgb)
    return tk.PhotoImage(data=ppm_header.encode('ascii') + raw_bytes, format='PPM')
