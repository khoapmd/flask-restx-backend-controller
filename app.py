# app.py
import os
from flask import Flask, Blueprint, render_template, request
from flask_restx import Api
from flask_cors import CORS
from database import init_db
from config import VALID_KEY

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as lilygos3_ns
from esp32_temi1500_endponits.routes import api as temi1500_ns
from firmware_control_endpoints.routes import api as firmware_ns
from redis_endpoints.routes import api as redis_ns

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all origins

# Initialize the database and migrations
init_db(app)

# Blueprint for API
blueprint = Blueprint('api', __name__, url_prefix='/api')
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
          doc='/docs')  # Serve Swagger UI at /doc endpoint

# Add namespaces for different endpoints
api.add_namespace(lilygos3_ns, path='/v1/temphumi')
api.add_namespace(temi1500_ns, path='/v1/temi1500')
api.add_namespace(firmware_ns, path='/v1/firmware')
api.add_namespace(redis_ns, path='/v1/redis')

# Register blueprint with the app
app.register_blueprint(blueprint)

@app.before_request
def validate_secret_key():
    if request.endpoint == 'api.doc' or request.endpoint == 'api.specs' :
        return
    
    if 'X-Secret-Key' not in request.headers or request.headers['X-Secret-Key'] != VALID_KEY:
        return {'message': 'Unauthorized. Invalid secret key.'}, 401

# Route for the home page
@app.route('/')
def index():
    return '<h1>Welcome to the Backend Management API</h1>'

# Route for custom Swagger UI
@app.route('/api/docs')
def custom_swagger_ui():
    return render_template('swagger-ui.html')

if __name__ == '__main__':
    app.run(debug=True)
    # pass
