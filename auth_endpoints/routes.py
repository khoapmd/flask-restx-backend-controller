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
sign_in_model = api.model('SignIn', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')
})

def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, SESSION_KEY, algorithm='HS256')

@api.route('/sign-in')
class SignIn(Resource):
    @api.expect(sign_in_model)
    def post(self):
        try:
            # Get data from request body as JSON
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {'success': False, 'message': 'Email and password are required'}, 400

            # Retrieve user from database
            user = User.query.filter_by(email=email).first()
            if not user:
                return {'success': False, 'message': 'Invalid email or password'}, 401

            # Check if password matches hashed password in the database
            if not user.check_password(password):
                return {'success': False, 'message': 'Invalid email or password'}, 401

            # Generate token
            token = generate_token(user)
            
            return {
                'success': True,
                'accessToken': token
            }, 200

        except Exception as e:
            print(f"Login error: {str(e)}")  # For debugging
            return {'success': False, 'message': 'Server error'}, 500

@api.route('/sign-out')
class SignOut(Resource):
    def post(self):
        # Clear all session data
        session.clear()
        
        # Return success response
        return {
            'success': True,
            'message': 'Successfully logged out'
        }, 200

@api.route('/me')
class CurrentUser(Resource):
    def get(self):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'No token provided'}, 401
            
            # Extract token from Bearer header
            token = auth_header.split(' ')[1]
            
            # Decode token
            try:
                payload = jwt.decode(token, SESSION_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return {'success': False, 'message': 'Token expired'}, 401
            except jwt.InvalidTokenError:
                return {'success': False, 'message': 'Invalid token'}, 401

            # Get user from database
            user = User.query.filter_by(id=payload['user_id']).first()
            if not user:
                return {'success': False, 'message': 'User not found'}, 404

            # Return user info
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role
                }
            }, 200

        except Exception as e:
            print(f"Get current user error: {str(e)}")  # For debugging
            return {'success': False, 'message': 'Server error'}, 500
