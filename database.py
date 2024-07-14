# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()  # This line brings all environment variables from .env into os.environ

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    # Configure the SQLAlchemy part of the app instance
    #app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/iot_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the extension
    db.init_app(app)
    migrate.init_app(app, db)
