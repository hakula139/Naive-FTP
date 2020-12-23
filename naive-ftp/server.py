import socket
import os
from utils import log

listen_host = socket.gethostname()
listen_port = 2121


class ftp_server():
    '''
    Naive-FTP server side
    '''

    def __init__(self, conn, client_addr):
        self.buffer_size = 1024
        self.conn = conn
        self.client_addr = client_addr

    def get(self, path):
        pass

    def post(self, path):
        pass

    def put(self, path):
        pass

    def patch(self, path):
        pass

    def delete(self, path):
        pass

    def router(self, raw_cmd):
        try:
            cmd = raw_cmd.split(None, 1)
            op = cmd[0]
            path = cmd[1] if len(cmd) == 2 else None
            method_dict = {
                'GET': self.get,
                'POS': self.post,
                'PUT': self.put,
                'PAT': self.patch,
                'DEL': self.delete,
            }
            method = method_dict.get(op[:3].upper())
            method(path) if path else method()
        except Exception as e:
            log('warn', 'router', f'Invalid client operation: {raw_cmd}')

    def run(self):
        log('info', 'run', f'Accept connection from {self.client_addr}')
        while True:
            try:
                raw_cmd = self.conn.recv(self.buffer_size).decode('utf-8')
                if not raw_cmd:
                    break
                log('debug', 'run', f"Operation: '{raw_cmd}'")
                self.router(raw_cmd)
            except socket.timeout:
                log('info', 'run',
                    f"Connection timeout for {self.client_addr}")
                break


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((listen_host, listen_port))
        s.listen(5)
        log('info', 'main',
            f'Naive-FTP server started, listening at {s.getsockname()}')

        while True:
            conn, client_addr = s.accept()
            conn.settimeout(300.0)
            with conn:
                ftp_server(conn, client_addr).run()
            log('info', 'main', f'Closed connection from {client_addr}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted.')
