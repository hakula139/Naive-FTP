import shutil
import socket
import os
from threading import Thread
from typing import Tuple, Type
from naive_ftp.utils import log, is_safe_path

# Control socket
listen_host: str = socket.gethostname()
listen_port: int = 2121


class ftp_server(Thread):
    '''
    Naive-FTP server instance
    '''

    def __init__(self, ctrl_conn: socket.socket, client_addr: Tuple[str, int]) -> None:
        '''
        Initialize server instance.
        '''

        super().__init__()

        # Properties
        self.buffer_size: int = 1024
        self.data_timeout_duration: float = 3.0
        self.max_allowed_conn: int = 5
        self.server_dir: str = os.path.realpath('server_files')

        # Current working directory
        self.cwd_path: str = '.'

        # Control connection
        self.ctrl_conn: socket.socket = ctrl_conn
        self.client_addr: Tuple[str, int] = client_addr

        # Data connection
        self.data_sock: socket.socket = None
        self.data_sock_name: Tuple[str, int] = None
        self.data_conn: socket.socket = None
        self.data_addr: Tuple[str, int] = None

    def send_status(self, status_code: int, *args) -> None:
        '''
        Send a response based on status code.

        :param status_code: status code
        :param *args: optional arguments
        '''

        def _parsed_addr(addr: Tuple[str, int]) -> str:
            '''
            Return a parsed host address for status code 227.

            Format: 'h1,h2,h3,h4,p1,p2'

            :param addr: the address for data connection
            '''

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
            227: '227 Entering Passive Mode {}.\r\n'.format(_parsed_addr(self.data_sock_name)),
            250: '250 Requested file action okay, completed.\r\n',
            257: '257 {}\r\n'.format(args[0] if len(args) else None),
            450: '450 Requested file action not taken.\r\n',
            501: '501 Syntax error in parameters or arguments.\r\n',
            550: '550 Requested action not taken. File unavailable.\r\n',
            553: '553 Requested action not taken. File name not allowed.\r\n',
        }

        status = status_dict.get(status_code)
        if status:
            self.ctrl_conn.sendall(status.encode('utf-8'))
        else:
            log('error', f'Invalid status code: {status_code}')

    def open_data_conn(self) -> None:
        '''
        Open data connection.
        '''

        if self.data_conn:
            self.close_data_conn()
        self.data_conn, self.data_addr = self.data_sock.accept()
        self.data_conn.settimeout(self.data_timeout_duration)
        log('info', f'Data connection opened: {self.data_addr}')
        self.send_status(225)

    def open_data_sock(self) -> None:
        '''
        Open data socket.
        '''

        if self.data_sock:
            self.close_data_sock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.data_timeout_duration)
        s.bind((listen_host, 0))
        s.listen(self.max_allowed_conn)
        self.data_sock = s
        self.data_sock_name = s.getsockname()
        log('info', f'Data server started, listening at {self.data_sock_name}')
        self.send_status(227)

    def close_data_conn(self) -> None:
        '''
        Close data connection.
        '''

        if self.data_conn:
            self.data_conn.close()
            self.data_conn = None

    def close_data_sock(self) -> None:
        '''
        Close data socket.
        '''

        self.close_data_conn()
        if self.data_sock:
            self.data_sock.close()
            self.data_sock = None

    def close_ctrl_conn(self) -> None:
        '''
        Close control connection.
        '''

        if self.ctrl_conn:
            self.ctrl_conn.close()
            self.ctrl_conn = None

    def close(self) -> None:
        '''
        Close all sockets.
        '''

        self.close_data_sock()
        self.close_ctrl_conn()

    def pong(self) -> None:
        '''
        Respond to client. Pong!
        '''

        self.send_status(220)

    def get_server_path(self, path: str) -> str:
        '''
        Parse the client request path to its real path on server.

        :param path: path extracted from client request
        '''

        if path.startswith('/'):
            server_path = os.path.join(self.server_dir, path[1:])
        else:
            cwd_path = '' if self.cwd_path == '/' else self.cwd_path
            server_path = os.path.join(self.server_dir, cwd_path, path)
        return os.path.realpath(server_path)

    def ls(self, path: str = '.') -> None:
        '''
        List information of a file or directory.

        :param path: server path to the file or directory
        '''

        def _parse_stat(raw_stat: os.stat_result) -> str:
            '''
            Parse the raw stat_result to a string for response.

            Return file size, file mode, last modified time, permissions and owner id.

            :param raw_stat: stat_result of a file or directory
            '''

            s = []
            s.append(raw_stat.st_size)   # file size
            s.append(raw_stat.st_mode)   # file mode
            s.append(raw_stat.st_mtime)  # last modified time
            s.append(raw_stat.st_uid)    # owner id
            return ' '.join([str(i) for i in s])

        def _send_info(file_name: str, info: str) -> None:
            '''
            Send file information to client.

            :param file_name: file name
            :param info: file information
            '''

            self.data_conn.sendall(f'{file_name} {info}\r\n'.encode('utf-8'))

        src_path = self.get_server_path(path)
        log('debug', f'Listing information of {src_path}')
        if not is_safe_path(src_path, self.server_dir, allow_base=True):
            self.send_status(553)
            return
        if not os.path.exists(src_path):
            self.send_status(550)
            return

        try:
            self.send_status(150)
            if not self.data_sock:
                self.open_data_sock()
            self.open_data_conn()
            if os.path.isdir(src_path):
                with os.scandir(src_path) as it:
                    for file in it:
                        if not file.name.startswith('.'):
                            file_name = file.name.replace(' ', '%20')
                            info = _parse_stat(file.stat())
                            _send_info(file_name, info)
            else:
                file_name = os.path.basename(src_path)
                if not file_name.startswith('.'):
                    file_name = file_name.replace(' ', '%20')
                    info = _parse_stat(os.stat(src_path))
                    _send_info(file_name, info)
            log('info', f'Finished listing information of {src_path}')
        except OSError as e:
            log('warn', f'System error: {e}')
            self.send_status(550)
        except socket.timeout:
            log('warn', f'Data connection timeout: {self.data_addr}')
            self.send_status(426)
        except socket.error:
            pass
        finally:
            self.close_data_sock()

    def retrieve(self, path: str) -> None:
        '''
        Retrieve a file from server.

        :param path: server path to the file
        '''

        src_path = self.get_server_path(path)
        log('debug', f'Sending file: {src_path}')
        if not is_safe_path(src_path, self.server_dir):
            self.send_status(553)
            return
        if not os.path.exists(src_path):
            self.send_status(550)
            return

        try:
            with open(src_path, 'rb') as src_file:
                self.send_status(150)
                if not self.data_sock:
                    self.open_data_sock()
                self.open_data_conn()
                while True:
                    data = src_file.read(self.buffer_size)
                    if not data:
                        break
                    self.data_conn.sendall(data)
            log('info', f'Sent file {src_path}')
        except OSError as e:
            log('warn', f'System error: {e}')
            self.send_status(550)
        except socket.timeout:
            log('warn', f'Data connection timeout: {self.data_addr}')
            self.send_status(426)
        except socket.error:
            pass
        finally:
            self.close_data_sock()

    def store(self, path: str) -> None:
        '''
        Store a file to server.

        :param path: local path to the file
        '''

        dst_path = self.get_server_path(os.path.basename(path))
        log('debug', f'Storing file: {dst_path}')
        if not is_safe_path(dst_path, self.server_dir):
            self.send_status(553)
            return
        dir_name, file_name = dst_path.rsplit(os.sep, 1)
        if not os.path.isdir(dir_name):
            if not self.mkdir(dir_name, is_client=False):  # failed to make directory
                return
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
            log('info', f'Stored file: {dst_path}')
        except OSError as e:
            log('warn', f'System error: {e}')
            self.send_status(550)
        except socket.timeout:
            log('warn', f'Data connection timeout: {self.data_addr}')
            self.send_status(426)
        except socket.error:
            pass
        finally:
            self.close_data_sock()

    def delete(self, path: str) -> None:
        '''
        Delete a file from server.

        :param path: server path to the file
        '''

        src_path = self.get_server_path(path)
        log('debug', f'Deleting file: {src_path}')
        if not is_safe_path(src_path, self.server_dir):
            self.send_status(553)
            return
        if not os.path.isfile(src_path):
            self.send_status(550)
            return

        try:
            os.remove(src_path)
            log('info', f'Deleted file: {src_path}')
            self.send_status(250)
        except OSError:
            log('warn', f'Failed to delete file: {src_path}')
            self.send_status(550)

    def cwd(self, path: str = '/') -> None:
        '''
        Change working directory.

        :param path: server path to the destination,
                     using root folder by default
        '''

        dst_path = self.get_server_path(path)
        log('debug', f'Changing working directory to {dst_path}')
        if not is_safe_path(dst_path, self.server_dir, allow_base=True):
            self.send_status(553)
            return

        if os.path.isdir(dst_path):
            self.cwd_path = dst_path[len(self.server_dir)+1:]
            if not self.cwd_path:
                self.cwd_path = '/'
            log('info', f'Changed working directory to {self.cwd_path}')
            self.send_status(257, self.cwd_path)
        else:
            self.send_status(550)

    def pwd(self) -> None:
        '''
        Print working directory.
        '''

        self.send_status(257, self.cwd_path)

    def mkdir(self, path: str, is_client: bool = True) -> bool:
        '''
        Make a directory recursively.

        Return True if succeeded.

        :param path: server path to the directory
        :param is_client: True for client, False for server internal use
        '''

        dst_path = self.get_server_path(path) if is_client else path
        log('debug', f'Creating directory: {dst_path}')
        if not is_safe_path(dst_path, self.server_dir):
            self.send_status(553)
            return False
        try:
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
            if os.path.isdir(dst_path):
                log('info', f'Created directory: {dst_path}')
                if is_client:
                    dir_path = dst_path.strip(self.server_dir)
                    self.send_status(257, dir_path)
                return True
            else:
                raise OSError
        except OSError:
            log('warn', f'Failed to make directory: {dst_path}')
            self.send_status(550)
            return False

    def rmdir(self, path: str, recursive: bool = False) -> None:
        '''
        Remove a directory.

        :param path: server path to the directory
        :param recursive: remove recursively if True
        '''

        src_path = self.get_server_path(path)
        log('debug', f'Removing directory: {src_path}')
        if not is_safe_path(src_path, self.server_dir):
            self.send_status(553)
            return
        try:
            if os.path.isdir(src_path):
                if recursive:
                    shutil.rmtree(src_path)
                else:
                    os.rmdir(src_path)
                log('info', f'Removed directory: {src_path}')
                self.send_status(250)
            else:
                raise OSError
        except OSError:
            log('warn', f'Failed to remove directory: {src_path}')
            self.send_status(550)

    def rmdir_all(self, path: str) -> None:
        '''
        Remove a directory recursively.

        :param path: server path to the directory
        '''

        self.rmdir(path, recursive=True)

    def router(self, raw_cmd: str) -> None:
        '''
        Route to the associated method based on client command.

        :param raw_cmd: raw client command
        '''

        method_dict = {
            'PING': self.pong,
            'LIST': self.ls,
            'RETR': self.retrieve,
            'STOR': self.store,
            'DELE': self.delete,
            'CWD': self.cwd,
            'PWD': self.pwd,
            'MKD': self.mkdir,
            'RMD': self.rmdir,
            'RMDA': self.rmdir_all,
        }

        try:
            log('debug', f'Operation: {raw_cmd}')
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
                log('warn', f'Invalid client operation: {raw_cmd}')
        except TypeError as e:
            log('warn', f'Invalid client operation: {raw_cmd}, error: {e}')
            self.send_status(501)

    def run(self) -> None:
        '''
        Main function for server.

        Receive a command from client and send it to router.
        '''

        try:
            self.send_status(220)
            while self.ctrl_conn:
                raw_cmd = (
                    self.ctrl_conn
                    .recv(self.buffer_size)
                    .decode('utf-8')
                    .strip('\r\n')
                )
                if not raw_cmd:  # connection closed
                    break
                self.router(raw_cmd)
        except (socket.timeout, socket.error):
            pass
        finally:
            self.close()


