from user import User

# Créer un utilisateur public
u1 = User("alex", "alex@gmail.com", "pass", "Alex", 20, "Belgium", is_public=True)
u1.posts.append("Hello Twinsa!")
u1.posts.append("Another day at school!")

print(">>> Testing public profile:")
u1.view_profile()


# Créer un utilisateur privé
u2 = User("sara", "sara@gmail.com", "pass", "Sara", 22, "France", is_public=False)
u2.posts.append("My private thoughts...")

print(">>> Testing private profile:")
u2.view_profile()
