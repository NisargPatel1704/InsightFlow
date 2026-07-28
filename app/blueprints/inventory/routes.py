from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Product, Category

inventory_bp = Blueprint("inventory", __name__, template_folder="../../templates/inventory")


@inventory_bp.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    stock_filter = request.args.get("stock", "all")

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()

    if stock_filter == "low":
        products = [p for p in products if p.is_low_stock]
    elif stock_filter == "out":
        products = [p for p in products if p.stock_quantity == 0]

    categories = Category.query.order_by(Category.name).all()
    total_value = sum(p.price * p.stock_quantity for p in Product.query.all())
    low_stock_count = sum(1 for p in Product.query.all() if p.is_low_stock)

    return render_template(
        "inventory/index.html",
        products=products,
        categories=categories,
        search=search,
        category_id=category_id,
        stock_filter=stock_filter,
        total_value=total_value,
        low_stock_count=low_stock_count,
    )


@inventory_bp.route("/<int:product_id>/adjust", methods=["POST"])
@login_required
def adjust_stock(product_id):
    product = Product.query.get_or_404(product_id)
    delta = request.form.get("delta", 0, type=int)
    product.stock_quantity = max(0, product.stock_quantity + delta)
    db.session.commit()
    flash(f"Stock for {product.name} updated to {product.stock_quantity}.", "success")
    return redirect(url_for("inventory.index"))
