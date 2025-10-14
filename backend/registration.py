# Registration

from users_db import UsersDatabase
from user import User 
users_db = UsersDatabase()

MIN_PASSWORD_LENGTH = 8

def is_strong_password(password):
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    length = len(password) >= MIN_PASSWORD_LENGTH
    return has_upper and has_lower and has_digit and has_special and length


def validate_registration(user : User, confirm_password : str):

    # Required fields check
    if not user.username or not user.email or not user.get_password() or not confirm_password:
        return False, "All fields are required."
    
    # Password match 
    if user.get_password() != confirm_password:
        return False, "Passwords do not match."
    
    # Password strength check
    if not is_strong_password(user.get_password()):
        return False, "Password must be at least " + str(MIN_PASSWORD_LENGTH) + " characters long and include uppercase, lowercase, digit, and special character."
    
    # Basic email format check
    if "@" not in user.email or "." not in user.email:
        return False, "Invalid email format."
    
    # No spaces in username and email
    if " " in user.username or " " in user.email:
        return False, "Username and email cannot contain spaces."
    
    # Unique username check
    if not users_db.unique_user(user.username):    
        return False, "Username already exists. Please choose a different username."
    
    # Unique email check
    for existing_user in users_db.users_list:
        if existing_user.email == user.email:
            return False, "Email already exists. Please choose a different email."
        
    # All checks passed
    return True, "Registration successful."

def registration():
    print("Create an account")
    username = input("Enter your username: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    confirm_password = input("Confirm your password: ")
    name = input("Enter your name: ") or "Unknown"
    age = input("Enter your age: ")
    if not age.isdigit():
        print(" Invalid age, defaulting to 0")
        age = 0
    else:
        age = int(age)
    country = input("Enter your country: ") or "Unknown"

    # If all checks pass, register the user
    new_user = User(username, email, password, name, age, country)
    valid, msg = validate_registration(new_user, confirm_password)
    print(msg)
    if valid:
        users_db.add_user(new_user)
        print("User registered successfully.")


if __name__ == "__main__":
    registration()

    