from datetime import datetime

class Post:
    def __init__(self, content, poster_username):
        self.content = content
        self.poster_username = poster_username
        self.date = datetime.now()
        self.likes = []
        self.comments = []

    def edit_post(self, new_content):
        self.content = new_content
        self.date = datetime.now()

class User:
    def __init__(self, username):
        self.username = username
        self.posts = []

    def delete_post(self, post):
        if post in self.posts:
            self.posts.remove(post)

class Feed:
    def __init__(self, user, all_posts):
        self.user = user
        self.posts = all_posts  # liste de tous les posts visibles

    def display_feed(self):
        for idx, post in enumerate(self.posts):
            print(f"[{idx}] {post.poster_username} ({post.date.strftime('%Y-%m-%d %H:%M:%S')})")
            print(f"    {post.content}")
            print(f"    Likes: {len(post.likes)} | Comments: {len(post.comments)}")
            print("-"*40)

    def edit_post(self, index, new_content):
        post = self.posts[index]
        if post.poster_username != self.user.username:
            print("Vous ne pouvez éditer que vos propres posts.")
            return
        post.edit_post(new_content)
        print("Post mis à jour !")

    def delete_post(self, index):
        post = self.posts[index]
        if post.poster_username != self.user.username:
            print("Vous ne pouvez supprimer que vos propres posts.")
            return
        confirm = input("Confirmez la suppression ? (y/n) ")
        if confirm.lower() == 'y':
            self.user.delete_post(post)
            print("Post supprimé !")
