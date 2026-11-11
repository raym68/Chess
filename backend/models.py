"""Данные шахматной партии: фигуры, доска и наборы фигур.

Здесь нет правил ходов и HTTP. Сериализация сохраняет формат JSON для фронтенда.
"""
from dataclasses import dataclass
from typing import List, Optional

BACK = ('R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R')
OPTIONS = frozenset(('B', 'G', 'C', 'E'))
PROMOTION = frozenset(('Q', 'R', 'B', 'N', 'G', 'C', 'E'))
SETUP_OPTIONS = (
    {'kind': 'B', 'name': 'Слон'},
    {'kind': 'G', 'name': 'Грифон'},
    {'kind': 'C', 'name': 'Верблюд'},
    {'kind': 'E', 'name': 'Прыгающий слон'},
)


@dataclass
class Piece:
    kind: str
    color: str
    moved: bool = False

    def to_dict(self):
        return {'kind': self.kind, 'color': self.color, 'moved': self.moved}


Board = List[List[Optional[Piece]]]


def new_board():
    return [[None for _ in range(8)] for _ in range(8)]


def board_to_dict(board):
    return [[piece.to_dict() if piece else None for piece in row] for row in board]
