import socket
import sys
import os
import re
from typing import Tuple
from utils import log

server_host: str = socket.gethostname()
server_port: int = 2121


class ftp_client():
    '''
    Naive-FTP client side
    '''

    def __init__(self) -> None:
        '''
        Initialize class variables.
        '''

        # Properties
        self.buffer_size: int = 1024
        self.ctrl_timeout_duration: float = 3.0
        self.data_timeout_duration: float = 3.0
        self.local_dir: str = os.path.join(os.getcwd(), 'local_files')

        # Control connection
        self.ctrl_conn: socket = None

        # Data connection
        self.data_conn: socket = None
        self.data_addr: Tuple[str, int] = None

    def check_resp(self, code: int) -> Tuple[bool, int, str]:
        '''
        Get a response from the server, and check its status code.

        Return the check result, the responded status code and the response message.
        The result is True if the status code is expected, otherwise False.

        :param code: expected status code
        '''

        def get_resp() -> str:
            return (
                self.ctrl_conn
                .recv(self.buffer_size)
                .decode('utf-8')
                .strip('\r\n')
            )

        try:
            resp = get_resp()
        except socket.timeout:
            log('info', f'No response received, should be: {code}')
            return False, 0, None
        except socket.error as e:
            log('info', f'Remote connection closed: {e}, should be: {code}')
            self.close_ctrl_conn()
            return False, 0, None

        try:
            resp_code, _ = resp.split(None, 1)
            if resp_code != str(code):
                log('debug', f'Response: {resp_code}, should be: {code}')
                return False, resp_code, resp
            return True, resp_code, resp
        except ValueError as e:
            log('error', f'Invalid response: {resp}')
            self.close_ctrl_conn()
            return False, 0, None

    def open_data_conn(self) -> None:
        '''
        Open data connection.
        '''

        self.data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_conn.settimeout(self.data_timeout_duration)

        # Gets data_addr
        expected, _, resp = self.check_resp(227)
        if not expected:  # not under passive mode
            self.close_data_conn()
            return
        addr = re.search(
            r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)',
            resp,
        )
        if not addr:  # invalid response
            log('warn', f'Invalid response: {resp}')
            self.close_data_conn()
            return
        self.data_addr = (
            '.'.join(addr.group(1, 2, 3, 4)),
            (int(addr.group(5)) << 8) + int(addr.group(6)),
        )
        err = self.data_conn.connect_ex(self.data_addr)
        if err:
            log('warn', f'Data connection failed, error: {err}')
            self.close_data_conn()
        else:
            log('info', f'Data connection opened: {self.data_addr}')

    def close_data_conn(self) -> None:
        '''
        Close data connection.
        '''

        if self.data_conn:
            self.data_conn.close()
            self.data_conn = None

    def open_ctrl_conn(self) -> None:
        '''
        Open control connection.
        '''

        if self.ping():
            op = input(
                'Already connected. Close and establish a new connection? (y/N): ',
            )
            if op.lower() != 'y':
                return
            self.close_ctrl_conn()

        self.ctrl_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctrl_conn.settimeout(self.ctrl_timeout_duration)
        err = self.ctrl_conn.connect_ex((server_host, server_port))
        if err:
            log('warn', f'Connection failed, error: {err}')
            self.close_ctrl_conn()
        elif not self.check_resp(220)[0]:
            self.close_ctrl_conn()
        else:
            log('info', 'Connected to server.')

    def close_ctrl_conn(self) -> None:
        '''
        Close control connection.
        '''

        if self.ctrl_conn:
            self.ctrl_conn.close()
            self.ctrl_conn = None
            log('info', 'Connection closed.')

    def open(self) -> None:
        '''
        Open connection to server.
        '''

        self.open_ctrl_conn()

    def close(self) -> None:
        '''
        Close all connections and quit.
        '''

        self.close_data_conn()
        self.close_ctrl_conn()
        print('Bye!')
        sys.exit()

    def ping(self) -> bool:
        '''
        Check connection to server. Ping!
        '''

        if not self.ctrl_conn:
            return False
        try:
            self.ctrl_conn.sendall('PING\r\n'.encode('utf-8'))
            if not self.check_resp(220)[0]:
                self.close_ctrl_conn()
                return False
        except (socket.timeout, socket.error):
            return False
        else:
            return True

    def retrieve(self, path: str) -> None:
        '''
        Retrieve a file from server.

        :param path: relative path to the file
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        dst_path = os.path.realpath(os.path.join(self.local_dir, path))
        log('info', f'Downloading file: {dst_path}')

        self.ctrl_conn.sendall(f'RETR {path}\r\n'.encode('utf-8'))

        expected, _, resp = self.check_resp(150)
        if not expected:
            log('warn', resp)
            return
        self.open_data_conn()
        if not self.check_resp(225)[0]:
            self.close_data_conn()
            return

        try:
            with open(dst_path, 'wb') as dst_file:
                while True:
                    data = self.data_conn.recv(self.buffer_size)
                    if not data:
                        break
                    dst_file.write(data)
        except OSError as e:
            log('warn', f'OS error: {e}')
        except socket.error:
            log('info', 'Data connection closed.')
        else:
            log('info', 'File successfully downloaded.')
        finally:
            self.close_data_conn()

    def store(self, path: str) -> None:
        '''
        Store a file to server.

        :param path: relative path to the file
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        src_path = os.path.realpath(os.path.join(self.local_dir, path))
        if not os.path.isfile(src_path):
            log('info', 'File not found.')
            return
        log('info', f'Uploading file: {src_path}')

        self.ctrl_conn.sendall(f'STOR {path}\r\n'.encode('utf-8'))

        expected, _, resp = self.check_resp(150)
        if not expected:
            log('info', resp)
            return
        self.open_data_conn()
        if not self.check_resp(225)[0]:
            self.close_data_conn()
            return

        try:
            with open(src_path, 'rb') as src_file:
                while True:
                    data = src_file.read(self.buffer_size)
                    if not data:
                        break
                    self.data_conn.sendall(data)
        except OSError as e:
            log('warn', f'OS error: {e}')
        except socket.error:
            log('info', 'Data connection closed.')
        else:
            log('info', 'File successfully uploaded.')
        finally:
            self.close_data_conn()

    def delete(self, path: str) -> None:
        '''
        Delete a file from server.

        :param path: relative path to the file
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        log('info', f'Deleting file: {path}')

        self.ctrl_conn.sendall(f'DELE {path}\r\n'.encode('utf-8'))

        expected, _, resp = self.check_resp(250)
        log('info' if expected else 'warn', resp)

    def mkdir(self, path: str) -> None:
        '''
        Make a directory recursively.

        :param path: relative path to the directory
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'MKD {path}\r\n'.encode('utf-8'))
        expected, _, resp = self.check_resp(250)
        log('info' if expected else 'warn', resp)

    def rmdir(self, path: str, recursive: bool = False) -> None:
        '''
        Remove a directory.

        :param path: relative path to the directory
        :param recursive: remove recursively if True
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        op = 'RMDA' if recursive else 'RMD'
        self.ctrl_conn.sendall(f'{op} {path}\r\n'.encode('utf-8'))
        expected, _, resp = self.check_resp(250)
        log('info' if expected else 'warn', resp)

    def rmdir_all(self, path: str) -> None:
        '''
        Remove a directory recursively.

        :param path: relative path to the directory
        '''

        self.rmdir(path, recursive=True)

    def router(self, raw_cmd: str) -> None:
        '''
        Route to the associated method based on user command.

        :param raw_cmd: raw user command
        '''

        try:
            cmd = raw_cmd.split(None, 1)
            op = cmd[0]
            path = cmd[1] if len(cmd) == 2 else None
            method_dict = {
                'OPEN': self.open,
                'QUIT': self.close,
                'EXIT': self.close,         # alias
                'RETR': self.retrieve,
                'GET': self.retrieve,       # alias
                'STOR': self.store,
                'PUT': self.store,          # alias
                'DELE': self.delete,
                'DEL': self.delete,         # alias
                'RM': self.delete,          # alias
                'MKD': self.mkdir,
                'MKDI': self.mkdir,         # alias
                'RMD': self.rmdir,
                'RMDI': self.rmdir,         # alias
                'RMDA': self.rmdir_all,
            }
            method = method_dict.get(op[:4].upper())
            if method:
                method(path) if path else method()
            else:
                log('info', f'Invalid operation: {raw_cmd}')
        except TypeError:
            log('info', f'Invalid operation: {raw_cmd}')

    def run(self) -> None:
        '''
        Main function for client.
        '''

        while True:
            try:
                raw_cmd = input('> ')
                if raw_cmd:
                    self.router(raw_cmd)
            except socket.timeout:
                log('info', f'Connection timeout.')
                self.close_ctrl_conn()
            except socket.error:
                log('info', f'Remote connection closed.')
                self.close_ctrl_conn()
            except KeyboardInterrupt:
                print('\nInterrupted.')
                self.close()
                break
            except Exception as e:
                log('error', f'Unexpected exception: {e}')
                self.close()
                raise


if __name__ == '__main__':
    ftp_client().run()
