import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta')
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@pagila1.cn7bggvpiqfk.us-east-1.rds.amazonaws.com:5432/pagila"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # Expiración de sesión en 1 hora
