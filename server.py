import os

import flask
import dash
from dotenv import load_dotenv

load_dotenv()

server = flask.Flask(__name__, static_url_path='/public', static_folder='./public')
server.secret_key = os.environ['SECRET_KEY']

app = dash.Dash(__name__, server=server, url_base_pathname='/')
app.title = 'GMOD Dashboard'
