from flask import jsonify, request
from app.models import db, Film  # Asegúrate de importar el modelo Film
# ...existing code...

@app.route('/rent_film/<int:film_id>', methods=['POST'])
def rent_film(film_id):
    # Obtener la película por ID
    film = Film.query.get(film_id)
    if not film:
        return jsonify({'success': False, 'message': 'Película no encontrada.'}), 404

    # Verificar disponibilidad
    if film.inventory_count <= 0:
        return jsonify({'success': False, 'message': 'No hay copias disponibles.'}), 400

    # Descontar una copia del inventario
    film.inventory_count -= 1
    db.session.commit()

    return jsonify({'success': True, 'message': 'Película rentada exitosamente.'})