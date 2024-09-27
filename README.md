# Flask-RESTX Backend

![img.png](https://github.com/khoapmd/flask-restx-backend-controller/blob/main/imgs/backend.png?raw=true)

## Overview

This Flask-RESTX backend serves as the central management system for the Temperature28LilyGo IoT project. It handles device registration, configuration management, and OTA updates for connected IoT devices.

## Features

- RESTful API using Flask-RESTX
- Database management with Flask-Migrate
- Authentication system for secure access
- Docker support for easy deployment
- Development and production environment configurations

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.7+ (for local development)
- pip (Python package manager)

## Setup and Installation

### Docker Environment (Recommended)

1. **Build and Run the Application**

   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Initialize the Database**

   ```bash
   docker exec -it flask-restx flask db init
   docker exec -it flask-restx flask db migrate -m "Initial migration"
   docker exec -it flask-restx flask db upgrade
   ```

3. **Create Authentication User**

   ```bash
   docker exec -it flask-restx python auth_endpoints/password_hash.py
   ```

   Follow the prompts to create a username and password. The script will generate a password hash.

4. **Add User to Database**

   Manually add the username and password hash to the User table in the database.

### Development Environment

1. **Set Up Virtual Environment** (Recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database**

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Create Authentication User**

   ```bash
   python auth_endpoints/password_hash.py
   ```

   Follow the prompts to create a username and password. The script will generate a password hash.

5. **Add User to Database**

   Manually add the username and password hash to the User table in the database.

6. **Run the Application**

   ```bash
   flask run
   ```

## Database Management

### Updating the Database

When you make changes to your models, update the database using these commands:

**Docker Environment:**
```bash
docker exec -it flask-restx flask db migrate -m "Update migration"
docker exec -it flask-restx flask db upgrade
```

**Development Environment:**
```bash
flask db migrate -m "Update migration"
flask db upgrade
```

## API Documentation

Once the application is running, you can access the Swagger UI documentation at:

`http://localhost:5000/api/docs`

This provides an interactive interface to explore and test the API endpoints.

## Security

- Ensure to use strong passwords for authentication users.
- The `password_hash.py` script uses secure hashing methods. Never store plain-text passwords.
- In production, always use HTTPS to encrypt data in transit.

## Troubleshooting

- If you encounter database connection issues in the Docker environment, ensure the database service is fully up before running Flask commands.
- For permission issues, make sure your user has the necessary rights to execute Docker commands.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
