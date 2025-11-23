# backend_airtable/notification_airtable.py

from datetime import datetime


class Notification:
    """
    Objet notification compatible Airtable.
    Ne dépend d’aucune autre classe (pas d'import User/Post pour éviter les circular imports).
    """
    def __init__(self, notif_type, sender_rec=None, message="", timestamp=None, extra=None):
        self.notif_type = notif_type
        self.sender = sender_rec              # record_id du sender
        self.message = message
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.extra = extra or {}              # ex : {"post": ["rec..."], "comment": ["rec..."]}

    @property
    def content(self):
        return self.message

    @content.setter
    def content(self, value):
        self.message = value


    def to_dict(self):
        return {
            "type": self.notif_type,
            "sender": [self.sender] if self.sender else [],
            "message": self.message,
            **self.extra
        }

    @staticmethod
    def from_dict(data):
        if not data:
            return None

        sender = None
        if "sender" in data and isinstance(data["sender"], list) and data["sender"]:
            sender = data["sender"][0]

        extra = {
            k: v for k, v in data.items()
            if k not in ("type", "sender", "message", "timestamp")
        }

        return Notification(
            notif_type=data.get("type"),
            sender_rec=sender,
            message=data.get("message"),
            timestamp=data.get("timestamp"),
            extra=extra
        )

    @staticmethod
    def get_notifications(user_record_id: str):
        from backend_airtable.notification_airtable_db import AirtableNotificationsDB
        import backend_airtable.airtable_secrets as secrets

        db = AirtableNotificationsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

        # Récupération des notifications filtrées par receiver = user_record_id
        records = db.get_notifications_for_user(user_record_id)

        # On convertit les records Airtable → objets Notification
        notifs = []
        for rec in records:
            fields = rec.get("fields", {})
            notif = Notification(
                notif_type=fields.get("type"),
                message=fields.get("message")
            )
            notif.record_id = rec.get("id")
            notifs.append(notif)

        return notifs

    @staticmethod
    def create_notification(user_record_id: str, content: str):
        """
        Méthode exigée par les tests.
        Crée une notification simple et la stocke dans Airtable.
        """
        from backend_airtable.notification_airtable_db import AirtableNotificationsDB
        import backend_airtable.airtable_secrets as secrets

        db = AirtableNotificationsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

        notif = Notification(
            notif_type="NewFollower",
            sender_rec=None,
            message=content
        )

        rec = db.add_notification(user_record_id, notif)
        return rec["id"]


class NotificationFactory:
    """
    Fabrique de notifications.
    N’utilise PLUS PostAirtable ou User directement → uniquement record_id.
    """

    @staticmethod
    def create_follow_request(sender_user, target_user):
        return Notification(
            notif_type="follow_request",
            sender_rec=sender_user.record_id,
            message=f"{sender_user.username} wants to follow you.",
        )

    @staticmethod
    def create_new_follower(sender_user, target_user):
        return Notification(
            notif_type="new_follower",
            sender_rec=sender_user.record_id,
            message=f"{sender_user.username} is now following you!",
        )

    @staticmethod
    def create_like_notif(sender_user, post_record_id):
        return Notification(
            notif_type="post_like",
            sender_rec=sender_user.record_id,
            message=f"{sender_user.username} liked your post.",
            extra={"post": [post_record_id] if post_record_id else []}
        )

    @staticmethod
    def create_comment_notif(sender_user, post_record_id, comment_record_id):
        return Notification(
            notif_type="post_comment",
            sender_rec=sender_user.record_id,
            message=f"{sender_user.username} commented on your post.",
            extra={
                "post": [post_record_id] if post_record_id else [],
                "comment": [comment_record_id]
            }
        )

# ======================================================================
#   UNIT TESTS — exécutés uniquement si on lance ce fichier directement
# ======================================================================

if __name__ == "__main__":
    print("\n===== TESTS UNITAIRES : notification_airtable =====\n")

    def check(cond, msg):
        if cond:
            print("✔", msg)
        else:
            raise AssertionError("❌ " + msg)

    # -------------------------------------------------------------
    # 1) TEST : Notification simple
    # -------------------------------------------------------------
    print("\n[TEST 1] Notification basic fields")
    notif = Notification("test_type", sender_rec="recSender", message="Hello")

    check(notif.notif_type == "test_type", "Type correct")
    check(notif.sender == "recSender", "Sender correct")
    check(notif.message == "Hello", "Message correct")

    d = notif.to_dict()
    check(d["type"] == "test_type", "to_dict type correct")
    check(d["sender"] == ["recSender"], "to_dict sender en liste")
    check("timestamp" in d, "timestamp présent")

    # -------------------------------------------------------------
    # 2) TEST : from_dict()
    # -------------------------------------------------------------
    print("\n[TEST 2] from_dict() reconstructs Notification")
    data = {
        "type": "comment",
        "sender": ["rec123"],
        "message": "Nice!",
        "timestamp": "2024-01-01T10:00:00",
        "post": ["recPost1"],
        "comment": ["recCom1"]
    }

    notif2 = Notification.from_dict(data)
    check(notif2.notif_type == "comment", "type ok")
    check(notif2.sender == "rec123", "sender ok")
    check(notif2.extra["post"] == ["recPost1"], "post extra ok")
    check(notif2.extra["comment"] == ["recCom1"], "comment extra ok")

    # -------------------------------------------------------------
    # 3) TEST : NotificationFactory follow request
    # -------------------------------------------------------------
    print("\n[TEST 3] NotificationFactory.create_follow_request()")
    class DummyUser:  # user mock
        def __init__(self, username, record_id):
            self.username = username
            self.record_id = record_id

    alice = DummyUser("alice", "recAlice")
    bob = DummyUser("bob", "recBob")

    notif3 = NotificationFactory.create_follow_request(alice, bob)
    check(notif3.notif_type == "follow_request", "type correct")
    check("wants to follow you" in notif3.message, "message correct")

    # -------------------------------------------------------------
    # 4) TEST : like notif
    # -------------------------------------------------------------
    print("\n[TEST 4] NotificationFactory.create_like_notif()")
    notif4 = NotificationFactory.create_like_notif(alice, "recPostX")

    check(notif4.notif_type == "post_like", "type ok")
    check(notif4.extra["post"] == ["recPostX"], "linked post correct")

    # -------------------------------------------------------------
    # 5) TEST : comment notif
    # -------------------------------------------------------------
    print("\n[TEST 5] NotificationFactory.create_comment_notif()")
    notif5 = NotificationFactory.create_comment_notif(
        alice, "recPostY", "recCommentZ"
    )

    check(notif5.extra["post"] == ["recPostY"], "post link OK")
    check(notif5.extra["comment"] == ["recCommentZ"], "comment link OK")

    # -------------------------------------------------------------
    # FIN DES TESTS
    # -------------------------------------------------------------
    print("\n===== ✔ TOUS LES TESTS notification_airtable ONT RÉUSSI =====\n")
