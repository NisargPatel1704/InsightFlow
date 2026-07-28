"""
Seed InsightFlow with realistic demo data so the dashboard looks complete
immediately after setup.

Usage:
    python seed.py            # seed if empty
    python seed.py --reset    # drop all tables and reseed from scratch
"""
import random
import sys
from datetime import date, timedelta, datetime

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, Customer, Sale, SaleItem, utcnow_naive

random.seed(42)

CATEGORIES = ["Electronics", "Office Supplies", "Furniture", "Software Licenses", "Packaging"]

PRODUCTS = [
    # name, category, price, cost, stock, reorder_level
    ("Wireless Mouse", "Electronics", 24.99, 11.50, 140, 30),
    ("Mechanical Keyboard", "Electronics", 79.99, 38.00, 65, 20),
    ("27\" 4K Monitor", "Electronics", 329.99, 210.00, 22, 10),
    ("USB-C Docking Station", "Electronics", 89.99, 47.00, 8, 15),
    ("Noise-Cancelling Headphones", "Electronics", 149.99, 72.00, 34, 15),
    ("A4 Printer Paper (500 ct)", "Office Supplies", 6.49, 3.10, 480, 100),
    ("Ballpoint Pens (Box of 50)", "Office Supplies", 9.99, 4.20, 300, 60),
    ("Sticky Notes Multipack", "Office Supplies", 5.49, 2.30, 210, 50),
    ("Desk Organizer Tray", "Office Supplies", 14.99, 6.80, 75, 20),
    ("Whiteboard Markers (Set of 8)", "Office Supplies", 8.99, 3.90, 5, 25),
    ("Ergonomic Office Chair", "Furniture", 249.99, 130.00, 18, 8),
    ("Standing Desk (Electric)", "Furniture", 449.99, 260.00, 12, 6),
    ("Filing Cabinet — 3 Drawer", "Furniture", 189.99, 95.00, 4, 6),
    ("Bookshelf — 5 Tier", "Furniture", 129.99, 68.00, 26, 10),
    ("Conference Table (8-seat)", "Furniture", 899.99, 520.00, 3, 3),
    ("CRM Suite — Annual License", "Software Licenses", 599.00, 90.00, 999, 50),
    ("Project Management Tool — Team Plan", "Software Licenses", 349.00, 40.00, 999, 50),
    ("Design Suite — Pro License", "Software Licenses", 259.00, 35.00, 999, 50),
    ("Corrugated Shipping Boxes (25 ct)", "Packaging", 19.99, 9.10, 160, 40),
    ("Bubble Mailers (100 ct)", "Packaging", 22.99, 10.50, 90, 30),
    ("Packing Tape (6-Pack)", "Packaging", 11.49, 4.80, 12, 20),
]

CUSTOMERS = [
    ("Elena Marsh", "Northwind Traders", "elena.marsh@northwindtraders.com"),
    ("Priya Chandran", "Beacon Logistics", "priya.chandran@beaconlogistics.io"),
    ("Marcus Webb", "Fieldstone Consulting", "marcus.webb@fieldstoneco.com"),
    ("Sofia Alvarez", "Alvarez & Reyes Law", "sofia@alvarezreyeslaw.com"),
    ("James Okafor", "Lumen Studio", "james@lumenstudio.design"),
    ("Grace Lindqvist", "Nordic Freight AB", "grace.lindqvist@nordicfreight.se"),
    ("Daniel Kim", "Kim Family Dental", "daniel@kimfamilydental.com"),
    ("Aaliyah Brooks", "Brooks Media Group", "aaliyah@brooksmediagroup.com"),
    ("Tom Fischer", "Fischer Manufacturing", "tom.fischer@fischermfg.com"),
    ("Hana Suzuki", "Suzuki Imports", "hana@suzukiimports.jp"),
    ("Liam O'Connor", "O'Connor & Sons Builders", "liam@oconnorbuilders.ie"),
    ("Chidi Eze", "Eze Retail Group", "chidi.eze@ezeretail.com"),
    ("Isabelle Laurent", "Laurent Boutique Hotels", "isabelle@laurenthotels.fr"),
    ("Ravi Patel", "Patel & Associates", "ravi@patelassociates.com"),
    ("Megan Coyle", "Coyle Creative Agency", "megan@coylecreative.com"),
    ("Oscar Nilsson", "Nilsson Engineering", "oscar@nilssoneng.se"),
    ("Fatima Rahman", "Rahman Textiles", "fatima@rahmantextiles.com"),
    ("Ben Whitfield", "Whitfield Realty", "ben@whitfieldrealty.com"),
    ("Nora Kristiansen", "Kristiansen Interiors", "nora@kristianseninteriors.no"),
    ("Carlos Mendez", "Mendez Auto Group", "carlos@mendezauto.com"),
    ("Yuki Tanaka", "Tanaka Consulting", "yuki@tanakaconsulting.jp"),
    ("Sarah Lindholm", "Lindholm & Partners", "sarah@lindholmpartners.com"),
    ("Omar Haddad", "Haddad Trading Co.", "omar@haddadtrading.com"),
    ("Ines Ferreira", "Ferreira Design Studio", "ines@ferreiradesign.pt"),
]

