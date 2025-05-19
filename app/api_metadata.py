from flask import Blueprint, jsonify
from app.models.gym_database import GymDatabaseManager

metadata_bp = Blueprint('metadata', __name__, url_prefix='/api')

@metadata_bp.route('/muscle-groups', methods=['GET'])
def get_muscle_groups():
    db = GymDatabaseManager()
    db.open_connection()
    groups = db.get_all_muscle_groups()
    db.close_connection()
    return jsonify(groups)

@metadata_bp.route('/objectives', methods=['GET'])
def get_objectives():
    db = GymDatabaseManager()
    db.open_connection()
    objs = db.get_all_objectives()
    db.close_connection()
    return jsonify(objs)

@metadata_bp.route('/difficulties', methods=['GET'])
def get_difficulties():
    db = GymDatabaseManager()
    db.open_connection()
    diffs = db.get_all_difficulties()
    db.close_connection()
    return jsonify(diffs)