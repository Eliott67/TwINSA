# backend_airtable/user_airtable.py

from datetime import datetime


class User:
    """
    Modèle User compatible Airtable.
    Aucun import vers Notification, Posts ou Comments -> évite les circular imports.
    """

    def __init__(
        self,
        username,
        email,
        password,
        name=None,
        age=None,
        country=None,
        is_public=True,
        followers=None,
        following=None,
        pending_requests=None,
        blocked_users=None,
        posts=None,
        comments=None,
        profile_picture=None,
        record_id=None
    ):
        self.record_id = record_id

        self.username = username
        self.email = email
        self._password = password  # stockage interne

        self.name = name
        self.age = age
        self.country = country
        self.is_public = is_public

        # linked records (list of record IDs)
        self.followers = followers or []
        self.following = following or []
        self.pending_requests = pending_requests or []
        self.blocked_users = blocked_users or []
        self.posts = posts or []
        self.comments = comments or []

        self.profile_picture = profile_picture

    # ---------------------------
    # PASSWORD ACCESSORS
    # ---------------------------
    def get_password(self):
        return self._password
    @property
    def password(self):
        return self._password

    # ---------------------------
    # SERIALIZATION
    # ---------------------------
    def to_dict_linked(self):
        """
        Format EXACT attendu par Airtable pour créer / update.
        Les champs linkés doivent être sous forme de LISTES de record IDs.
        """
        data = {
            "username": self.username,
            "email": self.email,
            "password": self._password,
            "name": self.name,
            "age": self.age,
            "country": self.country,
            "is_public": self.is_public,
            "profile_picture": self.profile_picture,
        }

        # On retire les None (car Airtable n'aime pas)
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_airtable(cls, record):
        fields = record["fields"]
        return cls(
            username=fields.get("username"),
            email=fields.get("email"),
            password=fields.get("password"),  # ou None si tu ne stockes pas le password
        )

    def change_password(self, old_password: str, new_password: str):
        # comparer avec attribut privé
        if self.get_password() != old_password:
            return False

        # mettre à jour l’objet
        self.set_password(new_password)

        # mettre à jour dans airtable
        if self.record_id:
            from backend_airtable.user_airtable_db import AirtableUsersDB
            import backend_airtable.airtable_secrets as secrets
            db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)
            db.update_user_fields(self.record_id, {"password": new_password})

        print("✅ Mot de passe changé avec succès.")
        return True

    @staticmethod
    def from_dict(data, record_id=None):
        if not data:
            return None

        return User(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            name=data.get("name"),
            age=data.get("age"),
            country=data.get("country"),
            is_public=data.get("is_public", True),

            followers=data.get("followers", []),
            following=data.get("following", []),
            pending_requests=data.get("pending_requests", []),
            blocked_users=data.get("blocked_users", []),

            posts=data.get("Posts", []),          # colonne Airtable réelle
            comments=data.get("Comments", []),    # colonne Airtable réelle

            profile_picture=data.get("profile_picture"),
            record_id=record_id
        )

# ---------------------------------------------------------------------------
# ----------------------------- UNIT TESTS ----------------------------------
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running tests for user_airtable.py...\n")

    def assert_equal(a, b, msg=""):
        if a != b:
            raise AssertionError(f"{msg} Expected {b}, got {a}")
    
    # --------------------------------------------------------
    # TEST 1 — Minimal creation
    # --------------------------------------------------------
    user = User(username="john", email="john@test.com", password="123")

    assert_equal(user.username, "john", "username mismatch")
    assert_equal(user.email, "john@test.com", "email mismatch")
    assert_equal(user.get_password(), "123", "password mismatch")

    assert_equal(user.followers, [], "followers must be empty list")
    assert_equal(user.following, [], "following must be empty list")
    assert_equal(user.pending_requests, [], "pending_requests must be empty")
    assert_equal(user.blocked_users, [], "blocked_users must be empty")
    assert_equal(user.posts, [], "posts must be empty")
    assert_equal(user.comments, [], "comments must be empty")

    print("✓ Test 1 passed")

    # --------------------------------------------------------
    # TEST 2 — to_dict_linked basic serialization
    # --------------------------------------------------------
    user = User(
        username="alice",
        email="alice@test.com",
        password="secret",
        age=25,
        country="FR",
        is_public=False,
        posts=["recPost1"],
        followers=["recUserX"]
    )

    d = user.to_dict_linked()

    assert_equal(d["username"], "alice")
    assert_equal(d["email"], "alice@test.com")
    assert_equal(d["password"], "secret")
    assert_equal(d["age"], 25)
    assert_equal(d["country"], "FR")
    assert_equal(d["is_public"], False)
    assert_equal(d["Posts"], ["recPost1"])
    assert_equal(d["followers"], ["recUserX"])

    # must not contain None values
    assert "name" not in d
    assert "record_id" not in d

    print("✓ Test 2 passed")

    # --------------------------------------------------------
    # TEST 3 — to_dict_linked removes Nones
    # --------------------------------------------------------
    user = User(username="bob", email="bob@test.com", password="pwd")
    d = user.to_dict_linked()

    assert "name" not in d
    assert "country" not in d
    assert "profile_picture" not in d

    print("✓ Test 3 passed")

    # --------------------------------------------------------
    # TEST 4 — from_dict deserialization
    # --------------------------------------------------------
    data = {
        "username": "mike",
        "email": "mike@mail.com",
        "password": "pwd",
        "country": "UK",
        "Posts": ["recP1", "recP2"],
        "followers": ["recF1"]
    }

    user = User.from_dict(data, record_id="recU1")

    assert_equal(user.record_id, "recU1")
    assert_equal(user.username, "mike")
    assert_equal(user.email, "mike@mail.com")
    assert_equal(user.get_password(), "pwd")
    assert_equal(user.country, "UK")
    assert_equal(user.posts, ["recP1", "recP2"])
    assert_equal(user.followers, ["recF1"])
    assert_equal(user.comments, [], "Missing comments should default to empty")

    print("✓ Test 4 passed")

    # --------------------------------------------------------
    # TEST 5 — Round-trip to_dict → from_dict
    # --------------------------------------------------------
    original = User(
        username="testuser",
        email="t@t.com",
        password="pass",
        name="John",
        age=30,
        country="FR",
        is_public=True,
        followers=["rec1"],
        following=["rec2"],
        pending_requests=["rec3"],
        blocked_users=["rec4"],
        posts=["post1"],
        comments=["com1"],
        profile_picture="http://img"
    )

    d = original.to_dict_linked()
    reconstructed = User.from_dict(d, record_id="recUser1")

    assert_equal(reconstructed.username, original.username)
    assert_equal(reconstructed.email, original.email)
    assert_equal(reconstructed.get_password(), original.get_password())
    assert_equal(reconstructed.name, original.name)
    assert_equal(reconstructed.age, original.age)
    assert_equal(reconstructed.country, original.country)
    assert_equal(reconstructed.is_public, original.is_public)
    assert_equal(reconstructed.profile_picture, original.profile_picture)

    assert_equal(reconstructed.followers, original.followers)
    assert_equal(reconstructed.following, original.following)
    assert_equal(reconstructed.pending_requests, original.pending_requests)
    assert_equal(reconstructed.blocked_users, original.blocked_users)
    assert_equal(reconstructed.posts, original.posts)
    assert_equal(reconstructed.comments, original.comments)

    print("✓ Test 5 passed")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY for user_airtable.py!")
