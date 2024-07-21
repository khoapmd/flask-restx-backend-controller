# app.py
import os
from flask import Flask, Blueprint, render_template, request, session, flash, redirect, url_for
from flask_restx import Api
from flask_cors import CORS
from database import init_db
from config import VALID_KEY

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as lilygos3_ns
from esp32_temi1500_endponits.routes import api as temi1500_ns
from firmware_control_endpoints.routes import api as firmware_ns
from redis_endpoints.routes import api as redis_ns
from auth_endpoints.routes import auth_bp  # Import the Blueprint for authentication

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
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
    whitelisted_endpoints = ['api.specs', 'home', 'static', 'docs', 'auth.login', 'auth.logout']
    whitelisted_paths = ['/login', '/logout']
    # print(request.endpoint)
    if request.endpoint in whitelisted_endpoints or request.path in whitelisted_paths:
        return
    if 'X-Secret-Key' not in request.headers or request.headers['X-Secret-Key'] != VALID_KEY:
        return {'message': 'Unauthorized. Invalid secret key.'}, 401

# Route for the home page
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Hello Boss!  <a href="auth/logout">Logout</a>'
    
# Route for custom Swagger UI
@app.route('/api/docs')
def docs():
    print(session.get('logged_in'))
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return render_template('swagger-ui.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
    # pass
