import unittest

from backend.game import Game
from backend.models import Piece, new_board


# Вспомогательная функция: расставляем нужные фигуры на пустую доску
def setup_board(*pieces, turn='white'):
    g = Game()
    g.board = new_board()
    g.turn = turn
    for square, kind, color in pieces:
        row = 8 - int(square[1])
        col = ord(square[0]) - ord('a')
        g.board[row][col] = Piece(kind, color)
    return g


class ClassicChessTests(unittest.TestCase):
    # Проверяем, что на старте все фигуры стоят на своих местах
    def test_initial_board_layout(self):
        g = Game()
        self.assertEqual([p.kind for p in g.board[7]], list('RNBQKBNR'))
        self.assertEqual([p.kind for p in g.board[6]], ['P'] * 8)
        self.assertEqual([p.kind for p in g.board[0]], list('RNBQKBNR'))
        self.assertEqual([p.kind for p in g.board[1]], ['P'] * 8)

    # Проверяем дурацкий мат за черных (самый быстрый мат в шахматах)
    def test_fools_mate(self):
        g = Game()
        g.move((6, 5), (5, 5))  # f2-f3
        g.move((1, 4), (3, 4))  # e7-e5
        g.move((6, 6), (4, 6))  # g2-g4
        g.move((0, 3), (4, 7))  # Qh4#
        self.assertEqual(g.status, 'Мат — победили чёрные')
        self.assertEqual(g.history[-1], 'Qh4#')

    # Проверяем короткую рокировку (O-O)
    def test_kingside_castling(self):
        g = setup_board(('e1', 'K', 'white'), ('h1', 'R', 'white'), ('e8', 'K', 'black'))
        # Король e1 ходит на g1 (с (7, 4) на (7, 6))
        self.assertIn((7, 6), g.legal(7, 4))
        g.move((7, 4), (7, 6))
        # Король должен встать на g1, а ладья перепрыгнуть на f1
        self.assertEqual(g.board[7][6].kind, 'K')
        self.assertEqual(g.board[7][5].kind, 'R')
        self.assertEqual(g.history[-1], 'O-O')

    # Проверяем, что нельзя делать рокировку через битое поле
    def test_castling_through_check_forbidden(self):
        # Черная ладья на d8 простреливает поле d1 (транзитное для длинной рокировки)
        g = setup_board(('e1', 'K', 'white'), ('a1', 'R', 'white'),
                        ('d8', 'R', 'black'), ('e8', 'K', 'black'))
        # Длинная рокировка на c1 (7, 2) должна быть заблокирована
        self.assertNotIn((7, 2), g.legal(7, 4))

    # Проверяем превращение пешки в ферзя на 8-й горизонтали
    def test_pawn_promotion(self):
        g = setup_board(('a7', 'P', 'white'), ('g7', 'K', 'black'), ('h1', 'K', 'white'))
        g.move((1, 0), (0, 0))  # a7-a8
        self.assertEqual(g.status, 'Выберите фигуру для превращения')
        g.promote('Q')
        self.assertEqual(g.board[0][0].kind, 'Q')
        self.assertEqual(g.history[-1], 'a8=Q')

    # Проверяем пат (когда ходов нет, но шаха королю тоже нет — ничья)
    def test_stalemate(self):
        # Классическая позиция пата: черный король в углу a8, белые на c7 и b6
        g = setup_board(('a8', 'K', 'black'), ('c7', 'Q', 'white'),
                        ('b6', 'K', 'white'), turn='white')
        g.finish_turn()  # передаем ход черным
        # Ходов у черных нет, но шах не объявлен
        self.assertFalse(g.in_check('black'))
        self.assertEqual(g.status, 'Пат — ничья')


if __name__ == '__main__':
    unittest.main()
