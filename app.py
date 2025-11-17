import os
import sys
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

# --- Make backend importable ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# --- Imports from backend ---
from backend.users_db import UsersDatabase
from backend.user import User
from backend.change_password import SecureUser
from backend.registration import validate_registration
from backend.posting import Post
from backend.editing_profile import update_personal_info, delete_account  # ✅ Ajout pour profil

app = Flask(__name__)
app.secret_key = "super_secret_key"

# --- Load database ---
db = UsersDatabase("backend/users_database.json")

# --- Posts file ---
POSTS_FILE = "posts.json"


# === Helper functions ===
def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, default=str)


def get_secure_user(username):
    """Convert backend user object into a SecureUser"""
    user_obj = db.get_user(username)
    if not user_obj:
        return None
    return SecureUser(
        username=user_obj.username,
        email=user_obj.email,
        password=user_obj.get_password(),
        name=user_obj.name,
        age=user_obj.age,
        country=user_obj.country
    )


# === ROUTES ===

@app.route("/")
def home():
    return render_template("home.html", username=session.get("username"))


# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if db.authenticate_user(username, password):
            session["username"] = username
            flash("Signed in successfully!", "success")
            return redirect(url_for("feed"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# --- REGISTER ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # New: read the toggle
        is_public_raw = request.form.get("is_public")  # "on" if checked, None if not
        is_public = bool(is_public_raw)  # True = public, False = private

        new_user = User(username, email, password, name="", age=0, country="")

        # Set the visibility flag on the user object
        new_user.is_public = is_public

        valid, msg = validate_registration(new_user, confirm_password)
        if not valid:
            flash(msg, "error")
            return redirect(url_for("register"))

        try:
            db.add_user(new_user)
            session["username"] = new_user.username
            flash("Account created successfully!", "success")
            return redirect(url_for("suggestions"))
        except ValueError:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")



# --- FORGOT PASSWORD ---
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        user_found = None
        for user_obj in db.get_all_users():
            if user_obj.email == email:
                user_found = user_obj
                break

        if not user_found:
            flash("Email not found.", "error")
            return redirect(url_for("forgot_password"))

        su = SecureUser(
            username=user_found.username,
            email=user_found.email,
            password=user_found.get_password(),
            name=user_found.name,
            age=user_found.age,
            country=user_found.country
        )
        su.generate_reset_token()
        print(f"[DEBUG] Reset token for {email}: {su.reset_token}")
        flash("Password reset code sent (check console).", "success")
        return redirect(url_for("home"))

    return render_template("forgot_password.html")


# --- FEED (POSTS) ---
@app.route("/feed", methods=["GET", "POST"])
def feed():
    if "username" not in session:
        flash("Please sign in to access TwINSA.", "error")
        return redirect(url_for("login"))

    posts = load_posts()
    username = session["username"]
    current_user = db.get_user(username)

    if request.method == "POST":
        content = request.form.get("tweet", "").strip()
        if not content:
            flash("Post cannot be empty!", "error")
            return redirect(url_for("feed"))

        # Crée un nouvel objet Post
        new_post = Post(content, session["username"], db)

        post_data = {
            "poster_username": new_post.poster_username,
            "content": new_post.content,
            "date": new_post.date.strftime("%Y-%m-%d %H:%M:%S"),
            "likes": new_post.likes,
            "comments": []
        }
        posts.insert(0, post_data)
        current_user.add_post(new_post)
        db.save_users()
        save_posts(posts)
        flash("Post created successfully!", "success")
        return redirect(url_for("feed"))
    
    # 🔎 Filter posts: only from me or people I follow
    visible_posts = posts
    if current_user is not None:
        # set of usernames whose posts I want to see
        allowed_usernames = set(current_user.following + [username])
        visible_posts = [
            p for p in posts
            if p.get("poster_username") in allowed_usernames
        ]
    
    # Last 20 notifications
    notifications = []
    if current_user is not None and hasattr(current_user, "notifications"):
        notifications = list(current_user.notifications)[-20:]
        notifications.reverse()

    return render_template("feed.html", username=session["username"], tweets=visible_posts,notifications=notifications)

# --- NOTIFICATIONS PAGE ---
@app.route("/notifications")
def notifications():
    if "username" not in session:
        flash("Please sign in to view notifications.", "error")
        return redirect(url_for("login"))

    username = session["username"]
    current_user = db.get_user(username)

    # Last 20 notifications
    notifications = []
    if current_user is not None and hasattr(current_user, "notifications"):
        notifications = list(current_user.notifications)[-20:]
        notifications.reverse()

    # Pending follow requests for the logged-in user
    pending_requests = []
    if current_user is not None and hasattr(current_user, "pending_requests"):
        pending_requests = current_user.pending_requests


    return render_template(
        "notifications.html",
        username=username,
        notifications=notifications,
        pending_requests=pending_requests
    )


# --- LIKE A POST ---
@app.route("/like/<int:post_index>")
def like(post_index):
    if "username" not in session:
        return redirect(url_for("login"))

    
    posts = load_posts()
    if 0 <= post_index < len(posts):
        post = posts[post_index]
        username = session["username"]

        # Was it already liked?
        already_liked = username in post["likes"]

        if already_liked:
            # Unlike
            post["likes"].remove(username)
        else:
            # New like
            post["likes"].append(username)

            # 🔔 Notify the owner of the post (if it's not yourself)
            owner_username = post.get("poster_username")
            if owner_username and owner_username != username:
                owner = db.get_user(owner_username)
                if owner is not None and hasattr(owner, "notifications"):
                    # Short preview of the post content
                    preview = post.get("content", "")
                    if len(preview) > 40:
                        preview = preview[:40] + "…"
                    owner.notifications.append(
                        f"{username} liked your post: \"{preview}\""
                    )
                    db.save_users()  # persist notifications

        save_posts(posts)
    
    return redirect(url_for("feed"))



# --- COMMENT ON A POST ---
@app.route("/comment/<int:post_index>", methods=["POST"])
def comment(post_index):
    if "username" not in session:
        return redirect(url_for("login"))

    posts = load_posts()
    if 0 <= post_index < len(posts):
        comment_text = request.form.get("comment", "").strip()
        if comment_text:
            username = session["username"]
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            comment = {"username": username, "comment": comment_text, "date": now}

            if "comments" not in posts[post_index]:
                posts[post_index]["comments"] = []
            posts[post_index]["comments"].append(comment)
            save_posts(posts)

            # 🔔 Notify the owner of the post (if commenter != owner)
            owner_username = posts[post_index].get("poster_username")
            if owner_username and owner_username != username:
                owner = db.get_user(owner_username)
                if owner is not None and hasattr(owner, "notifications"):
                    short = comment_text if len(comment_text) <= 40 else comment_text[:40] + "…"
                    owner.notifications.append(
                        f"{username} commented on your post: \"{short}\""
                    )
                    db.save_users()                    
    return redirect(url_for("feed"))



# --- DELETE A COMMENT ---
@app.route("/delete_comment/<int:post_index>/<int:comment_index>")
def delete_comment(post_index, comment_index):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    posts = load_posts()

    if 0 <= post_index < len(posts):
        comments = posts[post_index].get("comments", [])
        if 0 <= comment_index < len(comments):
            comment = comments[comment_index]
            # Seul l’auteur du commentaire peut le supprimer
            if comment["username"] == username:
                comments.pop(comment_index)
                posts[post_index]["comments"] = comments
                save_posts(posts)
                flash("Comment deleted successfully.", "success")

    return redirect(url_for("feed"))


# --- PROFILE PAGE ---
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if "username" not in session:
        flash("Please sign in to access your profile.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])  # connecté
    user = db.get_user(username)  # profil à afficher
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("feed")) 
    can_view = user.is_public or current_user.follows(user) or user.username == current_user.username

    if user.username == current_user.username and request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.age = int(request.form.get("age", user.age or 0)) if request.form.get("age") else user.age
        user.country = request.form.get("country", user.country)
        db.save_users()
        flash("Profile updated successfully!", "success")

    return render_template("profile.html", user=user, current_user=current_user, can_view=can_view)


# --- DELETE ACCOUNT ---
@app.route("/delete_account", methods=["POST"])
def delete_account_route():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    password = request.form.get("password")

    user = db.get_user(username)
    if user and user.get_password() == password:
        db.remove_user(username)
        session.pop("username", None)
        flash("Account deleted successfully.", "success")
        return redirect(url_for("home"))
    else:
        flash("Incorrect password.", "error")
        return redirect(url_for("profile", username=session["username"]))

# --- SEARCH USERS ---
@app.route("/search", methods=["GET", "POST"])
def search_users():
    if "username" not in session:
        flash("Please sign in to access search.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])

    # Historique de recherche stocké dans la session
    if "search_history" not in session:
        session["search_history"] = []

    results = []

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            all_users = db.get_all_users()
            # Recherche par prefixe (insensible à la casse)
            matches = [u for u in all_users if u.username.lower().startswith(query.lower())]

            # Trier : d'abord les suivis, puis alphabétique
            matches.sort(key=lambda u: (not current_user.follows(u), u.username.lower()))
            results = matches[:10]

            # Mettre à jour l'historique
            if query not in session["search_history"]:
                session["search_history"].insert(0, query)
            session["search_history"] = session["search_history"][:5]
            session.modified = True  # pour que Flask enregistre la session

    return render_template(
        "search.html",
        current_user=current_user,
        results=results,
        history=session.get("search_history", [])
    )

# --- VIEW PROFILE ---
@app.route("/view_profile/<username>")
def view_profile(username):
    if "username" not in session:
        flash("Please sign in to view profiles.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user = db.get_user(username)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("search_users"))

    # Vérifier la visibilité du profil
    can_view = user.is_public or current_user.follows(user)

    return render_template(
        "profile.html",
        user=user,
        current_user=current_user,
        can_view=can_view
    )

# --- FOLLOW USER ---
@app.route("/follow/<username>", methods=["POST"])
def follow_user(username):
    if "username" not in session:
        flash("Please sign in to follow users.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user_to_follow = db.get_user(username)
    if user_to_follow:
        current_user.follow(user_to_follow)
        flash(f"You are now following {username}", "success")
    else:
        flash("User not found.", "error")
    return redirect(request.referrer or url_for("feed"))

# --- UNFOLLOW USER ---
@app.route("/unfollow/<username>", methods=["POST"])
def unfollow_user(username):
    if "username" not in session:
        flash("Please sign in to unfollow users.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user_to_unfollow = db.get_user(username)
    if user_to_unfollow:
        current_user.unfollow(user_to_unfollow)
        flash(f"You have unfollowed {username}", "success")
    else:
        flash("User not found.", "error")
    return redirect(request.referrer or url_for("feed"))

# -- BLOCK USER --
@app.route("/block/<username>", methods=["POST"])
def block_user(username):
    if "username" not in session:
        flash("Please sign in to block users.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user_to_block = db.get_user(username)
    if user_to_block:
        current_user.block(user_to_block)
        flash(f"{username} has been blocked.", "success")
    else:
        flash("User not found.", "error")
    return redirect(request.referrer or url_for("feed"))

# --- UNBLOCK USER ---
@app.route("/unblock/<username>", methods=["POST"])
def unblock_user(username):
    if "username" not in session:
        flash("Please sign in to unblock users.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user_to_unblock = db.get_user(username)
    if user_to_unblock:
        current_user.unblock(user_to_unblock)
        flash(f"{username} has been unblocked.", "success")
    else:
        flash("User not found.", "error")
    return redirect(request.referrer or url_for("feed"))

# --- VIEW FOLLOWERS ---
@app.route("/followers/<username>")
def view_followers(username):
    if "username" not in session:
        flash("Please sign in to view followers.", "error")
        return redirect(url_for("login"))

    user = db.get_user(username)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("feed"))

    followers = user.followers  # liste d'objets User qui suivent cet utilisateur
    current_user = db.get_user(session["username"])

    return render_template("followers.html", user=user, followers=followers, current_user=current_user)


# --- VIEW FOLLOWING ---
@app.route("/following/<username>")
def view_following(username):
    if "username" not in session:
        flash("Please sign in to view following.", "error")
        return redirect(url_for("login"))

    user = db.get_user(username)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("feed"))

    following = user.following  # liste d'objets User que cet utilisateur suit
    current_user = db.get_user(session["username"])

    return render_template("following.html", user=user, following=following, current_user=current_user)

# --- CLEAR SEARCH HISTORY ---
@app.route("/clear_search_history", methods=["POST"])
def clear_search_history():
    if "username" not in session:
        flash("Please sign in to clear history.", "error")
        return redirect(url_for("login"))

    session["search_history"] = []
    session.modified = True
    flash("Search history cleared.", "success")
    return redirect(url_for("search_users"))

# --- SUGGESTIONS ---
@app.route("/suggestions")
def suggestions():
    if "username" not in session:
        flash("Please sign in to view suggestions.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    all_users = db.get_all_users()

    # Filtrer : public, non suivi et pas bloqué
    suggested_users = [
        u for u in all_users
        if u.username != current_user.username
        and current_user.follows(u) == False
        and u.username not in current_user.blocked_users
        and u.is_public
    ]

    # On peut trier par nombre de followers décroissant
    suggested_users.sort(key=lambda u: len(u.followers), reverse=True)

    return render_template("suggestions.html", current_user=current_user, suggested_users=suggested_users)


if __name__ == "__main__":
    app.run(debug=True)
