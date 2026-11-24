"""Модуль векторной отрисовки шахматных фигур на Tkinter Canvas.

Отрисовывает фигуры с помощью векторных примитивов (полигоны, овалы, линии),
обеспечивая четкое масштабирование без размытия, пиксельных лесенок и зависимости
от внешних графических файлов или установленных шрифтов.
"""
from typing import Tuple

# Цвета для фигур
WHITE_FILL = '#f8fafc'      # Чистый светлый оттенок белых фигур
WHITE_OUTLINE = '#0f172a'   # Темный контур для контраста
WHITE_DETAIL = '#64748b'    # Внутренние линии детализации белых фигур

BLACK_FILL = '#26262b'      # Благородный графитовый оттенок черных фигур
BLACK_OUTLINE = '#f1f5f9'   # Светлый контур (делает черные фигуры контрастными на темных клетках)
BLACK_DETAIL = '#94a3b8'    # Внутренние линии детализации черных фигур


def _colors(color: str) -> Tuple[str, str, str]:
    if color == 'white':
        return WHITE_FILL, WHITE_OUTLINE, WHITE_DETAIL
    return BLACK_FILL, BLACK_OUTLINE, BLACK_DETAIL


def _p(cx: float, cy: float, s: float, dx: float, dy: float) -> Tuple[float, float]:
    """Преобразует относительное смещение (-50..50) в координаты на холсте."""
    return cx + dx * s, cy + dy * s


def _poly(canvas, points, fill, outline, width=1.5):
    return canvas.create_polygon(points, fill=fill, outline=outline, width=width, joinstyle='round', smooth=False)


# --- Классические шахматные фигуры ---

