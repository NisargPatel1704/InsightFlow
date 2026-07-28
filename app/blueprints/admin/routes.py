from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Product, Customer, Sale
from app.blueprints.auth.routes import admin_required

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


@admin_bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = {
        "total_users": User.query.count(),
        "total_products": Product.query.count(),
        "total_customers": Customer.query.count(),
        "total_sales": Sale.query.count(),
    }
    return render_template("admin/index.html", users=users, stats=stats)


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@admin_required
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")
    if new_role in ("admin", "manager", "staff"):
        user.role = new_role
        db.session.commit()
        flash(f"{user.full_name}'s role updated to {new_role}.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't deactivate your own account.", "warning")
        return redirect(url_for("admin.index"))
    user.is_active_account = not user.is_active_account
    db.session.commit()
    status = "activated" if user.is_active_account else "deactivated"
    flash(f"{user.full_name}'s account was {status}.", "info")
    return redirect(url_for("admin.index"))
