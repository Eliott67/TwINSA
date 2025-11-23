# backend_airtable/post_airtable_db.py

from pyairtable import Table
from backend_airtable.posts_airtable import PostAirtable
import backend_airtable.airtable_secrets as secrets


class AirtablePostsDB:
    def __init__(self, airtable_token=None, base_id=None, table_name="Posts"):
        self.api_key = airtable_token or getattr(secrets, "AIRTABLE_TOKEN", None)
        self.base_id = base_id or getattr(secrets, "AIRTABLE_BASE_ID", None)
        self.table_name = table_name

        if not self.api_key or not self.base_id:
            raise ValueError("Airtable token and base_id must be provided.")

        self.table = Table(self.api_key, self.base_id, self.table_name)

    def add_post(self, post: PostAirtable):
        record = self.table.create(post.to_dict_linked())
        post.record_id = record["id"]
        return record

    def get_post(self, record_id: str):
        rec = self.table.get(record_id)
        return PostAirtable.from_dict(rec["fields"], rec["id"])

    def get_posts_by_user(self, user_record_id: str):
        formula = f"SEARCH('{user_record_id}', ARRAYJOIN({{poster}}))"
        records = self.table.all(formula=formula)
        return [PostAirtable.from_dict(r["fields"], r["id"]) for r in records]

    def update_post_fields(self, record_id: str, fields: dict):
        """
        Mise à jour partielle d’un post.
        """
        return self.table.update(record_id, fields)

    def get_all_posts(self):
        records = self.table.all()
        return [PostAirtable.from_dict(r["fields"], r["id"]) for r in records]

    def update_post(self, post: PostAirtable):
        if not post.record_id:
            raise ValueError("Post must have record_id to update.")
        return self.table.update(post.record_id, post.to_dict_linked())

    def delete_post(self, record_id: str):
        return self.table.delete(record_id)
    
# ======================================================================
#   UNIT TESTS — exécutés uniquement si ce fichier est lancé directement
# ======================================================================

if __name__ == "__main__":
    print("\n===== TESTS UNITAIRES : post_airtable_db =====\n")

    import types
    from backend_airtable.post_airtable_db import AirtablePostsDB
    from backend_airtable.posts_airtable import PostAirtable

    # -------------------------------------------------------------------
    # Fake Airtable Table (mock complet)
    # -------------------------------------------------------------------
    class FakeTable:
        def __init__(self):
            self.storage = {}
            self.counter = 1

        def create(self, data):
            rec_id = f"rec_{self.counter}"
            self.counter += 1
            self.storage[rec_id] = {"id": rec_id, "fields": data}
            return self.storage[rec_id]

        def get(self, rec_id):
            return self.storage.get(rec_id)

        def all(self, formula=None):
            # simple version : ignore formula
            return list(self.storage.values())

        def update(self, rec_id, data):
            if rec_id not in self.storage:
                raise KeyError("Record not found")
            self.storage[rec_id]["fields"].update(data)
            return self.storage[rec_id]

        def delete(self, rec_id):
            if rec_id in self.storage:
                del self.storage[rec_id]
                return {"deleted": True}
            return {"deleted": False}

    # -------------------------------------------------------------------
    # Patch de pyairtable.Table pour utiliser FakeTable
    # -------------------------------------------------------------------
    import backend_airtable.post_airtable_db as module
    module.Table = lambda *args, **kwargs: FakeTable()

    # -------------------------------------------------------------------
    # Initialisation DB mockée
    # -------------------------------------------------------------------
    db = AirtablePostsDB(
        airtable_token="TEST_TOKEN",
        base_id="TEST_BASE"
    )

    print("[TEST 1] Ajout d’un post...")
    post = PostAirtable("recUser1", "Hello world!", images=["img1.png"])
    rec = db.add_post(post)

    assert post.record_id == rec["id"]
    assert rec["fields"]["content"] == "Hello world!"
    print("✔ add_post OK")

    # -------------------------------------------------------------------
    print("\n[TEST 2] Récupération d’un post par ID...")
    fetched = db.get_post(post.record_id)
    assert fetched.owner_record_id == "recUser1"
    assert fetched.content == "Hello world!"
    print("✔ get_post OK")

    # -------------------------------------------------------------------
    print("\n[TEST 3] Récupération des posts d’un user...")
    posts_user = db.get_posts_by_user("recUser1")
    assert len(posts_user) == 1
    assert posts_user[0].content == "Hello world!"
    print("✔ get_posts_by_user OK")

    # -------------------------------------------------------------------
    print("\n[TEST 4] Récupération de tous les posts...")
    all_posts = db.get_all_posts()
    assert len(all_posts) == 1
    print("✔ get_all_posts OK")

    # -------------------------------------------------------------------
    print("\n[TEST 5] Mise à jour d’un post...")
    post.content = "Updated content"
    updated = db.update_post(post)
    assert updated["fields"]["content"] == "Updated content"
    print("✔ update_post OK")

    # -------------------------------------------------------------------
    print("\n[TEST 6] Suppression d’un post...")
    result = db.delete_post(post.record_id)
    assert result["deleted"] is True
    assert len(db.table.storage) == 0
    print("✔ delete_post OK")

    print("\n===== ✔ TOUS LES TESTS post_airtable_db ONT RÉUSSI =====\n")