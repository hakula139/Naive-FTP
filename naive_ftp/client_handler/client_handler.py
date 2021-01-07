'''
Naive-FTP client handler, a middleware between frontend and backend.

Pass requests from frontend to backend in string format,
and send responses back to frontend in JSON format.
'''

from flask import Flask
from flask_cors import CORS
from naive_ftp.client_handler.router import file_handler, dir_handler

app = Flask(__name__)
CORS(app)

app.register_blueprint(file_handler, url_prefix='/api')
app.register_blueprint(dir_handler, url_prefix='/api')
