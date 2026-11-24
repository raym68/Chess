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
        g = position(('d4', 'F', 'white'), ('d5', 'S', 'black'))
        self.assertNotIn((2, 3), g.attacks(4, 3))
        self.assertEqual(len(g.attacks(4, 3)), 15)
        g.board[4][3].kind = 'A'
        self.assertIn((2, 3), g.attacks(4, 3))
        self.assertEqual(len(g.attacks(4, 3)), 16)

    def test_phoenix_moves_captures_and_checks_at_both_distances(self):
        for kind in ('F', 'A'):
            for distance in (1, 2):
                with self.subTest(kind=kind, distance=distance):
                    g = position(('h1', 'T', 'white'), ('d4', kind, 'white'),
                                 ('a8', 'T', 'black'))
                    end = (4-distance, 3)
                    self.assertIn(end, g.legal(4, 3))
                    g.board[end[0]][end[1]] = Piece('S', 'black')
                    g.move((4, 3), end)
                    self.assertEqual(g.board[end[0]][3].kind, kind)
                    g.board[end[0]][3+distance] = g.board[0][0]
                    g.board[0][0] = None
                    self.assertTrue(g.in_check('black'))

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
        g = position(('e8', 'T', 'black'), ('d7', 'S', 'black'),
                     ('a1', 'T', 'white'), ('a2', 'R', 'white'))
        g.move((6, 0), (6, 4))
        self.assertEqual(g.board[0][4].kind, 'W')
        self.assertEqual(g.status, 'Шах')
        self.assertEqual(g.legal(0, 4), [(1, 3)])
        g.move((0, 4), (1, 3))
        self.assertEqual(g.board[0][4].kind, 'S')
        self.assertEqual(g.board[1][3].kind, 'W')
        self.assertEqual(g.history[-1], 'We8↔d7')

    def test_mate_after_transformation(self):
        g = position(('e8', 'T', 'black'), ('a1', 'T', 'white'), ('a2', 'R', 'white'))
        g.move((6, 0), (6, 4))
        self.assertTrue(g.status.startswith('Мат'))
        self.assertEqual(g.board[0][4].kind, 'W')

    def test_sprout_promotes_after_swap(self):
        g = position(('a8', 'W', 'white'), ('b7', 'S', 'white'), ('h8', 'T', 'black'))
        g.move((0, 0), (1, 1))
        self.assertEqual(g.pending_promotion, [0, 0])
        g.promote('F')
        self.assertEqual(g.board[0][0].kind, 'F')
        self.assertEqual(g.turn, 'black')

    def test_both_starting_positions(self):
        self.assertEqual([p.kind for p in Game(forest=True).board[7]], list('RNBFTBNR'))
        self.assertEqual([p.kind for p in Game().board[7]], list('RNBQKBNR'))

    def test_sprout_quiet_moves_and_attacks_for_both_colors(self):
        for color, row, step in [('white', 6, -1), ('black', 1, 1)]:
            for kind in ('S', 'M'):
                with self.subTest(color=color, kind=kind):
                    g = position()
                    g.board[row][0] = Piece(kind, color)
                    self.assertEqual(g.candidates(row, 0), [(row+step, 1)])
                    self.assertEqual(g.attacks(row, 0), [(row+step, 0)])
                    g.board[row+step][1] = Piece('B', 'black' if color == 'white' else 'white')
                    g.en_passant = (row+step, 1)
                    self.assertEqual(g.candidates(row, 0), [])
                    g.board[row+step][0] = Piece('R', color)
                    self.assertEqual(g.candidates(row, 0), [])

    def test_sprout_capture_and_promotion_leave_mini(self):
        for kind in ('S', 'M'):
            g = position(('a1', 'T', 'white'), ('h8', 'T', 'black'),
                         ('c7', kind, 'white'), ('c8', 'N', 'black'))
            g.move((1, 2), (0, 2))
            self.assertEqual(g.board[1][2], Piece('M', 'white', moved=True))
            g.promote('N')
            self.assertEqual(g.history, [kind + 'xc8=N'])
            self.assertEqual(g.board[1][2].kind, 'M')

    def test_diagonal_move_checks_straight_ahead(self):
        g = position(('a1', 'T', 'white'), ('c6', 'T', 'black'), ('b4', 'S', 'white'))
        g.move((4, 1), (3, 2))
        self.assertIsNone(g.board[4][1])
        self.assertEqual(g.board[2][2].kind, 'W')
        self.assertTrue(g.in_check('black'))
        self.assertEqual(g.history[-1], 'Sc5#')

    def test_ordinary_pawn_still_captures_en_passant(self):
        g = Game()
        for start, end in [((6, 4), (4, 4)), ((1, 0), (2, 0)), ((4, 4), (3, 4)),
                           ((1, 3), (3, 3)), ((3, 4), (2, 3))]:
            g.move(start, end)
        self.assertEqual(g.history[-1], 'exd6')
        self.assertIsNone(g.board[3][4])
        self.assertIsNone(g.board[3][3])
