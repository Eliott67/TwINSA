# backend_airtable/feed_airtable.py

from backend_airtable.user_airtable_db import AirtableUsersDB
from backend_airtable.post_airtable_db import AirtablePostsDB
import backend_airtable.airtable_secrets as secrets


class FeedAirtable:
    """
    Affichage, édition et suppression des posts pour un utilisateur connecté.
    """

    def __init__(self, username_or_record_id: str):
        # initialise DBs (utilisent airtable_secrets)
        self.users_db = AirtableUsersDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)
        self.posts_db = AirtablePostsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)

        # current user can be username or record_id
        self.current_user = self.users_db.get_user(username_or_record_id)
        if not self.current_user:
            raise ValueError(f"User '{username_or_record_id}' not found.")

        # load visible posts
        self.posts = self.posts_db.get_all_posts()

    def show_feed(self):
        if not self.posts:
            print("\nNo posts available.")
            return

        print("\n----- FEED -----")
        sorted_posts = sorted(self.posts, key=lambda p: p.date or "", reverse=True)

        for idx, post in enumerate(sorted_posts):
            owner_username = self.users_db.record_id_to_username(post.owner_record_id) or "unknown"
            print(f"\n[{idx}] {owner_username} — {post.date}")
            print(f"   {post.content}")
            print(f"   Likes: {len(post.likes)} | Comments: {len(post.Comments)}")
        print("\n----------------\n")

    def edit_post(self, index: int, new_content: str):
        post = self.posts[index]
        if post.owner_record_id != (self.current_user.record_id):
            print("❌ You can only edit your own posts.")
            return

        post.content = new_content
        self.posts_db.update_post(post)
        print("✅ Post updated.")

    def delete_post(self, index: int):
        post = self.posts[index]
        if post.owner_record_id != (self.current_user.record_id):
            print("❌ You can only delete your own posts.")
            return

        confirm = input("Delete this post? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled.")
            return

        self.posts_db.delete_post(post.record_id)
        print("🗑️ Post deleted.")
        self.posts = self.posts_db.get_all_posts()

    @staticmethod
    def build_feed():
        from backend_airtable.post_airtable_db import AirtablePostsDB
        import backend_airtable.airtable_secrets as secrets

        db = AirtablePostsDB(secrets.AIRTABLE_TOKEN, secrets.AIRTABLE_BASE_ID)
        records = db.table.all()

        feed = []
        for rec in records:
            fields = rec.get("fields", {})
            feed.append({
                "id": rec["id"],
                "owner_record_id": fields.get("owner_record_id"),
                "content": fields.get("content")
            })

        return feed