# app.py
import os
import jwt
from flask import Flask, Blueprint, render_template, request, session, flash, redirect, url_for, send_from_directory
from flask_restx import Api
from flask_cors import CORS
from database import init_db
from config import VALID_KEY, SESSION_KEY

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as lilygos3_ns
from esp32_temi1500_endponits.routes import api as temi1500_ns
from firmware_control_endpoints.routes import api as firmware_ns
from redis_endpoints.routes import api as redis_ns
from auth_endpoints.routes import auth_bp  # Import the Blueprint for authentication

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = SESSION_KEY
CORS(app)  # Enable CORS for all origins

# Initialize the database and migrations
init_db(app)

# Blueprint for API
blueprint = Blueprint('api', __name__, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register auth blueprint
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Secret-Key'
    }
}
api = Api(blueprint, 
          authorizations=authorizations,
          version='1.1', 
          title='Backend Management',
          description='A Flask-RESTx API for IoT devices management',
          doc='/doc')  # Serve Swagger UI at /docs endpoint

# Add namespaces for different endpoints
api.add_namespace(lilygos3_ns, path='/v1/temphumi')
api.add_namespace(temi1500_ns, path='/v1/temi1500')
api.add_namespace(firmware_ns, path='/v1/firmware')
api.add_namespace(redis_ns, path='/v1/redis')

# Register blueprint with the app
app.register_blueprint(blueprint)

@app.before_request
def validate_secret_key():
    whitelisted_endpoints = ['api.specs', 'home', 'static', 'docs', 'auth.login', 'auth.logout', 'favicon']
    whitelisted_paths = ['/login', '/logout']
    #print(request.endpoint)
    if request.endpoint in whitelisted_endpoints or request.path in whitelisted_paths:
        return
    
    api_key = request.headers.get('X-Secret-Key')
    if api_key:
        if api_key != VALID_KEY:
            return {'message': 'Unauthorized. Invalid API key.'}, 401
        return  # API key is valid, allow the request
    
    # If no API key, check for JWT token
    auth_token = request.headers.get('Authorization') or session.get('auth_token')
    
    if not auth_token:
        return {'message': 'Unauthorized. No token provided.'}, 401
    
    try:
        # Remove 'Bearer ' prefix if present
        if auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]
        
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload['role'] != 'admin' or payload['role'] != 'dev':
            return {'message': 'Unauthorized. Admin or Dev access required.'}, 403
    except jwt.ExpiredSignatureError:
        return {'message': 'Token expired. Please log in again.'}, 401
    except jwt.InvalidTokenError:
        return {'message': 'Invalid token. Please log in again.'}, 401

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

# Route for the home page
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')

# Route for custom Swagger UI
@app.route('/api/docs')
def docs():
    print(session.get('logged_in'))
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return render_template('swagger-ui.html')

if __name__ == '__main__':
    app.run(debug=True)
    # pass
