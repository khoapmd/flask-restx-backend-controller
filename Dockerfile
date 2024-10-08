# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    python3-dev
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run Gunicorn to serve the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--worker-class", "gevent", "app:app"]
