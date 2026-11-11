"""Небольшой HTTP-сервер без сторонних пакетов."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
from .game import Game

ROOT = Path(__file__).resolve().parents[1] / 'frontend'
game = Game()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_json(self):
        size = int(self.headers.get('Content-Length', '0'))
        if size > 4096:
            raise ValueError('Слишком большой запрос')
        return json.loads(self.rfile.read(size))

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/api/state':
            return self.send_json(game.serialize())
        if url.path == '/api/moves':
            try:
                query = parse_qs(url.query)
                r, c = int(query['r'][0]), int(query['c'][0])
                if not (0 <= r < 8 and 0 <= c < 8):
                    raise ValueError('Координаты от 0 до 7')
                return self.send_json({'moves': game.legal(r, c)})
            except (ValueError, KeyError, IndexError) as exc:
                return self.send_json({'error': str(exc)}, 400)
        return super().do_GET()

    def do_POST(self):
        global game
        try:
            data = self.read_json()
            if self.path == '/api/new':
                if 'back_rank' in data:
                    game = Game(data['back_rank'])
                elif 'back_pair' in data:  # совместимость со старой страницей в кэше браузера
                    pair = data['back_pair']
                    if not isinstance(pair, list) or len(pair) != 2:
                        raise ValueError('Нужны две фигуры для линий c и f')
                    rank = ['R', 'N', pair[0], 'Q', 'K', pair[1], 'N', 'R']
                    game = Game(rank)
                else:
                    raise ValueError('Нужна расстановка стартового ряда')
            elif self.path == '/api/move':
                start, end = data['start'], data['end']
                if not all(isinstance(pos, list) and len(pos) == 2 for pos in (start, end)):
                    raise ValueError('Нужны координаты начала и конца')
                game.move(start, end)
            elif self.path == '/api/promote':
                game.promote(data['kind'])
            else:
                return self.send_json({'error': 'Неизвестный адрес'}, 404)
            return self.send_json(game.serialize())
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self.send_json({'error': str(exc)}, 400)


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    print('Откройте http://127.0.0.1:8765')
    server.serve_forever()


if __name__ == '__main__':
    main()
