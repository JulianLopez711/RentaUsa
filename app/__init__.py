from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import Film  # Ajustar la importación según la nueva estructura
        from app.models.models import Customer, Rental, Store
        from app.routes.routes import routes  # Importar el Blueprint de rutas
        app.register_blueprint(routes)  # Registrar el Blueprint

    return app
