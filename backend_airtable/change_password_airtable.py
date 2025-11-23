# backend_airtable/change_password.py

import random
import string

from backend_airtable.user_airtable import User
from backend_airtable.user_airtable_db import AirtableUsersDB


class SecureUser(User):
    """
    Extension de User qui gère :
    - changement de mot de passe
    - génération et validation d’un token de reset
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_token = None

    # ----------------------------------------------
    # PASSWORD VERIFICATION
    # ----------------------------------------------
    def verify_password(self, password):
        return self.get_password() == password

    # ----------------------------------------------
    # CHANGE PASSWORD
    # ----------------------------------------------
    def change_password(self, old_password: str, new_password: str):
        """
        Change le mot de passe utilisateur :
        - vérifie l'ancien mdp
        - met à jour l'objet
        - met à jour Airtable via AirtableUsersDB
        """
        if self._password != old_password:
            return False

        # Mise à jour dans l'objet
        self._password = new_password

        # Mise à jour dans Airtable
        from backend_airtable.user_airtable_db import AirtableUsersDB
        import backend_airtable.airtable_secrets as secrets

        db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)
        db.update_user_password(self.record_id, new_password)

        print("✅ Mot de passe changé avec succès.")
        return True


    # ----------------------------------------------
    # GENERATE RESET TOKEN
    # ----------------------------------------------
    def generate_reset_token(self):
        chars = string.ascii_letters + string.digits
        self.reset_token = ''.join(random.choice(chars) for _ in range(8))
        print(f"🔑 Token envoyé à {self.email} : {self.reset_token}")
        return self.reset_token

    # ----------------------------------------------
    # RESET PASSWORD WITH TOKEN
    # ----------------------------------------------
    def reset_password(self, token, new_password):
        if token != self.reset_token:
            print("❌ Token invalide.")
            return False

        # Mise à jour locale
        self._User__password = new_password
        self.reset_token = None

        # Mise à jour Airtable
        db = AirtableUsersDB()
        user_data = db.get_user(self.username)

        if user_data and user_data.record_id:
            db.update_user_fields(user_data.record_id, {"password": new_password})

        print("✅ Mot de passe réinitialisé avec succès.")
        return True
