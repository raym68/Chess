import unittest

from backend.game import Game
from backend.models import Piece, new_board


def position(*pieces, turn='white'):
    game = Game(forest=True)
    game.board = new_board()
    game.turn = turn
    for square, kind, color in pieces:
        game.board[8-int(square[1])][ord(square[0])-ord('a')] = Piece(kind, color)
    return game


class ForestRules(unittest.TestCase):
    def test_phoenix_distance_and_obstacles(self):
        g = position(('d4', 'F', 'white'), ('d5', 'P', 'black'))
        self.assertNotIn((2, 3), g.attacks(4, 3))
        self.assertEqual(len(g.attacks(4, 3)), 7)
        g.board[4][3].kind = 'A'
        self.assertIn((2, 3), g.attacks(4, 3))
        self.assertEqual(len(g.attacks(4, 3)), 8)

    def test_rebirth_and_second_capture(self):
        g = position(('h1', 'T', 'white'), ('h7', 'T', 'black'),
                     ('d8', 'F', 'black'), ('d4', 'R', 'white'), ('c1', 'R', 'white'))
        g.move((4, 3), (0, 3))
        self.assertEqual(g.board[0][2].kind, 'A')
        self.assertTrue(g.events)
        g.move((1, 7), (2, 7))
        g.move((7, 2), (0, 2))
        self.assertFalse(any(p and p.kind == 'A' for row in g.board for p in row))

    def test_rebirth_can_make_capture_illegal(self):
        g = position(('d6', 'T', 'white'), ('h8', 'T', 'black'),
                     ('a4', 'F', 'black'), ('a1', 'R', 'white'))
        self.assertNotIn((4, 0), g.legal(7, 0))
        self.assertEqual(g.events, [])

    def test_first_check_and_swap(self):
        g = position(('e8', 'T', 'black'), ('d7', 'P', 'black'),
                     ('a1', 'T', 'white'), ('a2', 'R', 'white'))
        g.move((6, 0), (6, 4))
        self.assertEqual(g.board[0][4].kind, 'W')
        self.assertEqual(g.status, 'Шах')
        self.assertEqual(g.legal(0, 4), [(1, 3)])
        g.move((0, 4), (1, 3))
        self.assertEqual(g.board[0][4].kind, 'P')
        self.assertEqual(g.board[1][3].kind, 'W')
        self.assertEqual(g.history[-1], 'We8↔d7')

    def test_mate_after_transformation(self):
        g = position(('e8', 'T', 'black'), ('a1', 'T', 'white'), ('a2', 'R', 'white'))
        g.move((6, 0), (6, 4))
        self.assertTrue(g.status.startswith('Мат'))
        self.assertEqual(g.board[0][4].kind, 'W')

    def test_sprout_promotes_after_swap(self):
        g = position(('a8', 'W', 'white'), ('b7', 'P', 'white'), ('h8', 'T', 'black'))
        g.move((0, 0), (1, 1))
        self.assertEqual(g.pending_promotion, [0, 0])
        g.promote('F')
        self.assertEqual(g.board[0][0].kind, 'F')
        self.assertEqual(g.turn, 'black')

    def test_both_starting_positions(self):
        self.assertEqual([p.kind for p in Game(forest=True).board[7]], list('RNBFTBNR'))
        self.assertEqual([p.kind for p in Game().board[7]], list('RNBQKBNR'))
