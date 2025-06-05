from flask import Blueprint, render_template, session, redirect, url_for
from app.auth import login_required, trainer_required

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@home_bp.route('/home')
def home():
    return render_template('layout.html')

@home_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login.login'))
    return render_template('dashboard.html')

@home_bp.route('/about')
@login_required
def about():
    return render_template('about.html')