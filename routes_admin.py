"""Admin panel: edit content, products and view applications. URL: /admin"""
import getpass
import hashlib
import os
import re
import subprocess
import sys
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from models import AdminUser, Category, Inquiry, News, Product, Setting, Slide, Upload, db

ALLOWED_IMAGES = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                  "webp": "image/webp", "gif": "image/gif"}

admin_bp = Blueprint("admin", __name__)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-") or "item"


def unique_slug(model, text, current_id=None):
    base = slugify(text)
    slug, n = base, 2
    while True:
        existing = model.query.filter_by(slug=slug).first()
        if not existing or existing.id == current_id:
            return slug
        slug, n = f"{base}-{n}", n + 1


def _int(name, default=0):
    try:
        return int(str(request.form.get(name, default)).replace(",", "") or default)
    except ValueError:
        return default


def _float(name, default=0.0):
    try:
        return float(request.form.get(name, default) or default)
    except ValueError:
        return default


def save_upload(field, current=""):
    """Save an uploaded image in the database and return its /media/... address.
    Keeps the current value when nothing is uploaded; a typed URL in <field>_url wins."""
    url = request.form.get(field + "_url", "").strip()
    if request.form.get(field + "_remove"):
        return ""
    file = request.files.get(field)
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_IMAGES:
            flash("Image must be PNG, JPG, WEBP or GIF.", "danger")
            return current
        upload = Upload(filename=secure_filename(file.filename) or f"image.{ext}",
                        mimetype=ALLOWED_IMAGES[ext], data=file.read())
        db.session.add(upload)
        db.session.flush()  # gives upload.id before the caller commits
        return upload.url
    return url if url else current


# --- Auth --------------------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        user = AdminUser.query.filter_by(username=request.form.get("username", "").strip()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user)
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/admin") else url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        new = request.form.get("new_password", "")
        if not current_user.check_password(request.form.get("current_password", "")):
            flash("Current password is incorrect.", "danger")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "danger")
        elif new != request.form.get("confirm_password"):
            flash("New passwords do not match.", "danger")
        else:
            current_user.set_password(new)
            db.session.commit()
            flash("Password changed.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/password.html")


# --- Dashboard ---------------------------------------------------------------
@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "new": Inquiry.query.filter_by(status="New").count(),
        "applications": Inquiry.query.filter_by(kind="application").count(),
        "messages": Inquiry.query.filter_by(kind="contact").count(),
        "products": Product.query.filter_by(is_active=True).count(),
    }
    recent = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# --- Site settings -----------------------------------------------------------
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    items = Setting.query.order_by(Setting.sort_order).all()
    if request.method == "POST":
        for s in items:
            if s.key.startswith("img_"):
                s.value = save_upload(s.key, s.value or "")
            elif s.key in request.form:
                s.value = request.form[s.key].strip()
        db.session.commit()
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", items=items)


# --- Categories --------------------------------------------------------------
@admin_bp.route("/categories")
@login_required
def categories():
    return render_template("admin/categories.html",
                           categories=Category.query.order_by(Category.sort_order).all())


@admin_bp.route("/categories/new", methods=["GET", "POST"])
@admin_bp.route("/categories/<int:cat_id>", methods=["GET", "POST"])
@login_required
def category_form(cat_id=None):
    cat = db.session.get(Category, cat_id) if cat_id else Category(is_active=True, icon="bi-briefcase")
    if cat is None:
        return redirect(url_for("admin.categories"))
    if request.method == "POST":
        f = request.form
        if not f.get("name", "").strip():
            flash("Name is required.", "danger")
        else:
            cat.name = f["name"].strip()
            cat.slug = unique_slug(Category, f.get("slug") or cat.name, cat.id)
            cat.tagline = f.get("tagline", "").strip()
            cat.description = f.get("description", "").strip()
            cat.icon = f.get("icon", "").strip() or "bi-briefcase"
            cat.image = save_upload("image", cat.image or "")
            cat.sort_order = _int("sort_order")
            cat.is_active = "is_active" in f
            db.session.add(cat)
            db.session.commit()
            flash(f"Category '{cat.name}' saved.", "success")
            return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", cat=cat)


