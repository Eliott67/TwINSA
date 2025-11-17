from user import User
import users_db
import posting 
from notification import Notification, LikeNotification, CommentNotification, FollowRequestNotification

new_users_db = users_db.UsersDatabase()
new_users_db.new_database()

user1 = User("ines", "ines@mail.com", "pass123", "Inés", 20, "Andorra")
user2 = User("alex", "alex@mail.com", "pass321", "Alex", 19, "Miami")
user3 = User("maria", "maria@hotmail.com", "pass231", "María", 21, "Spain")

new_users_db.add_user(user1)
new_users_db.add_user(user2)
new_users_db.add_user(user3)
new_users_db.save_users()
#new_users_db.show_users()

post1 = posting.Post("Hello everyone! This is my first post.", "ines",new_users_db)
post1.add_like("alex")
post1.add_like("maria")
post1.add_comment("maria", "Welcome to the platform, Inés!")
post1.add_comment("alex", "Hi Inés! Nice to meet you.")
print("Notifications for Inés:")
print(user1.notifications)

