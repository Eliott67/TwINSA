from users_db import UsersDatabase
from profile_display import show_profile

db = UsersDatabase("./backend/users_database.json")
users = db.load_users()

print(">>> Testing Alex:")
for user in users:
    if user.username == "alex":
        show_profile(user)


print(">>> Testing Sara:")
for user in users:
    if user.username == "sara":
        show_profile(user)
