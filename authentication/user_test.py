import unittest
from user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User("ines", "ines@mail.com", "pass123", "Inés", 20, "Andorra")
        self.user2 = User("alex", "alex@mail.com", "pass321", "Alex", 19, "Miami")
    
    def test_user_attributes(self):
        self.assertEqual(self.user.username, "ines")
        self.assertEqual(self.user.email, "ines@mail.com")
        self.assertEqual(self.user.get_password(), "pass123")
        self.assertEqual(self.user.name, "Inés")
        self.assertEqual(self.user.age, 20)
        self.assertEqual(self.user.country, "Andorra")
        self.assertEqual(self.user.followers, [])
        self.assertEqual(self.user.following, [])

    def test_add_follower(self):
        self.user.add_follower("alex")
        self.assertIn("alex", self.user.followers)
        self.assertEqual(self.user.get_nb_followers(), 1)

    def test_add_following(self):
        self.user.add_following("alex")
        self.assertIn("alex", self.user.following)
        self.assertEqual(self.user.get_nb_following(), 1)

if __name__ == '__main__':
    unittest.main()

