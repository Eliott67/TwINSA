from users_db import UsersDatabase
from user import User
from posting import Post
from datetime import datetime

class PostInteractions:
  
    def __init__(self, database: UsersDatabase):
        self.db = database

    # Comment a post
    def write_comment(self, post: Post, commenter_username: str, comment_text: str):
        commenter = self.db.get_user(commenter_username)
        if not commenter:
            print("User not found.")
            return

        post.add_comment(commenter_username, comment_text)
        print(f" {commenter_username} commented: “{comment_text}” on {post.poster_username}'s post.")

    # Edit a comment
    def edit_comment(self, post: Post, comment_id: int, editor_username: str, new_text: str):
        post.edit_comment(comment_id, new_text, editor_username)
        print(f"{editor_username} edited comment #{comment_id} on {post.poster_username}'s post.")

    # Delete a comment
    def delete_comment(self, post: Post, comment_id: int, deleter_username: str):
        """Deletes a comment (if it's theirs or on their post)."""
        post.remove_comment(comment_id, deleter_username)
        print(f" Comment #{comment_id} deleted by {deleter_username} on {post.poster_username}'s post.")

    # Like or unlike a post
    def toggle_like(self, post: Post, liker_username: str):
        """Adds or removes a like."""
        if liker_username in post.likes:
            post.remove_like(liker_username)
            print(f" {liker_username} removed their like from {post.poster_username}'s post.")
        else:
            post.add_like(liker_username)
            print(f" {liker_username} liked {post.poster_username}'s post.")

    # Delete a post
    def delete_post(self, post: Post, deleter_username: str):
        if deleter_username == post.poster_username:
            user = self.db.get_user(deleter_username)
            user.delete_post(post)  
            print(f"{deleter_username} deleted their post.")
        else:
            print("You can only delete your own posts.")

    # Report a post
    #def report_post(self, post: Post, reporter_username: str):
    #    """Reports a post."""
     #   if reporter_username not in post.reports:
      #      post.report_post(reporter_username)
       #     print(f" {reporter_username} reported {post.poster_username}'s post.")
       # else:
        #    print(" You have already reported this post.")

    # Display post details
    def show_post_details(self, post: Post):
        """Displays all information about the post."""
        print("\n--- POST DETAILS ---")
        print(f"Author      : {post.poster_username}")
        print(f"Date        : {post.date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Content     : {post.content}")
        print(f"Likes       : {len(post.likes)} ({', '.join(post.likes) if post.likes else 'none'})")
        #print(f"Reports     : {len(post.reports)}")
        print(f"Comments ({len(post.comments)}):")
        for c in post.comments:
            print(f"  - [{c['id']}] {c['username']} ({c['date']}): {c['comment']}")
        print("--------------------\n")


