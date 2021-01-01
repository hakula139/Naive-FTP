import socket
import sys
import os
import re
import stat
from datetime import datetime
from typing import Callable, Tuple
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
        self.local_dir: str = os.path.realpath('local_files')

        # Control connection
        self.ctrl_conn: socket.socket = None

        # Data connection
        self.data_conn: socket.socket = None
        self.data_addr: Tuple[str, int] = None

    def check_resp(self, code: int) -> Tuple[bool, int, str]:
        '''
        Get a response from the server, and check its status code.

        Return the check result, the responded status code and the response message.
        The result is True if the status code is expected, otherwise False.

        :param code: expected status code
        '''

        def _get_resp() -> str:
            return (
                self.ctrl_conn
                .recv(self.buffer_size)
                .decode('utf-8')
                .strip('\r\n')
            )

        try:
            resp = _get_resp()
        except socket.timeout:
            log('debug', f'No response received, should be: {code}')
            return False, 0, None
        except socket.error as e:
            log('debug', f'Remote connection closed: {e}, should be: {code}')
            self.close_ctrl_conn()
            return False, 0, None

        try:
            resp_code, resp_msg = resp.split(None, 1)
            if resp_code != str(code):
                log('debug', f'Response: {resp_code}, should be: {code}')
                return False, resp_code, resp_msg
            return True, resp_code, resp_msg
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
        expected, _, resp_msg = self.check_resp(227)
        if not expected:  # not under passive mode
            self.close_data_conn()
            return
        addr = re.search(
            r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)',
            resp_msg,
        )
        if not addr:  # invalid response
            log('error', f'Invalid response: {resp_msg}')
            self.close_data_conn()
            return
        self.data_addr = (
            '.'.join(addr.group(1, 2, 3, 4)),
            (int(addr.group(5)) << 8) + int(addr.group(6)),
        )
        err = self.data_conn.connect_ex(self.data_addr)
        if err:
            log('error', f'Data connection failed, error: {err}')
            self.close_data_conn()
        else:
            log('debug', f'Data connection opened: {self.data_addr}')

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
            log('error', f'Connection failed, error: {err}')
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
            log('debug', 'Connection closed.')

    def help(self) -> None:
        '''
        Show a list of available commands.
        '''

        def _print_cmd(cmd: str, usage: str, descr: str) -> None:
            '''
            Print a command and its usage.

            :param cmd: command
            :param usage: the parameters of the command
            :param descr: the description of the command
            '''

            print(f'   {cmd:4} {usage:10} {descr}')

        def _read_doc(method: Callable) -> str:
            '''
            Read the first line of the docstring for a method.

            :param method: a given method
            '''

            return method.__doc__.split('\n')[1]

        print('COMMANDS:')
        _print_cmd('HELP', '', _read_doc(self.help))
        _print_cmd('OPEN', '', _read_doc(self.open))
        _print_cmd('QUIT', '', _read_doc(self.close))
        _print_cmd('EXIT', '', _read_doc(self.close))
        _print_cmd('LIST', '<path>', _read_doc(self.ls))
        _print_cmd('LS', '<path>', _read_doc(self.ls))
        _print_cmd('RETR', '<path>', _read_doc(self.retrieve))
        _print_cmd('GET', '<path>', _read_doc(self.retrieve))
        _print_cmd('STOR', '<path>', _read_doc(self.store))
        _print_cmd('PUT', '<path>', _read_doc(self.store))
        _print_cmd('DELE', '<path>', _read_doc(self.delete))
        _print_cmd('DEL', '<path>', _read_doc(self.delete))
        _print_cmd('RM', '<path>', _read_doc(self.delete))
        _print_cmd('CWD', '<path>', _read_doc(self.cwd))
        _print_cmd('CD', '<path>', _read_doc(self.cwd))
        _print_cmd('PWD', '', _read_doc(self.pwd))
        _print_cmd('MKD', '<path>', _read_doc(self.mkdir))
        _print_cmd('MKDI', '<path>', _read_doc(self.mkdir))
        _print_cmd('RMD', '<path>', _read_doc(self.rmdir))
        _print_cmd('RMDI', '<path>', _read_doc(self.rmdir))
        _print_cmd('RMDA', '<path>', _read_doc(self.rmdir_all))

    def open(self) -> None:
        '''
        Open a connection to server.
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

    def ls(self, path: str = '.') -> None:
        '''
        List information of a file or directory.

        :param path: relative path to the file or directory,
                     using current path by default
        '''

        def _parse_stat(resp: str) -> Tuple[str, str, str, str, str, str]:
            '''
            Parse a line of server response to a human readable list for output.

            Return file name, file size, file type, last modified time,
            permissions and owner.

            :param resp: a line of response
            '''

            def _parse_size(st_size: int) -> str:
                '''
                Interpret st_size to a human readable size.

                Return file size with a proper unit prefix.

                :param st_size: file size
                '''

                size = float(st_size)
                for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
                    if abs(size) < 1024.0:
                        return f'{size:4.1f} {unit}'
                    size /= 1024.0
                return f'{size:.1f} YB'

            def _parse_type(st_mode: int) -> str:
                '''
                Interpret the result of st_mode to file type.

                Return file type.

                :param st_mode: file mode
                '''

                type_dict = {
                    stat.S_ISREG: 'File',
                    stat.S_ISDIR: 'Dir',
                    stat.S_ISLNK: 'Link',
                }
                for check in type_dict:
                    if check(st_mode):
                        return type_dict[check]
                return 'Unk'

            def _parse_perms(st_mode: int) -> str:
                '''
                Interpret the result of st_mode to permissions.

                Return a Unix-like permission string.

                :param st_mode: file mode
                '''

                perm_dict = {
                    stat.S_IRUSR: 'r', stat.S_IWUSR: 'w', stat.S_IXUSR: 'x',
                    stat.S_IRGRP: 'r', stat.S_IWGRP: 'w', stat.S_IXGRP: 'x',
                    stat.S_IROTH: 'r', stat.S_IWOTH: 'w', stat.S_IXOTH: 'x',
                }
                perms = 'd' if stat.S_ISDIR(st_mode) else '-'
                for perm in perm_dict:
                    perms += perm_dict[perm] if st_mode & perm else '-'
                return perms

            if not resp:
                return
            try:
                file_name, st_size, st_mode, st_mtime, st_uid = resp.split(' ')
                file_name = file_name.replace('%20', ' ')
                file_size = _parse_size(int(st_size))
                file_type = _parse_type(int(st_mode))
                mod_time = (
                    datetime.fromtimestamp(float(st_mtime))
                    .strftime('%Y-%m-%d %H:%M:%S')
                )
                perms = _parse_perms(int(st_mode))
                owner = st_uid
            except (ValueError, TypeError) as e:
                log('error', f'Invalid response: {resp}, error: {e}')
                return
            else:
                return file_name, file_size, file_type, mod_time, perms, owner

        def _print_info(info: Tuple[str, str, str, str, str, str]) -> None:
            '''
            Print information of a file or directory.

            :param info: (file_name, file_size, file_type, mod_time, perms, owner)
            '''

            try:
                file_name, file_size, file_type, mod_time, perms, owner = info
                print(
                    '{:20} | {:>10} | {:4} | {:19} | {:10} | {:3}'
                    .format(file_name, file_size, file_type, mod_time, perms, owner)
                )
            except ValueError as e:
                log('error', f'Invalid response: {info}, error: {e}')

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'LIST {path}\r\n'.encode('utf-8'))

        expected, _, resp_msg = self.check_resp(150)
        if not expected:
            log('warn', resp_msg)
            return
        self.open_data_conn()
        if not self.check_resp(225)[0]:
            self.close_data_conn()
            return

        try:
            raw_resp = b''
            while True:
                data = self.data_conn.recv(self.buffer_size)
                if not data:
                    break
                raw_resp += data
            try:
                resp_list: list[str] = (
                    raw_resp
                    .decode('utf-8')
                    .strip('\r\n')
                    .split('\r\n')
                )
            except (ValueError, TypeError) as e:
                log('error', f'Invalid response: {raw_resp}, error: {e}')
            else:
                log('info', 'Start of list.')
                for resp in resp_list:
                    info = _parse_stat(resp)
                    if info:
                        _print_info(info)
                log('info', 'End of list.')
        except socket.error:
            log('debug', 'Data connection closed.')
        finally:
            self.close_data_conn()

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

        expected, _, resp_msg = self.check_resp(150)
        if not expected:
            log('warn', resp_msg)
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
            log('warn', f'System error: {e}')
        except socket.error:
            log('debug', 'Data connection closed.')
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

        expected, _, resp_msg = self.check_resp(150)
        if not expected:
            log('info', resp_msg)
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
            log('warn', f'System error: {e}')
        except socket.error:
            log('debug', 'Data connection closed.')
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

        expected, _, resp_msg = self.check_resp(250)
        log('info' if expected else 'warn', resp_msg)

    def cwd(self, path: str = '') -> None:
        '''
        Change working directory.

        :param path: relative path to the destination,
                     empty string means root folder
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'CWD {path}\r\n'.encode('utf-8'))
        expected, _, resp_msg = self.check_resp(257)
        if not expected:
            log('warn', resp_msg)
        else:
            log('info', f'Changed to directory: {resp_msg}')

    def pwd(self) -> None:
        '''
        Print working directory.
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'PWD\r\n'.encode('utf-8'))
        expected, _, resp_msg = self.check_resp(257)
        if not expected:
            log('warn', resp_msg)
        else:
            print(resp_msg)

    def mkdir(self, path: str) -> None:
        '''
        Make a directory recursively.

        :param path: relative path to the directory
        '''

        if not self.ping():
            log('info', 'Please connect to server first.')
            return

        self.ctrl_conn.sendall(f'MKD {path}\r\n'.encode('utf-8'))
        expected, _, resp_msg = self.check_resp(257)
        if not expected:
            log('warn', resp_msg)
        else:
            log('info', f'Created directory: {resp_msg}')

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
        expected, _, resp_msg = self.check_resp(250)
        log('info' if expected else 'warn', resp_msg)

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

        method_dict = {
            'HELP': self.help,
            'OPEN': self.open,
            'QUIT': self.close,
            'EXIT': self.close,         # alias
            'LIST': self.ls,
            'LS': self.ls,              # alias
            'RETR': self.retrieve,
            'GET': self.retrieve,       # alias
            'STOR': self.store,
            'PUT': self.store,          # alias
            'DELE': self.delete,
            'DEL': self.delete,         # alias
            'RM': self.delete,          # alias
            'CWD': self.cwd,
            'CD': self.cwd,             # alias
            'PWD': self.pwd,
            'MKD': self.mkdir,
            'MKDI': self.mkdir,         # alias
            'RMD': self.rmdir,
            'RMDI': self.rmdir,         # alias
            'RMDA': self.rmdir_all,
        }

        try:
            cmd = raw_cmd.split(None, 1)
            cmd_len = len(cmd)
            op = cmd[0]
            method = method_dict.get(op[:4].upper())
            if method:
                if cmd_len == 1:
                    method()
                else:
                    method(cmd[1])
            else:
                log('info', f'Invalid operation: {raw_cmd}')
        except TypeError as e:
            log('info', f'Invalid operation: {raw_cmd}, error: {e}')

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
                log('debug', f'Connection timeout.')
                self.close_ctrl_conn()
            except socket.error:
                log('debug', f'Remote connection closed.')
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
