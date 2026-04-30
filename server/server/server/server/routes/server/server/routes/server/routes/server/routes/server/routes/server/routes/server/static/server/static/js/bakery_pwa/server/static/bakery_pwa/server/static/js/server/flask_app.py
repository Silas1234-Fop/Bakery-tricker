from flask import Flask
from flask_cors import CORS
from .models import db, create_default_users
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app)

    from .routes.auth_routes import auth_bp
    from .routes.dashboard_routes import dashboard_bp
    from .routes.production_routes import production_bp
    from .routes.packaging_routes import packaging_bp
    from .routes.giveaway_routes import giveaway_bp
    from .routes.history_routes import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(packaging_bp)
    app.register_blueprint(giveaway_bp)
    app.register_blueprint(history_bp)

    with app.app_context():
        db.create_all()
        create_default_users()

    return app
