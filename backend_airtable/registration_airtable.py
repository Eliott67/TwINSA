import sys
import os

# Allow running the file directly from its folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.user_airtable import User
import backend_airtable.airtable_secrets as secrets

MIN_PASSWORD_LENGTH = 8

db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)


def is_strong_password(password: str) -> bool:
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    length_ok = len(password) >= MIN_PASSWORD_LENGTH
    return has_upper and has_lower and has_digit and has_special and length_ok


def validate_registration(user: User, confirm_password: str):
    if not user.username or not user.email or not user.get_password() or not confirm_password:
        return False, "All fields are required."

    if user.get_password() != confirm_password:
        return False, "Passwords do not match."

    if not is_strong_password(user.get_password()):
        return False, (
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters "
            "and include uppercase, lowercase, digit, and special character."
        )

    if "@" not in user.email or "." not in user.email:
        return False, "Invalid email format."

    if " " in user.username or " " in user.email:
        return False, "Username and email cannot contain spaces."

    if db.get_user_by_username(user.username) is not None:
        return False, "Username already exists."

    airtable_records = db.table.all()
    for rec in airtable_records:
        if rec["fields"].get("email", "").lower() == user.email.lower():
            return False, "Email already exists."

    return True, "Registration successful."


def registration():
    print("\n--- CREATE AN ACCOUNT ---")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    confirm_password = input("Confirm password: ").strip()
    name = input("Name: ").strip() or "Unknown"
    age = input("Age: ").strip()
    age = int(age) if age.isdigit() else 0
    country = input("Country: ").strip() or "Unknown"

    new_user = User(username=username, email=email, password=password,
                    name=name, age=age, country=country)

    valid, msg = validate_registration(new_user, confirm_password)
    print(msg)

    if valid:
        db.add_user(new_user)
        print("🎉 User successfully registered!")
        
# ======================================================================
#   UNIT TESTS — exécutés uniquement si on lance ce fichier directement
# ======================================================================

if __name__ == "__main__":
    import time
    from backend_airtable.user_airtable import User

    print("\n===== TESTS UNITAIRES : registration_airtable =====\n")

    def unique(prefix):
        """Génère un identifiant unique basé sur le timestamp."""
        return f"{prefix}_{int(time.time())}"

    print("[TEST 1] Vérification du validateur de mot de passe...")
    assert is_strong_password("Aa1!aaaa"), "❌ Mot de passe valide détecté comme invalide"
    assert not is_strong_password("aaaaaa"), "❌ Mot de passe faible accepté"
    print("✔ Validateur password OK")

    print("\n[TEST 2] Validation registration — champs manquants...")
    user = User(username="", email="", password="")
    ok, msg = validate_registration(user, "")
    assert not ok, "❌ Validation devrait échouer si informations manquantes"
    print("✔ Gestion champs manquants OK")

    print("\n[TEST 3] Validation registration — mots de passe différents...")
    user = User(username="test", email="test@mail.com", password="Aa1!aaaa")
    ok, msg = validate_registration(user, "BBBB")
    assert not ok, "❌ Validation devrait échouer si password != confirm"
    print("✔ Gestion confirmation password OK")

    print("\n[TEST 4] Validation registration — email invalide...")
    user = User(username="user", email="invalid", password="Aa1!aaaa")
    ok, msg = validate_registration(user, "Aa1!aaaa")
    assert not ok, "❌ Email sans @ ou . accepté"
    print("✔ Validation email OK")

    print("\n[TEST 5] Validation registration — username existant...")
    username = unique("regtest")
    email = f"{username}@example.com"
    user1 = User(username=username, email=email, password="Aa1!aaaa")
    db.add_user(user1)

    user2 = User(username=username, email=f"new_{email}", password="Aa1!aaaa")
    ok, msg = validate_registration(user2, "Aa1!aaaa")
    assert not ok, "❌ Username dupliqué accepté"
    print("✔ Détection username existant OK")

    print("\n[TEST 6] Validation registration — email existant...")
    user3 = User(username=unique("another"), email=email, password="Aa1!aaaa")
    ok, msg = validate_registration(user3, "Aa1!aaaa")
    assert not ok, "❌ Email dupliqué accepté"
    print("✔ Détection email existant OK")

    print("\n[TEST 7] Registration valide...")
    valid_user = User(
        username=unique("newuser"),
        email=f"valid_{unique('mail')}@example.com",
        password="Aa1!aaaa"
    )
    ok, msg = validate_registration(valid_user, "Aa1!aaaa")
    assert ok, f"❌ Validation a échoué alors qu'elle devrait réussir : {msg}"
    print("✔ Registration valide OK")

    print("\n===== ✔ TOUS LES TESTS registration_airtable ONT RÉUSSI =====\n")
