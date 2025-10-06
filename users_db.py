# Create a json file database to store users information

import json
import os       
import user

class UsersDatabase:
    def __init__(self, db_file='users_database.json'):
        self.db_file = db_file
        self.users_list = self.load_users()
        self.usernames_list = self.get_usernames()
    
    def show_users(self):
        for user in self.users_list:
            print(f"Username: {user.username}, Email: {user.email}, Name: {user.name}, Age: {user.age}, Country: {user.country}")

    def load_users(self):
        users_list = []
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                json_file = json.load(file)
            for user in json_file:
                username = json_file[user]['username']
                email = json_file[user]['email']
                password = json_file[user]['password']
                name = json_file[user]['name']
                age = json_file[user]['age']
                country = json_file[user]['country']
                user = user.User(username, email, password, name, age, country)
                users_list.append(user)
            
        return users_list
    
    def get_usernames(self):
        self.usernames_list = [user.username for user in self.users_list]
        return self.usernames_list
    
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
        if user in self.users_list:
            raise ValueError("User already exists")
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


