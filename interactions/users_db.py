# Create a json file database to store users information

import json
import os       
import user

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
        for user in self.users_list:
            print(f"Username: {user.username}, Email: {user.email}, Name: {user.name}, Age: {user.age}, Country: {user.country}")

    def load_users(self):
        users_list = []
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                json_file = json.load(file)
            for username_item in json_file.keys():
                username = json_file[username_item]['username']
                email = json_file[username_item]['email']
                password = json_file[username_item]['password']
                name = json_file[username_item]['name']
                age = json_file[username_item]['age']
                country = json_file[username_item]['country']
                user_new = user.User(username, email, password, name, age, country)
                users_list.append(user_new)
            
        return users_list
    
    def get_usernames(self):
        return [user.username for user in self.users_list]
    
    def save_users(self):
        users_dict = {}
        for user in self.users_list:
            users_dict[user.username] = {
                'username': user.username,
                'email': user.email,
                'password': user.get_password(),
                'name': user.name,
                'age': user.age,
                'country': user.country
            }
        with open(self.db_file, 'w') as file:
            json.dump(users_dict, file, indent=4)

    def add_user(self, user):
        if user.username in self.usernames_list:
            raise ValueError("Username already exists")
        self.users_list.append(user)
        self.usernames_list.append(user.username)
        self.save_users()

    def remove_user(self, username):
        if username not in self.usernames_list:
            raise ValueError("User does not exist")
        self.users_list.remove(self.get_user(username))
        self.usernames_list.remove(username)
        self.save_users()

    def get_user(self, username):
        if username in self.usernames_list:
            user_index = self.usernames_list.index(username)
            return self.users_list[user_index]
        return None

    def authenticate_user(self, username, password):
        if username in self.usernames_list:
            user_obj = self.get_user(username)
            if user_obj and user_obj.get_password() == password:
                return True
        return False
    
    def unique_user(self, username):
        return username not in self.usernames_list

    def get_all_users(self):
        return self.users_list


