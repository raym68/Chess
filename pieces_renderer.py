"""Модуль векторной отрисовки шахматных фигур высокого разрешения.

Использует 4x суперсэмплинг (anti-aliasing через PIL/LANCZOS) для получения
идеально гладких контуров фигур без пиксельной «лесенки». При отсутствии PIL
автоматически переключается на встроенные векторные примитивы Tkinter Canvas.
"""
from typing import Tuple

try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Цвета для светлых (белых) фигур
WHITE_FILL = (248, 250, 252, 255)       # Чистый молочно-белый #f8fafc
WHITE_OUTLINE = (15, 23, 42, 255)       # Чёткий тёмно-синий контур #0f172a
WHITE_DETAIL = (100, 116, 139, 255)     # Внутренние линии детализации #64748b

# Цвета для тёмных (чёрных) фигур
BLACK_FILL = (39, 39, 42, 255)          # Благородный тёмный графит #27272a
BLACK_OUTLINE = (244, 244, 245, 255)    # Светлый контрастный контур #f4f4f5
BLACK_DETAIL = (161, 161, 170, 255)     # Детали серым оттенком #a1a1aa

# Кэш готовых сглаженных иконок, чтобы не пересчитывать их при каждом кадре
_icon_cache = {}


def _get_palette(color: str):
    if color == 'white':
        return WHITE_FILL, WHITE_OUTLINE, WHITE_DETAIL
    return BLACK_FILL, BLACK_OUTLINE, BLACK_DETAIL


