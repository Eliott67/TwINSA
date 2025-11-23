# backend_airtable/posts_airtable.py

from datetime import datetime
from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.notification_airtable import NotificationFactory


class PostAirtable:
    """
    Post model. Linked fields are record IDs.
    """

    def __init__(
        self,
        owner_record_id,
        content: str,
        images=None,
        date=None,
        likes=None,
        Comments=None,
        Notifications=None,
        post_id=None,
    ):
        self.db = AirtableUsersDB()
        self.owner_record_id = owner_record_id  # record id of poster
        self.content = content
        self.images = images or []
        self.date = date if date else datetime.now()
        self.likes = likes or []         # list of user record_ids
        self.Comments = Comments or []   # list of comment record_ids
        self.Notifications = Notifications or []  # list of notification record_ids
        self.post_id = post_id           # custom post_id if used
        self.record_id = None            # airtable record id

    # create local post and optionally persist via posts DB
    @staticmethod
    def create(owner_record_id, content, images=None):
        post = PostAirtable(owner_record_id, content, images=images)
        return post

    def add_like(self, liker_record_id):
        if liker_record_id not in self.likes:
            self.likes.append(liker_record_id)
            # create notification for owner
            owner = self.db.get_user_by_record_id(self.owner_record_id)
            if owner:
                notif = NotificationFactory.create_like_notif(owner, self)
                owner.notifications.append(notif.to_dict())
                self.db.update_user(owner)  # persist notification in user record (if you store it there)

    def add_comment_local(self, comment_record_id):
        self.Comments.append(comment_record_id)

    def to_dict_linked(self):
        """Return dict suitable for Airtable Posts table: poster expects a linked record id list."""
        return {
            "poster": [self.owner_record_id] if self.owner_record_id else [],
            "content": self.content,
            "images": self.images,
        }

    @staticmethod
    def from_dict(fields: dict, record_id: str):
        # poster comes as list of record ids
        poster_list = fields.get("poster", []) or []
        poster_rec = poster_list[0] if poster_list else None

        date_str = fields.get("date")
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                date = None
        else:
            date = None


        post = PostAirtable(
            owner_record_id=poster_rec,
            content=fields.get("content", ""),
            images=fields.get("images", []),
            date=date,
            likes=fields.get("likes", []),
            Comments=fields.get("Comments", []),
            Notifications=fields.get("Notifications", []),
            post_id=fields.get("post_id"),
        )
        post.record_id = record_id
        return post
    
# ======================================================================
#   UNIT TESTS — exécutés uniquement si ce fichier est lancé directement
# ======================================================================

if __name__ == "__main__":
    print("\n===== TESTS UNITAIRES : posts_airtable =====\n")
    from backend_airtable.posts_airtable import PostAirtable
    from datetime import datetime

    # Utilitaire pour générer des valeurs uniques
    import time
    def unique(prefix):
        return f"{prefix}_{int(time.time())}"

    # ---------------------------------------------------------
    print("[TEST 1] Création d’un post...")
    owner = "recOWNER123"
    p = PostAirtable.create(owner, "Hello world!", images=["img1.png"])
    assert p.owner_record_id == owner
    assert p.content == "Hello world!"
    assert p.images == ["img1.png"]
    assert isinstance(p.date, datetime)
    assert p.likes == []
    assert p.Comments == []
    assert p.Notifications == []
    print("✔ Création OK")

    # ---------------------------------------------------------
    print("\n[TEST 2] Ajout d’un like (local)...")
    liker = "recLIKE123"
    p.add_like(liker)
    assert liker in p.likes, "❌ Le like n’a pas été ajouté correctement"
    print("✔ Like local OK")

    # ---------------------------------------------------------
    print("\n[TEST 3] Ajout d’un commentaire (local)...")
    comment_id = "recCOMMENT123"
    p.add_comment_local(comment_id)
    assert comment_id in p.Comments, "❌ Le commentaire n’a pas été ajouté"
    print("✔ Commentaire local OK")

    # ---------------------------------------------------------
    print("\n[TEST 4] Sérialisation vers Airtable (to_dict_linked)...")
    d = p.to_dict_linked()
    assert d["poster"] == [owner]
    assert d["content"] == "Hello world!"
    assert d["images"] == ["img1.png"]
    assert d["likes"] == [liker]
    assert d["Comments"] == [comment_id]
    print("✔ to_dict_linked OK")

    # ---------------------------------------------------------
    print("\n[TEST 5] Désérialisation depuis Airtable (from_dict)...")
    fields = {
        "poster": [owner],
        "content": "Reconstructed",
        "images": ["imgA.png"],
        "date": "2024-01-01 12:00:00",
        "likes": ["recX"],
        "Comments": ["recC"],
        "Notifications": ["recN"],
        "post_id": "POST42"
    }
    reconstructed = PostAirtable.from_dict(fields, record_id="recPOST999")

    assert reconstructed.record_id == "recPOST999"
    assert reconstructed.owner_record_id == owner
    assert reconstructed.content == "Reconstructed"
    assert reconstructed.images == ["imgA.png"]
    assert reconstructed.likes == ["recX"]
    assert reconstructed.Comments == ["recC"]
    assert reconstructed.Notifications == ["recN"]
    assert reconstructed.post_id == "POST42"
    print("✔ from_dict OK")

    print("\n===== ✔ TOUS LES TESTS posts_airtable ONT RÉUSSI =====\n")