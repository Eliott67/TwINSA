import datetime
import os
import json
from .user import User
from .users_db import UsersDatabase
from .notification import LikeNotification, CommentNotification

class Post:
    def __init__(self, content, poster_username, database):
        self.poster_username = poster_username
        self.database = database
        self.user = self.database.get_user(self.poster_username)
        self.content = content  # Pas de filtrage
        self.date = datetime.datetime.now()
        self.likes = []
        self.comments = []
        self.id_comment = 0
        if self.user is not None:
            self.post_id = len(self.user.posts) + 1
        else:
            self.post_id = 0  # déjà fourni

        self.update_poster_list_posts()

    def update_poster_list_posts(self):
        """Met à jour la liste des posts de l’utilisateur."""
        if self.user != None :
            if self not in self.user.posts:
                self.user.add_post(self)
            else:
                self.user.delete_post(self)
                self.user.add_post(self)

    # --- Likes ---
    def update_likes(self):
        self.user.likes[self.post_id] = len(self.likes)

    def add_like(self, username):
        if username not in self.likes:
            self.likes.append(username)
        self.update_likes()
        liker = self.database.get_user(username)
        liked = self.user
        like_notification = LikeNotification(liker, liked, self)
        like_notification.send()    

    def remove_like(self, username):
        if username in self.likes:
            self.likes.remove(username)
        self.update_likes()

    # --- Commentaires ---
    def add_comment(self, commenter_username, comment):
        self.id_comment += 1
        self.comments.append({
            "id": self.id_comment,
            "username": commenter_username,
            "comment": comment,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.update_poster_list_posts()

        commenter = self.database.get_user(commenter_username)
        commented = self.user
        comment_notification = CommentNotification(commenter, commented, self, comment)
        comment_notification.send()

    def remove_comment(self, id_comment, deleter_username):
        for c in list(self.comments):
            if c["id"] == id_comment and (
                c["username"] == deleter_username or deleter_username == self.poster_username
            ):
                self.comments.remove(c)
                break
        self.update_poster_list_posts()

    def edit_comment(self, id_comment, new_comment, editor_username):
        for c in self.comments:
            if c["id"] == id_comment and c["username"] == editor_username:
                c["comment"] = new_comment
                c["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_poster_list_posts()

    # --- Modifier le post ---
    def edit_post(self, new_content):
        self.content = new_content
        self.date = datetime.datetime.now()
        self.update_poster_list_posts()

    # --- Afficher dans la console (debug) ---
    def display_post(self):
        print(f"Post by {self.poster_username} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Content: {self.content}")
        print(f"Likes: {len(self.likes)}")
        if self.comments:
            print("Comments:")
            for c in self.comments:
                print(f"  [{c['id']}] {c['username']} ({c['date']}): {c['comment']}")
        else:
            print("No comments yet.")

