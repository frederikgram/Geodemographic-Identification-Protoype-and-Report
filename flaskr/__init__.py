import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    return app

app = create_app()

from .views import *

from .models import *

load_json_data()