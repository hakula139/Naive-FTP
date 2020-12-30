import socket
import os
from utils import log

listen_host = socket.gethostname()
listen_port = 2121
server_dir = 'server_files'


class ftp_server():
    '''
    Naive-FTP server side
    '''

    def __init__(self):
        # Properties
        self.buffer_size = 1024
        self.ctrl_timeout_duration = 60.0
        self.data_timeout_duration = 3.0

        # Control connection
        self.ctrl_sock = None
        self.ctrl_conn = None
        self.client_addr = None

        # Data connection
        self.data_sock = None
        self.data_conn = None
        self.data_addr = None

    def send_status(self, status_code):
        def parsed_addr(addr):
            try:
                return '{host},{p1},{p2}'.format(
                    host=','.join(addr[0].split('.')),
                    p1=addr[1] >> 8 & 0xFF,
                    p2=addr[1] & 0xFF,
                )
            except TypeError:
                return ''

        status_dict = {
            150: '150 File status okay; about to open data connection.\r\n',
            220: '220 Service ready for new user.\r\n',
            221: '221 Service closing control connection.\r\n',
            225: '225 Data connection open; no transfer in progress.\r\n',
            226: '226 Closing data connection. Requested file action successful.\r\n',
            227: '227 Entering Passive Mode {}.\r\n'.format(parsed_addr(self.data_addr)),
            501: '501 Syntax error in parameters or arguments.\r\n',
            550: '550 Requested action not taken. File unavailable.\r\n',
        }

        status = status_dict.get(status_code)
        if status:
            self.ctrl_conn.sendall(status.encode('utf-8'))
        else:
            log('warn', 'send_status', f'Invalid status code: {status_code}')

    def open_data_conn(self):
        if self.data_conn:
            self.close_data_conn()
        self.data_conn, self.data_addr = self.data_sock.accept()
        self.data_conn.settimeout(self.data_timeout_duration)
        log('info', 'open_data_conn',
            f'Data connection opened: {self.data_addr}')
        self.send_status(225)

    def open_data_sock(self):
        if self.data_sock:
            self.close_data_sock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.data_timeout_duration)
        s.bind((listen_host, 0))
        s.listen(5)
        self.data_sock = s
        self.data_addr = self.data_sock.getsockname()
        log('info', 'open_data_sock',
            f'Data server started, listening at {self.data_addr}')
        self.send_status(227)

    def close_data_conn(self):
        if self.data_conn:
            self.data_conn.close()
            self.data_conn = None
            log('info', 'close_data_conn',
                f'Data connection closed: {self.data_addr}')

    def close_data_sock(self):
        self.close_data_conn()
        if self.data_sock:
            self.data_sock.close()
            self.data_sock = None
            log('info', 'close_data_sock',
                f'Data socket closed: {self.data_addr}')

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
        s.settimeout(self.ctrl_timeout_duration)
        s.bind((listen_host, listen_port))
        s.listen(5)
        self.ctrl_sock = s
        log('info', 'open_ctrl_sock',
            f'Server started, listening at {self.ctrl_sock.getsockname()}')

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

    def close(self):
        self.close_data_sock()
        self.close_ctrl_sock()

    def retrieve(self, path):
        src_path = os.path.join(os.getcwd(), server_dir, path)
        log('info', 'retrieve', f'Retrieving file: {src_path}')

        if not os.path.exists(src_path):
            self.send_status(550)
            return

        try:
            with open(src_path, 'rb') as src_file:
                self.send_status(150)
                if not self.data_sock:
                    self.open_data_sock()
                self.open_data_conn()
                log('info', 'retrieve', 'Sending file.')
                while True:
                    data = src_file.read(self.buffer_size)
                    if not data:
                        break
                    self.data_conn.sendall(data)
        except OSError as e:
            log('warn', 'retrieve', f'OS error: {e}')
            self.send_status(550)
        except socket.timeout:
            log('warn', 'retrieve',
                f'Data connection timeout: {self.data_addr}')
            self.send_status(426)
        except socket.error:
            pass
        finally:
            self.close_data_sock()

    def store(self, path):
        dst_path = os.path.join(os.getcwd(), server_dir, path)
        log('info', 'store', f'Storing file: {dst_path}')
        dir_name, file_name = dst_path.rsplit(os.sep, 1)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            log('info', 'store', f'Directory created: {dir_name}')
        if not file_name:  # make directory only
            return

        try:
            with open(dst_path, 'wb') as dst_file:
                self.send_status(150)
                if not self.data_sock:
                    self.open_data_sock()
                self.open_data_conn()
                while True:
                    data = self.data_conn.recv(self.buffer_size)
                    if not data:
                        break
                    dst_file.write(data)
        except OSError as e:
            log('warn', 'store', f'OS error: {e}')
            self.send_status(550)
        except socket.timeout:
            log('warn', 'store', f'Data connection timeout: {self.data_addr}')
            self.send_status(426)
        except socket.error:
            pass
        finally:
            self.close_data_sock()

    def delete(self, path):
        pass

    def mkdir(self, path):
        dst_path = os.path.join(os.getcwd(), server_dir, path)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
            log('info', 'mkdir', f'Directory created: {dst_path}')
        else:
            log('info', 'mkdir', f'Directory already exists: {dst_path}')

    def router(self, raw_cmd):
        try:
            cmd = raw_cmd.split(None, 1)
            op = cmd[0]
            path = cmd[1] if len(cmd) == 2 else None
            method_dict = {
                'RETR': self.retrieve,
                'STOR': self.store,
                'DELE': self.delete,
                'MKD': self.mkdir,
            }
            method = method_dict.get(op[:4].upper())
            method(path) if path else method()
        except Exception as e:
            log('warn', 'router',
                f'Invalid client operation: {raw_cmd}, error: {e}')
            self.send_status(501)

    def run(self):
        try:
            self.open_ctrl_sock()
            while self.ctrl_sock:
                try:
                    self.open_ctrl_conn()
                    while self.ctrl_conn:
                        raw_cmd = (
                            self.ctrl_conn
                            .recv(self.buffer_size)
                            .decode('utf-8')
                            .strip('\r\n')
                        )
                        if not raw_cmd:  # connection closed
                            break
                        log('debug', 'run', f'Operation: {raw_cmd}')
                        self.router(raw_cmd)
                except (socket.timeout, socket.error) as e:
                    pass
                finally:
                    self.close_ctrl_conn()
        except KeyboardInterrupt:
            print('\nInterrupted.')
        except Exception as e:
            log('error', 'run', f'Unexpected exception: {e}')
            raise
        finally:
            self.close()


if __name__ == '__main__':
    ftp_server().run()
