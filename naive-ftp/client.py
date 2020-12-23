import socket
import sys
import os
import time
from utils import log

server_host = socket.gethostname()
server_port = 2121
local_dir = 'local_files'


class ftp_client():
    '''
    Naive-FTP client side
    '''

    def __init__(self):
        self.buffer_size = 1024
        self.conn = None

    def connect(self):
        if self.conn:
            op = input(
                'Already connected. Close and establish a new connection? (y/N): ',
            )
            if op.lower() != 'y':
                return
            self.conn.close()
            self.conn = None
            print('Connection closed.')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        err = self.conn.connect_ex((server_host, server_port))
        if err:
            print(f'Connection failed. error: {err}')
            self.conn = None
        else:
            print('Connected to server.')

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

    def close(self):
        print('Bye!')
        sys.exit()

    def router(self, raw_cmd):
        try:
            cmd = raw_cmd.split(None, 1)
            op = cmd[0]
            path = cmd[1] if len(cmd) == 2 else None
            method_dict = {
                'CON': self.connect,
                'GET': self.get,
                'POS': self.post,
                'PUT': self.put,
                'PAT': self.patch,
                'DEL': self.delete,
                'QUI': self.close,
                'EXI': self.close,
            }
            method = method_dict.get(op[:3].upper())
            method(path) if path else method()
        except Exception as e:
            print(f'Invalid operation: {raw_cmd}')

    def run(self):
        while True:
            raw_cmd = input('> ')
            self.router(raw_cmd)


def main():
    ftp_client().run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted.')
