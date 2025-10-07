# test_login_logout.py

import unittest
#import Login_logout
import Login_logout_v2 as login_logout


# 🔁 Création d'une fausse "base de données" d'utilisateurs pour les tests
class FakeUsersDB:
    fake_users = [
        {"username": "alice", "email": "alice@example.com", "password": "pass123"},
        {"username": "bob", "email": "bob@example.com", "password": "qwerty"},
    ]

    @classmethod
    def find_user(cls, identifier):
        for user in cls.fake_users:
            if user["username"] == identifier or user["email"] == identifier:
                return user
        return None

# 🧩 On remplace le module `users_db` utilisé dans `login_logout` par notre `FakeUsersDB`
login_logout.users_db = FakeUsersDB

# 🧪 Nos tests
class TestLoginLogout(unittest.TestCase):

    def test_login_success_username(self):
        user = login_logout.login("alice", "pass123")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "alice")

    def test_login_success_email(self):
        user = login_logout.login("bob@example.com", "qwerty")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "bob")

    def test_login_wrong_password(self):
        user = login_logout.login("alice", "wrongpass")
        self.assertIsNone(user)

    def test_login_user_not_found(self):
        user = login_logout.login("notfound", "pass123")
        self.assertIsNone(user)

    def test_login_empty_fields(self):
        user = login_logout.login("", "")
        self.assertIsNone(user)

    def test_logout(self):
        user = {"username": "alice"}
        result = login_logout.logout(user)
        self.assertIsNone(result)

    def test_logout_without_login(self):
        result = login_logout.logout(None)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
