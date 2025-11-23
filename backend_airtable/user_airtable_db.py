# backend_airtable/user_airtable_db.py

from . import airtable_secrets as secrets
from backend_airtable.user_airtable import User
from pyairtable import Table


class AirtableUsersDB:
    """
    DB wrapper for Users table. Works with linked records (record IDs).
    """

    def __init__(self, airtable_token=None, base_id=None, table_name="Users"):
        self.api_key = airtable_token or getattr(secrets, "AIRTABLE_TOKEN", None)
        self.base_id = base_id or getattr(secrets, "AIRTABLE_BASE_ID", None)
        self.table_name = table_name

        if not self.api_key or not self.base_id:
            raise ValueError("Airtable token and base_id must be provided (or set in airtable_secrets.py).")

        self.table = Table(self.api_key, self.base_id, self.table_name)

    # ------------------------
    # Helpers
    # ------------------------
    def _escape(self, s: str):
        return s.replace("'", "\\'") if s else s

    def _User(self):
        """Import local pour éviter circular import"""
        from backend_airtable.user_airtable import User
        return User

    # ------------------------
    # GETTERS
    # ------------------------
    def get_user_record(self, username: str):
        safe = self._escape(username)
        recs = self.table.all(formula=f"{{username}}='{safe}'")
        return recs[0] if recs else None

    def get_user_by_record_id(self, record_id: str):
        User = self._User()
        try:
            rec = self.table.get(record_id)
        except Exception:
            return None
        return User.from_dict(rec["fields"], record_id)

    def get_user(self, username_or_record):
        if not username_or_record:
            return None
        if username_or_record.startswith("rec"):
            return self.get_user_by_record_id(username_or_record)
        return self.get_user_by_username(username_or_record)

    def get_user_by_username(self, username: str):
        User = self._User()
        rec = self.get_user_record(username)
        if not rec:
            return None
        return User.from_dict(rec["fields"], rec["id"])

    def username_to_record_id(self, username: str):
        rec = self.get_user_record(username)
        return rec["id"] if rec else None

    def record_id_to_username(self, record_id: str):
        u = self.get_user_by_record_id(record_id)
        return u.username if u else None

    # ------------------------
    # CRUD
    # ------------------------
    def add_user(self, user: User):
        """
        Ajoute un utilisateur à Airtable proprement :
        - N’envoie PAS record_id (ça casse Airtable)
        - Assainit les champs None
        - Retourne l’ID Airtable et met à jour user.record_id
        """

        # Convertit en dict, mais retire record_id
        fields = user.to_dict_linked().copy()
        fields.pop("record_id", None)

        # Enlève les None (Airtable n’aime pas)
        fields = {k: v for k, v in fields.items() if v is not None}

        # Création Airtable
        record = self.table.create(fields)

        # Mise à jour de l'objet User
        user.record_id = record["id"]

        return record

    def update_user_password(self, record_id, new_password):
        self.table.update(record_id, {"password": new_password})

    def get_all_users(self):
        User = self._User()
        records = self.table.all()
        return [User.from_dict(r["fields"], r["id"]) for r in records]

    def update_user(self, user):
        if not user.record_id:
            raise ValueError("User must have record_id to be updated.")
        return self.table.update(user.record_id, user.to_dict_linked())

    def update_user_fields(self, record_id: str, fields: dict):
        return self.table.update(record_id, fields)

    def delete_user(self, identifier: str):
        if identifier.startswith("rec"):
            try:
                self.table.delete(identifier)
                return True
            except Exception:
                return False
        rec = self.get_user_record(identifier)
        if not rec:
            return False
        self.table.delete(rec["id"])
        return True

    def find_user(self, identifier: str):
        User = self._User()
        safe = self._escape(identifier)
        records = self.table.all(formula=f"OR(username = '{safe}', email = '{safe}')")
        if not records:
            return None
        rec = records[0]
        return User.from_dict(rec["fields"], rec["id"])
    
    def get_user_by_email(self, email: str):
        records = self.table.all(formula=f"{{email}} = '{email}'")
        if not records:
            return None
        return User.from_airtable(records[0])



# # ======================================================================
# # UNIT TESTS
# # ======================================================================

# if __name__ == "__main__":
#     import time
#     from backend_airtable.user_airtable import User

#     print("\n===== TESTS UNITAIRES : AirtableUsersDB =====\n")

#     def unique(prefix):
#         return f"{prefix}_{int(time.time())}"

#     db = AirtableUsersDB()

#     print("\n[TEST 1] add_user() …")
#     username = unique("testuser")
#     user = User(
#         username=username,
#         email=f"{username}@example.com",
#         password="Aa1!aaaa",
#         name="Test User",
#         age=25,
#         country="FR"
#     )
#     record = db.add_user(user)
#     assert "id" in record
#     print("✔ User created")

#     print("\n[TEST 2] get_user_by_username() …")
#     assert db.get_user_by_username(username) is not None
#     print("✔ OK")

#     print("\n[TEST 3] get_user_by_record_id() …")
#     assert db.get_user_by_record_id(user.record_id) is not None
#     print("✔ OK")

#     print("\n[TEST 4] find_user() …")
#     assert db.find_user(username)
#     assert db.find_user(f"{username}@example.com")
#     print("✔ OK")

#     print("\n[TEST 5] update_user_fields() …")
#     db.update_user_fields(user.record_id, {"country": "BE"})
#     assert db.get_user_by_record_id(user.record_id).country == "BE"
#     print("✔ OK")

#     print("\n===== ✔ ALL TESTS PASSED =====\n")

#pour avoir l'id, jsp si ça servira
# if __name__ == "__main__":
#     db = AirtableUsersDB()
#     print("record_id =", db.username_to_record_id("alex"))