def _draw_piece_hi_res(kind: str, color: str, size: int) -> 'ImageTk.PhotoImage':
    """Рисует фигуру в разрешении 240x240 с 4x суперсэмплингом и сжимает с фильтром LANCZOS."""
    dim = 240
    img = Image.new('RGBA', (dim, dim), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    fill, outline, detail = _get_palette(color)
    lw = 6  # Толщина контура в высоком разрешении (после сжатия станет аккуратными 1.5-2px)

    # Вспомогательные функции для рисования с контуром
    def circle(x0, y0, x1, y1, f=fill, o=outline, w=lw):
        d.ellipse((x0, y0, x1, y1), fill=f, outline=o, width=w)

    def poly(pts, f=fill, o=outline, w=lw):
        d.polygon(pts, fill=f, outline=o, width=w)

    def line(pts, o=outline, w=lw):
        d.line(pts, fill=o, width=w)

    # --- Классические шахматные фигуры ---
    if kind == 'P':  # Пешка
        circle(48, 175, 192, 210)
        poly([(84, 182), (94, 126), (146, 126), (156, 182)])
        circle(80, 114, 160, 134)
        circle(82, 54, 158, 124)
        circle(96, 68, 118, 90, f=detail, o=None, w=0)

    elif kind == 'R':  # Ладья
        circle(44, 175, 196, 210)
        poly([(76, 182), (86, 102), (154, 102), (164, 182)])
        # Зубцы крепости
        cren = [
            (68, 102), (68, 54), (92, 54), (92, 74), (110, 74),
            (110, 54), (130, 54), (130, 74), (148, 74), (148, 54),
            (172, 54), (172, 102)
        ]
        poly(cren)

    elif kind == 'N':  # Конь
        circle(44, 175, 196, 210)
        knight_head = [
            (78, 182), (66, 146), (58, 98), (46, 80), (54, 60),
            (82, 70), (98, 42), (118, 60), (142, 90), (162, 126),
            (168, 182)
        ]
        poly(knight_head)
        circle(74, 82, 86, 94, f=detail, o=outline, w=3)
        line([(58, 74), (68, 80)], o=detail, w=4)

    elif kind == 'B':  # Слон
        circle(44, 175, 196, 210)
        poly([(82, 182), (92, 122), (148, 122), (158, 182)])
        circle(74, 64, 166, 138)
        circle(108, 42, 132, 66)
        line([(98, 90), (142, 110)], o=detail, w=5)

    elif kind == 'Q':  # Ферзь
        circle(42, 175, 198, 210)
        poly([(80, 182), (88, 120), (152, 120), (160, 182)])
        crown = [
            (72, 122), (54, 62), (88, 90), (120, 50),
            (152, 90), (186, 62), (168, 122)
        ]
        poly(crown)
        for px, py in ((54, 56), (88, 84), (120, 44), (152, 84), (186, 56)):
            circle(px-7, py-7, px+7, py+7)

    elif kind == 'K':  # Король
        circle(42, 175, 198, 210)
        poly([(78, 182), (86, 112), (154, 112), (162, 182)])
        circle(74, 72, 166, 124)
        # Королевский крест
        poly([(114, 34), (126, 34), (126, 78), (114, 78)])
        poly([(96, 46), (144, 46), (144, 58), (96, 58)])

    # --- Авторские лесные фигуры ---
    elif kind == 'G':  # Грифон (орел-лев)
        circle(44, 175, 196, 210)
        griffin = [
            (74, 182), (60, 140), (44, 104), (68, 92), (84, 50),
            (106, 74), (128, 44), (144, 78), (170, 114), (166, 182)
        ]
        poly(griffin)
        circle(78, 88, 88, 98, f=detail, o=outline, w=3)
        line([(46, 102), (64, 98)], o=detail, w=4)

    elif kind == 'C':  # Верблюд
        circle(44, 175, 196, 210)
        camel = [
            (76, 182), (68, 134), (50, 82), (68, 62), (86, 76),
            (100, 114), (134, 68), (166, 104), (172, 142), (164, 182)
        ]
        poly(camel)
        circle(64, 72, 74, 82, f=detail, o=outline, w=3)

    elif kind == 'E':  # Прыгающий слон
        circle(44, 175, 196, 210)
        elephant = [
            (76, 182), (58, 142), (38, 100), (52, 76), (68, 94),
            (80, 58), (132, 46), (172, 94), (178, 142), (164, 182)
        ]
        poly(elephant)
        line([(58, 114), (40, 100)], o=outline, w=6)  # Бивень
        circle(82, 76, 92, 86, f=detail, o=outline, w=3)

    elif kind in ('F', 'A'):  # Феникс и Возрождённый феникс
        poly([(110, 188), (120, 206), (130, 188), (128, 130), (112, 130)])
        # Размашистые крылья
        is_reborn = (kind == 'A')
        wing_y = 36 if is_reborn else 48
        poly([(114, 144), (40, 110), (28, wing_y), (64, 78), (98, 96)])
        poly([(126, 144), (200, 110), (212, wing_y), (176, 78), (142, 96)])
        circle(104, 70, 136, 102)
        poly([(112, 74), (120, 36 if is_reborn else 44), (128, 74)])
        if is_reborn:
            circle(88, 48, 152, 112, f=None, o=detail, w=4)

    elif kind == 'T':  # Коронованная гусеница
        circle(50, 132, 102, 184)
        circle(86, 112, 146, 172)
        circle(124, 88, 188, 152)
        crown = [(140, 92), (134, 58), (156, 72), (174, 58), (170, 92)]
        poly(crown)
        circle(158, 110, 168, 120, f=detail, o=None, w=0)

    elif kind == 'W':  # Бабочка
        # Верхние крылья
        circle(36, 56, 116, 136)
        circle(124, 56, 204, 136)
        # Нижние крылья
        circle(52, 118, 114, 180)
        circle(126, 118, 188, 180)
        # Тело
        circle(114, 78, 126, 172)
        line([(118, 80), (102, 46)], o=outline, w=5)
        line([(122, 80), (138, 46)], o=outline, w=5)

    elif kind in ('S', 'M'):  # Росток и мини-росток
        s_scale = 0.76 if kind == 'M' else 1.0
        # Изогнутый стебель
        line([(120, 190), (120, 90)], o=outline, w=int(8 * s_scale))
        # Левый лист
        poly([(118, 148), (62, 132), (68, 90), (118, 112)])
        # Правый лист
        poly([(122, 132), (178, 116), (172, 74), (122, 96)])
        # Бутон
        circle(108, 64, 132, 88)

    # Высококачественное сжатие до нужного размера клетки с 8-точечным антиалиасингом
    target_dim = max(16, int(size * 0.88))
    img_smooth = img.resize((target_dim, target_dim), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img_smooth)


def render_piece(canvas, kind: str, color: str, cx: float, cy: float, cell_size: float):
    """Главная функция отрисовки фигуры: использует PIL 4x сглаживание или векторный Canvas fallback."""
    size_key = int(cell_size)

    if HAS_PIL:
        cache_key = (kind, color, size_key)
        if cache_key not in _icon_cache:
            _icon_cache[cache_key] = _draw_piece_hi_res(kind, color, size_key)

        photo = _icon_cache[cache_key]
        canvas.create_image(cx, cy, image=photo)
        return

    # Fallback на нативные примитивы Canvas, если PIL не установлен
    s = cell_size / 90.0
    fill = '#f8fafc' if color == 'white' else '#27272a'
    outline = '#0f172a' if color == 'white' else '#f4f4f5'
    w = max(1.5, cell_size * 0.028)

    if kind == 'P':
        canvas.create_oval(cx - 22*s, cy + 22*s, cx + 22*s, cy + 36*s, fill=fill, outline=outline, width=w)
        canvas.create_oval(cx - 14*s, cy - 30*s, cx + 14*s, cy - 4*s, fill=fill, outline=outline, width=w)
    else:
        canvas.create_oval(cx - 24*s, cy + 20*s, cx + 24*s, cy + 36*s, fill=fill, outline=outline, width=w)
        canvas.create_oval(cx - 18*s, cy - 26*s, cx + 18*s, cy + 10*s, fill=fill, outline=outline, width=w)
