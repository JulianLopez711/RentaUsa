import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta')
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:110723.Jv@rentadb.cluster-ro-cn7bggvpiqfk.us-east-1.rds.amazonaws.com/rentadb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