PAYMENT_METHODS = ["Credit Card", "Bank Transfer", "PayPal", "ACH", "Wire Transfer"]

STAFF_USERS = [
    ("Admin User", "admin", "admin@insightflow.io", "admin"),
    ("Naomi Chen", "naomi.chen", "naomi.chen@insightflow.io", "manager"),
    ("Diego Ramirez", "diego.ramirez", "diego.ramirez@insightflow.io", "staff"),
    ("Alex Turner", "alex.turner", "alex.turner@insightflow.io", "staff"),
]

DEFAULT_PASSWORD = "Admin123!"


def seed():
    app = create_app("development")
    with app.app_context():
        if "--reset" in sys.argv:
            print("Dropping all tables...")
            db.drop_all()

        db.create_all()

        if User.query.count() > 0 and "--reset" not in sys.argv:
            print("Database already has data. Run with --reset to reseed from scratch.")
            return

        print("Seeding users...")
        users = []
        for full_name, username, email, role in STAFF_USERS:
            u = User(full_name=full_name, username=username, email=email, role=role)
            u.set_password(DEFAULT_PASSWORD)
            db.session.add(u)
            users.append(u)
        db.session.commit()

        print("Seeding categories...")
        category_objs = {}
        for name in CATEGORIES:
            c = Category(name=name)
            db.session.add(c)
            category_objs[name] = c
        db.session.commit()

        print("Seeding products...")
        product_objs = []
        for idx, (name, cat_name, price, cost, stock, reorder) in enumerate(PRODUCTS):
            sku = f"IF-{cat_name[:3].upper()}-{idx+1:03d}"
            p = Product(
                name=name, sku=sku, category_id=category_objs[cat_name].id,
                price=price, cost=cost, stock_quantity=stock, reorder_level=reorder,
            )
            db.session.add(p)
            product_objs.append(p)
        db.session.commit()

        print("Seeding customers...")
        customer_objs = []
        for i, (name, company, email) in enumerate(CUSTOMERS):
            created_offset = random.randint(30, 400)
            c = Customer(
                name=name, company=company, email=email,
                phone=f"+1-555-{random.randint(1000,9999)}",
                status="active" if random.random() > 0.12 else "inactive",
                created_at=utcnow_naive() - timedelta(days=created_offset),
            )
            db.session.add(c)
            customer_objs.append(c)
        db.session.commit()

        print("Seeding sales & invoices...")
        today = date.today()
        invoice_seq = 1001
        for day_offset in range(180, -1, -1):
            sale_date = today - timedelta(days=day_offset)
            # More sales on weekdays, fewer on weekends; general upward trend recently
            is_weekend = sale_date.weekday() >= 5
            base_orders = 1 if is_weekend else 3
            recency_boost = 1 if day_offset < 30 else 0
            num_orders = max(0, base_orders + recency_boost + random.choice([-1, 0, 0, 1, 1, 2]))

            for _ in range(num_orders):
                customer = random.choice(customer_objs)
                rep = random.choice(users[1:])  # exclude admin as a "rep" mostly
                num_items = random.randint(1, 4)
                chosen_products = random.sample(product_objs, num_items)

                subtotal = 0.0
                sale = Sale(
                    invoice_number=f"INV-{invoice_seq:05d}",
                    customer_id=customer.id,
                    user_id=rep.id,
                    sale_date=sale_date,
                    due_date=sale_date + timedelta(days=30),
                    payment_method=random.choice(PAYMENT_METHODS),
                    created_at=datetime.combine(sale_date, datetime.min.time()),
                )
                invoice_seq += 1

                # Determine status: recent orders more likely pending/overdue
                if day_offset < 14:
                    status = random.choices(["paid", "pending"], weights=[70, 30])[0]
                elif day_offset < 35:
                    status = random.choices(["paid", "pending", "overdue"], weights=[75, 15, 10])[0]
                else:
                    status = random.choices(["paid", "overdue", "refunded"], weights=[92, 5, 3])[0]
                sale.status = status

                db.session.add(sale)
                db.session.flush()  # get sale.id

                for product in chosen_products:
                    qty = random.randint(1, 6)
                    item = SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, unit_price=product.price)
                    db.session.add(item)
                    subtotal += qty * product.price

                tax = round(subtotal * 0.075, 2)
                sale.subtotal = round(subtotal, 2)
                sale.tax = tax
                sale.total = round(subtotal + tax, 2)

        db.session.commit()

        # Nudge a handful of products into low-stock territory for realism (already set in data)

        total_sales = Sale.query.count()
        print(f"Done. Seeded {len(users)} users, {len(product_objs)} products, "
              f"{len(customer_objs)} customers, {total_sales} sales.")
        print(f"\nLog in with username 'admin' and password '{DEFAULT_PASSWORD}'")


if __name__ == "__main__":
    seed()