class server_listener(Thread):
    '''
    Naive-FTP server listener
    '''

    def __init__(self) -> None:
        '''
        Initialize server listener.
        '''

        super().__init__()

        # Properties
        self.ctrl_timeout_duration: float = 60.0
        self.max_allowed_conn: int = 5

        # Control connection
        self.ctrl_sock: socket.socket = None
        self.ctrl_sock_name: Tuple[str, int] = None
        self.ctrl_conn: socket.socket = None
        self.client_addr: Tuple[str, int] = None

    def open_ctrl_conn(self) -> None:
        '''
        Open control connection.
        '''

        self.ctrl_conn, self.client_addr = self.ctrl_sock.accept()
        self.ctrl_conn.settimeout(self.ctrl_timeout_duration)
        log('info', f'Accept connection: {self.client_addr}')

    def open_ctrl_sock(self) -> None:
        '''
        Open control socket.
        '''

        if self.ctrl_sock:
            self.close_ctrl_sock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((listen_host, listen_port))
        s.listen(self.max_allowed_conn)
        self.ctrl_sock = s
        self.ctrl_sock_name = s.getsockname()
        log('info', f'Server started, listening at {self.ctrl_sock_name}')

    def close_ctrl_sock(self) -> None:
        '''
        Close control socket.
        '''

        if self.ctrl_sock:
            self.ctrl_sock.close()
            self.ctrl_sock = None

    def close(self) -> None:
        '''
        Close all sockets.
        '''

        self.close_ctrl_sock()

    def run(self) -> None:
        '''
        Main function for server listener.
        '''

        self.open_ctrl_sock()
        server: Type[ftp_server] = None
        try:
            while self.ctrl_sock:
                self.open_ctrl_conn()
                server = ftp_server(self.ctrl_conn, self.client_addr)
                server.start()
        except (socket.timeout, socket.error):
            if server:
                server.close()
            self.close()


def main() -> None:
    print('Welcome to Naive-FTP server! Press q to exit.')

    listener = server_listener()
    listener.start()

    try:
        while True:
            if input().lower() == 'q':
                print('Bye!')
                break
    except KeyboardInterrupt:
        print('\nInterrupted.')
    finally:
        listener.close()
        log('info', 'Server stopped.')


if __name__ == '__main__':
    main()
