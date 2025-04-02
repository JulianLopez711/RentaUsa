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

    # Importa modelos dentro del contexto de la app, pero sin `db.create_all()`
    with app.app_context():
        from app.models.models import User, Movie, Rental  

    return app
