import unittest
import os
import json
from user import User
from users_db import UsersDatabase

class TestUsersDatabase(unittest.TestCase):

    def setUp(self):
        # Create a temporary JSON database file
        self.db_file = "test_users_db.json"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.db = UsersDatabase(db_file=self.db_file)

        # Reset lists
        self.db.users_list = []
        self.db.usernames_list = []

        # Create three sample user
        self.user = User("ines", "ines@mail.com", "pass123", "Inés", 20, "Andorra")
        self.user2 = User("alex", "alex@mail.com", "pass321", "Alex", 19, "Miami")
        self.user3 = User("cris", "cris@mail.com", "pass000", "Cristina", 48, "Encamp")
    
    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_add_user_and_save(self):
        self.db.add_user(self.user)
        self.assertIn("ines", self.db.usernames_list)
        self.assertTrue(os.path.exists(self.db_file))

    def test_remove_user(self):
        self.db.add_user(self.user)
        self.db.remove_user("ines")
        self.assertNotIn("ines", self.db.usernames_list)

    def test_show_users(self):
        self.db.add_user(self.user)
        self.db.add_user(self.user2)
        self.db.show_users() 

    def test_unique_user(self):
        self.db.add_user(self.user)
        self.assertFalse(self.db.unique_user("ines"))
        self.assertTrue(self.db.unique_user("alex"))

    def test_authenticate_user(self):
        # Manually simulate saved users for test
        self.db.usernames_list = ["ines"]
        self.db.users_list = [self.user]
        self.db.users = {"ines": {"password": "pass123"}}

        self.assertTrue(self.db.authenticate_user("ines", "pass123"))
        self.assertFalse(self.db.authenticate_user("ines", "wrongpass"))
        self.assertFalse(self.db.authenticate_user("alex", "pass123"))


print("--Testing UsersDatabase class--")
db_object = UsersDatabase()
db_object.new_database()
user1 = User("ines", "ines@mail.com", "pass123", "Inés", 20, "Andorra")
user2 = User("alex", "alex@mail.com", "pass321", "Alex", 19, "Miami")
user3 = User("cris", "cris@mail.com", "pass000", "Cristina", 48, "Encamp")
db_object.add_user(user1)
db_object.add_user(user2)
db_object.add_user(user3)
db_object.show_users()
db_object.remove_user("alex")
db_object.show_users()
db_object.new_database()
db_object.show_users()
print("--End of testing UsersDatabase class--")

if __name__ == '__main__':
    unittest.main()


