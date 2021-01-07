from waitress import serve
from naive_ftp.client_handler import client_handler

if __name__ == '__main__':
    serve(client_handler.app, host='127.0.0.1', port=5000)
