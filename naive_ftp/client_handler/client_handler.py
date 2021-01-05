import socket
from naive_ftp.client.client import ftp_client
from flask import Flask

server_host: str = socket.gethostname()
server_port: int = 2121

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'
