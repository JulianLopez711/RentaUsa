from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask import Blueprint
from datetime import datetime
from app import db  # Importar la instancia de SQLAlchemy
from app.models.models import Customer, Film, Rental, Category, Inventory, Store, Country, City, Address, Payment  # Agregar Payment
from sqlalchemy.exc import IntegrityError

routes = Blueprint('routes', __name__)

@routes.route('/')
def login_page():
    if 'customer_id' in session:  # Cambiar 'user_id' por 'customer_id'
        return redirect(url_for('routes.home'))
    return render_template('login.html')

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email'):  # Validar que el correo electrónico esté presente
        return jsonify({'success': False, 'message': 'Correo electrónico requerido'})

    email = data.get('email')
    customer = Customer.query.filter_by(email=email).first()

    if customer:
        session['customer_id'] = customer.customer_id
        session['email'] = customer.email

        # Cargar historial de renta en la sesión
        rentals = Rental.query.filter_by(customer_id=customer.customer_id).all()
        session['rental_history'] = [
            {
                'film_title': rental.inventory.film.title,
                'rental_date': rental.rental_date,
                'return_date': rental.return_date
            }
            for rental in rentals
        ]
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Correo electrónico no encontrado'})

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('email'):  # Solo validar el correo electrónico
            return jsonify({'success': False, 'message': 'Correo electrónico requerido'})
        email = data.get('email')
        
        if Customer.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'El correo electrónico ya está registrado'})
        
        new_customer = Customer(email=email, create_date=datetime.now(), active=True)
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({'success': True})
    
    return render_template('register.html')

@routes.route('/logout')
def logout():
    session.pop('customer_id', None)  # Cambiar 'user_id' por 'customer_id'
    session.pop('email', None)  # Cambiar 'username' por 'email'
    return redirect(url_for('routes.login_page'))

@routes.route('/home')
def home():
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('routes.login_page'))
    
    category_id = request.args.get('category_id', type=int)
    store_id = request.args.get('store_id', type=int)
    categories = Category.query.all()

    # Filtrar solo las tiendas que tienen películas disponibles
    stores = Store.query.join(Inventory).filter(Inventory.film_id.isnot(None)).distinct().all()
    
    query = Film.query.join(Inventory).join(Store)
    
    if category_id:
        query = query.join(Film.categories).filter(Category.category_id == category_id)
    if store_id:
        query = query.filter(Inventory.store_id == store_id)
    
    films = query.all()
    
    return render_template('home.html', films=films, categories=categories, stores=stores, selected_category=category_id, selected_store=store_id)

@routes.route('/film/<int:film_id>')
def film_details(film_id):
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('routes.login_page'))
    
    film = Film.query.get_or_404(film_id)
    
    # Verificar si hay inventario disponible para la película
    is_available = Inventory.query.filter_by(film_id=film_id).filter(
        ~Inventory.rentals.any(Rental.return_date == None)  # Inventario no rentado
    ).first() is not None

    return render_template('film_details.html', movie=film, is_available=is_available)

@routes.route('/rent/<int:film_id>', methods=['POST'])
def rent_film(film_id):
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    film = Film.query.get_or_404(film_id)
    
    # Verificar si hay inventario disponible para la película
    inventory = Inventory.query.filter_by(film_id=film_id).filter(
        ~Inventory.rentals.any(Rental.return_date == None)  # Inventario no rentado
    ).first()
    if not inventory:
        return jsonify({'success': False, 'message': 'Película no disponible en inventario'})

    # Obtener el staff_id del gerente de la sucursal
    store = Store.query.get(inventory.store_id)
    staff_id = store.manager_staff_id if store else None

    if not staff_id:
        return jsonify({'success': False, 'message': 'No se pudo determinar el empleado responsable del alquiler'})

    # Crear una nueva renta
    new_rental = Rental(
        customer_id=session['customer_id'],
        inventory_id=inventory.inventory_id,
        rental_date=datetime.now(),
        staff_id=staff_id,
        last_update=datetime.now()
    )
    db.session.add(new_rental)
    db.session.flush()  # Obtener el rental_id antes de confirmar la transacción

    # Registrar el pago
    new_payment = Payment(
        customer_id=session['customer_id'],
        staff_id=staff_id,
        rental_id=new_rental.rental_id,
        amount=film.rental_rate,
        payment_date=datetime.now()
    )
    db.session.add(new_payment)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "no partition of relation" in str(e):
            return jsonify({'success': False, 'message': 'No existe una partición para la fecha de pago. Contacta al administrador.'})
        return jsonify({'success': False, 'message': 'Error al procesar la renta.'})

    return jsonify({'success': True, 'message': 'Película rentada exitosamente'})

@routes.route('/my-rentals')
def my_rentals():
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('routes.login_page'))
    
    # Filtrar solo las rentas activas (sin fecha de devolución)
    rentals = db.session.query(Rental).join(Inventory).join(Film).filter(
        Rental.customer_id == session['customer_id'],
        Rental.return_date == None  # Solo rentas activas
    ).all()
    
    customer_rentals = [
        {
            'id': rental.rental_id,
            'film': {
                'title': rental.inventory.film.title,
                'price': rental.inventory.film.rental_rate
            },
            'rental_date': rental.rental_date,
            'return_date': rental.return_date,
            'status': 'active'
        }
        for rental in rentals
    ]
    
    return render_template('my_rentals.html', rentals=customer_rentals)

@routes.route('/return/<int:rental_id>', methods=['POST'])
def return_film(rental_id):
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})

    # Buscar el alquiler correspondiente
    rental = Rental.query.filter_by(rental_id=rental_id, customer_id=session['customer_id']).first()
    if not rental:
        return jsonify({'success': False, 'message': 'Alquiler no encontrado'})

    # Actualizar el estado del alquiler
    rental.return_date = datetime.now()
    rental.last_update = datetime.now()

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Película devuelta exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al devolver la película', 'error': str(e)})

@routes.route('/get-cities/<int:country_id>')
def get_cities(country_id):
    cities = City.query.filter_by(country_id=country_id).all()
    city_data = [{'city_id': city.city_id, 'city_name': city.city} for city in cities]
    return jsonify(city_data)

@routes.route('/stores', methods=['GET', 'POST'])
def stores():
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('routes.login_page'))
    
    countries = Country.query.all()
    selected_country = request.args.get('country_id', type=int)
    selected_city = request.args.get('city_id', type=int)
    stores = []
    if selected_city:
        stores = Store.query.join(Address).filter(Address.city_id == selected_city).all()

    return render_template('stores.html', countries=countries, stores=stores, selected_country=selected_country, selected_city=selected_city)

@routes.route('/store/<int:store_id>/films')
def store_films(store_id):
    if 'customer_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('routes.login_page'))
    
    store = Store.query.get_or_404(store_id)
    inventories = Inventory.query.filter_by(store_id=store_id).all()
    films = [inventory.film for inventory in inventories]

    return render_template('store_films.html', store=store, films=films)