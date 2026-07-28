from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, utcnow_naive

auth_bp = Blueprint("auth", __name__, template_folder="../../templates/auth")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need administrator access for that page.", "warning")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            if not user.is_active_account:
                flash("This account has been deactivated. Contact an administrator.", "danger")
                return render_template("auth/login.html")
            user.last_login = utcnow_naive()
            db.session.commit()
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name.split()[0]}.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not full_name or not username or not email or not password:
            errors.append("All fields are required.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if User.query.filter_by(username=username).first():
            errors.append("That username is already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("That email is already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/register.html", form_data=request.form)

        # First registered user becomes an admin automatically
        role = "admin" if User.query.count() == 0 else "staff"

        user = User(full_name=full_name, username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. You can sign in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/theme/toggle", methods=["POST"])
@login_required
def toggle_theme():
    current_user.theme_pref = "dark" if current_user.theme_pref == "light" else "light"
    db.session.commit()
    return jsonify({"theme": current_user.theme_pref})
