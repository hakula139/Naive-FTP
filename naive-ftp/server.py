import socket
import os
from utils import log

listen_host = socket.gethostname()
listen_port = 2121


class ftp_server():
    '''
    Naive-FTP server side
    '''

    def __init__(self):
        # Properties
        self.buffer_size = 1024
        self.ctrl_timeout_duration = 30.0
        self.data_timeout_duration = 1.0

        # Control connection
        self.ctrl_sock = None
        self.ctrl_conn = None
        self.client_addr = None

        # Data connection
        self.data_sock = None
        self.data_conn = None
        self.data_addr = None

    def send_status(self, status_code):
        status_dict = {
            220: '220 Service ready for new user.\r\n',
            221: '221 Service closing control connection.\r\n',
            225: '225 Data connection open; no transfer in progress.\r\n',
            501: '501 Syntax error in parameters or arguments.\r\n',
        }
        status = status_dict.get(status_code)
        if status:
            self.ctrl_conn.sendall(status.encode('utf-8'))
        else:
            log('warn', 'send_status', f'Invalid status code: {status_code}')

    def close_data_conn(self):
        if self.data_conn:
            self.data_conn.close()
            self.data_conn = None
            log('info', 'close_data_conn',
                f'Data connection closed: {self.client_addr}')

    def close_data_sock(self):
        self.close_data_conn()
        if self.data_sock:
            self.data_sock.close()
            self.data_sock = None
            log('info', 'close_data_sock',
                f'Data socket closed: {self.client_addr}')

    def open_data_conn(self):
        self.data_conn, self.data_addr = self.data_sock.accept()
        self.data_conn.settimeout(self.data_timeout_duration)
        log('info', 'open_data_conn',
            f'Data connection opened: {self.client_addr}')
        self.send_status(225)

    def open_data_sock(self):
        if self.data_sock:
            self.close_data_sock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((listen_host, 0))
        s.listen(5)
        self.data_sock = s
        self.open_data_conn()

    def close_ctrl_conn(self):
        if self.ctrl_conn:
            self.ctrl_conn.close()
            self.ctrl_conn = None
            log('info', 'close_ctrl_conn',
                f'Connection closed: {self.client_addr}')

    def close_ctrl_sock(self):
        self.close_ctrl_conn()
        if self.ctrl_sock:
            self.ctrl_sock.close()
            self.ctrl_sock = None
            log('info', 'close_ctrl_sock',
                f'Socket closed: {self.client_addr}')

    def open_ctrl_conn(self):
        self.ctrl_conn, self.client_addr = self.ctrl_sock.accept()
        self.ctrl_conn.settimeout(self.ctrl_timeout_duration)
        log('info', 'open_ctrl_conn', f'Accept connection: {self.client_addr}')
        self.send_status(220)

    def open_ctrl_sock(self):
        if self.ctrl_sock:
            self.close_ctrl_sock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((listen_host, listen_port))
        s.listen(5)
        self.ctrl_sock = s

    def close(self):
        self.close_data_sock()
        self.close_ctrl_sock()

    def retrieve(self, path):
        if not self.data_sock:
            self.open_data_sock()
        local_path = os.path.join(os.getcwd(), path)

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
                'RETR': self.retrieve,
                'STOR': self.store,
                'DELE': self.delete,
            }
            method = method_dict.get(op[:4].upper())
            method(path) if path else method()
        except Exception as e:
            log('warn', 'router', f'Invalid client operation: {raw_cmd}')
            self.send_status(501)

    def run(self):
        try:
            self.open_ctrl_sock()
            log('info', 'run',
                f'Server started, listening at {self.ctrl_sock.getsockname()}')
            while self.ctrl_sock:
                try:
                    self.open_ctrl_conn()
                    while self.ctrl_conn:
                        raw_cmd = self.ctrl_conn.recv(self.buffer_size)
                        if not raw_cmd:  # Connection closed
                            break
                        log('debug', 'run', f'Operation: {raw_cmd}')
                        self.router(raw_cmd.decode('utf-8'))
                except socket.timeout:
                    log('info', 'run',
                        f'Connection timeout: {self.client_addr}')
                except socket.error:
                    pass
                except Exception as e:
                    raise
                finally:
                    self.close_ctrl_conn()
        except socket.error:
            pass
        except Exception as e:
            log('warn', 'run', f'Unexpected exception: {e}')
            raise
        finally:
            self.close_ctrl_sock()


if __name__ == '__main__':
    try:
        ftp_server().run()
    except KeyboardInterrupt:
        print('\nInterrupted.')
