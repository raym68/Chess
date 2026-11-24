"""Правила шахмат. Координаты: (строка, столбец), от 0 до 7."""
from copy import deepcopy

from .models import BACK, SETUP_OPTIONS, SETUP_SLOTS, Piece, new_board, board_to_dict


NEW_BACK = tuple('GCEFTECG')
NEW_SETUP = tuple(item for item in SETUP_OPTIONS if item['kind'] in ('G', 'C', 'E'))
NEW_KINDS = frozenset(item['kind'] for item in NEW_SETUP)
SPROUTS = ('S', 'M')
ROYALS = ('K', 'T', 'W')
DIRECTIONS = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc)


def enemy(color):
    return 'black' if color == 'white' else 'white'


def inside(r, c):
    return 0 <= r < 8 and 0 <= c < 8


class Game:
    def __init__(self, back_rank=None, forest=False):
        if back_rank is None:
            back_rank = NEW_BACK if forest else BACK
        if not isinstance(back_rank, (list, tuple)) or len(back_rank) != 8:
            raise ValueError('В стартовом ряду должно быть восемь фигур')
        if forest:
            if tuple(back_rank[3:5]) != ('F', 'T') or any(back_rank[i] not in NEW_KINDS for i in SETUP_SLOTS):
                raise ValueError('В центре стоят феникс и гусеница, по краям — новые фигуры')
        elif tuple(back_rank) != BACK:
            raise ValueError('В классических шахматах используется стандартная расстановка')
        self.forest = forest
        self.events = []
        self.back_rank = tuple(back_rank)
        self.board = new_board()
        self.turn = 'white'
        self.en_passant = None
        self.pending_promotion = None
        self.status = 'Игра идёт'
        self.history = []
        self.pending_notation = None
        for color, row, pawn_row in [('black', 0, 1), ('white', 7, 6)]:
            for c, kind in enumerate(self.back_rank):
                self.board[row][c] = Piece(kind, color)
                self.board[pawn_row][c] = Piece('S' if forest else 'P', color)

    def serialize(self):
        checked_king = next(([r, c] for r in range(8) for c in range(8)
                             if self.board[r][c] and self.board[r][c].kind in ROYALS
                             and self.board[r][c].color == self.turn), None) if self.in_check(self.turn) else None
        return {'board': board_to_dict(self.board), 'turn': self.turn, 'status': self.status,
                'checked_king': checked_king,
                'promotion': self.pending_promotion, 'promotion_options': sorted(self.promotion_options),
                'setup_options': NEW_SETUP if self.forest else (), 'setup_slots': SETUP_SLOTS if self.forest else (),
                'back_rank': list(self.back_rank), 'back_pair': [self.back_rank[2], self.back_rank[5]],
                'history': self.history}

    @property
    def promotion_options(self):
        return NEW_KINDS | {'F'} if self.forest else frozenset('QRBN')

    def attacks(self, r, c):
        p = self.board[r][c]
        if not p:
            return []
        k, color = p.kind, p.color
        out = []
        if k in SPROUTS:
            front = r + (-1 if color == 'white' else 1), c
            return [front] if inside(*front) else []
        if k == 'P':
            d = -1 if color == 'white' else 1
            return [(r+d, c+dc) for dc in (-1, 1) if inside(r+d, c+dc)]
        jumps = []
        if k == 'C':
            jumps = [(a*sa, b*sb) for a, b in ((1, 3), (3, 1)) for sa in (-1, 1) for sb in (-1, 1)]
        elif k in ('N', 'G'):
            jumps = [(a*sa, b*sb) for a, b in ((1, 2), (2, 1)) for sa in (-1, 1) for sb in (-1, 1)]
        if k in ('F', 'A'):
            for dr, dc in DIRECTIONS:
                for distance in (1, 2):
                    nr, nc = r + distance * dr, c + distance * dc
                    if not inside(nr, nc):
                        break
                    out.append((nr, nc))
                    if k == 'F' and self.board[nr][nc]:
                        break
            return out
        if k == 'E':
            jumps = [(2*dr, 2*dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
        if k in ('K', 'T'):
            jumps = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
        for dr, dc in jumps:
            if inside(r+dr, c+dc):
                out.append((r+dr, c+dc))
        dirs = []
        if k in ('R', 'Q'):
            dirs += [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if k in ('B', 'Q', 'G'):
            dirs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while inside(nr, nc):
                out.append((nr, nc))
                if self.board[nr][nc]:
                    break
                nr, nc = nr+dr, nc+dc
        return out

    def attacked(self, square, by_color):
        return any(self.board[r][c] and self.board[r][c].color == by_color and
                   square in self.attacks(r, c) for r in range(8) for c in range(8))

    def in_check(self, color):
        kings = [(r, c) for r in range(8) for c in range(8)
                 if self.board[r][c] and self.board[r][c].color == color and self.board[r][c].kind in ROYALS]
        return not kings or self.attacked(kings[0], enemy(color))

    def candidates(self, r, c):
        p = self.board[r][c]
        if not p:
            return []
        color, k = p.color, p.kind
        moves = []
        if k == 'W':
            return [(r+dr, c+dc) for dr, dc in DIRECTIONS if inside(r+dr, c+dc)
                    and self.board[r+dr][c+dc] and self.board[r+dr][c+dc].color == color]
        if k in SPROUTS:
            for nr, nc in self.attacks(r, c):
                for col in (nc-1, nc+1):
                    if inside(nr, col) and self.board[nr][col] is None:
                        moves.append((nr, col))
                target = self.board[nr][nc]
                if target and target.color != color and target.kind not in ROYALS:
                    moves.append((nr, nc))
            return moves
        if k == 'P':
            d = -1 if color == 'white' else 1
            if inside(r+d, c) and not self.board[r+d][c]:
                moves.append((r+d, c))
                start = 6 if color == 'white' else 1
                if r == start and not p.moved and not self.board[r+2*d][c]:
                    moves.append((r+2*d, c))
            for nr, nc in self.attacks(r, c):
                target = self.board[nr][nc]
                if (target and target.color != color and target.kind not in ROYALS) or (nr, nc) == self.en_passant:
                    moves.append((nr, nc))
        else:
            for nr, nc in self.attacks(r, c):
                target = self.board[nr][nc]
                if not target or (target.color != color and target.kind not in ROYALS):
                    moves.append((nr, nc))
            if k == 'K' and not p.moved and not self.in_check(color):
                for rook_c, path, transit, dest in ((7, (5, 6), 5, 6), (0, (1, 2, 3), 3, 2)):
                    rook = self.board[r][rook_c]
                    if rook and rook.kind == 'R' and rook.color == color and not rook.moved and all(not self.board[r][x] for x in path) and not self.attacked((r, transit), enemy(color)) and not self.attacked((r, dest), enemy(color)):
                        moves.append((r, dest))
        return moves

    def apply(self, start, end):
        r, c = start
        nr, nc = end
        p = self.board[r][c]
        old_ep = self.en_passant
        self.en_passant = None
        captured = self.board[nr][nc]
        if p.kind == 'W':
            self.board[r][c], self.board[nr][nc] = captured, p
            captured.moved = p.moved = True
            return
        if p.kind == 'P' and old_ep == end and c != nc and not self.board[nr][nc]:
            self.board[r][nc] = None
        if p.kind == 'K' and abs(nc-c) == 2:
            rook_c, rook_dest = (7, 5) if nc > c else (0, 3)
            self.board[r][rook_dest] = self.board[r][rook_c]
            self.board[r][rook_c] = None
            self.board[r][rook_dest].moved = True
        self.board[nr][nc], self.board[r][c] = p, None
        p.moved = True
        if p.kind == 'P' and abs(nr-r) == 2:
            self.en_passant = ((nr+r)//2, c)

        if captured and p.kind in SPROUTS:
            self.board[r][c] = Piece('M', p.color, moved=True)
        if captured and captured.kind == 'F':
            home = 7 if captured.color == 'white' else 0
            slots = ((row, col) for row in range(8) for col in range(8) if not self.board[row][col])
            row, col = min(slots, key=lambda pos: (abs(pos[0]-home) + abs(pos[1]-3),
                                                   abs(pos[0]-home), pos[1]))
            self.board[row][col] = Piece('A', captured.color, moved=True)
            self.events.append('Феникс возродился на ' + self.square_name((row, col)))

    def legal(self, r, c):
        p = self.board[r][c]
        if not p or p.color != self.turn or self.pending_promotion or self.status.startswith(('Мат', 'Пат')):
            return []
        result = []
        for end in self.candidates(r, c):
            trial = deepcopy(self)
            trial.apply((r, c), end)
            if not trial.in_check(self.turn):
                result.append(end)
        return result

    def finish_turn(self):
        self.turn = enemy(self.turn)
        if self.forest and self.in_check(self.turn):
            for row in self.board:
                for piece in row:
                    if piece and piece.color == self.turn and piece.kind == 'T':
                        piece.kind = 'W'
                        self.events.append('Гусеница стала бабочкой')
        any_moves = any(self.legal(r, c) for r in range(8) for c in range(8))
        if not any_moves:
            self.status = 'Мат — победили ' + ('белые' if self.turn == 'black' else 'чёрные') if self.in_check(self.turn) else 'Пат — ничья'
        else:
            self.status = 'Шах' if self.in_check(self.turn) else 'Игра идёт'

    @staticmethod
    def square_name(pos):
        return 'abcdefgh'[pos[1]] + str(8 - pos[0])

    def move_notation(self, start, end):
        """Алгебраическая запись до изменения доски."""
        r, c = start
        nr, nc = end
        piece = self.board[r][c]
        kind = piece.kind
        if kind == 'W':
            return 'W' + self.square_name(start) + '↔' + self.square_name(end)
        if kind == 'K' and abs(nc - c) == 2:
            return 'O-O' if nc > c else 'O-O-O'
        capture = self.board[nr][nc] is not None or (kind == 'P' and c != nc)
        if kind == 'P':
            prefix = 'abcdefgh'[c] if capture else ''
        else:
            others = [(row, col) for row in range(8) for col in range(8)
                      if (row, col) != start and self.board[row][col]
                      and self.board[row][col].color == piece.color
                      and self.board[row][col].kind == kind
                      and end in self.legal(row, col)]
            if others:
                same_file = any(col == c for row, col in others)
                same_rank = any(row == r for row, col in others)
                prefix = kind + (('abcdefgh'[c] if not same_file else str(8-r))
                                 if not (same_file and same_rank) else 'abcdefgh'[c] + str(8-r))
            else:
                prefix = kind
        return prefix + ('x' if capture else '') + self.square_name(end)

    def record_move(self, notation):
        suffix = '#' if self.status.startswith('Мат') else '+' if self.status == 'Шах' else ''
        self.history.append(notation + suffix)

    def move(self, start, end):
        if not all(isinstance(pos, (list, tuple)) and len(pos) == 2 for pos in (start, end)):
            raise ValueError('Нужны координаты начала и конца')
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (*start, *end)) or not inside(*start) or not inside(*end):
            raise ValueError('Координаты должны быть от 0 до 7')
        start, end = tuple(start), tuple(end)
        r, c = start
        if end not in self.legal(r, c):
            raise ValueError('Недопустимый ход')
        notation = self.move_notation(start, end)
        self.events.clear()
        self.apply(start, end)
        # При обмене с бабочкой росток может оказаться на последней горизонтали.
        promotion_square = start if self.board[end[0]][end[1]].kind == 'W' else end
        pr, pc = promotion_square
        pawn = self.board[pr][pc]
        if pawn and pawn.kind in ('P', *SPROUTS) and pr == (0 if pawn.color == 'white' else 7):
            self.pending_promotion = list(promotion_square)
            self.pending_notation = notation
            self.status = 'Выберите фигуру для превращения'
        else:
            self.finish_turn()
            self.record_move(notation)

    def promote(self, kind):
        if not self.pending_promotion or kind not in self.promotion_options:
            raise ValueError('Недопустимое превращение')
        r, c = self.pending_promotion
        self.board[r][c] = Piece(kind, self.turn)
        self.board[r][c].moved = True
        self.pending_promotion = None
        notation = self.pending_notation + '=' + kind
        self.pending_notation = None
        self.finish_turn()
        self.record_move(notation)
