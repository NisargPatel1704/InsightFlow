from datetime import date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Sale, SaleItem, Product, Customer, Category

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../../templates/dashboard")


def _date_range(days):
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start, end


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()
    start_30, _ = _date_range(30)
    start_prev_30, _ = _date_range(60)

    # KPI: revenue this period vs previous period (paid sales only)
    revenue_current = db.session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
        Sale.status == "paid", Sale.sale_date >= start_30
    ).scalar()

    revenue_previous = db.session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
        Sale.status == "paid", Sale.sale_date >= start_prev_30, Sale.sale_date < start_30
    ).scalar()

    orders_current = Sale.query.filter(Sale.sale_date >= start_30).count()
    orders_previous = Sale.query.filter(
        Sale.sale_date >= start_prev_30, Sale.sale_date < start_30
    ).count()

    customers_total = Customer.query.count()
    new_customers_30 = Customer.query.filter(Customer.created_at >= start_30).count()

    avg_order_value = (revenue_current / orders_current) if orders_current else 0
    avg_order_value_prev = (revenue_previous / orders_previous) if orders_previous else 0

    def pct_change(cur, prev):
        if prev == 0:
            return 100.0 if cur > 0 else 0.0
        return round(((cur - prev) / prev) * 100, 1)

    kpis = {
        "revenue": {"value": revenue_current, "change": pct_change(revenue_current, revenue_previous)},
        "orders": {"value": orders_current, "change": pct_change(orders_current, orders_previous)},
        "aov": {"value": avg_order_value, "change": pct_change(avg_order_value, avg_order_value_prev)},
        "customers": {"value": customers_total, "change": pct_change(new_customers_30, max(customers_total - new_customers_30, 0))},
    }

    # Revenue trend for last 30 days (for the primary chart)
    trend_rows = (
        db.session.query(Sale.sale_date, func.coalesce(func.sum(Sale.total), 0))
        .filter(Sale.status == "paid", Sale.sale_date >= start_30)
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
        .all()
    )
    trend_map = {d.isoformat(): v for d, v in trend_rows}
    trend_labels, trend_values = [], []
    for i in range(30):
        d = start_30 + timedelta(days=i)
        trend_labels.append(d.strftime("%b %d"))
        trend_values.append(round(trend_map.get(d.isoformat(), 0), 2))

    # Revenue by category (doughnut)
    category_rows = (
        db.session.query(Category.name, func.coalesce(func.sum(SaleItem.quantity * SaleItem.unit_price), 0))
        .join(Product, Product.category_id == Category.id)
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.status == "paid")
        .group_by(Category.name)
        .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())
        .all()
    )
    category_labels = [r[0] for r in category_rows]
    category_values = [round(r[1], 2) for r in category_rows]

    # Top products by revenue
    top_products = (
        db.session.query(
            Product.name,
            func.sum(SaleItem.quantity).label("units"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.status == "paid")
        .group_by(Product.id)
        .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())
        .limit(5)
        .all()
    )

    # Recent sales / invoices
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(6).all()

    # Low stock alerts
    low_stock = [p for p in Product.query.filter(Product.is_active == True).all() if p.is_low_stock][:5]

    return render_template(
        "dashboard/index.html",
        kpis=kpis,
        trend_labels=trend_labels,
        trend_values=trend_values,
        category_labels=category_labels,
        category_values=category_values,
        top_products=top_products,
        recent_sales=recent_sales,
        low_stock=low_stock,
    )
