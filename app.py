"""Простой веб-сервер на стандартной библиотеке http.server:
GET-запросы отдают HTML-страницы, POST-запросы логируются в консоль."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 8000


class ContactsHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов: отдаёт HTML-страницы на GET,
        печатает тело запроса в консоль на POST."""

    def do_GET(self):
        """Обрабатывает любой GET-запрос — возвращает contacts.html."""

        with open('templates/contacts.html', 'r', encoding='utf-8') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        """Обрабатывает любой POST-запрос — читает тело запроса
               и печатает его (включая разобранные form-данные) в консоль."""
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length)
        body_str = raw_body.decode('utf-8')

        print(f'\n--- POST запрос на {self.path} ---')
        print(f'Заголовки:\n{self.headers}')
        print(f'Сырое тело: {body_str}')

        content_type = self.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            parsed = parse_qs(body_str)
            print(f'Разобранные данные формы: {parsed}')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<h1>Данные получены, смотри консоль сервера</h1>'.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=ContactsHandler):
    """Запускает HTTP-сервер на HOST:PORT и держит его активным."""
    server_address = (HOST, PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on http://{HOST}:{PORT}')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
