from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
from flask import Blueprint, render_template, session, redirect, url_for

pages_bp = Blueprint('pages', __name__)


# Route per la pagina di recupero password
@pages_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

# Route per la pagina di registrazione
@pages_bp.route('/register')
def register():
    return render_template('register.html')

# Route per la pagina di gestione degli allenamenti
@pages_bp.route('/workouts')
def workouts():
    return render_template('workouts.html')

# Route per la pagina di gestione dei clienti
@pages_bp.route('/clients')
def clients():
    return render_template('clients.html')

# Route per la pagina di gestione degli esercizi
@pages_bp.route('/exercises')
def exercises():
    return render_template('exercises.html')

# Route per la pagina di gestione dei trainer
@pages_bp.route('/trainers')
def trainers():
    return render_template('trainers.html')

# Route per la pagina di gestione dei piani di allenamento
@pages_bp.route('/plans')
def plans():
    return render_template('plans.html')

# Route per la pagina di gestione delle statistiche
@pages_bp.route('/statistics')
def statistics():
    return render_template('statistics.html')

# Route per la pagina di gestione delle attrezzature
@pages_bp.route('/equipment')
def equipment():
    return render_template('equipment.html')



# Route per la pagina di contatto
@pages_bp.route('/contact')
def contact():
    return render_template('contact.html')

# Route per la pagina di errore 404
@pages_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