def draw_pawn(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 24*s, cy + 24*s, cx + 24*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Ствол
    points = [
        _p(cx, cy, s, -14, 25),
        _p(cx, cy, s, -8, -6),
        _p(cx, cy, s, 8, -6),
        _p(cx, cy, s, 14, 25)
    ]
    _poly(canvas, points, fill, outline, width)
    # Воротник
    canvas.create_oval(cx - 15*s, cy - 10*s, cx + 15*s, cy - 2*s, fill=fill, outline=outline, width=width)
    # Голова
    canvas.create_oval(cx - 14*s, cy - 34*s, cx + 14*s, cy - 6*s, fill=fill, outline=outline, width=width)
    # Блик на голове
    canvas.create_oval(cx - 8*s, cy - 28*s, cx - 2*s, cy - 20*s, fill=detail, outline='', width=0)


def draw_knight(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Голова коня
    points = [
        _p(cx, cy, s, -18, 25),
        _p(cx, cy, s, -22, 10),
        _p(cx, cy, s, -20, -10),
        _p(cx, cy, s, -26, -14),
        _p(cx, cy, s, -24, -26),  # морда
        _p(cx, cy, s, -10, -22),
        _p(cx, cy, s, -2, -34),   # ухо
        _p(cx, cy, s, 6, -26),
        _p(cx, cy, s, 16, -12),   # грива
        _p(cx, cy, s, 22, 6),
        _p(cx, cy, s, 20, 25),
    ]
    _poly(canvas, points, fill, outline, width)
    # Глаз
    canvas.create_oval(cx - 14*s, cy - 19*s, cx - 9*s, cy - 14*s, fill=detail, outline=outline, width=max(1, width*0.7))
    # Линия ноздри
    canvas.create_line(cx - 21*s, cy - 16*s, cx - 18*s, cy - 18*s, fill=detail, width=width)


def draw_bishop(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Тело
    points = [
        _p(cx, cy, s, -16, 25),
        _p(cx, cy, s, -10, 2),
        _p(cx, cy, s, 10, 2),
        _p(cx, cy, s, 16, 25)
    ]
    _poly(canvas, points, fill, outline, width)
    # Митра (каплевидная голова)
    canvas.create_oval(cx - 17*s, cy - 26*s, cx + 17*s, cy + 6*s, fill=fill, outline=outline, width=width)
    # Шарик на верхушке
    canvas.create_oval(cx - 5*s, cy - 35*s, cx + 5*s, cy - 25*s, fill=fill, outline=outline, width=width)
    # Диагональный разрез на митре
    canvas.create_line(cx - 8*s, cy - 18*s, cx + 8*s, cy - 8*s, fill=detail, width=max(1.5, width))


def draw_rook(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Башня
    points = [
        _p(cx, cy, s, -17, 25),
        _p(cx, cy, s, -14, -8),
        _p(cx, cy, s, 14, -8),
        _p(cx, cy, s, 17, 25)
    ]
    _poly(canvas, points, fill, outline, width)
    # Зубцы крепости
    cren = [
        _p(cx, cy, s, -20, -8),
        _p(cx, cy, s, -20, -28),
        _p(cx, cy, s, -12, -28),
        _p(cx, cy, s, -12, -18),
        _p(cx, cy, s, -4, -18),
        _p(cx, cy, s, -4, -28),
        _p(cx, cy, s, 4, -28),
        _p(cx, cy, s, 4, -18),
        _p(cx, cy, s, 12, -18),
        _p(cx, cy, s, 12, -28),
        _p(cx, cy, s, 20, -28),
        _p(cx, cy, s, 20, -8),
    ]
    _poly(canvas, cren, fill, outline, width)


def draw_queen(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 28*s, cy + 24*s, cx + 28*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Корпус
    points = [
        _p(cx, cy, s, -18, 25),
        _p(cx, cy, s, -12, 0),
        _p(cx, cy, s, 12, 0),
        _p(cx, cy, s, 18, 25)
    ]
    _poly(canvas, points, fill, outline, width)
    # Корона с 5 лучами
    crown = [
        _p(cx, cy, s, -18, 2),
        _p(cx, cy, s, -24, -22),
        _p(cx, cy, s, -12, -12),
        _p(cx, cy, s, 0, -26),
        _p(cx, cy, s, 12, -12),
        _p(cx, cy, s, 24, -22),
        _p(cx, cy, s, 18, 2),
    ]
    _poly(canvas, crown, fill, outline, width)
    # Жемчужины на кончиках короны
    for dx, dy in ((-24, -23), (-12, -13), (0, -27), (12, -13), (24, -23)):
        canvas.create_oval(cx + (dx-3)*s, cy + (dy-3)*s, cx + (dx+3)*s, cy + (dy+3)*s, fill=fill, outline=outline, width=width)


def draw_king(canvas, cx, cy, s, fill, outline, detail, width):
    # Основание
    canvas.create_oval(cx - 28*s, cy + 24*s, cx + 28*s, cy + 38*s, fill=fill, outline=outline, width=width)
    # Корпус
    points = [
        _p(cx, cy, s, -18, 25),
        _p(cx, cy, s, -14, -2),
        _p(cx, cy, s, 14, -2),
        _p(cx, cy, s, 18, 25)
    ]
    _poly(canvas, points, fill, outline, width)
    # Купол короны
    canvas.create_oval(cx - 18*s, cy - 22*s, cx + 18*s, cy + 2*s, fill=fill, outline=outline, width=width)
    # Королевский крест
    cross_w, cross_h = 4*s, 16*s
    # Вертикальная перекладина
    canvas.create_rectangle(cx - cross_w/2, cy - 36*s, cx + cross_w/2, cy - 20*s, fill=fill, outline=outline, width=width)
    # Горизонтальная перекладина
    canvas.create_rectangle(cx - 10*s, cy - 31*s, cx + 10*s, cy - 25*s, fill=fill, outline=outline, width=width)


# --- Авторские фигуры режима «Магический лес» ---

def draw_griffin(canvas, cx, cy, s, fill, outline, detail, width):
    """Грифон: орел-лев с острым клювом, перьями и ушками."""
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    points = [
        _p(cx, cy, s, -18, 25),
        _p(cx, cy, s, -22, 6),
        _p(cx, cy, s, -26, -6),   # клюв
        _p(cx, cy, s, -14, -12),
        _p(cx, cy, s, -8, -32),   # ухо-перо
        _p(cx, cy, s, 2, -22),
        _p(cx, cy, s, 12, -34),   # второе перо
        _p(cx, cy, s, 18, -16),   # крыло
        _p(cx, cy, s, 24, 8),
        _p(cx, cy, s, 20, 25),
    ]
    _poly(canvas, points, fill, outline, width)
    # Глаз хищника
    canvas.create_oval(cx - 12*s, cy - 16*s, cx - 7*s, cy - 11*s, fill=detail, outline=outline, width=max(1, width*0.7))


def draw_camel(canvas, cx, cy, s, fill, outline, detail, width):
    """Верблюд: характерный горб, длинная шея и голова."""
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    points = [
        _p(cx, cy, s, -16, 25),
        _p(cx, cy, s, -18, 4),
        _p(cx, cy, s, -24, -18),  # морда
        _p(cx, cy, s, -14, -26),  # лоб
        _p(cx, cy, s, -8, -20),   # затылок
        _p(cx, cy, s, -4, -6),    # изгиб шеи
        _p(cx, cy, s, 8, -24),    # горб верблюда
        _p(cx, cy, s, 22, -6),
        _p(cx, cy, s, 18, 25),
    ]
    _poly(canvas, points, fill, outline, width)
    canvas.create_oval(cx - 18*s, cy - 22*s, cx - 13*s, cy - 17*s, fill=detail, outline=outline, width=max(1, width*0.7))


def draw_elephant(canvas, cx, cy, s, fill, outline, detail, width):
    """Прыгающий слон: мощный силуэт, загнутый хобот и бивень."""
    canvas.create_oval(cx - 26*s, cy + 24*s, cx + 26*s, cy + 38*s, fill=fill, outline=outline, width=width)
    points = [
        _p(cx, cy, s, -18, 25),
        _p(cx, cy, s, -24, 12),
        _p(cx, cy, s, -28, -6),   # хобот загибается вверх
        _p(cx, cy, s, -22, -18),
        _p(cx, cy, s, -16, -10),
        _p(cx, cy, s, -12, -26),  # лоб
        _p(cx, cy, s, 10, -30),   # спина / ухо
        _p(cx, cy, s, 24, -4),
        _p(cx, cy, s, 20, 25),
    ]
    _poly(canvas, points, fill, outline, width)
    # Бивень
    canvas.create_line(cx - 18*s, cy - 2*s, cx - 26*s, cy - 8*s, fill=outline, width=max(2.0, width*1.3))
    # Глаз
    canvas.create_oval(cx - 12*s, cy - 18*s, cx - 7*s, cy - 13*s, fill=detail, outline=outline, width=max(1, width*0.7))


def draw_phoenix(canvas, cx, cy, s, fill, outline, detail, width, reborn=False):
    """Феникс (F) и Возрождённый феникс (A): раскинутые крылья и пламенное оперение."""
    # Тело и хвост
    body = [
        _p(cx, cy, s, -6, 26),
        _p(cx, cy, s, 0, 36),
        _p(cx, cy, s, 6, 26),
        _p(cx, cy, s, 8, 4),
        _p(cx, cy, s, -8, 4),
    ]
    _poly(canvas, body, fill, outline, width)
    # Левое крыло
    left_wing = [
        _p(cx, cy, s, -6, 10),
        _p(cx, cy, s, -34, -4),
        _p(cx, cy, s, -30, -22 if reborn else -16),
        _p(cx, cy, s, -18, -14),
        _p(cx, cy, s, -8, -6),
    ]
    _poly(canvas, left_wing, fill, outline, width)
    # Правое крыло
    right_wing = [
        _p(cx, cy, s, 6, 10),
        _p(cx, cy, s, 34, -4),
        _p(cx, cy, s, 30, -22 if reborn else -16),
        _p(cx, cy, s, 18, -14),
        _p(cx, cy, s, 8, -6),
    ]
    _poly(canvas, right_wing, fill, outline, width)
    # Голова и пламенный хохолок
    canvas.create_oval(cx - 8*s, cy - 22*s, cx + 8*s, cy - 6*s, fill=fill, outline=outline, width=width)
    crest = [
        _p(cx, cy, s, -4, -20),
        _p(cx, cy, s, 0, -36 if reborn else -30),
        _p(cx, cy, s, 4, -20),
    ]
    _poly(canvas, crest, fill, outline, width)
    if reborn:
        # У возрождённого феникса сияющий ореол
        canvas.create_oval(cx - 14*s, cy - 32*s, cx + 14*s, cy - 4*s, fill='', outline=detail, width=width)


def draw_caterpillar(canvas, cx, cy, s, fill, outline, detail, width):
    """Коронованная гусеница: три округлых сегмента и корона."""
    # Задний сегмент
    canvas.create_oval(cx - 28*s, cy + 4*s, cx - 6*s, cy + 28*s, fill=fill, outline=outline, width=width)
    # Средний сегмент
    canvas.create_oval(cx - 16*s, cy - 2*s, cx + 8*s, cy + 24*s, fill=fill, outline=outline, width=width)
    # Голова
    canvas.create_oval(cx - 4*s, cy - 14*s, cx + 24*s, cy + 18*s, fill=fill, outline=outline, width=width)
    # Маленькая корона на голове
    crown = [
        _p(cx, cy, s, 2, -12),
        _p(cx, cy, s, 0, -28),
        _p(cx, cy, s, 8, -20),
        _p(cx, cy, s, 16, -28),
        _p(cx, cy, s, 14, -12),
    ]
    _poly(canvas, crown, fill, outline, width)
    # Глаз
    canvas.create_oval(cx + 10*s, cy - 4*s, cx + 15*s, cy + 2*s, fill=detail, outline='', width=0)


def draw_butterfly(canvas, cx, cy, s, fill, outline, detail, width):
    """Бабочка: симметричные верхние и нижние крылья с изящным телом."""
    # Тело
    canvas.create_oval(cx - 5*s, cy - 18*s, cx + 5*s, cy + 24*s, fill=fill, outline=outline, width=width)
    # Верхнее левое крыло
    canvas.create_oval(cx - 34*s, cy - 26*s, cx - 2*s, cy + 2*s, fill=fill, outline=outline, width=width)
    # Верхнее правое крыло
    canvas.create_oval(cx + 2*s, cy - 26*s, cx + 34*s, cy + 2*s, fill=fill, outline=outline, width=width)
    # Нижнее левое крыло
    canvas.create_oval(cx - 28*s, cy - 4*s, cx - 2*s, cy + 26*s, fill=fill, outline=outline, width=width)
    # Нижнее правое крыло
    canvas.create_oval(cx + 2*s, cy - 4*s, cx + 28*s, cy + 26*s, fill=fill, outline=outline, width=width)
    # Усики
    canvas.create_line(cx - 2*s, cy - 16*s, cx - 14*s, cy - 32*s, fill=outline, width=width)
    canvas.create_line(cx + 2*s, cy - 16*s, cx + 14*s, cy - 32*s, fill=outline, width=width)


def draw_sprout(canvas, cx, cy, s, fill, outline, detail, width, mini=False):
    """Росток (S) и мини-росток (M): стебель и два листика."""
    scale_factor = 0.7 if mini else 1.0
    s *= scale_factor
    # Стебель
    canvas.create_line(cx, cy + 28*s, cx, cy - 8*s, fill=outline, width=max(2.5, width*1.5))
    # Левый лист
    left_leaf = [
        _p(cx, cy, s, 0, 10),
        _p(cx, cy, s, -26, 4),
        _p(cx, cy, s, -22, -14),
        _p(cx, cy, s, 0, -4),
    ]
    _poly(canvas, left_leaf, fill, outline, width)
    # Правый лист
    right_leaf = [
        _p(cx, cy, s, 0, 4),
        _p(cx, cy, s, 26, -2),
        _p(cx, cy, s, 22, -20),
        _p(cx, cy, s, 0, -10),
    ]
    _poly(canvas, right_leaf, fill, outline, width)
    # Бутон на верхушке
    canvas.create_oval(cx - 6*s, cy - 26*s, cx + 6*s, cy - 12*s, fill=fill, outline=outline, width=width)


def render_piece(canvas, kind: str, color: str, cx: float, cy: float, cell_size: float):
    """Главная функция отрисовки фигуры по её типу и цвету на заданных координатах."""
    fill, outline, detail = _colors(color)
    s = (cell_size / 90.0)
    width = max(1.5, cell_size * 0.028)

    if kind == 'P':
        draw_pawn(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'N':
        draw_knight(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'B':
        draw_bishop(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'R':
        draw_rook(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'Q':
        draw_queen(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'K':
        draw_king(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'G':
        draw_griffin(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'C':
        draw_camel(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'E':
        draw_elephant(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'F':
        draw_phoenix(canvas, cx, cy, s, fill, outline, detail, width, reborn=False)
    elif kind == 'A':
        draw_phoenix(canvas, cx, cy, s, fill, outline, detail, width, reborn=True)
    elif kind == 'T':
        draw_caterpillar(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'W':
        draw_butterfly(canvas, cx, cy, s, fill, outline, detail, width)
    elif kind == 'S':
        draw_sprout(canvas, cx, cy, s, fill, outline, detail, width, mini=False)
    elif kind == 'M':
        draw_sprout(canvas, cx, cy, s, fill, outline, detail, width, mini=True)
