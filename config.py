import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta')
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@dbrenta.cn7bggvpiqfk.us-east-1.rds.amazonaws.com/dbrenta"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
