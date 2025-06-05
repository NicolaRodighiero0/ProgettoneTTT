from flask import (
    Blueprint, render_template, session,
    redirect, url_for, request, flash, jsonify, abort
)
from app.models.gym_database import GymDatabaseManager
from app.auth import login_required, trainer_required
import json

# Blueprint per le pagine HTML del trainer
trainer_page_bp = Blueprint(
    'trainer_page',
    __name__,
    url_prefix='/trainer'
)

@trainer_page_bp.route('/dashboard')
@login_required
@trainer_required
def dashboard():
    return render_template('trainer/dashboard.html')

@trainer_page_bp.route('/clients', methods=['GET', 'POST'])
@login_required
@trainer_required
def manage_clients():
    db = GymDatabaseManager()
    db.open_connection()
    trainer_id = session['user_id']

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Devi inserire username e password', 'warning')
        else:
            new_id = db.create_client(username, password, trainer_id)
            if new_id:
                flash(f'Cliente "{username}" creato con successo!', 'success')
            else:
                flash(f'Errore: lo username "{username}" esiste già.', 'danger')

        db.close_connection()
        return redirect(url_for('trainer_page.manage_clients'))

    clients = db.get_trainer_clients(trainer_id)
    db.close_connection()
    return render_template('trainer/clients.html', clients=clients)


@trainer_page_bp.route('/exercises')
@login_required 
@trainer_required
def exercises_page():
    db = GymDatabaseManager(); db.open_connection()
    exercises = db.list_exercises(order_by="name")
    # aggiungi i gruppi per la visualizzazione
    for ex in exercises:
        prim, sec = db.get_exercise_groups(ex["id"])
        ex["prim_str"] = ", ".join(prim)
        ex["sec_str"]  = ", ".join(sec)
    db.close_connection()
    return render_template('trainer/exercises.html', exercises=exercises)


@trainer_page_bp.route('/exercises/new', methods=['GET', 'POST'])
@login_required
@trainer_required
def new_exercise():
    db = GymDatabaseManager(); db.open_connection()

    objectives    = db.get_all_objectives()
    difficulties  = db.get_all_difficulties()
    muscle_groups = db.get_all_muscle_groups()
    machines      = db.get_machine_list()

    # ───────── POST: crea esercizio ─────────
    if request.method == 'POST':
        form = request.form

        # link video: None se il campo è vuoto
        video_url = form.get('video_url') or None

        data = {
            'name'       : form['name'],
            'description': form.get('description', ''),
            'objective'  : form.get('objective') or None,
            'difficulty' : form.get('difficulty') or None,
            'video_url'  : video_url,
            'machine_name': form.get('machine_name') or None,
            # flags (checkbox)
            'requires_repetitions': 'requires_repetitions' in form,
            'requires_sets'      : 'requires_sets'       in form,
            'requires_duration'  : 'requires_duration'   in form,
            'requires_rest'      : 'requires_rest'       in form,
            'requires_machine'   : 'requires_machine'    in form,
            'requires_weight'    : 'requires_weight'     in form,
            # gruppi muscolari (grazie al [] nel name arrivano sempre come lista)
            'primary_groups'   : form.getlist('primary_groups[]'),
            'secondary_groups' : form.getlist('secondary_groups[]'),
        }

        db.add_exercise(data)
        db.close_connection()
        flash('Esercizio creato', 'success')
        return redirect(url_for('trainer_page.exercises_page'))

    db.close_connection()
    return render_template('trainer/exercise_form.html',
                           mode='new',
                           objectives=objectives,
                           difficulties=difficulties,
                           muscle_groups=muscle_groups,
                           machines=machines)


