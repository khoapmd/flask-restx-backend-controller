# models.py

from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'user': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
        }
