from flask import Blueprint, render_template, session, redirect, url_for, abort
from app.models.gym_database import GymDatabaseManager
from app.auth import login_required

client_bp = Blueprint('client', __name__, url_prefix='/client')


# ───────── DASHBOARD (già esistente) ─────────
@client_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'client':
        return redirect(url_for('login.login_page'))

    db = GymDatabaseManager(); db.open_connection()
    plans = db.get_client_workout_plans(session['user_id'], include_archived=False)
    db.close_connection()
    return render_template('client/dashboard.html', plans=plans)


# ───────── LISTA ESERCIZI (Avvia allenamento) ─────────
@client_bp.route('/workout/<int:plan_id>/start')
@login_required
def workout_start(plan_id):
    if session.get('role') != 'client':
        return redirect(url_for('login.login_page'))

    db = GymDatabaseManager(); db.open_connection()
    header, rows = db.get_workout_plan(plan_id)
    db.close_connection()

    if not header or header['client_id'] != session['user_id']:
        abort(404)

    # rows sono già ordinati (ord_idx)
    return render_template('client/workout_start.html',
                           plan=header, exercises=rows)


# ───────── SCHERMATA SINGOLO ESERCIZIO ─────────
@client_bp.route('/workout/<int:plan_id>/exercise/<int:pos>')
@login_required
def workout_do(plan_id, pos):
    if session.get('role') != 'client':
        return redirect(url_for('login.login_page'))

    db = GymDatabaseManager(); db.open_connection()
    header, rows = db.get_workout_plan(plan_id)
    db.close_connection()

    if not header or header['client_id'] != session['user_id']:
        abort(404)

    if pos < 1 or pos > len(rows):
        abort(404)

    ex = rows[pos-1]
    next_pos = pos + 1 if pos < len(rows) else None
    prev_pos = pos - 1 if pos > 1 else None

    return render_template('client/workout_do.html',
                           plan=header, ex=ex,
                           pos=pos, total=len(rows),
                           next_pos=next_pos, prev_pos=prev_pos)
