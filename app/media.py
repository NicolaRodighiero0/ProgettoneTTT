from flask import Blueprint, request, jsonify
import yt_dlp  # per scaricare video da YouTube
from app.models.gym_database import GymDatabaseManager  # Percorso 

media_bp = Blueprint('media', __name__)

@media_bp.route('/api/exercises/<int:exercise_id>/media', methods=['POST'])
def add_exercise_media(exercise_id):
    """Aggiunge media a un esercizio, supportando YouTube"""
    data = request.get_json()
    url = data.get('url')
    
    if 'youtube.com' in url or 'youtu.be' in url:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
    else:
        video_url = url  # Se non è YouTube, usa l'URL direttamente
            
    db = GymDatabaseManager()
    db.open_connection()
    media_id = db.add_exercise_media(exercise_id, video_url, 'video')
    db.close_connection()
    
    return jsonify({'id': media_id}), 201