# app.py
import os
from flask import Flask, Blueprint, render_template
from flask_restx import Api
from database import init_db, db

# Import namespaces and models
from esp32_temphumi_endpoints.routes import api as esp32_ns
from esp32_temi1500_endponits.routes import api as esp32_cs
from esp32_temphumi_endpoints.models import LILYGOS3DATA, SENSORTEMPHUMIDATA
from esp32_temi1500_endponits.models import ESPTEMI1500Data

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Initialize the database and migrations
init_db(app)

# Create or upgrade database schema
with app.app_context():
    try:
        db.create_all()
        print("Tables created successfully")

        # Print out the tables that exist in the database for verification
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print("Existing tables:")
        for table_name in inspector.get_table_names():
            print(table_name)

    except Exception as e:
        print(f"An error occurred while creating tables: {e}")

# Blueprint for API
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, 
          version='1.0', 
          title='Backend Management', 
          description='A Flask-RESTx API for IoT devices management',
          doc='/doc')  # Serve Swagger UI at /doc endpoint

# Add namespaces for different endpoints
api.add_namespace(esp32_ns, path='/esp32/temphumi')
api.add_namespace(esp32_cs, path='/esp32/temi1500')

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
