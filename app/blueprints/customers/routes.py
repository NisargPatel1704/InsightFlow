from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Customer, Sale

customers_bp = Blueprint("customers", __name__, template_folder="../../templates/customers")


@customers_bp.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    query = Customer.query
    if search:
        query = query.filter(
            Customer.name.ilike(f"%{search}%") | Customer.company.ilike(f"%{search}%")
        )
    customers = query.order_by(Customer.name).all()
    customers = sorted(customers, key=lambda c: c.total_spent, reverse=True)

    total_customers = Customer.query.count()
    active_customers = Customer.query.filter_by(status="active").count()

    return render_template(
        "customers/index.html",
        customers=customers,
        search=search,
        total_customers=total_customers,
        active_customers=active_customers,
    )


@customers_bp.route("/<int:customer_id>")
@login_required
def detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    sales = customer.sales.order_by(Sale.sale_date.desc()).all()
    return render_template("customers/detail.html", customer=customer, sales=sales)
