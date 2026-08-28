# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 8000


class ContactsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        with open('templates/contacts.html', 'r', encoding='utf-8') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
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
    server_address = (HOST, PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on http://{HOST}:{PORT}')
    httpd.serve_forever()


if __name__ == '__main__':
    run()