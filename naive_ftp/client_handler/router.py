from naive_ftp.client.client import ftp_client
from flask import Blueprint, request

# STOR
# DELE
# MKD
# RMD
# RMDA

list_handler = Blueprint('list_handler', __name__)
retr_handler = Blueprint('retr_handler', __name__)
dir_handler = Blueprint('dir_handler', __name__)

client = ftp_client(cli_mode=False)


@list_handler.route('/list', methods=['GET'])
def list():
    '''
    LIST <server_path>

    req: GET /api/list?path=:server_path
    resp: { data: list[dict] }
    '''

    if not client.open():
        return '', '503 Server down'
    path = request.args.get('path', default='', type=str)
    data = client.ls(path)
    if not data:
        return '', '404 Not found'
    return {
        'data': data,
    }


@retr_handler.route('/retr', methods=['GET'])
def retr():
    '''
    RETR <server_path>

    req: GET /api/retr?path=:server_path
    resp: { msg: str }
    '''

    if not client.open():
        return '', '503 Server down'
    src_path = request.args.get('path', type=str)
    if not src_path:
        return '', '400 Bad Request'
    dst_path = client.retrieve(src_path)
    if not dst_path:
        return '', '404 Failed to download'
    return {
        'msg': dst_path,
    }


@dir_handler.route('/dir', methods=['GET', 'POST'])
def dir():
    '''
    CWD <server_path>

    req: POST /api/dir
    req_body: { path: str }
    resp: { msg: str }

    PWD

    req: GET /api/dir
    resp: { msg: str }
    '''

    if not client.open():
        return '', '503 Server down'
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

    if request.method == 'GET':
        path = client.pwd()
        if not path:
            return '', '500 Internal Server Error'
        return {
            'msg': path,
        }
