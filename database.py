# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
from config import DATABASE_URI, REDIS_HOST, REDIS_PORT, REDIS_DB

db = SQLAlchemy()
migrate = Migrate()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def init_db(app):
    # Configure the SQLAlchemy part of the app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://iot_backend:3Jp8VJyia7ECaj@postgres:5432/iot_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the extension
    db.init_app(app)
    migrate.init_app(app, db)
