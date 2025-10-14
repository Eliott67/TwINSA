import os
from users_db import UsersDatabase
from user import User

users_db = UsersDatabase()

def view_profile(user: User):
    """Affiche toutes les informations du profil de l'utilisateur."""
    print("=== My Profile ===")
    print(f"Username: {user.username}")
    print(f"Name: {user.name}")
    print(f"Age: {user.age}")
    print(f"Country: {user.country}")
    print(f"Followers: {user.get_nb_followers()}")
    print(f"Following: {user.get_nb_following()}")
    print(f"Posts: {len(user.posts)}")
    print(f"Likes received: {user.likes}")

    if hasattr(user, "profile_picture") and user.profile_picture:
        print(f"Profile Picture: {user.profile_picture}")
    else:
        print("No profile picture set.")

    # Afficher les 3 derniers posts
    print("\nRecent Posts:")
    for post in user.posts[-3:]:
        print(f"- {post}")


def edit_personal_info(user: User):
    """Permet de modifier les informations personnelles."""
    print("=== Edit Personal Information ===")
    print("1. Name\n2. Age\n3. Country")
    choice = input("Select the field to edit: ")

    if choice == "1":
        new_name = input("Enter new name: ")
        user.name = new_name
    elif choice == "2":
        new_age = input("Enter new age: ")
        if new_age.isdigit():
            user.age = int(new_age)
        else:
            print("Invalid age, no changes made.")
    elif choice == "3":
        new_country = input("Enter new country: ")
        user.country = new_country
    else:
        print("Invalid option.")

    users_db.save_users()
    print("✅ Personal information updated successfully.")


def edit_profile_picture(user: User):
    """Permet de choisir une photo de profil depuis le disque."""
    print("=== Edit Profile Picture ===")
    picture_path = input("Enter the file path of your new profile picture: ")

    if not os.path.exists(picture_path):
        print("❌ File not found. Please try again.")
        return

    user.profile_picture = picture_path
    users_db.save_users()
    print(f"✅ Profile picture updated: {picture_path}")


def delete_account(user: User):
    """Permet de supprimer le compte utilisateur avec vérification du
mot de passe."""
    print("=== Delete Account ===")
    password = input("Enter your password to confirm: ")

    if user.get_password() == password:
        # Supprimer l’utilisateur de la base
        users_db.remove_user(user.username)

        # Supprimer des listes followers/following
        for u in users_db.users_list:
            if user.username in u.followers:
                u.followers.remove(user.username)
            if user.username in u.following:
                u.following.remove(user.username)
        users_db.save_users()
        print("✅ Account deleted successfully.")
        return True
    else:
        print("❌ Wrong password. Account not deleted.")
        return False