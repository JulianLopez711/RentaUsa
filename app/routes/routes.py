from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from datetime import datetime
from app import db  # Importar la instancia de SQLAlchemy
from app.models.models import User, Movie, Rental  # Importar modelos

routes = Blueprint('routes', __name__)

@routes.route('/')
def login_page():  # Renombrar esta función para evitar conflicto con la otra 'home'
    if 'user_id' in session:
        return redirect(url_for('routes.home'))  # Redirigir a la página principal
    return render_template('login.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):  # Validar datos
            return jsonify({'success': False, 'message': 'Datos incompletos'})
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})
    
    return render_template('login.html')

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):  # Validar datos
            return jsonify({'success': False, 'message': 'Datos incompletos'})
        username = data.get('username')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'El nombre de usuario ya está en uso'})
        
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True})
    
    return render_template('register.html')

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('routes.login_page'))  # Cambiar 'routes.login' por 'routes.login_page'

@routes.route('/home')
def home():  # Mantener esta función como la principal para la página de inicio
    if 'user_id' not in session:
        return redirect(url_for('routes.login_page'))  # Cambiar 'routes.login' por 'routes.login_page'
    
    movies = Movie.query.all()
    return render_template('home.html', movies=movies)

@routes.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    movie = Movie.query.get_or_404(movie_id)  # Usar get_or_404 para manejar errores automáticamente
    is_rented = Rental.query.filter_by(user_id=session['user_id'], movie_id=movie_id, status='active').first() is not None
    
    return render_template('movie_details.html', movie=movie, is_rented=is_rented)

@routes.route('/rent/<int:movie_id>', methods=['POST'])
def rent_movie(movie_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    movie = Movie.query.get_or_404(movie_id)  # Usar get_or_404 para manejar errores automáticamente
    
    existing_rental = Rental.query.filter_by(user_id=session['user_id'], movie_id=movie_id, status='active').first()
    if existing_rental:
        return jsonify({'success': False, 'message': 'Ya has rentado esta película'})
    
    # Validar que la película esté disponible antes de rentarla
    if movie.stock <= 0:
        return jsonify({'success': False, 'message': 'La película no está disponible'})
    
    new_rental = Rental(
        user_id=session['user_id'],
        movie_id=movie_id,
        rent_date=datetime.now(),
        price=movie.price,
        status='active'
    )
    movie.stock -= 1  # Reducir el stock de la película
    db.session.add(new_rental)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Película rentada exitosamente'})

@routes.route('/my-rentals')
def my_rentals():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))  # Corregir redirección
    
    rentals = db.session.query(Rental, Movie).join(Movie, Rental.movie_id == Movie.id).filter(Rental.user_id == session['user_id']).all()
    user_rentals = [
        {
            'id': rental.Rental.id,
            'movie': {
                'title': rental.Movie.title,
                'price': rental.Movie.price
            },
            'rent_date': rental.Rental.rent_date,
            'return_date': rental.Rental.return_date,
            'status': rental.Rental.status
        }
        for rental in rentals
    ]
    
    return render_template('my_rentals.html', rentals=user_rentals)

@routes.route('/return/<int:rental_id>', methods=['POST'])
def return_movie(rental_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    rental = Rental.query.filter_by(id=rental_id, user_id=session['user_id']).first_or_404()  # Usar first_or_404
    rental.status = 'returned'
    rental.return_date = datetime.now()
    
    # Incrementar el stock de la película al devolverla
    movie = Movie.query.get(rental.movie_id)
    if movie:
        movie.stock += 1
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Película devuelta exitosamente'})