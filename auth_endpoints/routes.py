# auth_routes.py

from flask import Blueprint, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from .models import User # Assuming you have a User model defined

auth_bp = Blueprint('auth', __name__)

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
            return {'success': True}
    return {'success': False}

@auth_bp.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))
