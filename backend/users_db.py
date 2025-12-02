# Create a json file database to store users information

import json
import os
from backend.user import *  # module user.py qui contient la classe User
from backend.change_password import SecureUser

class UsersDatabase:
    def __init__(self, db_file='users_database.json'):
        self.db_file = db_file
        self.users_list = self.load_users()
        self.usernames_list = self.get_usernames()

    def new_database(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.users_list = []
        self.usernames_list = []
        self.save_users()
    
    def show_users(self):
        print("Current users in the database:")
        for u in self.users_list:
            print(
                f"Username: {u.username}, Email: {u.email}, "
                f"Name: {u.name}, Age: {u.age}, Country: {u.country}"
            )

    def load_users(self):
        users_list = []
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding="utf-8") as file:
                json_file = json.load(file)
            for username_item, data in json_file.items():
                image = json_file[username_item].get('profile_picture', None)
                email = json_file[username_item]['email']
                password = json_file[username_item]['password']
                name = json_file[username_item]['name']
                age = json_file[username_item]['age']
                country = json_file[username_item]['country']
                is_public = data.get('is_public', True)

                # listes sérialisables dans le JSON (usernames)
                followers = data.get('followers', [])
                following = data.get('following', [])
                blocked_users = data.get('blocked_users', [])
                pending_requests = data.get('pending_requests', [])
                notifications = data.get('notifications', [])

                # on recrée l'objet User
                user_new = SecureUser(username_item, email, password, name, age, country, is_public, profile_picture=image, hashed=True)

                # on réinjecte les listes (listes de usernames)
                user_new.followers = followers
                user_new.following = following
                user_new.blocked_users = blocked_users
                user_new.pending_requests = pending_requests
                user_new.notifications = notifications

                users_list.append(user_new)
            
        return users_list
    
    def get_usernames(self):
        return [u.username for u in self.users_list]
    
    def save_users(self):
        """
        Sauvegarde les utilisateurs dans le JSON en ne stockant
        que des types sérialisables (str, int, bool, listes, dict).
        """
        users_dict = {}

        for user in self.users_list : 
            users_dict[user.username] = user.to_dict()

        with open(self.db_file, 'w', encoding="utf-8") as file:
            json.dump(users_dict, file, indent=4)

    def add_user(self, u):
        if u.username in self.usernames_list:
            raise ValueError("Username already exists")
        self.users_list.append(u)
        self.usernames_list.append(u.username)
        self.save_users()

    def remove_user(self, username):
        if username not in self.usernames_list:
            raise ValueError("User does not exist")
        self.users_list.remove(self.get_user(username))
        self.usernames_list.remove(username)
        self.save_users()

    def get_user(self, username):
        if username in self.usernames_list:
            idx = self.usernames_list.index(username)
            return self.users_list[idx]
        return None

    def authenticate_user(self, username, password):
        if username in self.usernames_list:
            user_obj = self.get_user(username)
            if user_obj and user_obj.check_password(password):
                return True
        return False
    
    def unique_user(self, username):
        return username not in self.usernames_list

    def get_all_users(self):
        return self.users_list
