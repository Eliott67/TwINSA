import re
import os
import sys
import json
import datetime
import uuid
from backend.posting import *
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from urllib.parse import urlencode

UPLOAD_FOLDER = "static/profile_pics"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

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
from backend.editing_profile import update_personal_info, delete_account
from backend.notification import FollowRequestNotification

app = Flask(__name__)
app.secret_key = "super_secret_key"

# --- Load database ---
db = UsersDatabase("backend/users_database.json")

# --- Password reset tokens (email -> token) ---
reset_tokens = {}

# --- Posts file ---
POSTS_FILE = "posts.json"


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


def load_posts_bis(db):
    raw_posts = load_posts()
    posts = []

    for p in raw_posts:
        post = Post.__new__(Post)
        post.poster_username = p["poster_username"]
        post.database = db
        post.user = db.get_user(post.poster_username)
        post.content = p["content"]
        post.image = p.get("image", None)
        post.date = datetime.datetime.strptime(p["date"], "%Y-%m-%d %H:%M:%S")
        post.likes = p["likes"]
        post.comments = p["comments"]
        post.post_id = p.get("post_id", 0)
        posts.append(post)

    return posts


def get_secure_user(username):
    user_obj = db.get_user(username)
    if not user_obj:
        return None
    return SecureUser(
        username=user_obj.username,
        email=user_obj.email,
        password=user_obj.get_password(),
        name=user_obj.name,
        age=user_obj.age,
        country=user_obj.country,
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

        is_public_raw = request.form.get("is_public")
        is_public = bool(is_public_raw)

        new_user = User(username, email, password, name="", age=0, country="")
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

        # Générer un token aléatoire (UUID)
        token = str(uuid.uuid4())

        # Stocker en mémoire
        reset_tokens[email] = token

        reset_link = url_for("reset_password", _external=True)
        print(f"[DEBUG] Reset token for {email}: {token}")
        print(f"[DEBUG] Reset link: {reset_link}")

        flash("Password reset code generated (see server console for the token).", "success")
        return redirect(url_for("reset_password"))

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

    for idx, p in enumerate(posts):
        p["index"] = idx

    image_file = None
    image_filename = None

    if request.method == "POST":
        content = request.form.get("tweet", "").strip()
        image_file = request.files.get("image")

        if not content and (not image_file or image_file.filename == ""):
            flash("You must provide text or an image!", "error")
            return redirect(url_for("feed"))

        hashtags = Post.extract_hashtags(content)
        is_valid, error_msg = Post.validate_hashtags(hashtags)

        if not is_valid:
            flash(
                error_msg
                or "Hashtags must have max 10 characters and contain only letters or numbers.",
                "error",
            )
            return redirect(url_for("feed"))

        if image_file and image_file.filename != "":
            uploads_dir = os.path.join("static", "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            image_filename = (
                f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_"
                f"{secure_filename(image_file.filename)}"
            )
            image_file.save(os.path.join(uploads_dir, image_filename))

        new_post = Post(content, session["username"], db, image_filename)
        poster_user = db.get_user(new_post.poster_username)

        post_data = {
            "poster_username": new_post.poster_username,
            "poster_pfp": poster_user.profile_picture if poster_user else "default.png",
            "content": new_post.content,
            "image": image_filename,
            "date": new_post.date.strftime("%Y-%m-%d %H:%M:%S"),
            "likes": new_post.likes,
            "comments": [],
            "hashtags": new_post.hashtags,
            "post_id": new_post.post_id,
        }
        posts.insert(0, post_data)
        current_user.add_post(new_post)
        db.save_users()
        save_posts(posts)
        flash("Post created successfully!", "success")

        return redirect(url_for("feed"))

    for idx, p in enumerate(posts):
        p["index"] = idx

    feed_type = request.args.get("feed_type", "friends")
    visible_posts = posts

    if current_user is not None:
        if feed_type == "discover":
            visible = []
            for p in posts:
                poster = p.get("poster_username")
                if not poster or poster == username:
                    continue

                author = db.get_user(poster)
                if author is None:
                    continue

                if getattr(author, "is_public", False) and poster not in current_user.following:
                    visible.append(p)

            visible_posts = visible
        else:
            allowed_usernames = set(current_user.following + [username])
            visible_posts = [
                p for p in posts if p.get("poster_username") in allowed_usernames
            ]

    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            start_date = None

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d") + datetime.timedelta(days=1)
        except ValueError:
            end_date = None

    content_filters = request.args.getlist("content_type")

    raw_hashtags = request.args.get("hashtags", "").strip()
    selected_hashtags = []
    if raw_hashtags:
        selected_hashtags = [h.strip().lower() for h in raw_hashtags.split(",") if h.strip()]

    if selected_hashtags:
        filtered_posts = []
        for p in visible_posts:
            tags = p.get("hashtags", [])
            if not tags and "content" in p:
                temp_post = Post(p["content"], p["poster_username"], db)
                tags = temp_post.hashtags
                p["hashtags"] = tags

            tags_lower = [t.lower() for t in tags]
            if any(tag in tags_lower for tag in selected_hashtags):
                filtered_posts.append(p)

        filtered_posts.sort(
            key=lambda p: datetime.datetime.strptime(p["date"], "%Y-%m-%d %H:%M:%S"),
            reverse=True,
        )
        visible_posts = filtered_posts

    if start_date or end_date:
        filtered_by_date = []
        for p in visible_posts:
            date_str = p.get("date", "")
            try:
                post_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            if start_date and post_date < start_date:
                continue
            if end_date and post_date >= end_date:
                continue

            filtered_by_date.append(p)

        visible_posts = filtered_by_date

    if content_filters:
        filtered = []
        for p in visible_posts:
            ok = False
            content = p.get("content", "") or ""
            image = p.get("image")
            hashtags = p.get("hashtags", []) or []

            if "text" in content_filters and content.strip():
                ok = True

            if "image" in content_filters and image:
                ok = True

            if "hashtag" in content_filters and hashtags:
                ok = True

            if "emoji" in content_filters:
                if re.search(r"[\U0001F300-\U0001FAFF]", content):
                    ok = True

            if ok:
                filtered.append(p)

        visible_posts = filtered

    notifications = []
    if current_user is not None and hasattr(current_user, "notifications"):
        notifications = list(current_user.notifications)[-20:]
        notifications.reverse()

    for p in visible_posts:
        user = db.get_user(p["poster_username"])
        if user and user.profile_picture:
            p["poster_pfp"] = user.profile_picture
        else:
            p["poster_pfp"] = "default_pfp.png"

    formatted_posts = []
    for p in visible_posts:
        post_obj = Post(p["content"], p["poster_username"], db)
        post_obj.hashtags = p.get("hashtags", [])
        formatted_posts.append({**p, "html_content": post_obj.get_html_content()})

    unselect_urls = {}
    for tag in selected_hashtags:
        remaining = [t for t in selected_hashtags if t != tag]
        if remaining:
            unselect_urls[tag] = url_for("feed", hashtags=",".join(remaining))
        else:
            unselect_urls[tag] = url_for("feed")

    return render_template(
        "feed.html",
        username=session["username"],
        tweets=formatted_posts,
        notifications=notifications,
        selected_hashtags=selected_hashtags,
        unselect_urls=unselect_urls,
    )


# --- NOTIFICATIONS PAGE ---
@app.route("/notifications")
def notifications():
    if "username" not in session:
        flash("Please sign in to view notifications.", "error")
        return redirect(url_for("login"))

    username = session["username"]
    current_user = db.get_user(username)

    notifications = []
    if current_user is not None and hasattr(current_user, "notifications"):
        notifications = list(current_user.notifications)[-20:]
        notifications.reverse()

    pending_requests = []
    if current_user is not None and hasattr(current_user, "pending_requests"):
        pending_requests = current_user.pending_requests

    return render_template(
        "notifications.html",
        username=username,
        notifications=notifications,
        pending_requests=pending_requests,
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

        already_liked = username in post["likes"]

        if already_liked:
            post["likes"].remove(username)
        else:
            post["likes"].append(username)

            owner_username = post.get("poster_username")
            if owner_username and owner_username != username:
                owner = db.get_user(owner_username)
                if owner is not None and hasattr(owner, "notifications"):
                    preview = post.get("content", "")
                    if len(preview) > 40:
                        preview = preview[:40] + "…"
                    owner.notifications.append(
                        f"{username} liked your post: \"{preview}\""
                    )
                    db.save_users()

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


# --- DELETE A POST ---
@app.route("/delete_post/<int:post_index>", methods=["POST"])
def delete_post_route(post_index):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    posts = load_posts()

    if 0 <= post_index < len(posts):
        post = posts[post_index]
        if post["poster_username"] != username:
            flash("You can only delete your own posts.", "error")
            return redirect(url_for("feed"))

        posts.pop(post_index)
        save_posts(posts)
        flash("Post deleted successfully!", "success")

    return redirect(url_for("feed"))


# --- EDIT A POST ---
@app.route("/edit_post/<int:post_index>", methods=["POST"])
def edit_post_route(post_index):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    posts = load_posts()

    if 0 <= post_index < len(posts):
        post = posts[post_index]
        if post["poster_username"] != username:
            flash("You can only edit your own posts.", "error")
            return redirect(url_for("feed"))

        new_content = request.form.get("new_content", "").strip()
        if not new_content:
            flash("Content cannot be empty.", "error")
            return redirect(url_for("feed"))

        post["content"] = new_content
        post["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_posts(posts)
        flash("Post updated!", "success")

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
            if comment["username"] == username:
                comments.pop(comment_index)
                posts[post_index]["comments"] = comments
                save_posts(posts)
                flash("Comment deleted successfully.", "success")

    return redirect(url_for("feed"))


# --- PROFILE ---
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if "username" not in session:
        flash("Please sign in to access your profile.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user = db.get_user(username)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("feed"))

    origin = request.args.get("origin")
    entry = request.args.get("entry")

    if origin in ("followers", "following"):
        back_url = url_for(origin, username=username, entry=entry)
    else:
        if entry:
            if entry.startswith("/"):
                back_url = entry
            elif entry == "feed":
                back_url = url_for("feed")
            elif entry.startswith("search"):
                if "?" in entry:
                    base, q = entry.split("?", 1)
                    back_url = url_for("search_users") + "?" + q
                else:
                    back_url = url_for("search_users")
            else:
                back_url = url_for("feed")
        else:
            back_url = url_for("feed")

    can_view = (
        user.is_public
        or current_user.follows(user)
        or user.username == current_user.username
    )

    followers = [db.get_user(u) for u in user.followers]
    followers = [f for f in followers if f is not None]
    following = [db.get_user(u) for u in user.following]
    following = [f for f in following if f is not None]

    visible = []
    if can_view:
        posts = load_posts_bis(db)
        visible = [p for p in posts if p.poster_username == username]

    return render_template(
        "profile.html",
        user=user,
        back_url=back_url,
        current_user=current_user,
        can_view=can_view,
        visible=visible,
        followers=followers,
        following=following,
    )


# --- EDIT PROFILE ---
@app.route("/edit_profile/<username>/edit", methods=["GET", "POST"])
def edit_profile2(username):
    if "username" not in session:
        flash("Please sign in to edit your profile.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user = db.get_user(username)

    if not user or user.username != current_user.username:
        flash("You can only edit your own profile.", "error")
        return redirect(url_for("profile", username=username))

    file = request.files.get("profile_picture")

    if file and file.filename != "":
        ext = file.filename.rsplit(".", 1)[1].lower()
        if ext in ALLOWED_EXT:
            filename = secure_filename(f"{username}_pfp.{ext}")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            user.profile_picture = filename
            db.save_users()
        else:
            flash(
                f"Invalid file type: .{ext}. Allowed types: {', '.join(ALLOWED_EXT)}",
                "error",
            )
            return redirect(url_for("edit_profile2", username=username))

    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.age = (
            int(request.form.get("age", user.age or 0))
            if request.form.get("age")
            else user.age
        )
        user.country = request.form.get("country", user.country)

        privacy = request.form.get("privacy")
        if privacy == "private":
            user.is_public = False
        else:
            user.is_public = True

        db.save_users()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile", username=user.username))

    return render_template("edit_profile2.html", user=user, current_user=current_user)


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

    if "search_history" not in session:
        session["search_history"] = []

    results = []

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            all_users = db.get_all_users()
            matches = [
                u for u in all_users if u.username.lower().startswith(query.lower())
            ]

            matches.sort(
                key=lambda u: (not current_user.follows(u), u.username.lower())
            )
            results = matches[:10]

            if query not in session["search_history"]:
                session["search_history"].insert(0, query)
            session["search_history"] = session["search_history"][:5]
            session.modified = True

    return render_template(
        "search.html",
        current_user=current_user,
        results=results,
        history=session.get("search_history", []),
    )


# --- SEARCH Suggestions  ---
@app.route("/api/search_suggestions")
def search_suggestions():
    if "username" not in session:
        return {"results": []}

    query = request.args.get("q", "").strip().lower()
    if not query:
        return {"results": []}

    current_user = db.get_user(session["username"])
    all_users = db.get_all_users()

    matches = [u.username for u in all_users if u.username.lower().startswith(query)]

    matches.sort(
        key=lambda uname: (
            not current_user.follows(db.get_user(uname)),
            uname.lower(),
        )
    )

    return {"results": matches[:10]}


# --- VIEW PROFILE (via search / followers / following) ---
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

    ref = request.referrer or ""
    origin = request.args.get("from_page")

    if origin in ("followers", "following"):
        session["intermediate_page"] = request.referrer
    elif "/feed" in ref or "/search" in ref:
        session["root_entry_page"] = ref
        session["intermediate_page"] = None

    if session.get("intermediate_page"):
        back_url = session["intermediate_page"]
    else:
        back_url = session.get("root_entry_page", url_for("feed"))

    can_view = user.is_public or current_user.follows(user)
    visible = []
    if can_view:
        posts = load_posts_bis(db)
        visible = [p for p in posts if p.poster_username == username]

    followers = [db.get_user(u) for u in user.followers if u is not None]
    followers = [f for f in followers if f is not None]
    following = [db.get_user(u) for u in user.following if u is not None]
    following = [f for f in following if f is not None]

    return render_template(
        "profile.html",
        user=user,
        back_url=back_url,
        current_user=current_user,
        can_view=can_view,
        visible=visible,
        followers=followers,
        following=following,
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


# -- SEND FOLLOW REQUEST --
@app.route("/send_follow_request/<username>", methods=["POST"])
def send_follow_request(username):
    if "username" not in session:
        flash("Please sign in to send follow requests.", "error")
        return redirect(url_for("login"))

    current_user = db.get_user(session["username"])
    user = db.get_user(username)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("search_users"))

    if user.username == current_user.username or current_user.follows(user):
        flash("Cannot follow this user.", "error")
        return redirect(url_for("search_users"))

    notif = FollowRequestNotification(sender=current_user, receiver=user)
    notif.send_request()

    flash(f"Follow request sent to {user.username}!", "success")
    return redirect(url_for("search_users"))


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

    entry = request.args.get("entry", "feed")

    followers = [db.get_user(u) for u in user.followers if u is not None]
    followers = [f for f in followers if f is not None]
    current_user = db.get_user(session["username"])

    return render_template(
        "followers.html",
        entry=entry,
        user=user,
        followers=followers,
        current_user=current_user,
    )


# --- VIEW FOLLOWING ---
@app.route("/following/<username>")
def view_following(username):
    if "username" not in session:
        flash("Please sign in to view following.", "error")
        return redirect(url_for("login"))

    entry = request.args.get("entry", "feed")

    user = db.get_user(username)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("feed"))

    following = [db.get_user(u) for u in user.following if u is not None]
    following = [f for f in following if f is not None]
    current_user = db.get_user(session["username"])

    return render_template(
        "following.html",
        entry=entry,
        user=user,
        following=following,
        current_user=current_user,
    )


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

    suggested_users = [
        u
        for u in all_users
        if u.username != current_user.username
        and current_user.follows(u) is False
        and u.username not in current_user.blocked_users
        and u.is_public
    ]

    suggested_users.sort(key=lambda u: len(u.followers), reverse=True)

    return render_template(
        "suggestions.html",
        current_user=current_user,
        suggested_users=suggested_users,
    )


# --- CHANGE PASSWORD (WHEN LOGGED IN) ---
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        flash("Please sign in.", "error")
        return redirect(url_for("login"))

    user = db.get_user(session["username"])

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        if user.get_password() != old_password:
            flash("Incorrect current password.", "error")
            return redirect(url_for("change_password"))

        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("change_password"))

        user.password = new_password
        db.save_users()
        flash("Password updated successfully!", "success")
        return redirect(url_for("profile", username=user.username))

    return render_template("change_password.html")


# --- RESET PASSWORD WITH TOKEN ---
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        token = request.form.get("token", "").strip()
        new_password = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        user = None
        for u in db.get_all_users():
            if u.email == email:
                user = u
                break

        if not user:
            flash("Email not found.", "error")
            return redirect(url_for("reset_password"))

        expected_token = reset_tokens.get(email)
        if not expected_token or expected_token != token:
            flash("Invalid or expired reset token.", "error")
            return redirect(url_for("reset_password"))

        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("reset_password"))

        user.password = new_password
        db.save_users()
        del reset_tokens[email]

        flash("Password reset successfully! You can now sign in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


# --- HASHTAG FEED ---
@app.route("/hashtag/<tag>", methods=["GET", "POST"])
def hashtag_feed(tag):
    if "username" not in session:
        flash("Please sign in to access TwINSA.", "error")
        return redirect(url_for("login"))

    posts = load_posts()
    username = session["username"]
    current_user = db.get_user(username)

    if request.method == "POST":
        content = request.form.get("tweet", "").strip()
        image_file = request.files.get("image")

        if not content and (not image_file or image_file.filename == ""):
            flash("You must provide text or an image!", "error")
            return redirect(url_for("hashtag_feed", tag=tag))

        hashtags = Post.extract_hashtags(content)
        is_valid, error_msg = Post.validate_hashtags(hashtags)
        if not is_valid:
            flash(
                error_msg
                or "Hashtags must have max 10 characters and contain only letters or numbers.",
                "error",
            )
            return redirect(url_for("hashtag_feed", tag=tag))

        image_filename = None
        if image_file and image_file.filename != "":
            uploads_dir = os.path.join("static", "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            image_filename = (
                f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_"
                f"{secure_filename(image_file.filename)}"
            )
            image_file.save(os.path.join(uploads_dir, image_filename))

        new_post = Post(content, username, db, image_filename)
        poster_user = db.get_user(new_post.poster_username)

        post_data = {
            "poster_username": new_post.poster_username,
            "poster_pfp": poster_user.profile_picture if poster_user else "default.png",
            "content": new_post.content,
            "image": image_filename,
            "date": new_post.date.strftime("%Y-%m-%d %H:%M:%S"),
            "likes": new_post.likes,
            "comments": [],
            "hashtags": new_post.hashtags,
            "post_id": new_post.post_id,
        }

        posts.insert(0, post_data)
        current_user.add_post(new_post)
        db.save_users()
        save_posts(posts)
        flash("Post created successfully!", "success")

        return redirect(url_for("hashtag_feed", tag=tag))

    for idx, p in enumerate(posts):
        p["index"] = idx

    visible_posts = posts
    if current_user is not None:
        allowed_usernames = set(current_user.following + [username])
        visible_posts = [
            p for p in posts if p.get("poster_username") in allowed_usernames
        ]

    tag_lower = tag.lower()

    filtered = []
    for p in visible_posts:
        hashtags = p.get("hashtags")

        if not hashtags:
            temp_post = Post(p["content"], p["poster_username"], db)
            hashtags = temp_post.hashtags
            p["hashtags"] = hashtags

        hashtags_lower = [h.lower() for h in hashtags]
        if tag_lower in hashtags_lower:
            filtered.append(p)

    filtered.sort(
        key=lambda p: datetime.datetime.strptime(p["date"], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    notifications = []
    if current_user is not None and hasattr(current_user, "notifications"):
        notifications = list(current_user.notifications)[-20:]
        notifications.reverse()

    formatted_posts = []
    for p in filtered:
        post_obj = Post(p["content"], p["poster_username"], db)
        post_obj.hashtags = p.get("hashtags", [])
        formatted_posts.append({**p, "html_content": post_obj.get_html_content()})

    return render_template(
        "feed.html",
        username=username,
        tweets=formatted_posts,
        notifications=notifications,
        selected_hashtag=tag_lower,
    )


# --- SEARCH HASHTAG SUGGESTIONS ---
@app.route("/api/hashtag_suggestions")
def hashtag_suggestions():
    if "username" not in session:
        return {"results": []}

    query = request.args.get("q", "").strip().lower()
    if not query:
        return {"results": []}

    if query.startswith("#"):
        query = query[1:]

    posts = load_posts()
    all_tags = {}

    for p in posts:
        tags = p.get("hashtags", [])
        if not tags and "content" in p:
            temp_post = Post(p["content"], p["poster_username"], db)
            tags = temp_post.hashtags
            p["hashtags"] = tags

        for t in tags:
            t_norm = t.lower()
            all_tags[t_norm] = all_tags.get(t_norm, 0) + 1

    suggestions = [t for t in all_tags.keys() if t.startswith(query)]
    suggestions.sort(key=lambda x: (-all_tags[x], x))

    return {"results": suggestions[:10]}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
