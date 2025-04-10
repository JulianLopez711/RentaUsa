from app import db

class Film(db.Model):
    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    release_year = db.Column(db.Integer)
    language_id = db.Column(db.Integer, db.ForeignKey('language.language_id'), nullable=False)
    rental_duration = db.Column(db.Integer, nullable=False, default=3)
    rental_rate = db.Column(db.Numeric(4, 2), nullable=False, default=4.99)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Numeric(5, 2), nullable=False, default=19.99)
    rating = db.Column(db.String(10))
    special_features = db.Column(db.String(255))
    last_update = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    inventory_count = db.Column(db.Integer, nullable=False, default=0)

    language = db.relationship('Language', backref=db.backref('films', lazy=True))
    actors = db.relationship('Actor', secondary='film_actor', backref=db.backref('films', lazy=True))

    def __repr__(self):
        return f'<Film {self.title}>'