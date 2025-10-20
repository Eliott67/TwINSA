#Search Users

from users_db import UsersDatabase
from user import User
<<<<<<< HEAD:backend/search_userv2.py
from login_logout import get_connected_users
=======
from Login_LogoutV2 import get_connected_users
>>>>>>> a5d4772 (Added profile page, improved feed design, fixed comments system):backend/search_user2.py

def go_to_search_bar():
    print("\n--- Search Users ---")
    history = []

    db = UsersDatabase()

    connected = get_connected_users()
    if not connected:
        print("No user is currently logged in. Please log in first.")
        return
    current_user = connected[0]  # On prend le premier utilisateur connecté
    print(f"Connected as: {current_user.username}")

    def display_history():
        if history:
            print("\nLast 5 Searches:")
            for item in history:
                print(f"- {item}")
        else:
            print("\nNo recent searches.")

    # Fonction to search users
    def search(query):
        nonlocal history
        print(f"\nSearching for users matching: '{query}'")
        
        # Get matching users by prefix (case insensitive)
        all_users = db.get_all_users()
        matches = [u for u in all_users if u.username.lower().startswith(query.lower())]

        if not matches:
            print("No users found.")
            return

        # Sort: followed users first, then alphabetical
        matches.sort(key=lambda u: (not current_user.follows(u), u.username.lower()))

        # Limit to 10 results
        results = matches[:10]

        # Add search to history
        history.insert(0, query)
        history = history[:5]

        print("\nResults:")
        for user in results:
            followed = "(Followed)" if current_user.follows(user) else ""
            print(f"- {user.username} {followed}")

    # Clear history
    def clear_history():
        nonlocal history
        history.clear()
        print("\nSearch history cleared.")

    # Simulate user interaction
    while True:
        print("\n--- Search Menu ---")
        print("1. Focus Search Bar (show history)")
        print("2. Search for Users")
        print("3. Clear Search")
        print("4. View User Profile")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            display_history()

        elif choice == "2":
            query = input("Type your search: ")
            search(query)

        elif choice == "3":
            clear_history()

        elif choice == "4":
            username = input("Enter username to view profile: ")
            user = db.get_user(username)
            if not user:
                print("User not found.")
                continue

            print(f"\n--- {user.username}'s Profile ---")
            if user.is_public or current_user.follows(user):
                print(f"Full profile of {user.username}:")
                print(f"- Name: {user.name}")
                print(f"- Age: {user.age}")
                print(f"- Country: {user.country}")
                print(f"- Account Type: {'Public' if user.is_public else 'Private'}")
                # ➕ Ajout : sous-menu pour voir followers/following
                while True:
                    print("\nView:")
                    print("1. Followers")
                    print("2. Following")
                    if current_user.follows(user):
                        print("3. Unfollow")
                    else:
                        print("3. Follow")
                    if current_user.blocks(user):
                        print("4. Unblock")
                    else:
                        print("4. Block")
                    print("5. View common friends")
                    print("6. Back to Search Menu")
                    sub_choice = input("Choose an option: ")

                    if sub_choice == "1":
                        user.display_followers()
                    elif sub_choice == "2":
                        user.display_following()
                    elif sub_choice == "3":
                        if current_user.follows(user):
                            current_user.unfollow(user)
                        else:
                            current_user.follow(user)
                    elif sub_choice == "4":
                        if current_user.blocks(user):
                            current_user.unblock(user)
                        else:
                            current_user.block(user)
                    elif sub_choice == "5":
                        current_user.get_common_friends(user)
                    elif sub_choice == "6":
                        break
                    else:
                        print("Invalid choice.")

            
            else:
                print("This account is private. Follow the user to see more information.")
                while True:
                    print("\nActions:")
                    print("1. Send Follow Request")
                    if current_user.blocks(user):
                        print("2. Unblock")
                    else:
                        print("2. Block")
                    print("3. Back to Search Menu")
                    sub_choice = input("Choose an option: ")

                    if sub_choice == "1":
                        current_user.follow(user)  # Cela va envoyer une demande
                    elif sub_choice == "2":
                        if current_user.blocks(user):
                            current_user.unblock(user)
                        else:
                            current_user.block(user)
                    elif sub_choice == "3":
                        break
                    else:
                        print("Invalid choice.")


        elif choice == "5":
            print("Exiting search.")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    from users_db import UsersDatabase
    from user import User

    print("=== INITIALISATION DE LA BASE DE TEST ===")

    db = UsersDatabase()
    db.new_database()  # vide la base existante

    # Création de l'utilisateur "mat"
    user_mat = User(
        username="mat",
        email="mat@example.com",
        password="Pass123!",  # doit correspondre au mot de passe du login
        name="Matthieu",
        age=30,
        country="France",
        is_public=True
    )
    db.add_user(user_mat)

# Création de l'utilisateur "bob"
    user_bob = User(
        username="bob",
        email="bob@mail.com",
        password="5678",  # doit correspondre au mot de passe du login
        name="Bob",
        age=28,
        country="USA",
        is_public=False
    )
    db.add_user(user_bob)
    user_mat.add_following(user_bob.username)  # mat suit bob
    user_bob.add_follower(user_mat.username)   # bob a mat comme follower
    db.save_users()

    # Optionnel : ajouter d'autres utilisateurs à rechercher
    db.add_user(User("alice", "alice@mail.com", "1234", "Alice", 25, "Canada",is_public=False))
    db.add_user(User("matheo", "matheo@mail.com", "0000", "Matheo", 22, "France",is_public=True))

    print("Base de test initialisée avec les utilisateurs : mat, alice, bob, matheo")

    # === Lancement des tests ===
    print("\n=== TEST AVEC AUCUN UTILISATEUR CONNECTÉ ===")
    go_to_search_bar()

    print("\n=== TEST AVEC UN UTILISATEUR CONNECTÉ ===")
<<<<<<< HEAD:backend/search_userv2.py
    from login_logout import login
=======
    from Login_LogoutV2 import login
>>>>>>> a5d4772 (Added profile page, improved feed design, fixed comments system):backend/search_user2.py
    login("mat", "Pass123!")  # devrait fonctionner maintenant
    go_to_search_bar()
