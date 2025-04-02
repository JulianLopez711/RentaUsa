from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app.routes.routes import routes  # Importar el blueprint

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(routes)  # Registrar el blueprint

    # Manejo de errores global
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'success': False, 'message': 'Recurso no encontrado'}), 404

    return app
