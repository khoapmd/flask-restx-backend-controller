from werkzeug.security import generate_password_hash

password = 'password123'  # Replace with the actual password you want to hash

# Generate the password hash
password_hash = generate_password_hash(password)

print(password_hash)