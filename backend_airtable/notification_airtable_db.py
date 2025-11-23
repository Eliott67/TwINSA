from pyairtable import Table
from backend_airtable.notification_airtable import Notification
import backend_airtable.airtable_secrets as secrets


class AirtableNotificationsDB:

    def __init__(self, token, base_id):
        self.token = token
        self.base_id = base_id
        self.table_name = "notifications"
        self.table = Table(self.token, self.base_id, self.table_name)
    def add_notification(self, user_record_id: str, notif: Notification):
        fields = {
            "receiver": [user_record_id],   # <-- champ réel Airtable
            "message": notif.message,       # <-- champ réel Airtable
            "type": notif.notif_type,       # <-- champ existant aussi
        }

        # Ajouter dynamiquement extra (post/comment)
        for k, v in notif.extra.items():
            fields[k] = v

        rec = self.table.create(fields)
        notif.record_id = rec["id"]
        return rec

    def get_notifications_for_user(self, user_record_id: str):
        formula = f"FIND('{user_record_id}', ARRAYJOIN(receiver))"
        rows = self.table.all(formula=formula)
        return [Notification.from_dict(r["fields"]) for r in rows]