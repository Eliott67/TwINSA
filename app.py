import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session

# --- Add backend to path (for imports when running from root) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# --- Imports from backend ---
from backend.change_password import SecureUser
from backend.users_db import UsersDatabase
from backend.user import User
from backend.registration import validate_registration

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Load user database
DB_FILE = "users_db.json"
db = UsersDatabase(DB_FILE)


# --- Utility: build a SecureUser from database ---
def get_secure_user(username: str):
    data = getattr(db, "users", {}).get(username)
    if not data:
        return None
    return SecureUser(
        username=username,
        email=data.get("email", ""),
        password=data.get("password", ""),
        name="",
        age=None,
        country=""
    )


# --- HOME PAGE ---
@app.route("/")
def home():
    return render_template("home.html", username=session.get("username"))


# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_secure_user(username)
        if user and user.verify_password(password):
            session["username"] = username
            flash("Signed in successfully!", "success")
            return redirect(url_for("home"))

        flash("Invalid credentials.", "error")
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

        # Create temporary User object
        new_user = User(username, email, password, name="", age=None, country="")

        # Validate using backend function
        valid, msg = validate_registration(new_user, confirm_password)

        if not valid:
            flash(msg, "error")
            return redirect(url_for("register"))

        # Add user to JSON database
        if not hasattr(db, "users") or db.users is None:
            db.users = {}
        db.users[username] = {
            "email": email,
            "password": password
        }
        if hasattr(db, "save_users"):
            db.save_users()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# --- FORGOT PASSWORD ---
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        username = None
        for u, data in getattr(db, "users", {}).items():
            if data.get("email") == email:
                username = u
                break

        if not username:
            flash("Email not found.", "error")
            return redirect(url_for("forgot_password"))

        su = get_secure_user(username)
        su.generate_reset_token()
        print(f"[DEBUG] Reset token for {email}: {su.reset_token}")
        flash("Password reset code sent to your email (visible in console for testing).", "success")
        return redirect(url_for("home"))

    return render_template("forgot_password.html")


# --- RUN APP ---
if __name__ == "__main__":
    print(f"Using database: {os.path.abspath(DB_FILE)}")
    app.run(debug=True)
