from dotenv import load_dotenv
import os

load_dotenv()
VALID_KEY = os.environ['VALID_KEY']
def checkKEY(key):
    if key != VALID_KEY:
            return {'message': 'Invalid API Key'}, 403