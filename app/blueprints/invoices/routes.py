from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, case
from app.extensions import db
from app.models import Sale

invoices_bp = Blueprint("invoices", __name__, template_folder="../../templates/invoices")


@invoices_bp.route("/")
@login_required
def index():
    status = request.args.get("status", "all")

    # Summary always reflects the full invoice book, independent of the
    # table filter/pagination below, computed as SQL aggregates rather
    # than pulling every row into Python.
    summary_row = db.session.query(
        func.count(case((Sale.status == "paid", 1))),
        func.count(case((Sale.status == "pending", 1))),
        func.count(case((Sale.status == "overdue", 1))),
        func.coalesce(func.sum(case((Sale.status.in_(["pending", "overdue"]), Sale.total), else_=0)), 0),
    ).first()

    summary = {
        "paid": summary_row[0],
        "pending": summary_row[1],
        "overdue": summary_row[2],
        "total_outstanding": summary_row[3],
    }

    query = Sale.query.order_by(Sale.sale_date.desc(), Sale.id.desc())
    if status != "all":
        query = query.filter(Sale.status == status)

    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    return render_template(
        "invoices/index.html",
        invoices=pagination.items,
        pagination=pagination,
        status=status,
        summary=summary,
    )


@invoices_bp.route("/<int:sale_id>")
@login_required
def detail(sale_id):
    invoice = Sale.query.get_or_404(sale_id)
    return render_template("invoices/detail.html", invoice=invoice)
