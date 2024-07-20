import os

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/iot_db'
os.environ['VALID_KEY'] = 'XXV7lnIse9q4YGA11pXA'
os.environ['LILYGOS3_FIRMWARE_DIR'] = 'C:\\firmware\\lilygos3'
os.environ['TEMI1500_FIRMWARE_DIR'] = 'C:\\firmware\\temi1500'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_DB'] = '0'