@admin_bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@login_required
def category_delete(cat_id):
    cat = db.session.get(Category, cat_id)
    if cat and cat.products:
        flash("Move or delete this category's products first.", "danger")
    elif cat:
        db.session.delete(cat)
        db.session.commit()
        flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


# --- Products ----------------------------------------------------------------
@admin_bp.route("/products")
@login_required
def products():
    cats = Category.query.order_by(Category.sort_order).all()
    return render_template("admin/products.html", categories=cats)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_bp.route("/products/<int:prod_id>", methods=["GET", "POST"])
@login_required
def product_form(prod_id=None):
    prod = db.session.get(Product, prod_id) if prod_id else Product(
        is_active=True, icon="bi-cash-coin", category_id=request.args.get("category", type=int))
    if prod is None:
        return redirect(url_for("admin.products"))
    cats = Category.query.order_by(Category.sort_order).all()
    if request.method == "POST":
        f = request.form
        category = db.session.get(Category, _int("category_id"))
        if not f.get("name", "").strip() or not category:
            flash("Name and category are required.", "danger")
        else:
            prod.name = f["name"].strip()
            prod.slug = unique_slug(Product, f.get("slug") or prod.name, prod.id)
            prod.category = category
            prod.short_description = f.get("short_description", "").strip()
            prod.description = f.get("description", "").strip()
            prod.features = f.get("features", "").strip()
            prod.requirements = f.get("requirements", "").strip()
            prod.icon = f.get("icon", "").strip() or "bi-cash-coin"
            prod.image = save_upload("image", prod.image or "")
            prod.min_amount = _int("min_amount")
            prod.max_amount = _int("max_amount")
            prod.interest_rate = _float("interest_rate")
            prod.max_term_months = _int("max_term_months")
            prod.sort_order = _int("sort_order")
            prod.is_active = "is_active" in f
            db.session.add(prod)
            db.session.commit()
            flash(f"Product '{prod.name}' saved.", "success")
            return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", prod=prod, categories=cats)


@admin_bp.route("/products/<int:prod_id>/delete", methods=["POST"])
@login_required
def product_delete(prod_id):
    prod = db.session.get(Product, prod_id)
    if prod:
        Inquiry.query.filter_by(product_id=prod.id).update({"product_id": None})
        db.session.delete(prod)
        db.session.commit()
        flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))


# --- Applications & messages -------------------------------------------------
@admin_bp.route("/inquiries")
@login_required
def inquiries():
    q = Inquiry.query
    kind, status = request.args.get("kind", ""), request.args.get("status", "")
    if kind:
        q = q.filter_by(kind=kind)
    if status:
        q = q.filter_by(status=status)
    items = q.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin/inquiries.html", items=items, kind=kind, status=status,
                           statuses=Inquiry.STATUSES)


@admin_bp.route("/inquiries/<int:inq_id>", methods=["GET", "POST"])
@login_required
def inquiry_detail(inq_id):
    inq = db.get_or_404(Inquiry, inq_id)
    if request.method == "POST":
        if request.form.get("status") in Inquiry.STATUSES:
            inq.status = request.form["status"]
        inq.admin_note = request.form.get("admin_note", "").strip()
        db.session.commit()
        flash("Updated.", "success")
        return redirect(url_for("admin.inquiry_detail", inq_id=inq.id))
    return render_template("admin/inquiry_detail.html", inq=inq, statuses=Inquiry.STATUSES)


# --- Home page slides --------------------------------------------------------
@admin_bp.route("/slides")
@login_required
def slides():
    return render_template("admin/slides.html", slides=Slide.query.order_by(Slide.sort_order).all())


@admin_bp.route("/slides/new", methods=["GET", "POST"])
@admin_bp.route("/slides/<int:slide_id>", methods=["GET", "POST"])
@login_required
def slide_form(slide_id=None):
    slide = db.session.get(Slide, slide_id) if slide_id else Slide(is_active=True)
    if slide is None:
        return redirect(url_for("admin.slides"))
    if request.method == "POST":
        f = request.form
        if not f.get("title", "").strip():
            flash("Title is required.", "danger")
        else:
            slide.eyebrow = f.get("eyebrow", "").strip()
            slide.title = f["title"].strip()
            slide.text = f.get("text", "").strip()
            slide.button_text = f.get("button_text", "").strip()
            slide.button_link = f.get("button_link", "").strip()
            slide.image = save_upload("image", slide.image or "")
            slide.sort_order = _int("sort_order")
            slide.is_active = "is_active" in f
            db.session.add(slide)
            db.session.commit()
            flash("Slide saved.", "success")
            return redirect(url_for("admin.slides"))
    return render_template("admin/slide_form.html", slide=slide)


