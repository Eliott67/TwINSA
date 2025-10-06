import random
import string
from user import User  

class SecureUser(User):
    def __init__(self, username, email, password, name, age, country):
        super().__init__(username, email, password, name, age, country)
        self.reset_token = None  # pour mdp oublié

    def verify_password(self, password):
        """Vérifie si le mot de passe correspond."""
        return self.password == password

    def change_password(self, old_password, new_password):
        """Permet de changer le mot de passe si l'ancien est correct."""
        if self.verify_password(old_password):
            self.password = new_password
            print("✅ Mot de passe changé avec succès.")
        else:
            print("❌ Ancien mot de passe incorrect.")

    def generate_reset_token(self):
        """Génère un token de réinitialisation (simulant un envoi par email)."""
        letters_digits = string.ascii_letters + string.digits
        self.reset_token = ''.join(random.choice(letters_digits) for _ in range(8))
        print(f"🔑 Token de réinitialisation généré et envoyé à {self.email} : {self.reset_token}")

    def reset_password(self, token, new_password):
        """Réinitialise le mot de passe avec un token valide."""
        if self.reset_token == token:
            self.password = new_password
            self.reset_token = None
            print("✅ Mot de passe réinitialisé avec succès.")
        else:
            print("❌ Token invalide ou expiré.")
