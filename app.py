# app.py
import os
import jwt
from flask import Flask, Blueprint, render_template, request, send_from_directory
from flask_restx import Api
from flask_cors import CORS
from database import init_db
from config import VALID_KEY, SESSION_KEY

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as lilygos3_ns
from esp32_chamber_endponits.routes import api as chamber_ns
from firmware_control_endpoints.routes import api as firmware_ns
from redis_endpoints.routes import api as redis_ns
from auth_endpoints.routes import api as auth_ns

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = SESSION_KEY

# Update CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3031"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type", 
            "Authorization", 
            "Accept", 
            "X-Secret-Key",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods"
        ],
        "expose_headers": ["Authorization"],
        "supports_credentials": True,
        "max_age": 3600,
        # "allow_origin": "*"  # Be careful with this in production
    }
})

# Initialize the database and migrations
init_db(app)

# Blueprint for API
blueprint = Blueprint('api', __name__, url_prefix='/api')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Secret-Key'
    },
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(blueprint, 
          authorizations=authorizations,
          version='1.1', 
          title='Backend Management',
          description='A Flask-RESTx API for IoT devices management',
          doc='/doc')

# Add namespaces for different endpoints
api.add_namespace(lilygos3_ns, path='/v1/temphumi')
api.add_namespace(chamber_ns, path='/v1/chamber')
api.add_namespace(firmware_ns, path='/v1/firmware')
api.add_namespace(redis_ns, path='/v1/redis')
api.add_namespace(auth_ns, path='/auth')
# Register blueprint with the app
app.register_blueprint(blueprint)

# Add OPTIONS request handling
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return {"success": True}, 200, {
            'Access-Control-Allow-Origin': 'http://localhost:3031',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Secret-Key',
            'Access-Control-Max-Age': '3600'
        }

@app.before_request
def validate_request():
    # Skip validation for OPTIONS requests
    if request.method == "OPTIONS":
        return
        
    print(f"Path: {request.path}")
    # print(f"Endpoint: {request.endpoint}")
    # print(f"Method: {request.method}")
    # print(f"Headers: {request.headers}")

    # Whitelist paths that don't need authentication
    whitelisted_endpoints = ['api.specs', 'home', 'static', 'docs', 'auth.sign_in', 'auth.sign_out', 'auth.me']
    whitelisted_paths = ['/login', '/api/auth/sign-in', '/api/auth/sign-out', '/api/auth/me']
    
    if request.endpoint in whitelisted_endpoints or request.path in whitelisted_paths:
        print("Path is whitelisted")
        return

    # Check for API key first
    api_key = request.headers.get('X-Secret-Key')
    if api_key:
        if api_key != VALID_KEY:
            return {'message': 'Unauthorized. Invalid API key.'}, 401
        return  # API key is valid, allow the request
    
    # If no API key, check for Bearer token
    auth_header = request.headers.get('Authorization')
    print(f"Auth header: {auth_header}")
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'message': 'Unauthorized. No token provided.'}, 401
    
    try:
        token = auth_header.split(' ')[1]
        print(f"Token: {token[:20]}...")  # Print first 20 chars for debugging
        payload = jwt.decode(token, SESSION_KEY, algorithms=['HS256'])
        print(f"Decoded payload: {payload}")
        
        if payload['role'] == 'admin' or payload['role'] == 'dev':
            print("Valid admin/dev token")
            return
        else:
            return {'message': 'Unauthorized. Admin or Dev access required.'}, 403
    except jwt.ExpiredSignatureError:
        return {'message': 'Token expired. Please log in again.'}, 401
    except jwt.InvalidTokenError as e:
        print(f"Token validation error: {str(e)}")
        return {'message': 'Invalid token. Please log in again.'}, 401

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/docs')
def docs():
    return render_template('swagger-ui.html')

if __name__ == '__main__':
    app.run(debug=True)
