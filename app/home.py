from flask import Blueprint, render_template, session, redirect, url_for

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