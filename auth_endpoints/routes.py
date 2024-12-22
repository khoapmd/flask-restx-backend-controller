# auth_routes.py
import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, session, redirect, url_for, jsonify
from flask_restx import Api, Resource, fields
from . import api
from werkzeug.security import check_password_hash
from .models import User # Assuming you have a User model defined
from config import SESSION_KEY

# Define models for swagger documentation
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, SESSION_KEY, algorithm='HS256')

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Retrieve user from database
        user = User.query.filter_by(username=username).first()
        if user:
            # Check if password matches hashed password in the database
            stored_password_hash = user.password_hash
            if check_password_hash(stored_password_hash, password):
                session['logged_in'] = True
                session['user_role'] = user.role 
                token = generate_token(user)
                session['auth_token'] = token
                return {
                    'success': True,
                    'token': token
                }
        return {'success': False}

@api.route('/logout')
class Logout(Resource):
    def post(self):
        # Clear all session data
        session.clear()
        
        # Return success response
        return {
            'success': True,
            'message': 'Successfully logged out'
        }, 200
