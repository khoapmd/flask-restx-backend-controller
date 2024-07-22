# auth_routes.py
import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from .models import User # Assuming you have a User model defined
from config import SESSION_KEY

auth_bp = Blueprint('auth', __name__)

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, SESSION_KEY, algorithm='HS256')

@auth_bp.route('/login', methods=['POST'])
def login():
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
            session['auth_token'] = generate_token(user)
            return {'success': True}
    return {'success': False}

@auth_bp.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))
