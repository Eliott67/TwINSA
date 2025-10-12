# login_logout.py

import users_db  # ce module sera remplacé par FakeUsersDB pendant les tests

# Liste des utilisateurs connectés
connected_users = []

def login(identifier=None, password=None):
    print("=== Log in ===")
    
    if identifier is None:
        identifier = input("Enter your username or email: ")
    if password is None:
        password = input("Enter your password: ")

    if not identifier or not password:
        print("All fields are required.")
        return None

    user = users_db.find_user(identifier)
    if not user:
        print("User not found. Please check your username/email.")
        return None

    if user["password"] != password:
        print("Wrong password.")
        return None

    print(f"Login successful. Welcome back, {user['username']}!")

    # Ajouter à la liste des connectés si pas déjà dedans
    if user not in connected_users:
        connected_users.append(user)

    return user

def logout(current_user):
    if not current_user:
        print("You are not logged in.")
        return None

    print(f"User {current_user['username']} has been logged out.")

    # Retirer de la liste des connectés
    if current_user in connected_users:
        connected_users.remove(current_user)

    return None

def get_connected_users():
    return connected_users
