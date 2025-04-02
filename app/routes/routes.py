# Rutas



@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        users = get_users()
        for user in users:
            if user['username'] == username and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        users = get_users()
        
        # Verificar si el usuario ya existe
        for user in users:
            if user['username'] == username:
                return jsonify({'success': False, 'message': 'El nombre de usuario ya está en uso'})
        
        # Crear nuevo usuario
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': generate_password_hash(password)
        }
        
        users.append(new_user)
        save_users(users)
        
        return jsonify({'success': True})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    movies = get_movies()
    return render_template('home.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    movies = get_movies()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    
    if movie:
        # Verificar si la película ya está rentada por el usuario
        rentals = get_rentals()
        is_rented = any(r['user_id'] == session['user_id'] and r['movie_id'] == movie_id and r['status'] == 'active' for r in rentals)
        
        return render_template('movie_details.html', movie=movie, is_rented=is_rented)
    
    return redirect(url_for('home'))

@app.route('/rent/<int:movie_id>', methods=['POST'])
def rent_movie(movie_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    movies = get_movies()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    
    if not movie:
        return jsonify({'success': False, 'message': 'Película no encontrada'})
    
    # Verificar si la película ya está rentada por el usuario
    rentals = get_rentals()
    if any(r['user_id'] == session['user_id'] and r['movie_id'] == movie_id and r['status'] == 'active' for r in rentals):
        return jsonify({'success': False, 'message': 'Ya has rentado esta película'})
    
    # Crear nueva renta
    new_rental = {
        'id': len(rentals) + 1,
        'user_id': session['user_id'],
        'movie_id': movie_id,
        'rent_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'return_date': None,
        'price': movie['price'],
        'status': 'active'
    }
    
    rentals.append(new_rental)
    save_rentals(rentals)
    
    return jsonify({'success': True})

@app.route('/my-rentals')
def my_rentals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rentals = get_rentals()
    movies = get_movies()
    
    # Filtrar rentas del usuario actual y agregar información de la película
    user_rentals = []
    for rental in rentals:
        if rental['user_id'] == session['user_id']:
            movie = next((m for m in movies if m['id'] == rental['movie_id']), None)
            if movie:
                rental_info = rental.copy()
                rental_info['movie'] = movie
                user_rentals.append(rental_info)
    
    return render_template('my_rentals.html', rentals=user_rentals)

@app.route('/return/<int:rental_id>', methods=['POST'])
def return_movie(rental_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    rentals = get_rentals()
    rental_index = next((i for i, r in enumerate(rentals) if r['id'] == rental_id and r['user_id'] == session['user_id']), None)
    
    if rental_index is None:
        return jsonify({'success': False, 'message': 'Renta no encontrada'})
    
    # Actualizar estado de la renta
    rentals[rental_index]['status'] = 'returned'
    rentals[rental_index]['return_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_rentals(rentals)
    
    return jsonify({'success': True})