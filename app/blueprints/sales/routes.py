from datetime import date
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, extract
from app.extensions import db
from app.models import Sale, Customer, User

sales_bp = Blueprint("sales", __name__, template_folder="../../templates/sales")


@sales_bp.route("/")
@login_required
def index():
    status = request.args.get("status", "all")
    query = Sale.query.order_by(Sale.sale_date.desc())
    if status != "all":
        query = query.filter(Sale.status == status)

    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=12, error_out=False)

    return render_template(
        "sales/index.html",
        sales=pagination.items,
        pagination=pagination,
        status=status,
    )


@sales_bp.route("/analytics")
@login_required
def analytics():
    # Monthly revenue for the current year
    year = date.today().year
    rows = (
        db.session.query(extract("month", Sale.sale_date), func.coalesce(func.sum(Sale.total), 0))
        .filter(Sale.status == "paid", extract("year", Sale.sale_date) == year)
        .group_by(extract("month", Sale.sale_date))
        .all()
    )
    monthly_map = {int(m): v for m, v in rows}
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_values = [round(monthly_map.get(i, 0), 2) for i in range(1, 13)]

    # Revenue by payment method
    payment_rows = (
        db.session.query(Sale.payment_method, func.coalesce(func.sum(Sale.total), 0))
        .filter(Sale.status == "paid")
        .group_by(Sale.payment_method)
        .all()
    )
    payment_labels = [r[0] or "Other" for r in payment_rows]
    payment_values = [round(r[1], 2) for r in payment_rows]

    # Revenue by sales rep
    rep_rows = (
        db.session.query(User.full_name, func.coalesce(func.sum(Sale.total), 0))
        .join(Sale, Sale.user_id == User.id)
        .filter(Sale.status == "paid")
        .group_by(User.id)
        .order_by(func.sum(Sale.total).desc())
        .all()
    )

    total_revenue = db.session.query(func.coalesce(func.sum(Sale.total), 0)).filter(Sale.status == "paid").scalar()
    total_orders = Sale.query.filter(Sale.status == "paid").count()
    avg_order = (total_revenue / total_orders) if total_orders else 0

    return render_template(
        "sales/analytics.html",
        month_labels=month_labels,
        monthly_values=monthly_values,
        payment_labels=payment_labels,
        payment_values=payment_values,
        rep_rows=rep_rows,
        total_revenue=total_revenue,
        total_orders=total_orders,
        avg_order=avg_order,
    )
