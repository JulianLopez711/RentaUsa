from app import db

class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)  # Relación con address
    active = db.Column(db.Boolean, nullable=False, default=True)
    create_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=True)

class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

class FilmCategory(db.Model):
    __tablename__ = 'film_category'

    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    last_update = db.Column(db.DateTime, nullable=False)

class Film(db.Model):
    __tablename__ = 'film'  

    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.language_id'), nullable=False)  # Relación con language
    rental_duration = db.Column(db.Integer, nullable=False)
    rental_rate = db.Column(db.Float, nullable=False)
    length = db.Column(db.Integer, nullable=True)
    replacement_cost = db.Column(db.Float, nullable=False)
    rating = db.Column(db.String(10), nullable=True)
    last_update = db.Column(db.DateTime, nullable=False)

    categories = db.relationship('Category', secondary='film_category', backref='films')

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)  # Definir como clave foránea
    last_update = db.Column(db.DateTime, nullable=False)

    film = db.relationship('Film', backref='inventories')
    store = db.relationship('Store', backref='inventories')  # Relación con Store

class Rental(db.Model):
    __tablename__ = 'rental'

    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    inventory = db.relationship('Inventory', backref='rentals')
    film = db.relationship('Film', secondary='inventory', viewonly=True)  # Relación indirecta con Film

class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    store_id = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    username = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(40), nullable=True)
    last_update = db.Column(db.DateTime, nullable=False)

    rentals = db.relationship('Rental', backref='staff')

class City(db.Model):
    __tablename__ = 'city'

    city_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    # Relación con Country (sin backref redundante)
    country = db.relationship('Country', back_populates='cities')

class Country(db.Model):
    __tablename__ = 'country'

    country_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    # Relación con City (usar back_populates en lugar de backref)
    cities = db.relationship('City', back_populates='country')

class Address(db.Model):
    __tablename__ = 'address'

    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    address2 = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(20), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    postal_code = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    city = db.relationship('City', backref='addresses')

class Store(db.Model):
    __tablename__ = 'store'

    store_id = db.Column(db.Integer, primary_key=True)
    manager_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    manager = db.relationship('Staff', backref='managed_store', foreign_keys=[manager_staff_id])
    address = db.relationship('Address', backref='stores')
    # La relación con Inventory ya está definida en el modelo Inventory

class Language(db.Model):
    __tablename__ = 'language'

    language_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    films = db.relationship('Film', backref='language')

# Tabla de asociación para la relación muchos-a-muchos entre Film y Actor
film_actor = db.Table(
    'film_actor',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.actor_id'), primary_key=True),
    db.Column('film_id', db.Integer, db.ForeignKey('film.film_id'), primary_key=True),
    db.Column('last_update', db.DateTime, nullable=False)
)

class Actor(db.Model):
    __tablename__ = 'actor'

    actor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    films = db.relationship('Film', secondary=film_actor, backref='actors')

class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.rental_id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)

    customer = db.relationship('Customer', backref='payments')
    staff = db.relationship('Staff', backref='payments')
    rental = db.relationship('Rental', backref='payments')




