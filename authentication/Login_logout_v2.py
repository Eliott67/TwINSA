# login_logout.py

import users_db  # ce module sera remplacé par FakeUsersDB pendant les tests

def login(identifier=None, password=None):
    print("=== Log in ===")
    
    # Si aucun argument n'est donné, on demande à l'utilisateur
    if identifier is None:
        identifier = input("Enter your username or email: ")
    if password is None:
        password = input("Enter your password: ")

    # Vérification des champs
    if not identifier or not password:
        print("All fields are required.")
        return None

    # Vérifie si l'utilisateur existe
    user = users_db.find_user(identifier)
    if not user:
        print("User not found. Please check your username/email.")
        return None

    # Vérifie le mot de passe
    if user["password"] != password:
        print("Wrong password.")
        return None

    print(f"Login successful. Welcome back, {user['username']}!")
    return user  # retourne l'utilisateur connecté


def logout(current_user):
    if not current_user:
        print("You are not logged in.")
        return None

    print(f"User {current_user['username']} has been logged out.")
    return None
