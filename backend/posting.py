import datetime
import os
import json
import re
from .user import User
from .users_db import UsersDatabase
from .notification import LikeNotification, CommentNotification

class Post:
     # 🔹 Liste générale de tous les hashtags rencontrés (en mémoire)
    general_hashtags = set()
    def __init__(self, content, poster_username, database, image=None):
        self.poster_username = poster_username
        self.database = database
        self.user = self.database.get_user(self.poster_username)
        self.content = content
        self.image = image  # Pas de filtrage
        self.date = datetime.datetime.now()
        self.likes = []
        self.comments = []
        self.id_comment = 0
        # 🔹 Extraction des hashtags dans le contenu
        self.hashtags = self.extract_hashtags(self.content)
        # 🔹 Mise à jour de la liste générale
        Post.general_hashtags.update(self.hashtags)
        if self.user is not None:
            self.post_id = len(self.user.posts) + 1
        else:
            self.post_id = 0  # déjà fourni


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

    @staticmethod
    def extract_hashtags(text: str):
        """
        Extrait les hashtags d'un texte.
        Règle simple : mots qui commencent par # suivis de lettres/chiffres/underscore.
        On renvoie une liste de tags sans le #, en minuscules, sans doublons.
        """
        if not text:
            return []

        # Exemple : "Coucou #Insa #maths #Insa_2025" -> ['insa', 'maths', 'insa_2025']
        raw_tags = re.findall(r"#(\w+)", text)

        seen = set()
        tags = []
        for t in raw_tags:
            t_norm = t.lower()
            if t_norm not in seen:
                seen.add(t_norm)
                tags.append(t_norm)
        return tags

    @classmethod
    def get_general_hashtags(cls):
        """Renvoie la liste générale triée de tous les hashtags."""
        return sorted(cls.general_hashtags)


    def get_html_content(self):
        """
        Retourne le contenu du post où les hashtags sont remplacés
        par des liens cliquables <a href="/hashtag/...">.
        """
        formatted = self.content

        for tag in self.hashtags:
            formatted = formatted.replace(
                f"#{tag}",
                f'<a href="/hashtag/{tag}" class="hashtag">#{tag}</a>'
            )

        return formatted
    
    @staticmethod
    def validate_hashtags(hashtags):
        """
        Vérifie que chaque hashtag respecte :
        - max 10 caractères
        - uniquement lettres et chiffres
        Retourne (True, None) si OK
        Retourne (False, message) si erreur
        """
        import re
        
        for tag in hashtags:
            if len(tag) > 10:
                return False, f"The hashtag #{tag} is too long (max 10 characters)."

            if not re.match(r"^[a-zA-Z0-9]+$", tag):
                return False, f"The hashtag #{tag} contains invalid characters (letters and numbers only)."

        return True, None


