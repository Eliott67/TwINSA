import notification

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
        self.blocked_users = []
        self.posts = []  # List of Post objects
        self.likes = {}  # dict: post_id -> number of likes
        self.total_likes = sum(self.likes.values())
        self.notifications = []
        self.pending_requests = []

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

    def follows(self, other_user): #fonction de test
         # Vérifie si self suit other_user
         return other_user.username in self.following

        
    def unfollow(self, target_user):
        if target_user.username in self.following:
            self.following.remove(target_user.username)
            if self.username in target_user.followers:
                target_user.followers.remove(self.username)
            print(f"You unfollowed {target_user.username}.")
        else:
            print(f"You are not following {target_user.username}.")

    def display_followers(self):
        print(f"{self.username}'s followers:")
        for u in self.followers:
            print(f"- {u}")

    def display_following(self):
        print(f"{self.username} is following:")
        for u in self.following:
            print(f"- {u}")

    def follow(self, target_user):
        if target_user.username in self.following:
            print(f"You are already following {target_user.username}.")
            return
        
        if self.username in target_user.blocked_users:
            print(f"You cannot follow {target_user.username}. You are blocked.")
            return

        if target_user.username in self.blocked_users:
            print(f"You have blocked {target_user.username}. Unblock them to follow.")
            return

        if target_user.is_public:
            self.add_following(target_user.username)
            target_user.add_follower(self.username)

            # Notification
            notif = notification.NewFollowerNotification(sender=self, receiver=target_user)
            notif.send()

            print(f"You are now following {target_user.username}.")
        else:
            # Follow request
            request = notification.FollowRequestNotification(sender=self, receiver=target_user)
            request.send_request()
            print(f"Follow request sent to {target_user.username}.")

    def get_common_friends(self, other_user):
        common = set(self.following) & set(other_user.following)
        if common:
            print(f"Common friends with {other_user.username}:")
            for friend in common:
                print(f"- {friend}")
        else:
            print(f"No common friends with {other_user.username}.")

    def block(self, target_user):
        if target_user.username not in self.blocked_users:
            self.blocked_users.append(target_user.username)
            print(f"{target_user.username} has been blocked.")

            # Remove them from your followers
            if target_user.username in self.followers:
                self.followers.remove(target_user.username)
            if self.username in target_user.following:
                target_user.following.remove(self.username)

            # Remove from your following
            if target_user.username in self.following:
                self.following.remove(target_user.username)
            if self.username in target_user.followers:
                target_user.followers.remove(self.username)
        else:
            print(f"{target_user.username} is already blocked.")

    def blocks(self, other_user): #fonction de test
         # Vérifie si self bloque other_user
         return other_user.username in self.blocked_users

    def unblock(self, target_user):
        if target_user.username in self.blocked_users:
            self.blocked_users.remove(target_user.username)
            print(f"You have unblocked {target_user.username}.")
        else:
            print(f"{target_user.username} is not in your blocked list.")


    def view_profile(self):
        print("\n===== USER PROFILE =====")
        print(f"👤 Username: @{self.username}")
        print(f"📛 Name: {self.name}")
        print(f"🎂 Age: {self.age}")
        print(f"🌍 Country: {self.country}")
        print(f"🔒 Public profile: {self.is_public}")

        print("\n--- Posts ---")
        if not self.is_public:
            print("🚫 This profile is private. Posts are hidden.")
        else:
            if not self.posts:
                print("No posts yet.")
            else:
                for i, post in enumerate(self.posts, 1):
                    print(f"{i}. {post}")

        print("========================\n")

    