@admin_bp.route("/slides/<int:slide_id>/delete", methods=["POST"])
@login_required
def slide_delete(slide_id):
    slide = db.session.get(Slide, slide_id)
    if slide:
        db.session.delete(slide)
        db.session.commit()
        flash("Slide deleted.", "success")
    return redirect(url_for("admin.slides"))


# --- News & events -----------------------------------------------------------
@admin_bp.route("/news")
@login_required
def news():
    items = News.query.order_by(News.published_on.desc(), News.id.desc()).all()
    return render_template("admin/news.html", items=items)


@admin_bp.route("/news/new", methods=["GET", "POST"])
@admin_bp.route("/news/<int:news_id>", methods=["GET", "POST"])
@login_required
def news_form(news_id=None):
    item = db.session.get(News, news_id) if news_id else News(is_published=True, published_on=date.today())
    if item is None:
        return redirect(url_for("admin.news"))
    if request.method == "POST":
        f = request.form
        if not f.get("title", "").strip():
            flash("Title is required.", "danger")
        else:
            item.title = f["title"].strip()
            item.slug = unique_slug(News, f.get("slug") or item.title, item.id)
            item.summary = f.get("summary", "").strip()
            item.body = f.get("body", "").strip()
            item.image = save_upload("image", item.image or "")
            try:
                item.published_on = date.fromisoformat(f.get("published_on", ""))
            except ValueError:
                item.published_on = date.today()
            item.is_published = "is_published" in f
            db.session.add(item)
            db.session.commit()
            flash("News item saved.", "success")
            return redirect(url_for("admin.news"))
    return render_template("admin/news_form.html", item=item)


@admin_bp.route("/news/<int:news_id>/delete", methods=["POST"])
@login_required
def news_delete(news_id):
    item = db.session.get(News, news_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("News item deleted.", "success")
    return redirect(url_for("admin.news"))


# --- Update the live website from GitHub -------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _git(*args):
    result = subprocess.run(["git", *args], cwd=APP_DIR, capture_output=True, text=True, timeout=120)
    return (result.stdout + result.stderr).strip()


def _file_hash(name):
    try:
        with open(os.path.join(APP_DIR, name), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return ""


def _wsgi_file():
    """PythonAnywhere reloads the website when its WSGI file is touched."""
    path = os.environ.get("WSGI_FILE") or f"/var/www/{getpass.getuser()}_pythonanywhere_com_wsgi.py"
    return path if os.path.exists(path) else ""


@admin_bp.route("/update", methods=["GET", "POST"])
@login_required
def update_site():
    output = ""
    if request.method == "POST":
        before = _file_hash("requirements.txt")
        output = _git("pull", "--ff-only", "origin", "main")
        if _file_hash("requirements.txt") != before:
            pip = os.path.join(sys.prefix, "bin", "pip")
            if os.path.exists(pip):
                r = subprocess.run([pip, "install", "-q", "-r", "requirements.txt"], cwd=APP_DIR,
                                   capture_output=True, text=True, timeout=600)
                output += "\n\n[pip] " + ((r.stdout + r.stderr).strip() or "packages updated")
        wsgi = _wsgi_file()
        if wsgi and "Already up to date" not in output:
            os.utime(wsgi, None)
            flash("Website updated from GitHub and reloaded. Refresh the site in a few seconds.", "success")
        elif "Already up to date" in output:
            flash("Already up to date - no new changes on GitHub.", "info")
        else:
            flash("Code updated. Restart the server (python app.py) to see the changes.", "warning")
    current = _git("log", "-1", "--format=%h  %ad  %s", "--date=format:%Y-%m-%d %H:%M")
    return render_template("admin/update.html", current=current, output=output, is_live=bool(_wsgi_file()))
