from users_db import UsersDatabase
from user import User
from posting import Post
from posts_display import Feed  # ton fichier backend/posts_display.py

# --- Initialisation de la base et des utilisateurs ---
db = UsersDatabase()
db.new_database()  # pour partir d’une base vide

# Création d'utilisateurs de test
user1 = User("Perine", "perine@test.com", "Pass123!", "Perine", 20, "France")
user2 = User("Eliott", "eliott@test.com", "Twinsa123!", "Eliott", 22, "France")
user3 = User("Jules", "jules@test.com", "123JULEs!", "Jules", 21, "France")

db.add_user(user1)
db.add_user(user2)
db.add_user(user3)

# Définir les relations de suivi
user1.add_following("Eliott")
user1.add_following("Jules")

# --- Création de posts ---
Post("Salut tout le monde!", "Perine", db)
Post("Bonjour!", "Eliott", db)
Post("Hey!", "Jules", db)

# --- Création du feed pour Perine ---
feed = Feed(user1, db)

# --- Scénario : Display all posts ---
print("\n--- Affichage du feed initial ---")
feed.display_feed()

# --- Scénario : Make a post ---
print("\n--- Création d'un nouveau post ---")
feed.make_post("Nouveau post de Perine")
feed.display_feed()

# --- Scénario : Edit a post ---
print("\n--- Edition du premier post de Perine ---")
feed.edit_post(0, "Post modifié de Perine")
feed.display_feed()

# --- Scénario : Delete un post ---
print("\n--- Suppression du deuxième post de Perine ---")
# Pour tester automatiquement, on peut modifier delete_post pour confirmer automatiquement
# Ici on fait manuel, tape 'y' dans la console
feed.delete_post(1)
feed.display_feed()

# --- Scénario : Open author’s profile ---
print("\n--- Affichage du profil du premier post ---")
feed.open_author_profile(0)
