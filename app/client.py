from flask import Blueprint, render_template, session, redirect, url_for, abort, request, flash
from app.models.gym_database import GymDatabaseManager
from app.auth import login_required
import json

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



@client_bp.route('/workouts/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workout(plan_id):
    db = GymDatabaseManager(); db.open_connection()
    header, rows = db.get_workout_plan(plan_id)

    if not header or header['client_id'] != session['user_id']:
        db.close_connection(); abort(404)

    # ---------- POST ----------
    if request.method == 'POST':
        for field, values in request.form.lists():
            if field.startswith('row_'):
                row_id = int(field[4:])          # rimuove 'row_'
                db.update_plan_row_from_client(row_id, json.loads(values[0]))

        db.close_connection()
        flash('Scheda aggiornata!', 'success')
        return redirect(url_for('client.dashboard', plan_id=plan_id, pos=1))

    # ---------- GET ----------
    exercises = db.list_exercises()              # lista di dict
    flags = {e['id']: e for e in exercises}      # ←  mapping id → esercizio
    db.close_connection()

    return render_template('client/workout_edit.html',
                           plan=header,
                           rows=rows,
                           flags=flags)          # ←  passato al template
    
    # ───────── DETTAGLIO (sola lettura) ─────────
@client_bp.route('/workouts/<int:plan_id>/view')
@login_required
def workout_view(plan_id):
    # solo utenti con ruolo client
    if session.get('role') != 'client':
        return redirect(url_for('login.login_page'))

    db = GymDatabaseManager(); db.open_connection()
    header, rows = db.get_workout_plan(plan_id)
    db.close_connection()

    # sicurezza: la scheda deve essere dell’utente loggato
    if not header or header['client_id'] != session['user_id']:
        abort(404)

    return render_template('client/workout_view.html',
                           plan=header, rows=rows)
