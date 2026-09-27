"""Database tables (SQLAlchemy ORM)."""
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def add_missing_columns():
    """Tiny auto-migration: when a new column is added to a model above, add it to
    an existing database too (create_all only creates missing *tables*)."""
    inspector = db.inspect(db.engine)
    for table in db.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            continue
        existing = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name not in existing:
                col_type = column.type.compile(dialect=db.engine.dialect)
                with db.engine.begin() as conn:
                    conn.execute(db.text(f'ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}'))


class Setting(db.Model):
    """Key/value site settings: company name, address, phone, hero text ..."""
    __tablename__ = "settings"
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, default="")
    label = db.Column(db.String(100), default="")
    sort_order = db.Column(db.Integer, default=0)


class Category(db.Model):
    """A service group, e.g. Business Loans, Micro Leasing, Micro Group Loans."""
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    tagline = db.Column(db.String(200), default="")
    description = db.Column(db.Text, default="")
    icon = db.Column(db.String(50), default="bi-briefcase")  # Bootstrap Icons class
    image = db.Column(db.String(255), default="")  # file in static/uploads or full URL
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    products = db.relationship("Product", back_populates="category", order_by="Product.sort_order")

    @property
    def active_products(self):
        return [p for p in self.products if p.is_active]


class Product(db.Model):
    """A single loan / leasing product shown on the site."""
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    short_description = db.Column(db.String(255), default="")
    description = db.Column(db.Text, default="")
    features = db.Column(db.Text, default="")       # one per line
    requirements = db.Column(db.Text, default="")   # one per line
    icon = db.Column(db.String(50), default="bi-cash-coin")
    image = db.Column(db.String(255), default="")  # file in static/uploads or full URL
    min_amount = db.Column(db.Integer, default=0)
    max_amount = db.Column(db.Integer, default=0)
    interest_rate = db.Column(db.Float, default=0)  # annual %, used by the calculator
    max_term_months = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    category = db.relationship("Category", back_populates="products")

    @property
    def feature_list(self):
        return [f.strip() for f in (self.features or "").splitlines() if f.strip()]

    @property
    def requirement_list(self):
        return [r.strip() for r in (self.requirements or "").splitlines() if r.strip()]


class Inquiry(db.Model):
    """Loan applications and contact messages sent from the website."""
    __tablename__ = "inquiries"
    STATUSES = ["New", "Contacted", "Approved", "Rejected", "Closed"]

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), default="contact")  # contact | application
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    full_name = db.Column(db.String(120), nullable=False)
    nic = db.Column(db.String(20), default="")
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), default="")
    address = db.Column(db.String(255), default="")
    amount = db.Column(db.Integer, nullable=True)
    term_months = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="New")
    admin_note = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.now)

    product = db.relationship("Product")


class Slide(db.Model):
    """Home page banner slides."""
    __tablename__ = "slides"
    id = db.Column(db.Integer, primary_key=True)
    eyebrow = db.Column(db.String(100), default="")
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, default="")
    button_text = db.Column(db.String(50), default="")
    button_link = db.Column(db.String(255), default="")
    image = db.Column(db.String(255), default="")  # file in static/uploads or full URL
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class News(db.Model):
    """News, notices, events, tenders and auctions."""
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    summary = db.Column(db.String(300), default="")
    body = db.Column(db.Text, default="")
    image = db.Column(db.String(255), default="")
    published_on = db.Column(db.Date, default=lambda: datetime.now().date())
    is_published = db.Column(db.Boolean, default=True)


class Upload(db.Model):
    """Images uploaded from the admin panel, stored in the database so they survive
    server restarts on hosts without a permanent disk (e.g. Render)."""
    __tablename__ = "uploads"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def url(self):
        return f"/media/{self.id}/{self.filename}"


class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
