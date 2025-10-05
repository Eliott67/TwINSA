# Registration

# PROBLEME :  add_user ne prend pas l'email ni la confirmation du mot de passe

from users_db import UsersDatabase
users_db = UsersDatabase()

min=8

def is_strong_password(password):
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    length = len(password) >= min
    return has_upper and has_lower and has_digit and has_special and length

def registration():
    print("Create an account")
    username = input("Enter your username: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    confirm_password = input("Confirm your password: ")

    # Required fields check
    if not username or not email or not password or not confirm_password:
        print("All fields are required.")
        return # Exit the function if any field is empty
    
    # Password match 
    if password != confirm_password:
        print("Passwords do not match.")
        return 
    
    # Password strength check
    if not is_strong_password(password):
        print("Password must be at leas " + str(min) +" characters long and include uppercase, lowercase, digit, and special character.")
        return
    
    # Basic email format check
    if "@" not in email or "." not in email:
        print("Invalid email format.")
        return
    
    # No spaces in username and email
    if " " in username or " " in email:
        print("Username and email cannot contain spaces.")
        return
    
    # Unique username check
    if not users_db.unique_user(username):
        print("Username already exists. Please choose a different username.")
        return
    
    # Unique email check
    if not users_db.unique_user2(email):
        print("Email already exists. Please choose a different email.")
        return

    # If all checks pass, register the user
    users_db.add_user(username, password)
    print("Registration successful for " + str(username) + " !")

if __name__ == "__main__":
    registration()