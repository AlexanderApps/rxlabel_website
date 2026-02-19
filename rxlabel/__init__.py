import os
from flask import Flask
from .extensions import db
from .blueprints.main import main_bp
from .blueprints.license import license_bp
from .blueprints.admin import admin_bp


def create_app():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(root, "templates"),
        static_folder=os.path.join(root, "static"),
        instance_path=os.path.join(root, "instance"),
        instance_relative_config=False,
    )

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-me-in-production"),
        DATABASE=os.path.join(root, "instance", "rxlabel.db"),
        ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME", "admin"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "rxlabel2026"),
        # ── Email (Gmail App Password recommended) ────────
        MAIL_HOST=os.environ.get("MAIL_HOST", "smtp.gmail.com"),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
        MAIL_USERNAME=os.environ.get(
            "MAIL_USERNAME", "rxlabelapp@gmail.com"
        ),  # set in env
        MAIL_PASSWORD=os.environ.get(
            "MAIL_PASSWORD", "nprp xtnj escl livg"
        ),  # set in env
        MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", "RxLabel"),
    )

    os.makedirs(os.path.join(root, "instance"), exist_ok=True)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(license_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
