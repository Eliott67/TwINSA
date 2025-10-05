# Create a json file database to store users information

import json
import os       

class UsersDatabase:
    def __init__(self, db_file='users_database.json'):
        self.db_file = db_file
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                return json.load(file)
        return {}

    def save_users(self):
        with open(self.db_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def add_user(self, username, password):
        if username in self.users:
            raise ValueError("User already exists")
        self.users[username] = {'password': password}
        self.save_users()

    def remove_user(self, username):
        if username not in self.users:
            raise ValueError("User does not exist")
        del self.users[username]
        self.save_users()

    def authenticate_user(self, username, password):
        if username in self.users and self.users[username]['password'] == password:
            return True
        return False
    
    def unique_user(self, username):
        return username not in self.users
    
    def unique_user2(self, email):
        return email not in self.users

    def get_all_users(self):
        return list(self.users.keys())