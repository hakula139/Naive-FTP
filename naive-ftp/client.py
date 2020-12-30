import socket
import sys
import os
import re
from utils import log

server_host = socket.gethostname()
server_port = 2121
local_dir = 'local_files'


class ftp_client():
    '''
    Naive-FTP client side
    '''

    def __init__(self):
        # Properties
        self.buffer_size = 1024
        self.ctrl_timeout_duration = 3.0
        self.data_timeout_duration = 3.0

        # Control connection
        self.ctrl_conn = None

        # Data connection
        self.data_conn = None
        self.data_addr = None

    def check_resp(self, code):
        '''
        Gets a response from server, and checks its status code.
        Returns the response if the status code matches the given argument,
        else returns None.
        '''

        def get_resp():
            return (
                self.ctrl_conn
                .recv(self.buffer_size)
                .decode('utf-8')
                .strip('\r\n')
            )

        try:
            resp = get_resp()
        except socket.timeout as e:
            log('info', 'check_resp',
                f'No response received, should be: {code}')
            return None
        except socket.error as e:
            log('info', 'check_resp',
                f'Remote connection closed: {e}, should be: {code}')
            self.close_ctrl_conn()
            return None

        try:
            if resp[:3] != str(code):
                log('debug', 'check_resp',
                    f'Response: {resp[:3]}, should be: {code}')
                return None
            return resp
        except Exception as e:
            log('error', 'check_resp', f'Unexpected exception: {e}')
            self.close_ctrl_conn()
            return None

    def open_data_conn(self):
        self.data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_conn.settimeout(self.data_timeout_duration)

        # Gets data_addr
        resp = self.check_resp(227)
        if not resp:  # not under passive mode
            self.close_data_conn()
            return
        addr = re.search(
            r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)',
            resp,
        )
        if not addr:  # invalid response
            log('warn', 'open_data_conn', f'Invalid server response: {resp}')
            self.close_data_conn()
            return
        self.data_addr = (
            '.'.join(addr.group(1, 2, 3, 4)),
            (int(addr.group(5)) << 8) + int(addr.group(6)),
        )
        err = self.data_conn.connect_ex(self.data_addr)
        if err:
            log('warn', 'open_data_conn',
                f'Data connection failed. error: {err}')
            self.close_data_conn()
        else:
            log('info', 'open_data_conn',
                f'Data connection opened: {self.data_addr}')

    def close_data_conn(self):
        if self.data_conn:
            self.data_conn.close()
            self.data_conn = None

    def open_ctrl_conn(self):
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
            log('warn', 'open_ctrl_conn', f'Connection failed. error: {err}')
            self.close_ctrl_conn()
        elif not self.check_resp(220):
            self.close_ctrl_conn()
        else:
            log('info', 'open_ctrl_conn', 'Connected to server.')

    def close_ctrl_conn(self):
        if self.ctrl_conn:
            self.ctrl_conn.close()
            self.ctrl_conn = None
            log('info', 'close_ctrl_conn', 'Connection closed.')

    def open(self):
        self.open_ctrl_conn()

    def close(self):
        self.close_data_conn()
        self.close_ctrl_conn()
        print('Bye!')
        sys.exit()

    def ping(self):
        if not self.ctrl_conn:
            return False
        self.ctrl_conn.sendall('PING\r\n'.encode('utf-8'))
        if not self.check_resp(220):
            self.close_ctrl_conn()
            return False
        return True

    def retrieve(self, path):
        if not self.ping():
            log('info', 'retrieve', 'Please connect to server first.')
            return

        dst_path = os.path.join(os.getcwd(), local_dir, path)
        log('info', 'retrieve', f'Downloading file: {dst_path}')

        self.ctrl_conn.sendall(f'RETR {path}\r\n'.encode('utf-8'))

        if not self.check_resp(150):  # requested file available
            log('info', 'retrieve', 'Requested file does not exist.')
            return
        self.open_data_conn()
        if not self.check_resp(225):  # data connection established
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
            log('warn', 'retrieve', f'OS error: {e}')
        except socket.error:
            log('info', 'retrieve', 'Data connection closed.')
        else:
            log('info', 'retrieve', 'File successfully downloaded.')
        finally:
            self.close_data_conn()

    def store(self, path):
        if not self.ping():
            log('info', 'store', 'Please connect to server first.')
            return

        src_path = os.path.join(os.getcwd(), local_dir, path)
        if not os.path.isfile(src_path):
            log('info', 'store', 'File does not exist.')
            return
        log('info', 'store', f'Uploading file: {src_path}')

        self.ctrl_conn.sendall(f'STOR {path}\r\n'.encode('utf-8'))

        if not self.check_resp(150):  # server status ok
            return
        self.open_data_conn()
        if not self.check_resp(225):  # data connection established
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
            log('warn', 'store', f'OS error: {e}')
        except socket.error:
            log('info', 'store', 'Data connection closed.')
        else:
            log('info', 'store', 'File successfully uploaded.')
        finally:
            self.close_data_conn()

    def delete(self, path):
        if not self.ping():
            log('info', 'delete', 'Please connect to server first.')
            return

        log('info', 'delete', f'Deleting file: {path}')

        self.ctrl_conn.sendall(f'DELE {path}\r\n'.encode('utf-8'))

        if not self.check_resp(250):
            log('info', 'delete', 'Requested file does not exist.')
        else:
            log('info', 'delete', 'File successfully deleted.')

    def mkdir(self, path):
        if not self.ping():
            log('info', 'mkdir', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'MKD {path}\r\n'.encode('utf-8'))
        if not self.check_resp(250):
            log('warn', 'mkdir', 'Failed to make directory. See server log for details.')
        else:
            log('info', 'mkdir', 'Directory successfully created.')

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
                'MKD': self.mkdir,
            }
            method = method_dict.get(op[:4].upper())
            if method:
                method(path) if path else method()
            else:
                log('info', 'router', f'Invalid operation: {raw_cmd}')
        except TypeError as e:
            log('info', 'router', f'Invalid operation: {raw_cmd}')

    def run(self):
        while True:
            try:
                raw_cmd = input('> ')
                if raw_cmd:
                    self.router(raw_cmd)
            except socket.timeout:
                log('info', 'run', f'Connection timeout.')
                self.close_ctrl_conn()
            except socket.error:
                log('info', 'run', f'Remote connection closed.')
                self.close_ctrl_conn()
            except KeyboardInterrupt:
                print('\nInterrupted.')
                self.close()
                break
            except Exception as e:
                log('error', 'run', f'Unexpected exception: {e}')
                self.close()
                raise


if __name__ == '__main__':
    ftp_client().run()
