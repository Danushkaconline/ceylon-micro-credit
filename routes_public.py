"""Public website pages."""
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for

from models import Category, Inquiry, News, Product, Slide, Upload, db

public_bp = Blueprint("public", __name__)


def _to_int(value):
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def active_products():
    return (Product.query.join(Category)
            .filter(Product.is_active.is_(True), Category.is_active.is_(True))
            .order_by(Category.sort_order, Product.sort_order).all())


@public_bp.route("/")
def home():
    slides = Slide.query.filter_by(is_active=True).order_by(Slide.sort_order).all()
    news = News.query.filter_by(is_published=True).order_by(News.published_on.desc(), News.id.desc()).limit(3).all()
    return render_template("index.html", slides=slides, products=active_products(), news=news)


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/services")
def services():
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template("services.html", categories=categories)


@public_bp.route("/services/<slug>")
def category(slug):
    cat = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template("category.html", category=cat)


@public_bp.route("/products/<slug>")
def product(slug):
    prod = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    if not prod.category.is_active:
        return render_template("404.html"), 404
    related = [p for p in prod.category.active_products if p.id != prod.id]
    return render_template("product.html", product=prod, related=related)


@public_bp.route("/calculator")
def calculator():
    return render_template("calculator.html", products=active_products(),
                           selected=request.args.get("product", ""))


@public_bp.route("/apply", methods=["GET", "POST"])
def apply():
    products = active_products()
    form = request.form
    if request.method == "POST":
        errors = []
        if not form.get("full_name", "").strip():
            errors.append("Please enter your full name.")
        if len([c for c in form.get("phone", "") if c.isdigit()]) < 9:
            errors.append("Please enter a valid phone number.")
        product = db.session.get(Product, _to_int(form.get("product_id")) or 0)
        if not product:
            errors.append("Please select a loan / leasing type.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("apply.html", products=products, form=form)

        db.session.add(Inquiry(
            kind="application", product=product,
            full_name=form["full_name"].strip(), nic=form.get("nic", "").strip(),
            phone=form["phone"].strip(), email=form.get("email", "").strip(),
            address=form.get("address", "").strip(),
            amount=_to_int(form.get("amount")), term_months=_to_int(form.get("term_months")),
            message=form.get("message", "").strip(),
        ))
        db.session.commit()
        flash("Thank you! Your application has been received. Our officer will call you shortly.", "success")
        return redirect(url_for("public.apply"))

    selected = Product.query.filter_by(slug=request.args.get("product", "")).first()
    return render_template("apply.html", products=products,
                           form={"product_id": str(selected.id) if selected else "",
                                 "amount": request.args.get("amount", ""),
                                 "term_months": request.args.get("term", "")})


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = request.form
    if request.method == "POST":
        if not form.get("full_name", "").strip() or not form.get("phone", "").strip() \
                or not form.get("message", "").strip():
            flash("Please fill in your name, phone number and message.", "danger")
            return render_template("contact.html", form=form)
        db.session.add(Inquiry(
            kind="contact", full_name=form["full_name"].strip(), phone=form["phone"].strip(),
            email=form.get("email", "").strip(), message=form["message"].strip(),
        ))
        db.session.commit()
        flash("Thank you for contacting us. We will get back to you soon.", "success")
        return redirect(url_for("public.contact"))
    return render_template("contact.html", form={})


@public_bp.route("/news")
def news_list():
    items = News.query.filter_by(is_published=True).order_by(News.published_on.desc(), News.id.desc()).all()
    return render_template("news_list.html", items=items)


@public_bp.route("/news/<slug>")
def news_detail(slug):
    item = News.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("news_detail.html", item=item)


@public_bp.route("/media/<int:upload_id>/<path:filename>")
def media(upload_id, filename):
    """Serve an image uploaded from the admin panel."""
    upload = db.session.get(Upload, upload_id)
    if not upload:
        abort(404)
    return Response(upload.data, mimetype=upload.mimetype,
                    headers={"Cache-Control": "public, max-age=31536000"})
