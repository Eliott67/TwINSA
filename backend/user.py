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
        self.posts = []  # List of Post objects
        self.likes = {}  # dict: post_id -> number of likes
        self.total_likes = sum(self.likes.values())

    def display_info(self):
        print(f"Name: {self.name}, Email: {self.email}, Age: {self.age}, Country: {self.country}")

    def display_posts(self):
        if not self.posts:
            print(f"{self.username} has no posts.")
        else :
            print(f"Posts by {self.username}:")
            for post in self.posts:
                post.display_post()
                print("-" * 20)

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

    def delete_post(self, post):
        if post in self.posts:
            self.posts.remove(post)

    def follows(self, other_user):
         # Vérifie si self suit other_user
         return other_user.username in self.following

