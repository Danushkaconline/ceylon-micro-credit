"""Ceylon Micro Credit website - run with:  python app.py"""
import os
import secrets

from flask import Flask, abort, render_template, request, session, url_for
from flask_login import LoginManager

from config import BASE_DIR, Config
from models import AdminUser, Category, Setting, add_missing_columns, db
from seed import seed_defaults


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(AdminUser, int(user_id))

    from routes_admin import admin_bp
    from routes_public import public_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --- CSRF protection for every POST form ---------------------------------
    def csrf_token():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        return session["_csrf"]

    @app.before_request
    def check_csrf():
        if request.method == "POST":
            if not request.form.get("_csrf") or request.form.get("_csrf") != session.get("_csrf"):
                abort(400, "Form expired. Please go back, refresh the page and try again.")

    # --- Values available in every template ----------------------------------
    @app.context_processor
    def inject_globals():
        settings = {s.key: s.value for s in Setting.query.all()}
        nav_categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
        return {"site": settings, "nav_categories": nav_categories, "csrf_token": csrf_token}

    @app.template_filter("rs")
    def format_rupees(value):
        try:
            return "Rs. {:,.0f}".format(value or 0)
        except (TypeError, ValueError):
            return value

    @app.template_filter("tel")
    def tel_link(value):
        return "".join(ch for ch in (value or "") if ch.isdigit() or ch == "+")

    @app.template_filter("img")
    def image_src(value):
        """Uploaded file name -> /static/uploads/<name>; full URLs are used as-is."""
        if not value:
            return ""
        if value.startswith(("http://", "https://", "/")):
            return value
        return url_for("static", filename="uploads/" + value)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()
        add_missing_columns()
        seed_defaults(app.config["ADMIN_USERNAME"], app.config["ADMIN_PASSWORD"])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=os.environ.get("FLASK_DEBUG") == "1")
