from datetime import datetime, date, timezone
from flask_login import UserMixin
from app.extensions import db, bcrypt, login_manager


def utcnow_naive():
    """Timezone-aware UTC now, stripped to naive for storage in
    timezone-naive DateTime columns (avoids the deprecated
    datetime.utcnow() while keeping the existing schema)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")  # admin | manager | staff
    theme_pref = db.Column(db.String(10), nullable=False, default="light")  # light | dark
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow_naive)
    last_login = db.Column(db.DateTime, nullable=True)

    sales = db.relationship("Sale", backref="rep", lazy="dynamic")

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    @property
    def initials(self):
        parts = self.full_name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.full_name[:2].upper()

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(40), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    price = db.Column(db.Float, nullable=False, default=0.0)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow_naive)

    sale_items = db.relationship("SaleItem", backref="product", lazy="dynamic")

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def margin_pct(self):
        if self.price == 0:
            return 0
        return round(((self.price - self.cost) / self.price) * 100, 1)

    def __repr__(self):
        return f"<Product {self.sku}>"


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")  # active | inactive
    created_at = db.Column(db.DateTime, default=utcnow_naive)

    sales = db.relationship("Sale", backref="customer", lazy="dynamic")

    @property
    def total_spent(self):
        return sum(s.total for s in self.sales if s.status == "paid")

    @property
    def order_count(self):
        return self.sales.count()

    def __repr__(self):
        return f"<Customer {self.name}>"


class Sale(db.Model):
    """A Sale doubles as the invoice record for that transaction."""

    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(30), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    sale_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="paid")  # paid | pending | overdue | refunded
    payment_method = db.Column(db.String(30), nullable=True)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=utcnow_naive)

    items = db.relationship("SaleItem", backref="sale", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale {self.invoice_number}>"


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)

    @property
    def line_total(self):
        return round(self.quantity * self.unit_price, 2)
