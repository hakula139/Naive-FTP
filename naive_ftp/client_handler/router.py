from naive_ftp.client.client import ftp_client
from flask import Blueprint, request

# STOR
# DELE
# RMDA

file_handler = Blueprint('file_handler', __name__)
dir_handler = Blueprint('dir_handler', __name__)

client = ftp_client(cli_mode=False)


@file_handler.route('/file', methods=['GET'])
def file():
    '''
    RETR <server_path>

        req: GET /api/retr?path=:server_path
        resp: { msg: str }
    '''

    if not client.open():
        return '', '503 Server down'

    if request.method == 'GET':
        src_path = request.args.get('path', type=str)
        if not src_path:
            return '', '400 Bad Request'
        dst_path = client.retrieve(src_path)
        if not dst_path:
            return '', '404 Failed to download'
        return {
            'msg': dst_path,
        }


@dir_handler.route('/dir', methods=['GET', 'POST', 'PUT'])
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
    '''

    if not client.open():
        return '', '503 Server down'

    # LIST
    if request.method == 'GET':
        path = request.args.get('path', default='', type=str)
        data = client.ls(path)
        if not data:
            return '', '404 Not found'
        return {
            'data': data,
        }

    # CWD
    if request.method == 'POST':
        data: dict = request.get_json()
        dst_path = data.get('path')
        if not dst_path:
            dst_path = '/'
        status = client.cwd(dst_path)
        if not status:
            return '', '404 Failed to change directory'
        return {
            'msg': dst_path,
        }

    # MKD
    if request.method == 'PUT':
        data: dict = request.get_json()
        dst_path = data.get('path')
        if not dst_path:
            dst_path = '/'
        status = client.mkdir(dst_path)
        if not status:
            return '', '403 Failed to create directory'
        return {
            'msg': dst_path,
        }
