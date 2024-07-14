# app.py
import os
from flask import Flask, Blueprint, render_template
from flask_restx import Api
from database import init_db

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as lilygos3_ns
from esp32_temi1500_endponits.routes import api as temi1500_ns

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Initialize the database and migrations
init_db(app)

# Blueprint for API
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, 
          version='1.0', 
          title='Backend Management',
          description='A Flask-RESTx API for IoT devices management',
          doc='/doc')  # Serve Swagger UI at /doc endpoint

# Add namespaces for different endpoints
api.add_namespace(lilygos3_ns, path='/v1/temphumi')
api.add_namespace(temi1500_ns, path='/v1/temi1500')

# Register blueprint with the app
app.register_blueprint(blueprint)

# Route for the home page
@app.route('/')
def index():
    return '<h1>Welcome to the Backend Management API</h1>'

# Route for custom Swagger UI
@app.route('/api/doc')
def custom_swagger_ui():
    return render_template('swagger-ui.html')

if __name__ == '__main__':
    app.run(debug=True)
