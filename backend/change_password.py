import random
import string
import bcrypt
from backend.user import User  

class SecureUser(User):
    def __init__(self, username, email, password, name, age, country,is_public,profile_picture=None,hashed=True):
        super().__init__(username, email, password, name, age, country,is_public,profile_picture,hashed)
        self.reset_token = None  # pour mdp oublié

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self._User__password.encode())

    def change_password(self, old_password, new_password):
        """Change le mot de passe après vérification (bcrypt)."""
        if self.verify_password(old_password):
            self._User__password = self.hash_password(new_password)
            print("✅ Mot de passe changé avec succès.")
        else:
            print("❌ Ancien mot de passe incorrect.")

    def generate_reset_token(self):
        """Génère un token simple de réinitialisation."""
        letters_digits = string.ascii_letters + string.digits
        self.reset_token = ''.join(random.choice(letters_digits) for _ in range(8))
        print(f"🔑 Token envoyé à {self.email} : {self.reset_token}")

    def reset_password(self, token, new_password):
        """Réinitialise le mot de passe avec un token valide."""
        if self.reset_token == token:
            self._User__password = self.hash_password(new_password)
            self.reset_token = None
            print("✅ Mot de passe réinitialisé avec succès.")
        else:
            print("❌ Token invalide ou expiré.")
