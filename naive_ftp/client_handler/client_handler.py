'''
Naive-FTP client handler, a middleware between frontend and backend.

Pass requests from frontend to backend in string format,
and send responses back to frontend in JSON format.
'''

from flask import Flask
from flask_cors import CORS
from naive_ftp.client_handler.router import list_handler

app = Flask(__name__)
CORS(app)

app.register_blueprint(list_handler, url_prefix='/api')
