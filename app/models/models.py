from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Movie(db.Model):
    __tablename__ = 'movies'  # Definir explícitamente el nombre de la tabla

    id = db.Column(db.Integer, primary_key=True)  # Clave primaria
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, default=2)
    price = db.Column(db.Float, nullable=False, default=5.99)
    image_url = db.Column(db.String(200), nullable=True)


class Rental(db.Model):
    __tablename__ = 'rentals'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete="CASCADE"), nullable=False)  # Cambia 'movie' a 'movies'
    rent_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)



