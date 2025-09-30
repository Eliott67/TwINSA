class user:
    def __init__(self, username, email, password, name, age, country):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.age = age
        self.country = country
        self.followers = []
        self.following = []
        self.posts = []
        self.likes = 0

    def display_info(self):
        print(f"Name: {self.name}, Email: {self.email}, Age: {self.age}, Country: {self.country}")

    def add_follower(self, friend_username):
        self.followers.append(friend_username)
        print(f"{friend_username} is now following {self.username}.")
        
    def follow(self, friend_username):
        self.following.append(friend_username)
        print(f"{self.username} is now following {friend_username}.")