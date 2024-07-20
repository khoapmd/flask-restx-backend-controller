# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import redis

db = SQLAlchemy()
migrate = Migrate()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0),
    decode_responses=True
)

def init_db(app):
    # Configure the SQLAlchemy part of the app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://iot_backend:3Jp8VJyia7ECaj@postgres:5432/iot_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the extension
    db.init_app(app)
    migrate.init_app(app, db)
