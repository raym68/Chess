"""Модуль отрисовки шахматных фигур с антиалиасингом и гладкими кривыми.

1. Для авторских фигур режима «Магический лес» использует оригинальные
   иллюстрации авторов проекта из assets/pieces (192x192), сглаженные фильтром LANCZOS.
2. Для классических фигур использует плавные кривые Безье и округлые формы,
   избавляя от угловатости и пиксельной «лесенки».
3. При отсутствии Pillow обеспечивает корректный fallback.
"""
from pathlib import Path
import sys
from typing import Tuple

try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Соответствие кодов лесных фигур именам графических файлов авторов
PIECE_FILES = {
    'G': 'griffin',
    'C': 'camel',
    'E': 'elephant',
    'F': 'phoenix',
    'A': 'reborn',
    'T': 'caterpillar',
    'W': 'butterfly',
    'S': 'sprout',
    'M': 'sprout',
}

# Кэш готовых сглаженных иконок, чтобы не выполнять масштабирование каждый кадр
_icon_cache = {}


def get_asset_dir() -> Path:
    """Возвращает путь к папке с графикой (работает и из исходников, и из собранного .exe)."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / 'assets' / 'pieces'
    return Path(__file__).resolve().parent / 'assets' / 'pieces'


def _bezier_points(p0, p1, p2, p3, steps=14):
    """Генерирует массив точек плавной кубической кривой Безье."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _draw_classic_piece(kind: str, color: str, size: int) -> 'ImageTk.PhotoImage':
    """Рисует классическую фигуру (пешка, ладья, конь, слон, ферзь, король) с плавными формами."""
    dim = 240
    img = Image.new('RGBA', (dim, dim), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Цветовая гамма
    if color == 'white':
        fill = (248, 250, 252, 255)
        outline = (15, 23, 42, 255)
        detail = (148, 163, 184, 255)
    else:
        fill = (39, 39, 42, 255)
        outline = (244, 244, 245, 255)
        detail = (161, 161, 170, 255)

    lw = 6

    def poly(pts):
        d.polygon(pts, fill=fill, outline=outline, width=lw)

    def circle(x0, y0, x1, y1, f=fill, o=outline, w=lw):
        d.ellipse((x0, y0, x1, y1), fill=f, outline=o, width=w)

    def line(pts, o=outline, w=lw):
        d.line(pts, fill=o, width=w)

    if kind == 'P':  # Пешка: гладкий постамент, талия с изгибом Безье, воротник и круглая голова
        # Пьедестал
        circle(48, 180, 192, 206)
        # Изогнутый корпус
        pts = [(62, 188)]
        pts.extend(_bezier_points((62, 188), (76, 150), (90, 126), (92, 114)))
        pts.extend([(148, 114)])
        pts.extend(_bezier_points((148, 114), (150, 126), (164, 150), (178, 188)))
        poly(pts)
        circle(84, 106, 156, 124)  # Воротник
        circle(82, 44, 158, 120)   # Голова

    elif kind == 'R':  # Ладья: мощное основание, изогнутая башня и прямые зубцы
        circle(44, 180, 196, 206)
        pts = [(60, 186)]
        pts.extend(_bezier_points((60, 186), (72, 146), (82, 110), (84, 98)))
        pts.extend([(156, 98)])
        pts.extend(_bezier_points((156, 98), (158, 110), (168, 146), (180, 186)))
        poly(pts)
        # Зубцы
        cren = [
            (68, 98), (68, 52), (92, 52), (92, 72), (110, 72),
            (110, 52), (130, 52), (130, 72), (148, 72), (148, 52),
            (172, 52), (172, 98)
        ]
        poly(cren)

    elif kind == 'N':  # Конь: плавные анатомические изгибы морды, уха, затылка и груди
        circle(44, 180, 196, 206)
        pts = [(64, 186)]
        # Грудь
        pts.extend(_bezier_points((64, 186), (56, 144), (46, 102), (40, 84)))
        # Морда
        pts.extend([(48, 64), (72, 72)])
        # Затылок и ухо
        pts.extend(_bezier_points((72, 72), (84, 52), (90, 38), (96, 38)))
        pts.extend([(102, 54)])
        # Грива и спина
        pts.extend(_bezier_points((102, 54), (132, 76), (158, 114), (176, 186)))
        poly(pts)
        circle(68, 86, 78, 96, f=detail, o=outline, w=3)  # Глаз
        line([(50, 76), (62, 82)], o=detail, w=4)        # Ноздря

    elif kind == 'B':  # Слон: округлая митра, плавный переход и шарик на верхушке
        circle(44, 180, 196, 206)
        pts = [(62, 186)]
        pts.extend(_bezier_points((62, 186), (76, 146), (88, 120), (90, 110)))
        pts.extend([(150, 110)])
        pts.extend(_bezier_points((150, 110), (152, 120), (164, 146), (178, 186)))
        poly(pts)
        circle(76, 62, 164, 136)   # Митра
        circle(108, 42, 132, 66)   # Шарик
        line([(98, 88), (142, 110)], o=detail, w=5)  # Прорезь

    elif kind == 'Q':  # Ферзь: грациозный стан и плавная корона с жемчужинами
        circle(42, 180, 198, 206)
        pts = [(60, 186)]
        pts.extend(_bezier_points((60, 186), (74, 144), (86, 114), (88, 104)))
        pts.extend([(152, 104)])
        pts.extend(_bezier_points((152, 104), (154, 114), (166, 144), (180, 186)))
        poly(pts)
        crown = [
            (72, 106), (54, 58), (88, 86), (120, 48),
            (152, 86), (186, 58), (168, 106)
        ]
        poly(crown)
        for px, py in ((54, 54), (88, 82), (120, 44), (152, 82), (186, 54)):
            circle(px-7, py-7, px+7, py+7)

    elif kind == 'K':  # Король: монарший купол и четкий крест
        circle(42, 180, 198, 206)
        pts = [(60, 186)]
        pts.extend(_bezier_points((60, 186), (74, 142), (86, 110), (88, 98)))
        pts.extend([(152, 98)])
        pts.extend(_bezier_points((152, 98), (154, 110), (166, 142), (180, 186)))
        poly(pts)
        circle(74, 68, 166, 120)  # Купол
        # Крест
        poly([(114, 30), (126, 30), (126, 74), (114, 74)])
        poly([(96, 42), (144, 42), (144, 54), (96, 54)])

    target_dim = max(16, int(size * 0.88))
    img_smooth = img.resize((target_dim, target_dim), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img_smooth)


def _load_forest_piece(kind: str, color: str, size: int) -> 'ImageTk.PhotoImage':
    """Загружает авторскую 192x192 фигуру и плавно масштабирует фильтром LANCZOS."""
    file_name = f'{PIECE_FILES[kind]}-{color}.gif'
    file_path = get_asset_dir() / file_name

    if not file_path.exists():
        # Запасной вариант, если файла нет
        return _draw_classic_piece(kind, color, size)

    im = Image.open(file_path).convert('RGBA')

    # Мини-росток пропорционально чуть меньше
    scale = 0.72 if kind == 'M' else 0.90
    target_dim = max(16, int(size * scale))

    im_smooth = im.resize((target_dim, target_dim), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(im_smooth)


def render_piece(canvas, kind: str, color: str, cx: float, cy: float, cell_size: float):
    """Отрисовывает фигуру на Canvas: использует кэш и высококачественное сглаживание."""
    size_key = int(cell_size)

    if HAS_PIL:
        cache_key = (kind, color, size_key)
        if cache_key not in _icon_cache:
            if kind in PIECE_FILES:
                _icon_cache[cache_key] = _load_forest_piece(kind, color, size_key)
            else:
                _icon_cache[cache_key] = _draw_classic_piece(kind, color, size_key)

        photo = _icon_cache[cache_key]
        canvas.create_image(cx, cy, image=photo)
        return

    # Запасной fallback на стандартный Canvas (если PIL не установлен)
    s = cell_size / 90.0
    fill = '#f8fafc' if color == 'white' else '#27272a'
    outline = '#0f172a' if color == 'white' else '#f4f4f5'
    w = max(1.5, cell_size * 0.028)
    canvas.create_oval(cx - 24*s, cy + 20*s, cx + 24*s, cy + 36*s, fill=fill, outline=outline, width=w)
    canvas.create_oval(cx - 16*s, cy - 24*s, cx + 16*s, cy + 8*s, fill=fill, outline=outline, width=w)
