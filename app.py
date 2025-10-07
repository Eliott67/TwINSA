from flask import Flask, render_template, request, redirect, url_for, flash, session
from backend.change_password import SecureUser
from backend.users_db import UsersDatabase

app = Flask(__name__)
app.secret_key = "super_secret_key"  # nécessaire pour sessions et flash

# Charger la DB
db = UsersDatabase("users_db.json")


# --- Fonction utilitaire pour récupérer un SecureUser depuis le JSON ---
def get_secure_user(username):
    user_data = db.users.get(username)
    if not user_data:
        return None
    return SecureUser(
        username=username,
        email=user_data.get("email", ""),
        password=user_data.get("password", ""),
        name=user_data.get("name", ""),
        age=user_data.get("age", None),
        country=user_data.get("country", "")
    )


# --- Page d'accueil ---
@app.route("/")
def home():
    username = session.get("username")
    return render_template("home.html", username=username)


# --- Connexion ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_secure_user(username)
        if user and user.verify_password(password):
            session["username"] = username
            flash("Connexion réussie !", "success")
            return redirect(url_for("home"))
        else:
            flash("Identifiants incorrects", "error")
    return render_template("login.html")


# --- Déconnexion ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("home"))


# --- Inscription ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Vérifie si username ou email existe déjà
        if not db.unique_user(username):
            flash("Nom d'utilisateur déjà pris", "error")
            return redirect(url_for("register"))

        if any(u.get("email") == email for u in db.users.values()):
            flash("Email déjà utilisé", "error")
            return redirect(url_for("register"))

        # Crée le nouvel utilisateur
        new_user = SecureUser(username, email, password, name="", age=None, country="")
        db.users[username] = {
            "email": new_user.email,
            "password": new_user.password,
            "name": new_user.name,
            "age": new_user.age,
            "country": new_user.country
        }
        db.save_users()
        flash("Compte créé avec succès !", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# --- Mot de passe oublié ---
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        # Chercher l'utilisateur par email
        user = None
        username = None
        for u, u_data in db.users.items():
            if u_data.get("email") == email:
                username = u
                user = u_data
                break

        if user:
            # Crée un SecureUser temporaire pour générer le token
            su = SecureUser(
                username=username,
                email=user["email"],
                password=user["password"],
                name=user.get("name", ""),
                age=user.get("age", None),
                country=user.get("country", "")
            )
            su.generate_reset_token()
            # Affichage du token en console pour l’instant
            print(f"[DEBUG] Token pour {email} : {su.reset_token}")
            flash("✅ Code de réinitialisation envoyé à votre adresse e-mail ! (token en console pour test)", "success")
        else:
            flash("❌ Adresse e-mail inconnue", "error")

    return render_template("forgot_password.html")


# --- Lancer l'application ---
if __name__ == "__main__":
    app.run(debug=True)

