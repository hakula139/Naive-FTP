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

    def open(self):
        if self.conn:
            op = input(
                'Already connected. Close and establish a new connection? (y/N): ')
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

    def close(self):
        print('Bye!')
        sys.exit()

    def retrieve(self, path):
        if not self.conn:
            print('Please connect to server first.')

        self.conn.sendall(f'RETR {path}'.encode('utf-8'))

        local_path = os.path.join(os.getcwd(), path)
        dst_file = open(path, 'wb')

    def store(self, path):
        pass

    def delete(self, path):
        pass

    def router(self, raw_cmd):
        try:
            cmd = raw_cmd.split(None, 1)
            op = cmd[0]
            path = cmd[1] if len(cmd) == 2 else None
            method_dict = {
                'OPEN': self.open,
                'QUIT': self.close,
                'EXIT': self.close,
                'RETR': self.retrieve,
                'STOR': self.store,
                'DELE': self.delete,
            }
            method = method_dict.get(op[:4].upper())
            method(path) if path else method()
        except Exception as e:
            print(f'Invalid operation: {raw_cmd}')

    def run(self):
        while True:
            raw_cmd = input('> ')
            self.router(raw_cmd)


if __name__ == '__main__':
    try:
        ftp_client().run()
    except KeyboardInterrupt:
        print('\nInterrupted.')