@trainer_page_bp.route('/exercises/<int:ex_id>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_exercise(ex_id):
    db = GymDatabaseManager(); db.open_connection()
    ex = db.get_exercise_by_id(ex_id)
    if not ex:
        db.close_connection(); abort(404)

    # gruppi correnti per la preselezione
    ex['primary_groups'], ex['secondary_groups'] = db.get_exercise_groups(ex_id)

    objectives    = db.get_all_objectives()
    difficulties  = db.get_all_difficulties()
    muscle_groups = db.get_all_muscle_groups()
    machines      = db.get_machine_list()

    # ───────── POST: aggiorna ─────────
    if request.method == 'POST':
        form = request.form
        video_url = form.get('video_url') or None

        data = {
            'name'       : form['name'],
            'description': form.get('description', ''),
            'objective'  : form.get('objective') or None,
            'difficulty' : form.get('difficulty') or None,
            'video_url'  : video_url,
            'machine_name': form.get('machine_name') or None,
            'requires_repetitions': 'requires_repetitions' in form,
            'requires_sets'      : 'requires_sets'       in form,
            'requires_duration'  : 'requires_duration'   in form,
            'requires_rest'      : 'requires_rest'       in form,
            'requires_machine'   : 'requires_machine'    in form,
            'requires_weight'    : 'requires_weight'     in form,
            'primary_groups'   : form.getlist('primary_groups[]'),
            'secondary_groups' : form.getlist('secondary_groups[]'),
        }

        db.update_exercise(ex_id, data)
        db.close_connection()
        flash('Esercizio aggiornato', 'success')
        return redirect(url_for('trainer_page.exercises_page'))

    db.close_connection()
    return render_template('trainer/exercise_form.html',
                           mode='edit', ex=ex,
                           objectives=objectives,
                           difficulties=difficulties,
                           muscle_groups=muscle_groups,
                           machines=machines)

@trainer_page_bp.route('/exercises/<int:ex_id>/delete', methods=['POST'])
@login_required 
@trainer_required
def delete_exercise(ex_id):
    db = GymDatabaseManager(); db.open_connection()
    db.delete_exercise(ex_id); db.close_connection()
    flash('Esercizio eliminato', 'success')
    return redirect(url_for('trainer_page.exercises_page'))


@trainer_page_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
@trainer_required
def delete_client(client_id):
    db = GymDatabaseManager(); db.open_connection()
    if not db.verify_trainer_client(session['user_id'], client_id):
        db.close_connection()
        abort(404)

    db.delete_client(client_id)
    db.close_connection()
    flash('Cliente eliminato con successo', 'success')
    return redirect(url_for('trainer_page.manage_clients'))


@trainer_page_bp.route('/clients/<int:client_id>/workouts')
@login_required
@trainer_required
def list_workouts(client_id):
    db = GymDatabaseManager(); db.open_connection()
    if not db.verify_trainer_client(session['user_id'], client_id):
        db.close_connection(); abort(404)

    plans = db.get_client_workout_plans(client_id)
    client = db.get_user(client_id)          # per header pagina
    db.close_connection()
    return render_template('trainer/workouts.html',
                           client=client, plans=plans)

# form nuova scheda
@trainer_page_bp.route('/clients/<int:client_id>/workouts/new', methods=['GET', 'POST'])
@login_required
@trainer_required
def new_workout(client_id):
    db = GymDatabaseManager(); db.open_connection()
    if not db.verify_trainer_client(session['user_id'], client_id):
        db.close_connection(); abort(404)

    all_exercises = db.list_exercises()  # per la select nel form

    if request.method == 'POST':
        name = request.form['plan_name']
        # qui recuperi i campi dinamici degli esercizi dal form (JS -> hidden json)
        exercises = json.loads(request.form['exercise_payload'])
        db.create_workout_plan(client_id, session['user_id'], name, exercises)
        db.close_connection()
        flash('Scheda creata con successo', 'success')
        return redirect(url_for('trainer_page.list_workouts', client_id=client_id))

    
    all_exercises = db.list_exercises()        # ora restituisce *tutte* le colonne
    all_machines  = db.get_machine_list()
    db.close_connection()               # [{'id':1,'name':'Leg Press'}, …]

    return render_template('trainer/workout_form.html',
                       client_id=client_id,
                       exercises=all_exercises,
                       machines=all_machines,
                       mode='new')

# modifica scheda
@trainer_page_bp.route('/workouts/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_workout(plan_id):
    db = GymDatabaseManager(); db.open_connection()
    header, body = db.get_workout_plan(plan_id)
    if not header or header['trainer_id'] != session['user_id']:
        db.close_connection(); abort(404)

    all_exercises = db.list_exercises()
    all_machines  = db.get_machine_list()            

    if request.method == 'POST':
        name = request.form['plan_name']
        exercises = json.loads(request.form['exercise_payload'])
        db.update_workout_plan(plan_id, name, exercises)
        db.close_connection()
        flash('Scheda aggiornata', 'success')
        return redirect(url_for('trainer_page.list_workouts',
                                client_id=header['client_id']))

    db.close_connection()
    return render_template('trainer/workout_form.html',
                           plan=header,
                           rows=body,
                           exercises=all_exercises,
                           machines=all_machines,            
                           mode='edit')

# archivia (storico)
@trainer_page_bp.route('/workouts/<int:plan_id>/archive', methods=['POST'])
@login_required
@trainer_required
def archive_workout(plan_id):
    db = GymDatabaseManager(); db.open_connection()
    header, _ = db.get_workout_plan(plan_id)
    if not header or header['trainer_id'] != session['user_id']:
        db.close_connection(); abort(404)

    db.archive_workout_plan(plan_id)
    db.close_connection()
    flash('Scheda spostata nello storico', 'success')
    return redirect(url_for('trainer_page.list_workouts',
                            client_id=header['client_id']))
    
    

@trainer_page_bp.route('/workouts/<int:plan_id>/view', methods=['GET'])
@login_required
@trainer_required
def view_workout(plan_id):
    """
    Pagina di dettaglio read‑only di una scheda.
    """
    db = GymDatabaseManager(); db.open_connection()
    header, rows = db.get_workout_plan(plan_id)
    db.close_connection()

    if not header or header["trainer_id"] != session["user_id"]:
        abort(404)

    return render_template('trainer/workout_view.html',
                           plan=header, rows=rows)

# Blueprint per le API del trainer
trainer_api_bp = Blueprint(
    'trainer_api',
    __name__,
    url_prefix='/api/trainer'
)

@trainer_api_bp.route('/clients', methods=['GET'])
@login_required
@trainer_required
def get_clients_api():
    db = GymDatabaseManager(); db.open_connection()
    clients = db.get_trainer_clients(session['user_id'])
    db.close_connection()
    return jsonify(clients), 200

@trainer_api_bp.route('/clients', methods=['POST'])
@login_required
@trainer_required
def create_client_api():
    data = request.get_json() or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Dati mancanti'}), 400

    db = GymDatabaseManager(); db.open_connection()
    if db.get_user_by_username(data['username']):
        db.close_connection()
        return jsonify({'error': 'Username già in uso'}), 400

    client_id = db.insert_user(
        username=data['username'],
        password=data['password'],
        role='client',
        trainer_id=session['user_id']
    )
    db.close_connection()

    return jsonify({
        'success': True,
        'client': {'id': client_id, 'username': data['username']}
    }), 201

@trainer_api_bp.route('/workouts/<int:client_id>', methods=['POST'])
@login_required
@trainer_required
def create_client_workout_api(client_id):
    data = request.get_json() or {}
    if 'exercises' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    db = GymDatabaseManager(); db.open_connection()
    if not db.verify_trainer_client(session['user_id'], client_id):
        db.close_connection()
        return jsonify({'error': 'Cliente non trovato'}), 404

    workout_id = db.create_workout_plan(
        client_id=client_id,
        trainer_id=session['user_id'],
        exercises=data['exercises']
    )
    db.close_connection()
    return jsonify({'id': workout_id}), 201

@trainer_api_bp.route('/stats', methods=['GET'])
@login_required
@trainer_required
def get_stats_api():
    db = GymDatabaseManager(); db.open_connection()
    stats = {
        'clients': db.count_trainer_clients(session['user_id']),
        'workouts': db.count_workouts_by_trainer(session['user_id']),
        'exercises': db.count_exercises(),
        'machines' : db.count_machines()
    }
    db.close_connection()
    return jsonify(stats), 200



@trainer_page_bp.route('/machines', methods=['GET', 'POST'])
@login_required
@trainer_required
def machines_page():
    db = GymDatabaseManager(); db.open_connection()

    # POST → aggiungi nuovo macchinario dall’inline-form in pagina
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip() or None
        if not name:
            flash('Il nome del macchinario è obbligatorio', 'warning')
        elif db.create_machine(name, desc):
            flash('Macchinario aggiunto', 'success')
        else:
            flash('Errore durante il salvataggio', 'danger')
        db.close_connection()
        return redirect(url_for('trainer_page.machines_page'))

    machines = db.list_machines()
    db.close_connection()
    return render_template('trainer/machines.html', machines=machines)


# FORM NUOVO -----------------------------------
@trainer_page_bp.route('/machines/new', methods=['GET', 'POST'])
@login_required
@trainer_required
def new_machine():
    if request.method == 'POST':
        db = GymDatabaseManager(); db.open_connection()
        mid = db.create_machine(request.form['name'],
                                request.form.get('description'))
        db.close_connection()
        flash('Macchinario creato', 'success')
        return redirect(url_for('trainer_page.machines_page'))
    return render_template('trainer/machine_form.html', mode='new')


# EDIT -----------------------------------------
@trainer_page_bp.route('/machines/<int:mid>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_machine(mid):
    db = GymDatabaseManager(); db.open_connection()
    machine = db.get_machine(mid)
    if not machine: db.close_connection(); abort(404)

    if request.method == 'POST':
        db.update_machine(mid,
                          request.form['name'],
                          request.form.get('description'))
        db.close_connection()
        flash('Macchinario aggiornato', 'success')
        return redirect(url_for('trainer_page.machines_page'))

    db.close_connection()
    return render_template('trainer/machine_form.html',
                           mode='edit', machine=machine)


# DELETE ---------------------------------------
@trainer_page_bp.route('/machines/<int:mid>/delete', methods=['POST'])
@login_required
@trainer_required
def delete_machine(mid):
    db = GymDatabaseManager(); db.open_connection()
    db.delete_machine(mid); db.close_connection()
    flash('Macchinario eliminato', 'success')
    return redirect(url_for('trainer_page.machines_page'))