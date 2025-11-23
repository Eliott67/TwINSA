# backend_airtable/login_logout_airtable.py

import backend_airtable.airtable_secrets as secrets
from backend_airtable.user_airtable_db import AirtableUsersDB

CONNECTED_USERS = []


def login(identifier=None, password=None):
    print("=== Log in ===")

    if identifier is None:
        identifier = input("Enter your username or email: ")
    if password is None:
        password = input("Enter your password: ")

    if not identifier or not password:
        print("All fields are required.")
        return None

    db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

    user = db.find_user(identifier)
    if not user:
        print("User not found. Please check your username/email.")
        return None

    if user.get_password() != password:
        print("Wrong password.")
        return None

    print(f"Login successful. Welcome back, {user.username}!")
    CONNECTED_USERS.append(user)
    return user


def logout(current_user):
    if not current_user:
        print("You are not logged in.")
        return None

    if current_user in CONNECTED_USERS:
        CONNECTED_USERS.remove(current_user)

    print(f"User {current_user.username} has been logged out.")
    return None


def get_connected_users():
    return CONNECTED_USERS

# ======================================================================
#   UNIT TESTS — exécutés uniquement si on lance ce fichier directement
# ======================================================================
if __name__ == "__main__":
    print("\n===== TESTS UNITAIRES : login_logout_airtable =====\n")

    def check(cond, msg):
        if cond:
            print("✔", msg)
        else:
            raise AssertionError("❌ " + msg)

    # -------------------------------------------------------------
    # Mock User + DB (remplace AirtableUsersDB)
    # -------------------------------------------------------------

    class MockUser:
        def __init__(self, username, email, password, record_id):
            self.username = username
            self.email = email
            self._password = password
            self.record_id = record_id

        def get_password(self):
            return self._password

    class MockUsersDB:
        def __init__(self):
            self.users = {
                "alice": MockUser("alice", "alice@mail.com", "pwd123", "recAlice"),
                "bob": MockUser("bob", "bob@mail.com", "secret", "recBob")
            }

        def find_user(self, identifier):
            for u in self.users.values():
                if identifier in (u.username, u.email):
                    return u
            return None

    # on monkey-patche AirtableUsersDB pour utiliser notre mock
    AirtableUsersDB_backup = AirtableUsersDB
    AirtableUsersDB = lambda *_args, **_kwargs: MockUsersDB()

    # Clean connected users
    CONNECTED_USERS.clear()

    # -------------------------------------------------------------
    # Test 1 — Login OK
    # -------------------------------------------------------------
    print("\n[TEST 1] Login success")
    user = login(identifier="alice", password="pwd123")
    check(user is not None, "login returns user")
    check(user.username == "alice", "correct user")
    check(len(CONNECTED_USERS) == 1, "user added to CONNECTED_USERS")

    # -------------------------------------------------------------
    # Test 2 — Wrong password
    # -------------------------------------------------------------
    print("\n[TEST 2] Wrong password")
    user2 = login(identifier="bob", password="wrong")
    check(user2 is None, "login fails with wrong password")
    check(len(CONNECTED_USERS) == 1, "CONNECTED_USERS unchanged")

    # -------------------------------------------------------------
    # Test 3 — Unknown user
    # -------------------------------------------------------------
    print("\n[TEST 3] Unknown user")
    user3 = login(identifier="nobody", password="x")
    check(user3 is None, "login fails for unknown user")
    check(len(CONNECTED_USERS) == 1, "CONNECTED_USERS unchanged")

    # -------------------------------------------------------------
    # Test 4 — Logout
    # -------------------------------------------------------------
    print("\n[TEST 4] Logout")
    logout(CONNECTED_USERS[0])
    check(len(CONNECTED_USERS) == 0, "CONNECTED_USERS emptied after logout")

    # Restore original AirtableUsersDB
    AirtableUsersDB = AirtableUsersDB_backup

    # -------------------------------------------------------------
    # FIN DES TESTS
    # -------------------------------------------------------------
    print("\n===== ✔ TOUS LES TESTS login_logout_airtable ONT RÉUSSI =====\n")
