
from users_db import UsersDatabase
from user import User
from posting import Post
from post_interactions import PostInteractions

def post_interactions_test():
    db = UsersDatabase()
    db.new_database()  

    # Create users
    alice = User("alice", "alice@email.com", "Pass123!", "Alice", 25, "USA")
    bob = User("bob", "bob@email.com", "Pass456!", "Bob", 30, "UK")
    charlie = User("charlie", "charlie@email.com", "Pass789!", "Charlie", 28, "France")
    db.add_user(alice)
    db.add_user(bob)
    db.add_user(charlie)

    # Bob creates a post
    post = Post("Hello world! My first post", bob.username, db)

    # Initialize interactions
    interactions = PostInteractions(db)

    print("\n--- Initial Post ---")
    interactions.show_post_details(post)

    # --- Test likes/unlikes ---
    interactions.toggle_like(post, "alice")      # Alice likes
    interactions.toggle_like(post, "charlie")    # Charlie likes
    interactions.toggle_like(post, "alice")      # Alice unlikes
    interactions.show_post_details(post)

    # --- Test comments ---
    interactions.write_comment(post, "alice", "Great post, Bob!")         # Alice comments
    interactions.write_comment(post, "charlie", "Welcome to TwINSA!")     # Charlie comments
    interactions.show_post_details(post)

    # Edit comment
    interactions.edit_comment(post, 1, "alice", "Really awesome post!")  # Alice edits her comment
    interactions.show_post_details(post)

    # Delete comment
    interactions.delete_comment(post, 2, "charlie")                        # Charlie deletes own comment
    interactions.show_post_details(post)

    # Delete comment by post owner
    interactions.delete_comment(post, 1, "bob")                            # Bob deletes Alice's comment
    interactions.show_post_details(post)

    # --- Test post deletion ---
    interactions.delete_post(post, "alice")  # Should fail (not owner)
    interactions.delete_post(post, "bob")    # Bob deletes his post
    interactions.show_post_details(post)     # Should show empty / removed

    # --- Test reports ---
    # Bob creates new post
    post2 = Post("Another post from Bob", bob.username, db)

    #interactions.report_post(post2, "alice")     # Alice reports
    #interactions.report_post(post2, "charlie")   # Charlie reports
    #interactions.report_post(post2, "alice")     # Alice reports again (should warn)
    #interactions.show_post_details(post2)

if __name__ == "__main__":
    post_interactions_test()
