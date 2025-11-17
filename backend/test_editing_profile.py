import unittest
from user import User
from users_db import UsersDatabase
from editing_profile import delete_account
import os

class TestEditingProfile(unittest.TestCase):

    def setUp(self):
        self.db = UsersDatabase(db_file="test_editing_profile.json")
        self.db.new_database()
        self.user = User("ines", "ines@mail.com", "pass123", "Inés", 20, "Andorra")
        self.db.add_user(self.user)

    def tearDown(self):
        if os.path.exists("test_editing_profile.json"):
            os.remove("test_editing_profile.json")

    def test_delete_account_success(self):
        result = delete_account(self.user)
        self.assertTrue(result)

    def test_delete_account_wrong_password(self):
        self.user.password = "wrongpass"
        result = delete_account(self.user)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
