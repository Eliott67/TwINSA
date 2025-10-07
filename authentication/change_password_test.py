import unittest
from backend.change_password import SecureUser 
import string

class TestSecureUser(unittest.TestCase):

    def setUp(self):
        self.user = SecureUser(
            username="eliottoster",
            email="eliottost@gmail.com",
            password="oldpass",
            name="Eliott Oster",
            age=20,
            country="France"
        )

    def test_verify_password(self):
        self.assertTrue(self.user.verify_password("oldpass"))
        self.assertFalse(self.user.verify_password("wrongpass"))

    def test_change_password_success(self):
        self.user.change_password("oldpass", "newpass")
        self.assertTrue(self.user.verify_password("newpass"))

    def test_change_password_failure(self):
        self.user.change_password("wrongpass", "newpass")
        self.assertTrue(self.user.verify_password("oldpass"))  # pas changé

    def test_generate_reset_token(self):
        self.user.generate_reset_token()
        self.assertIsNotNone(self.user.reset_token)
        self.assertEqual(len(self.user.reset_token), 8)
        # Vérifie que le token est bien composé de lettres et chiffres
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in self.user.reset_token))

    def test_reset_password_success(self):
        self.user.generate_reset_token()
        token = self.user.reset_token
        self.user.reset_password(token, "newsecurepass")
        self.assertTrue(self.user.verify_password("newsecurepass"))
        self.assertIsNone(self.user.reset_token)  # token doit être invalidé

    def test_reset_password_failure(self):
        self.user.generate_reset_token()
        wrong_token = "wrong123"
        self.user.reset_password(wrong_token, "newsecurepass")
        self.assertTrue(self.user.verify_password("oldpass"))  # mdp pas changé


if __name__ == "__main__":
    unittest.main()
