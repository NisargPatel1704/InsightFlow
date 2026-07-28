from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models import Sale

api_bp = Blueprint("api", __name__)


@api_bp.route("/revenue-trend")
@login_required
def revenue_trend():
    days = request.args.get("days", 30, type=int)
    days = max(7, min(days, 365))

    end = date.today()
    start = end - timedelta(days=days - 1)

    rows = (
        db.session.query(Sale.sale_date, func.coalesce(func.sum(Sale.total), 0))
        .filter(Sale.status == "paid", Sale.sale_date >= start)
        .group_by(Sale.sale_date)
        .all()
    )
    trend_map = {d.isoformat(): v for d, v in rows}

    labels, values = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        values.append(round(trend_map.get(d.isoformat(), 0), 2))

    return jsonify({"labels": labels, "values": values})
