import os
from backend.users_db import UsersDatabase
from backend.user import User
import bcrypt

users_db = UsersDatabase("backend/users_database.json")

def update_personal_info(user: User, name=None, age=None, country=None):
    """Met à jour les informations personnelles de l'utilisateur."""
    if name is not None:
        user.name = name
    if age is not None:
        try:
            user.age = int(age)
        except ValueError:
            pass
    if country is not None:
        user.country = country

    users_db.save_users()
    return True


def update_profile_picture(user: User, picture_path):
    """Change la photo de profil (chemin vers un fichier uploadé)."""
    if not os.path.exists(picture_path):
        return False
    user.profile_picture = picture_path
    users_db.save_users()
    return True


def delete_account(user: User, password):
    """Supprime le compte si le mot de passe est correct."""
    stored_hash = user.password.encode()  # hash stocké dans l'objet user
    if bcrypt.checkpw(password.encode(), stored_hash):
        users_db.remove_user(user.username)
        users_db.save_users()
        return True
    return False
