import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FRONTEND_URL = os.getenv('FRONTEND_URL')
VALID_KEY = os.getenv('VALID_KEY')
DATABASE_URI = os.getenv('DATABASE_URI')
REDIS_HOST=os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT=os.getenv('REDIS_PORT', 6379)
REDIS_DB=os.getenv('REDIS_DB', 0)
REDIS_EX=os.getenv('REDIS_EX', 3600)
FIRMWARE_DIR = os.getenv('FIRMWARE_DIR')
SESSION_KEY = os.getenv('SESSION_KEY')