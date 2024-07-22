from werkzeug.security import generate_password_hash

def hash_password():
    # Prompt the user to enter a password
    password = input("Enter the password you want to hash: ")

    # Generate the password hash
    password_hash = generate_password_hash(password)

    # Print the generated hash
    print("\nGenerated Password Hash:")
    print(password_hash)

    # Wait for user input before closing
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    hash_password()