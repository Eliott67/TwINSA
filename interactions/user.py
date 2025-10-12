class User:
    def __init__(self, username, email, password, name, age, country, is_public=True):
        self.username = username
        self.email = email
        self.__password = password # Private attribute
        self.name = name
        self.age = age
        self.country = country
        self.is_public = is_public
        self.followers = []
        self.following = []
        self.posts = []
        self.likes = 0

    def display_info(self):
        print(f"Name: {self.name}, Email: {self.email}, Age: {self.age}, Country: {self.country}")

    def add_follower(self, friend_username):
        self.followers.append(friend_username)
        print(f"{friend_username} is now following {self.username}.")
        
    def add_following(self, friend_username):
        self.following.append(friend_username)
        print(f"{self.username} is now following {friend_username}.")
    
    def get_password(self):
        return self.__password

    def get_nb_followers(self):
        return len(self.followers)
                   
    def get_nb_following(self):
        return len(self.following)
    
    def add_post(self, post):
        self.posts.append(post)
        self.likes += post.likes
        #finish...

    def follows(self, other_user):
         # Vérifie si self suit other_user
         return other_user.username in self.following

        
