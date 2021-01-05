from naive_ftp.client.client import ftp_client
from flask import Blueprint, request

# RETR
# STOR
# DELE
# CWD
# PWD
# MKD
# RMD
# RMDA

list_handler = Blueprint('list_handler', __name__)

client = ftp_client(cli_mode=False)


@list_handler.route('/list', methods=['GET'])
def get_list():
    if not client.open():
        return 'Server down', 503
    path = request.args.get('path', default='', type=str)
    data = client.ls(path)
    if not data:
        return 'Not found', 404
    return {
        'status_code': 200,
        'msg': 'Success',
        'data': data,
    }
