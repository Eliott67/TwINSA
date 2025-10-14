import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session

# --- Make backend importable ---
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

# --- Load your database ---
db = UsersDatabase("backend/users_database.json")


# --- Utility: get SecureUser instance from username ---
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
        country=user_obj.country
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

        if db.authenticate_user(username, password):
            session["username"] = username
            flash("Signed in successfully!", "success")
            return redirect(url_for("home"))
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

        # Search for user by email
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
        flash("Password reset code sent to your email (visible in console for testing).", "success")
        return redirect(url_for("home"))

    return render_template("forgot_password.html")


if __name__ == "__main__":
    app.run(debug=True)
