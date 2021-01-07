from naive_ftp.client.client import ftp_client
from flask import Blueprint, request

file_handler = Blueprint('file_handler', __name__)
dir_handler = Blueprint('dir_handler', __name__)

client = ftp_client(cli_mode=False)


@file_handler.route('/file', methods=['GET', 'PUT', 'DELETE'])
def file():
    '''
    RETR <server_path>

        req: GET /api/file?path=:server_path
        resp: { msg: str }

    STOR <local_path>

        req: PUT /api/file
        req_body: { path: str }
        resp: { msg: str }

    DELE <server_path>

        req: DELETE /api/file
        req_body: { data: { path: str } }
        resp: { msg: str }
    '''

    if not client.open():
        return '', '503 Server down'

    # RETR
    if request.method == 'GET':
        src_path: str = request.args.get('path', type=str)
        if not src_path:
            return '', '400 Bad Request'
        dst_path: str = client.retrieve(src_path)
        if not dst_path:
            return '', '404 Failed to download'
        return {
            'msg': dst_path,
        }

    # STOR
    if request.method == 'PUT':
        data: dict = request.get_json()
        path: str = data.get('path')
        if not path:
            return '', '400 Bad Request'
        status: bool = client.store(path)
        if not status:
            return '', '404 Failed to upload'
        return {
            'msg': path,
        }

    # DELE
    if request.method == 'DELETE':
        data: dict = request.get_json()
        payload: dict = data.get('data')
        if not payload:
            return '', '400 Bad Request'
        path: str = payload.get('path')
        if not path:
            return '', '400 Bad Request'
        status: bool = client.delete(path)
        if not status:
            return '', '404 Failed to delete'
        return {
            'msg': path,
        }


@dir_handler.route('/dir', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dir():
    '''
    LIST <server_path>

        req: GET /api/dir?path=:server_path
        resp: { data: list[dict] }

    CWD <server_path>

        req: POST /api/dir
        req_body: { path: str }
        resp: { msg: str }

    MKD <server_path>

        req: PUT /api/dir
        req_body: { path: str }
        resp: { msg: str }

    RMDA <server_path>

        req: DELETE /api/dir
        req_body: { data: { path: str } }
        resp: { msg: str }
    '''

    if not client.open():
        return '', '503 Server down'

    # LIST
    if request.method == 'GET':
        path: str = request.args.get('path', default='', type=str)
        data: list[dict] = client.ls(path)
        if data == None:
            return '', '404 Not found'
        return {
            'data': data,
        }

    # CWD
    if request.method == 'POST':
        data: dict = request.get_json()
        path: str = data.get('path')
        if not path:
            path = '/'
        status: bool = client.cwd(path)
        if not status:
            return '', '404 Failed to change directory'
        return {
            'msg': path,
        }

    # MKD
    if request.method == 'PUT':
        data: dict = request.get_json()
        path: str = data.get('path')
        if not path:
            return '', '400 Bad Request'
        status: bool = client.mkdir(path)
        if not status:
            return '', '403 Failed to create directory'
        return {
            'msg': path,
        }

    # RMDA
    if request.method == 'DELETE':
        data: dict = request.get_json()
        payload = data.get('data')
        if not payload:
            return '', '400 Bad Request'
        path = payload.get('path')
        if not path:
            return '', '400 Bad Request'
        status = client.rmdir_all(path)
        if not status:
            return '', '403 Failed to remove directory'
        return {
            'msg': path,
        }
