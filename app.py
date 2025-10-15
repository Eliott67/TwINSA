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

        new_user = User(username, email, password, name="", age=0, country="")

        valid, msg = validate_registration(new_user, confirm_password)
        if not valid:
            flash(msg, "error")
            return redirect(url_for("register"))

        try:
            db.add_user(new_user)
            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
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
        save_posts(posts)
        flash("Post created successfully!", "success")
        return redirect(url_for("feed"))

    return render_template("feed.html", username=session["username"], tweets=posts)


# --- LIKE A POST ---
@app.route("/like/<int:post_index>")
def like(post_index):
    if "username" not in session:
        return redirect(url_for("login"))

    posts = load_posts()
    if 0 <= post_index < len(posts):
        post = posts[post_index]
        username = session["username"]

        if username in post["likes"]:
            post["likes"].remove(username)
        else:
            post["likes"].append(username)

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

    return redirect(url_for("feed"))

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


if __name__ == "__main__":
    app.run(debug=True)
