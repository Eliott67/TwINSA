from datetime import datetime
from user import User
from users_db import UsersDatabase
from posting import Post

class Feed:
    def __init__(self, user: User, database: UsersDatabase):
        self.user = user
        self.db = database
        self.posts = self.refresh_feed()

    def refresh_feed(self):
        """Récupère tous les posts visibles, triés par date décroissante."""
        all_posts = self.user.posts.copy()
        for username in self.user.following:
            followed_user = self.db.get_user(username)
            if followed_user:
                all_posts.extend(followed_user.posts)
        all_posts.sort(key=lambda post: post.date, reverse=True)
        self.posts = all_posts
        return self.posts

    def display_feed(self):
        """Affiche le fil d'actualité avec infos essentielles."""
        if not self.posts:
            print("Aucun post à afficher.")
            return
        print(f"\n--- {self.user.username}'s Feed ---\n")
        for i, post in enumerate(self.posts, start=1):
            print(f"[{i}] {post.poster_username} ({post.date.strftime('%Y-%m-%d %H:%M:%S')})")
            print(f"    {post.content}")
            print(f"    Likes: {len(post.likes)} | Comments: {len(post.comments)}")
            print("-" * 50)

    def open_author_profile(self, post_index):
        """Affiche le profil de l'auteur d'un post."""
        if 0 <= post_index < len(self.posts):
            author_username = self.posts[post_index].poster_username
            author = self.db.get_user(author_username)
            if author:
                print(f"\n--- Profil de {author_username} ---")
                author.display_info()
                author.display_posts()
        else:
            print("Post invalide.")

    def make_post(self, content):
        """Créer un nouveau post."""
        new_post = Post(content, self.user.username, self.db)
        print("TwINSA Posted!")
        self.refresh_feed()

    def edit_post(self, post_index, new_content):
        """Modifier un de ses posts."""
        post = self.posts[post_index]
        if post.poster_username != self.user.username:
            print("Vous ne pouvez éditer que vos propres posts.")
            return
        post.edit_post(new_content)
        print("Post mis à jour !")
        self.refresh_feed()

    def delete_post(self, post_index):
        """Supprimer un de ses posts."""
        post = self.posts[post_index]
        if post.poster_username != self.user.username:
            print("Vous ne pouvez supprimer que vos propres posts.")
            return
        confirm = input("Confirmez la suppression ? (y/n) ")
        if confirm.lower() == 'y':
            self.user.delete_post(post)
            print("Post supprimé !")
            self.refresh_feed()
