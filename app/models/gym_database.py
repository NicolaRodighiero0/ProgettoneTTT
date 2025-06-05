import sqlite3
import bcrypt
import os
from datetime import datetime, date

class GymDatabaseManager:
    def __init__(self, db_name='gym_database.db'):
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
        # Punta al folder db/ a livello di root
        self.db_name = os.path.join(project_root, 'db', db_name)
        self.conn = None
        self.cursor = None

    def open_connection(self):
        """
        Apre la connessione al database SQLite, abilita:
        - enforcement delle foreign key
        - modalità WAL per ridurre i lock
        Imposta inoltre il row_factory su sqlite3.Row.
        """
        # 1) apri la connessione con timeout
        self.conn = sqlite3.connect(
            self.db_name,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            timeout=5.0
        )
        self.conn.row_factory = sqlite3.Row

        # 2) esegui i PRAGMA direttamente sulla connessione, così
        #    non restano cursori aperti in attesa di fetch
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")

        # 3) crea il cursore "normale" per tutte le altre query
        self.cursor = self.conn.cursor()

    def close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None

    # Creazione tabelle
    def create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('trainer', 'client')) NOT NULL,
                trainer_id INTEGER,
                FOREIGN KEY (trainer_id) REFERENCES users(id)
            );
        """)

    def create_jwt_sessions_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jwt_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                issued_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_valid INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

    def create_muscle_groups_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS muscle_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)
        
        # Inserisci i gruppi muscolari di default se la tabella è vuota
        self.cursor.execute("SELECT COUNT(*) FROM muscle_groups")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            muscle_groups = [
                "Spalle", "Pettorali", "Bicipiti", "Avambracci", "Addominali", 
                "Abduttori", "Quadricipiti", "Cardio", "Stretching", "Trapezi", 
                "Tricipiti", "Dorsali", "Glutei", "Adduttori", "Femorali", "Polpacci"
            ]
            for group in muscle_groups:
                self.cursor.execute("INSERT INTO muscle_groups (name) VALUES (?)", (group,))

    def create_exercise_muscle_groups_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_muscle_groups (
                exercise_id INTEGER,
                muscle_group_id INTEGER,
                is_primary BOOLEAN NOT NULL,
                FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE,
                FOREIGN KEY (muscle_group_id) REFERENCES muscle_groups(id),
                PRIMARY KEY (exercise_id, muscle_group_id)
            );
        """)

    def create_objectives_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)
        # seed di default
        self.cursor.execute("SELECT COUNT(*) FROM exercise_objectives")
        if self.cursor.fetchone()[0] == 0:
            for name in ["Dimagrimento","Tonificazione","Massa muscolare","Mobilità","Propriocezione"]:
                self.cursor.execute(
                    "INSERT INTO exercise_objectives(name) VALUES(?)", (name,)
                )

    def create_difficulty_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_difficulty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL UNIQUE CHECK(level IN ('Facile','Medio','Difficile'))
            );
        """)
        # seed di default
        self.cursor.execute("SELECT COUNT(*) FROM exercise_difficulty")
        if self.cursor.fetchone()[0] == 0:
            for lvl in ["Facile","Medio","Difficile"]:
                self.cursor.execute(
                    "INSERT INTO exercise_difficulty(level) VALUES(?)", (lvl,)
                )

    def create_machines_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );
        """)

    def create_media_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                type TEXT CHECK(type IN ('image', 'video')) NOT NULL
            );
        """)

    def create_exercises_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                objective_id INTEGER,
                difficulty_id INTEGER,
                media_url TEXT,
                requires_repetitions BOOLEAN DEFAULT 0,
                requires_duration BOOLEAN DEFAULT 0,
                requires_rest BOOLEAN DEFAULT 0,
                requires_sets BOOLEAN DEFAULT 0,
                requires_machine BOOLEAN DEFAULT 0,
                requires_weight BOOLEAN DEFAULT 0,
                FOREIGN KEY (objective_id) REFERENCES exercise_objectives(id),
                FOREIGN KEY (difficulty_id) REFERENCES exercise_difficulty(id)
                
            );
        """)

    def create_workout_plans_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_plans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id   INTEGER NOT NULL,
            trainer_id  INTEGER NOT NULL,
            name        TEXT    NOT NULL,         -- es. “Ipertrofia 4‑split maggio”
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            archived    INTEGER DEFAULT 0,        -- 0 = attiva, 1 = storica
            FOREIGN KEY (client_id)  REFERENCES users(id),
            FOREIGN KEY (trainer_id) REFERENCES users(id)
        );
        """)

    def create_workout_exercises_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_plan_id  INTEGER NOT NULL,
                exercise_id      INTEGER NOT NULL,
                machine_id       INTEGER,
                repetitions      INTEGER,
                execution_time   INTEGER,      -- in secondi
                sets             INTEGER,
                rest_time        INTEGER,      -- in secondi
                suggested_weight REAL,
                order_position   INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (workout_plan_id) REFERENCES workout_plans(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id)     REFERENCES exercise(id)      ON DELETE CASCADE,
                FOREIGN KEY (machine_id)      REFERENCES machines(id)      ON DELETE SET NULL,

                UNIQUE (workout_plan_id, order_position)   -- opzionale, per garantire un ordine univoco
            );
        """)

    def create_workout_sessions_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_plan_id INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                FOREIGN KEY (workout_plan_id) REFERENCES workout_plans(id)
            );
        """)

    def create_exercise_logs_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                exercise_id INTEGER,
                reps INTEGER,
                weight REAL,
                duration INTEGER,
                notes TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id),
                FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
            );
        """)
        
    # Tabella per le notifiche
    def create_notifications_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

    def create_user_profile_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE,
                birth_date TEXT,
                phone TEXT,
                address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        self.conn.commit()
        
        
        
    def create_workout_plan_exercises_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_plan_exercises (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id      INTEGER NOT NULL,
                exercise_id  INTEGER NOT NULL,
                machine      TEXT,
                repetitions  INTEGER,
                exec_time_s  INTEGER,
                sets         INTEGER,
                rest_s       INTEGER,
                suggested_kg REAL,
                ord_idx      INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (plan_id)     REFERENCES workout_plans(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercise(id)      ON DELETE CASCADE,
                UNIQUE (plan_id, ord_idx)
            );
        """)

    def create_all_tables(self):
        """Create all necessary tables for the application"""
        self.create_users_table()
        self.create_jwt_sessions_table()
        self.create_muscle_groups_table()
        self.create_objectives_table()
        self.create_difficulty_table()
        self.create_machines_table()
        self.create_media_table()
        self.create_exercises_table() 
        self.create_exercise_muscle_groups_table()
        self.create_workout_plans_table()
        self.create_workout_exercises_table()
        self.create_workout_sessions_table()
        self.create_exercise_logs_table()
        self.create_notifications_table()
        self.create_user_profile_table()
        self.create_workout_plan_exercises_table()
        
        # Crea l'utente trainer di default
        self.ensure_default_trainer()
        
        print("All tables have been created")

    def ensure_default_trainer(self):
        """Ensure that a default trainer account exists"""
        existing_trainer = self.get_user_by_username("trainer")
        if not existing_trainer:
            self.insert_user("trainer", "trainerpass", "trainer")
            print("Default trainer created")

    
    def drop_all_tables(self):
        """
        Cancella tutte le tabelle create da `create_all_tables()`.

        • Se la connessione è chiusa la apre e in coda la richiude.
        • Disattiva i vincoli FK durante il DROP per evitare errori.
        • Ricorda di aggiornare la lista se in futuro aggiungerai altre tabelle.
        """
        opened_here = False
        if self.conn is None:
            self.open_connection()
            opened_here = True

        self.conn.execute("PRAGMA foreign_keys = OFF;")

        # Ordine: prima quelle con più dipendenze, poi le master
        tables = [
            "exercise_logs",
            "workout_sessions",
            "workout_plan_exercises",
            "workout_exercises",
            "workout_plans",
            "exercise_muscle_groups",
            "exercise",
            "media",
            "machines",
            "exercise_difficulty",
            "exercise_objectives",
            "muscle_groups",
            "jwt_sessions",
            "user_profiles",
            "notifications",
            "users",
        ]

        for tbl in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS `{tbl}`;")

        self.conn.commit()
        self.conn.execute("PRAGMA foreign_keys = ON;")

        if opened_here:
            self.close_connection()
    
    # Gestione utenti
    def get_user_by_username(self, username):
        """Get a user by username"""
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def insert_user(self, username, password, role, trainer_id=None):
        """Insert a new user into the database"""
        # Controlla se l'username esiste già
        if self.get_user_by_username(username):
            print(f"User '{username}' already exists.")
            return None

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Inserisci l'utente
        if role == 'client' and trainer_id:
            self.cursor.execute("""
                INSERT INTO users (username, password, role, trainer_id)
                VALUES (?, ?, ?, ?)
            """, (username, hashed_password.decode('utf-8'), role, trainer_id))
        else:
            self.cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, hashed_password.decode('utf-8'), role))

        self.conn.commit()
        return self.cursor.lastrowid

    def verify_password(self, username, password):
        """Verify user password"""
        user = self.get_user_by_username(username)
        if not user:
            return False
            
        stored_password = user['password']
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))

    def authenticate_user(self, username, password):
        """Authenticate a user and return user info if successful"""
        if self.verify_password(username, password):
            return self.get_user_by_username(username)
        return None

    

    def create_notification(self, user_id, type, message):
        """Crea una nuova notifica"""
        self.cursor.execute("""
            INSERT INTO notifications (user_id, type, message)
            VALUES (?, ?, ?)
        """, (user_id, type, message))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_client_progress(self, client_id, start_date, end_date):
        """Recupera i progressi del cliente in un intervallo di date"""
        self.cursor.execute("""
            SELECT 
                e.name as exercise_name,
                el.completed_at,
                el.reps,
                el.weight,
                el.duration
            FROM exercise_logs el
            JOIN workout_sessions ws ON el.session_id = ws.id
            JOIN workout_plans wp ON ws.workout_plan_id = wp.id
            JOIN exercise e ON el.exercise_id = e.id
            WHERE wp.client_id = ?
            AND el.completed_at BETWEEN ? AND ?
            ORDER BY el.completed_at DESC
        """, (client_id, start_date, end_date))
        
        return [dict(row) for row in self.cursor.fetchall()]

    def get_exercise_statistics(self, exercise_id, client_id=None):
        """Recupera statistiche per un esercizio specifico"""
        query = """
            SELECT 
                AVG(el.reps) as avg_reps,
                MAX(el.reps) as max_reps,
                AVG(el.weight) as avg_weight,
                MAX(el.weight) as max_weight,
                AVG(el.duration) as avg_duration,
                COUNT(DISTINCT ws.id) as total_sessions
            FROM exercise_logs el
            JOIN workout_sessions ws ON el.session_id = ws.id
            JOIN workout_plans wp ON ws.workout_plan_id = wp.id
            WHERE el.exercise_id = ?
        """
        
        params = [exercise_id]
        if client_id:
            query += " AND wp.client_id = ?"
            params.append(client_id)
            
        self.cursor.execute(query, params)
        return dict(self.cursor.fetchone())

    def verify_workout_session(self, session_id, user_id):
        """Verifica che una sessione appartenga a un cliente"""
        self.cursor.execute("""
            SELECT 1
            FROM workout_sessions ws
            JOIN workout_plans wp ON ws.workout_plan_id = wp.id
            WHERE ws.id = ? AND wp.client_id = ?
        """, (session_id, user_id))
        
        return bool(self.cursor.fetchone())

    def get_workout_plan_exercises(self, plan_id):
        """Recupera tutti gli esercizi di una scheda"""
        self.cursor.execute("""
            SELECT 
                e.id,
                e.name,
                e.description,
                we.repetitions,
                we.execution_time,
                we.sets,
                we.rest_time,
                we.suggested_weight,
                m.name as machine_name,
                d.level as difficulty,
                o.name as objective,
                med.url as media_url
            FROM workout_exercises we
            JOIN exercise e ON we.exercise_id = e.id
            LEFT JOIN machines m ON we.machine_id = m.id
            LEFT JOIN exercise_difficulty d ON e.difficulty_id = d.id
            LEFT JOIN exercise_objectives o ON e.objective_id = o.id
            LEFT JOIN media med ON e.media_id = med.id
            WHERE we.workout_plan_id = ?
            ORDER BY we.order_position
        """, (plan_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    
    def get_client_workout_plans(self, client_id:int, include_archived=True):
        self.cursor.execute(f"""
            SELECT
                wp.id,
                COALESCE(wp.name, 'Scheda del ' || DATE(wp.created_at)) AS name,
                wp.created_at,
                t.username AS trainer_name
            FROM workout_plans wp
            JOIN users t ON t.id = wp.trainer_id
            WHERE wp.client_id = ?
            {'AND wp.archived = 0' if not include_archived else ''}
            ORDER BY wp.created_at DESC
        """, (client_id,))
        return [dict(r) for r in self.cursor.fetchall()]
    
    
    
    def count_trainer_clients(self, trainer_id):
        """Numero di clienti assegnati a questo trainer."""
        self.cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM users
            WHERE role = 'client' AND trainer_id = ?
        """, (trainer_id,))
        return self.cursor.fetchone()["cnt"]

    def count_workouts_by_trainer(self, trainer_id):
        """Numero di workout creati da questo trainer."""
        self.cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM workout_plans
            WHERE trainer_id = ?
        """, (trainer_id,))
        return self.cursor.fetchone()["cnt"]

    def count_exercises(self):
        """Numero totale di esercizi disponibili."""
        self.cursor.execute("SELECT COUNT(*) AS cnt FROM exercise")
        return self.cursor.fetchone()["cnt"]
    
    
    def get_trainer_clients(self, trainer_id):
        """
        Restituisce la lista di clienti assegnati a un trainer specifico.
        Ogni elemento è un dict con 'id' e 'username'.
        """
        self.cursor.execute("""
            SELECT id, username
            FROM users
            WHERE role = 'client' AND trainer_id = ?
            ORDER BY username
        """, (trainer_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_filtered_exercises(self, filters):
        """
        Restituisce gli esercizi filtrati per gruppo muscolare, obiettivo e difficoltà.
        filters è un dict con chiavi 'muscle_group', 'objective', 'difficulty'.
        """
        query = """
            SELECT DISTINCT 
                e.id, e.name, e.description,
                o.name   AS objective,
                d.level  AS difficulty
            FROM exercise e
            LEFT JOIN exercise_objectives o
                ON e.objective_id = o.id
            LEFT JOIN exercise_difficulty d
                ON e.difficulty_id = d.id
            LEFT JOIN exercise_muscle_groups emg
                ON e.id = emg.exercise_id
            LEFT JOIN muscle_groups mg
                ON emg.muscle_group_id = mg.id
            WHERE 1=1
        """
        params = []

        if filters.get('muscle_group'):
            query += " AND mg.name = ?"
            params.append(filters['muscle_group'])
        if filters.get('objective'):
            query += " AND o.name = ?"
            params.append(filters['objective'])
        if filters.get('difficulty'):
            query += " AND d.level = ?"
            params.append(filters['difficulty'])

        query += " ORDER BY e.name"

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_objectives(self):
        self.cursor.execute("SELECT * FROM exercise_objectives ORDER BY name")
        print("ciao")
        return [dict(r) for r in self.cursor.fetchall()]

    def get_all_difficulties(self):
        self.cursor.execute("SELECT * FROM exercise_difficulty ORDER BY level")
        return [dict(r) for r in self.cursor.fetchall()]
    
    def get_all_muscle_groups(self):
        """
        Ritorna tutti i gruppi muscolari ordinati per nome.
        Usato da /api/muscle-groups.
        """
        self.cursor.execute("""
            SELECT id, name
            FROM muscle_groups
            ORDER BY name
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    
    def _resolve_or_insert_machine(self, machine_name: str | None) -> str | None:
        """
        Se machine_name è passato, lo inserisce in 'machines' (se non esiste)
        e ritorna lo stesso nome; altrimenti None.
        """
        if not machine_name:
            return None
        self.cursor.execute("INSERT OR IGNORE INTO machines (name) VALUES (?)",
                            (machine_name,))
        return machine_name


    def _insert_media(self, video_url: str | None) -> int | None:
        """Inserisce il video (se presente) in 'media' e torna media_id."""
        if not video_url:
            return None
        self.cursor.execute(
            "INSERT INTO media (url, type) VALUES (?, 'video')", (video_url,))
        return self.cursor.lastrowid


    def _write_exercise_groups(self, ex_id: int,
                            primary: list[str], secondary: list[str]):
        """Sovrascrive i (primary/secondary) gruppi associati a ex_id."""
        cur = self.cursor
        cur.execute("DELETE FROM exercise_muscle_groups WHERE exercise_id=?", (ex_id,))

        def link(names, is_primary: bool):
            for name in names:
                cur.execute("SELECT id FROM muscle_groups WHERE name=?", (name,))
                row = cur.fetchone()
                if row:
                    cur.execute("""
                        INSERT INTO exercise_muscle_groups
                            (exercise_id, muscle_group_id, is_primary)
                        VALUES (?,?,?)
                    """, (ex_id, row["id"], int(is_primary)))

        link(primary,   True)
        link(secondary, False)


    # ------------------------------------------------------------------
    #  INSERT
    # ------------------------------------------------------------------
    def add_exercise(self, data: dict) -> int:
        """
        Crea un nuovo esercizio.

        data contiene TUTTI i campi del form:
        - name, description, objective, difficulty, video_url, machine_name
        - checkbox requires_*
        - primary_groups[], secondary_groups[]
        Restituisce l'id del nuovo esercizio.
        """
        # ---------- normalizza: liste ➜ scalari ----------
        scalars = ['name', 'description', 'objective', 'difficulty',
                'video_url', 'machine_name']
        for k in scalars:
            if isinstance(data.get(k), list):
                data[k] = data[k][0]          # prende il primo valore

        flags = ['requires_repetitions', 'requires_sets', 'requires_duration',
                'requires_rest', 'requires_machine', 'requires_weight']
        for f in flags:
            v = data.get(f)
            data[f] = bool(v and (v[0] if isinstance(v, list) else v))

        for grp in ('primary_groups', 'secondary_groups'):
            if isinstance(data.get(grp), str):
                data[grp] = [data[grp]]

        # ---------- resolve FK objective / difficulty ----------
        objective_id = None
        if data.get('objective'):
            self.cursor.execute(
                "SELECT id FROM exercise_objectives WHERE name=?",
                (data['objective'],)
            )
            row = self.cursor.fetchone()
            objective_id = row['id'] if row else None

        difficulty_id = None
        if data.get('difficulty'):
            self.cursor.execute(
                "SELECT id FROM exercise_difficulty WHERE level=?",
                (data['difficulty'],)
            )
            row = self.cursor.fetchone()
            difficulty_id = row['id'] if row else None

        # ---------- insert exercise ----------
        self.cursor.execute("""
            INSERT INTO exercise
            (name, description, objective_id, difficulty_id, media_url,
            requires_repetitions, requires_duration, requires_rest,
            requires_sets, requires_machine, requires_weight)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data['name'],
            data.get('description', ''),
            objective_id,
            difficulty_id,
            data.get('video_url') or None,          # media_url
            int(data['requires_repetitions']),
            int(data['requires_duration']),
            int(data['requires_rest']),
            int(data['requires_sets']),
            int(data['requires_machine']),
            int(data['requires_weight']),
        ))
        ex_id = self.cursor.lastrowid

        # ---------- gruppi muscolari ----------
        self._write_exercise_groups(
            ex_id,
            data.get('primary_groups', []),
            data.get('secondary_groups', [])
        )

        self.conn.commit()
        return ex_id


    # ──────────────────────────────────────────────────────────────
    #  UPDATE
    # ──────────────────────────────────────────────────────────────
    def update_exercise(self, exercise_id: int, data: dict) -> bool:
        """
        Aggiorna TUTTI i campi dell'esercizio e sovrascrive i gruppi muscolari.
        Ritorna True se l'update è andato a buon fine.
        """
        # esiste?
        self.cursor.execute("SELECT 1 FROM exercise WHERE id=?", (exercise_id,))
        if not self.cursor.fetchone():
            return False

        # ---------- normalizza (stesso schema di add_exercise) ----------
        scalars = ['name', 'description', 'objective', 'difficulty',
                'video_url', 'machine_name']
        for k in scalars:
            if isinstance(data.get(k), list):
                data[k] = data[k][0]

        flags = ['requires_repetitions', 'requires_sets', 'requires_duration',
                'requires_rest', 'requires_machine', 'requires_weight']
        for f in flags:
            v = data.get(f)
            data[f] = bool(v and (v[0] if isinstance(v, list) else v))

        for grp in ('primary_groups', 'secondary_groups'):
            if isinstance(data.get(grp), str):
                data[grp] = [data[grp]]

        # ---------- resolve FK ----------
        objective_id = None
        if data.get('objective'):
            self.cursor.execute(
                "SELECT id FROM exercise_objectives WHERE name=?",
                (data['objective'],)
            )
            row = self.cursor.fetchone()
            objective_id = row['id'] if row else None

        difficulty_id = None
        if data.get('difficulty'):
            self.cursor.execute(
                "SELECT id FROM exercise_difficulty WHERE level=?",
                (data['difficulty'],)
            )
            row = self.cursor.fetchone()
            difficulty_id = row['id'] if row else None

        media_url = data.get('video_url') or None

        # ---------- update ----------
        self.cursor.execute("""
            UPDATE exercise
            SET name                 = ?,
                description          = ?,
                objective_id         = ?,
                difficulty_id        = ?,
                media_url            = ?,   -- salva direttamente l'URL
                requires_repetitions = ?,
                requires_duration    = ?,
                requires_rest        = ?,
                requires_sets        = ?,
                requires_machine     = ?,
                requires_weight      = ?
            WHERE id = ?
        """, (
            data['name'],
            data.get('description', ''),
            objective_id,
            difficulty_id,
            media_url,
            int(data['requires_repetitions']),
            int(data['requires_duration']),
            int(data['requires_rest']),
            int(data['requires_sets']),
            int(data['requires_machine']),
            int(data['requires_weight']),
            exercise_id
        ))

        # ---------- gruppi ----------
        self._write_exercise_groups(
            exercise_id,
            data.get('primary_groups', []),
            data.get('secondary_groups', [])
        )

        self.conn.commit()
        return True


    # ──────────────────────────────────────────────────────────────
    #  DELETE
    # ──────────────────────────────────────────────────────────────
    def delete_exercise(self, exercise_id: int) -> bool:
        """
        Elimina l'esercizio e i relativi link nei gruppi muscolari.
        """
        self.cursor.execute("SELECT 1 FROM exercise WHERE id=?", (exercise_id,))
        if not self.cursor.fetchone():
            return False

        self.cursor.execute(
            "DELETE FROM exercise_muscle_groups WHERE exercise_id=?",
            (exercise_id,))
        self.cursor.execute(
            "DELETE FROM exercise WHERE id=?",
            (exercise_id,))
        self.conn.commit()
        return True
    
    
    def get_trainer_clients(self, trainer_id):
        """
        Ritorna tutti i clienti assegnati al trainer con id = trainer_id.
        Usato da GET /api/trainer/clients
        """
        self.cursor.execute("""
            SELECT id, username
            FROM users
            WHERE role = 'client' AND trainer_id = ?
            ORDER BY username
        """, (trainer_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def seed_clients_for_trainer(self, trainer_id, clients):
        """
        Inserisce una lista di (username, password) come client assegnati
        al trainer con ID = trainer_id. Skippa quelli già esistenti.
        """
        # Assicurati di avere connessione aperta
        if not self.conn:
            self.open_connection()

        for username, password in clients:
            # Se l’utente non esiste ancora
            if not self.get_user_by_username(username):
                self.insert_user(
                    username=username,
                    password=password,
                    role='client',
                    trainer_id=trainer_id
                )

        # Se l’avevi aperta qui, la chiudi
        self.close_connection()
    
    def create_client(self, username, password, trainer_id):
        """
        Crea un nuovo cliente assegnato al trainer.
        Ritorna l'id del nuovo cliente.
        """
        return self.insert_user(username=username,
                                password=password,
                                role='client',
                                trainer_id=trainer_id)

    def get_user_profile(self, user_id):
        self.cursor.execute("""
            SELECT first_name, last_name, email, birth_date, phone, address 
            FROM user_profiles 
            WHERE user_id = ?
        """, (user_id,))
        return dict(self.cursor.fetchone())

    def update_user_profile(self, user_id, profile_data):
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, first_name, last_name, email, birth_date, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                profile_data.get('first_name'),
                profile_data.get('last_name'),
                profile_data.get('email'),
                profile_data.get('birth_date'),
                profile_data.get('phone'),
                profile_data.get('address')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
        
    def seed_machines(self, machines):
        """
        Popola la tabella machines con i nomi passati.
        Usa INSERT OR IGNORE per non duplicare.
        """
        for name in machines:
            self.cursor.execute(
                "INSERT OR IGNORE INTO machines (name) VALUES (?)",
                (name,)
            )
        self.conn.commit()
        print("macchine")

    def seed_initial_exercises(self):
        """
        Popola la tabella `exercise` con alcuni esempi.
        Da quando il campo è diventato `media_url` (TEXT) salviamo
        direttamente l’URL, senza passare da `media`.
        """
        exercises = [
            {
                'name': 'Squat',
                'description': 'Accosciata con carico corporeo',
                'objective': 'Massa muscolare',
                'difficulty': 'Medio',
                'video_url': 'https://www.youtube.com/watch?v=aclHkVaku9U',
                'requires_repetitions': True,
                'requires_sets': True,
                'requires_duration': False,
                'requires_rest': True,
                'requires_machine': False,
                'requires_weight': True,
                'machine_name': None,
                'primary_groups': ['Quadricipiti', 'Glutei'],
                'secondary_groups': ['Femorali']
            },
            {
                'name': 'Push-up',
                'description': 'Flessioni a terra',
                'objective': 'Tonificazione',
                'difficulty': 'Facile',
                'video_url': 'https://www.youtube.com/watch?v=_l3ySVKYVJ8',
                'requires_repetitions': True,
                'requires_sets': True,
                'requires_duration': False,
                'requires_rest': True,
                'requires_machine': False,
                'requires_weight': False,
                'machine_name': None,
                'primary_groups': ['Pettorali', 'Tricipiti'],
                'secondary_groups': ['Spalle']
            },
            {
                'name': 'Leg Press',
                'description': 'Spinta gambe alla pressa',
                'objective': 'Massa muscolare',
                'difficulty': 'Medio',
                'video_url': 'https://www.youtube.com/watch?v=IZxyjW7MPJQ',
                'requires_repetitions': True,
                'requires_sets': True,
                'requires_duration': False,
                'requires_rest': True,
                'requires_machine': True,
                'requires_weight': True,
                'machine_name': 'Leg Press',
                'primary_groups': ['Quadricipiti'],
                'secondary_groups': ['Glutei', 'Femorali']
            },
            {
                'name': 'Tapis Roulant Running',
                'description': 'Corsa su tapis roulant',
                'objective': 'Cardio',
                'difficulty': 'Facile',
                'video_url': 'https://www.youtube.com/watch?v=QkN2Ota4Jx0',
                'requires_repetitions': False,
                'requires_sets': False,
                'requires_duration': True,
                'requires_rest': False,
                'requires_machine': True,
                'requires_weight': False,
                'machine_name': 'Tapis Roulant',
                'primary_groups': ['Cardio'],
                'secondary_groups': []
            },
            {
                'name': 'Plank',
                'description': 'Mantenimento posizione plank',
                'objective': 'Core',
                'difficulty': 'Medio',
                'video_url': 'https://www.youtube.com/watch?v=pSHjTRCQxIw',
                'requires_repetitions': False,
                'requires_sets': False,
                'requires_duration': True,
                'requires_rest': True,
                'requires_machine': False,
                'requires_weight': False,
                'machine_name': None,
                'primary_groups': ['Addominali'],
                'secondary_groups': []
            }
        ]

        for ex in exercises:
            # --- assicurati che la macchina esista (se richiesta) -------------
            self._resolve_or_insert_machine(ex.get('machine_name'))

            # --- foreign key objective / difficulty ---------------------------
            self.cursor.execute(
                "SELECT id FROM exercise_objectives WHERE name = ?",
                (ex['objective'],)
            )
            obj_row = self.cursor.fetchone()
            objective_id = obj_row['id'] if obj_row else None

            self.cursor.execute(
                "SELECT id FROM exercise_difficulty WHERE level = ?",
                (ex['difficulty'],)
            )
            diff_row = self.cursor.fetchone()
            difficulty_id = diff_row['id'] if diff_row else None

            # --- inserisci esercizio ------------------------------------------
            self.cursor.execute("""
                INSERT INTO exercise
                    (name, description, objective_id, difficulty_id, media_url,
                    requires_repetitions, requires_duration, requires_rest,
                    requires_sets, requires_machine, requires_weight)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                ex['name'], ex['description'], objective_id, difficulty_id,
                ex['video_url'],
                int(ex['requires_repetitions']), int(ex['requires_duration']),
                int(ex['requires_rest']), int(ex['requires_sets']),
                int(ex['requires_machine']), int(ex['requires_weight'])
            ))
            exercise_id = self.cursor.lastrowid

            # --- collega i gruppi muscolari -----------------------------------
            self._write_exercise_groups(
                exercise_id,
                ex.get('primary_groups', []),
                ex.get('secondary_groups', [])
            )

        self.conn.commit()    


    def delete_client(self, client_id: int):
        """
        Cancella il record dell'utente *e* eventuali dati correlati
        (workout plans, storico, ecc. se necessario).
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (client_id,))
        self.conn.commit()

    def verify_trainer_client(self, trainer_id: int, client_id: int) -> bool:
        """
        Verifica che il client con `client_id` sia effettivamente assegnato al
        trainer con `trainer_id`. Restituisce True se esiste, False altrimenti.
        """
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM users WHERE id = ? AND trainer_id = ?",
            (client_id, trainer_id)
        )
        found = cur.fetchone() is not None
        cur.close()
        return found
    


    def create_workout_plan(self, client_id: int, trainer_id: int, name: str, exercises: list[dict]) -> int:
        """
        Inserisce una nuova workout_plan e le relative righe in workout_plan_exercises.
        Usa sempre lo stesso cursor e lo chiude prima del commit, così non restano
        statement “in sospeso” che bloccano il commit.
        """
        # 1) prepara il cursor
        cur = self.conn.cursor()

        # 2) inserisci la pianificazione
        cur.execute(
            "INSERT INTO workout_plans (client_id, trainer_id, name) VALUES (?, ?, ?)",
            (client_id, trainer_id, name)
        )
        plan_id = cur.lastrowid

        # 3) inserisci ciascun esercizio
        for idx, ex in enumerate(exercises, start=1):
            cur.execute(
                """
                INSERT INTO workout_plan_exercises
                  (plan_id, exercise_id, machine, repetitions, exec_time_s,
                   sets, rest_s, suggested_kg, ord_idx)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    ex['exercise_id'],
                    ex.get('machine_id'),
                    ex.get('repetitions'),
                    ex.get('exec_time_s'),
                    ex.get('sets'),
                    ex.get('rest_s'),
                    ex.get('suggested_kg'),
                    idx
                )
            )

        # 4) chiudi il cursor prima del commit
        cur.close()

        # 5) commit pulito, non ci sono statement aperti in sospeso
        self.conn.commit()

        return plan_id

# --- READ ---
    def get_client_workout_plans(self, client_id:int, include_archived=True):
        cur = self.conn.cursor()
        query = "SELECT * FROM workout_plans WHERE client_id=?"
        if not include_archived:
            query += " AND archived=0"
        cur.execute(query + " ORDER BY created_at DESC", (client_id,))
        return [dict(row) for row in cur.fetchall()]

    def get_workout_plan(self, plan_id: int):
        """
        Ritorna una tupla (header, rows) dove:
        • header  = dict con le info principali della scheda
        • rows    = lista di dict già ordinati per ord_idx — ciascuno contiene:
            - campi workout_plan_exercises (sets, repetitions, exec_time_s, …)
            - nome esercizio, descrizione, media_url
            - objective, difficulty
            - flags requires_*
            - gruppi muscolari primari / secondari come stringhe
        """
        cur = self.conn.cursor()

        # ---------- HEADER ----------
        cur.execute("""
            SELECT wp.*, u.username AS trainer_name
            FROM workout_plans wp
            JOIN users u ON u.id = wp.trainer_id
            WHERE wp.id = ?
        """, (plan_id,))
        header = cur.fetchone()

        # ---------- BODY ----------
        cur.execute("""
            SELECT
                wpe.*,
                /* alias per compatibilità con il template ------------------- */
                wpe.exec_time_s          AS execution_time,
                wpe.rest_s               AS rest_time,
                wpe.suggested_kg         AS suggested_weight,

                /* dati dall’esercizio -------------------------------------- */
                e.name                   AS exercise_name,
                e.description,
                e.media_url,
                e.requires_repetitions,
                e.requires_sets,
                e.requires_duration,
                e.requires_rest,
                e.requires_machine,
                e.requires_weight,
                obj.name                 AS objective,
                diff.level               AS difficulty,
                m.name                   AS machine_name,

                /* gruppi muscolari primari / secondari --------------------- */
                IFNULL((
                SELECT GROUP_CONCAT(mg.name, ', ')
                FROM exercise_muscle_groups emg
                JOIN muscle_groups mg ON mg.id = emg.muscle_group_id
                WHERE emg.exercise_id = e.id AND emg.is_primary = 1
                ), '') AS primary_groups,

                IFNULL((
                SELECT GROUP_CONCAT(mg.name, ', ')
                FROM exercise_muscle_groups emg
                JOIN muscle_groups mg ON mg.id = emg.muscle_group_id
                WHERE emg.exercise_id = e.id AND emg.is_primary = 0
                ), '') AS secondary_groups

            FROM workout_plan_exercises      wpe
            JOIN exercise                    e   ON e.id  = wpe.exercise_id
            LEFT JOIN exercise_objectives    obj ON obj.id = e.objective_id
            LEFT JOIN exercise_difficulty    diff ON diff.id = e.difficulty_id
            LEFT JOIN machines               m   ON m.id  = wpe.machine
            WHERE wpe.plan_id = ?
            ORDER BY wpe.ord_idx
        """, (plan_id,))
        body = cur.fetchall()

        return (dict(header) if header else None,
                [dict(r) for r in body])

    # --- UPDATE ---
    def update_workout_plan(self, plan_id: int, name: str, exercises: list[dict]):
        cur = self.conn.cursor()

        # 1) aggiorna il nome della scheda
        cur.execute(
            "UPDATE workout_plans SET name = ? WHERE id = ?",
            (name, plan_id)
        )

        # 2) elimina le vecchie righe
        cur.execute(
            "DELETE FROM workout_plan_exercises WHERE plan_id = ?",
            (plan_id,)
        )

        # 3) reinserisci le righe aggiornate
        for idx, ex in enumerate(exercises, start=1):
            mc_id = ex.get("machine_id")            # ← ora la chiave è machine_id
            cur.execute(
                """INSERT INTO workout_plan_exercises
                    (plan_id, exercise_id, machine,       -- «machine» è la colonna del tuo schema
                    repetitions, exec_time_s,
                    sets,        rest_s,
                    suggested_kg, ord_idx)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    plan_id,
                    int(ex["exercise_id"]),
                    int(mc_id) if mc_id else None,   # None ⇒ NULL nel DB
                    ex.get("repetitions"),
                    ex.get("exec_time_s"),
                    ex.get("sets"),
                    ex.get("rest_s"),
                    ex.get("suggested_kg"),
                    idx
                )
            )

        self.conn.commit()

    # --- ARCHIVE/DELETE ---
    def archive_workout_plan(self, plan_id:int):
        self.conn.execute("UPDATE workout_plans SET archived=1 WHERE id=?", (plan_id,))
        self.conn.commit()

    def delete_workout_plan(self, plan_id:int):
        self.conn.execute("DELETE FROM workout_plan_exercises WHERE plan_id=?", (plan_id,))
        self.conn.execute("DELETE FROM workout_plans WHERE id=?", (plan_id,))
        self.conn.commit()

    def main(self):
         # 1) apro e creo lo schema
        self.open_connection()
        self.create_all_tables()
        # 2) assicuro che tutte le CREATE TABLE vengano committate
        self.conn.commit()

        # (opzionale) attivo WAL per ridurre i lock
        self.cursor.execute("PRAGMA journal_mode = WAL;")

        # 3) ora posso fare i seed senza incorrere in "database is locked"
        self.seed_machines([
            'Tapis Roulant', 'Leg Press', 'Lat Machine', 'Smith Machine',
          'Panca Piana', 'Panca Inclinata', 'Cavi', 'Dip Station',
            'Kettlebell', 'Panca Scott', 'Ellittica', 'Cyclette'
        ])
        print("macchine seedate")
        self.seed_initial_exercises()

        # 4) chiudo finalmente la connessione
        self.close_connection()


    def get_user(self, user_id: int):
        """
        Ritorna un dict con tutte le colonne della tabella 'users'
        per lo user_id indicato, oppure None se non esiste.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_exercises(self, order_by: str = "name"):
        """
        Restituisce tutti gli esercizi con nome, obiettivo e difficoltà.
        Ora chiude il cursor subito dopo il fetch.
        """
        allowed = {"name", "id", "difficulty"}
        if order_by not in allowed:
            order_by = "name"

        cur = self.conn.cursor()
        cur.execute(f"""
            SELECT 
                e.*,
                o.name  AS objective,
                d.level AS difficulty
            FROM exercise e
            LEFT JOIN exercise_objectives o ON e.objective_id  = o.id
            LEFT JOIN exercise_difficulty d ON e.difficulty_id = d.id
            ORDER BY e.{order_by}
        """)
        rows = cur.fetchall()
        cur.close()                   # <— chiudo il cursor qui
        return [dict(r) for r in rows]
    
    def get_machine_list(self):
        """
        Restituisce la lista delle macchine ordinate per nome.
        Ora chiude il cursor subito dopo il fetch.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM machines ORDER BY name")
        rows = cur.fetchall()
        cur.close()                   # <— chiudo il cursor qui
        return [dict(r) for r in rows]
    
    
    
    
    
    def get_exercise_by_id(self, ex_id):
        self.cursor.execute("SELECT * FROM exercise WHERE id=?", (ex_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    
    def get_exercise_groups(self, ex_id):
        self.cursor.execute("""
            SELECT mg.name, emg.is_primary
            FROM exercise_muscle_groups emg
            JOIN muscle_groups mg ON mg.id = emg.muscle_group_id
            WHERE emg.exercise_id = ?
        """, (ex_id,))
        prim, sec = [], []
        for r in self.cursor.fetchall():
            (prim if r['is_primary'] else sec).append(r['name'])
        return prim, sec

    def _write_exercise_groups(self, ex_id: int,
                           primary: list[str], secondary: list[str]):
        """Sovrascrive i gruppi muscolari associati a un esercizio."""
        cur = self.conn.cursor()
        # 1) cancella vecchi link
        cur.execute("DELETE FROM exercise_muscle_groups WHERE exercise_id = ?", (ex_id,))

        # 2) reinserisci
        def _link(group_names, is_primary: bool):
            for name in group_names:
                cur.execute("SELECT id FROM muscle_groups WHERE name = ?", (name,))
                row = cur.fetchone()
                if row:                                       # solo se il gruppo esiste
                    cur.execute("""
                        INSERT INTO exercise_muscle_groups
                            (exercise_id, muscle_group_id, is_primary)
                        VALUES (?,?,?)
                    """, (ex_id, row["id"], int(is_primary)))

        _link(primary,   True)
        _link(secondary, False)
        self.conn.commit()
        
    def _insert_media(self, video_url):
        if not video_url:          # None o ''  ➜  no insert
            return None
        self.cursor.execute(
            "INSERT INTO media (url, type) VALUES (?, 'video')", (video_url,))
        return self.cursor.lastrowid
    
    def alterTable(self):
        self.cursor.execute("""
            ALTER TABLE exercise ADD COLUMN media_url TEXT;
        """)
        self.conn.commit()
        
        
    
        
        
    def add_machines(self, names: list[str]) -> None:
        """
        Aggiunge alla tabella `machines` tutti i nomi in `names`,
        ignorando quelli già presenti (INSERT OR IGNORE),
        e fa subito il commit.
        """
        for name in names:
            self.cursor.execute(
                "INSERT OR IGNORE INTO machines (name) VALUES (?)",
                (name,)
            )
        self.conn.commit()
        
    def seed_default_machines(self) -> None:
        """
        Popola la tabella `machines` con la lista di default
        usata dal progetto.
        """
        default_machines = [
            'Tapis Roulant', 'Leg Press', 'Lat Machine', 'Smith Machine',
            'Panca Piana', 'Panca Inclinata', 'Cavi', 'Dip Station',
            'Kettlebell', 'Panca Scott', 'Ellittica', 'Cyclette'
        ]
        self.add_machines(default_machines)
        
        
    def list_machines(self):
        cur = self.conn.execute("SELECT * FROM machines ORDER BY name")
        return [dict(row) for row in cur]

    def get_machine(self, mid: int):
        cur = self.conn.execute("SELECT * FROM machines WHERE id=?", (mid,))
        row = cur.fetchone()
        return dict(row) if row else None

    def create_machine(self, name: str, description: str | None = None):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO machines (name, description) VALUES (?, ?)",
            (name, description)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_machine(self, mid: int, name: str, description: str | None = None):
        self.conn.execute(
            "UPDATE machines SET name=?, description=? WHERE id=?",
            (name, description, mid)
        )
        self.conn.commit()

    def delete_machine(self, mid: int):
        self.conn.execute("DELETE FROM machines WHERE id=?", (mid,))
        self.conn.commit()
        
        
    def count_machines(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM machines")
        return cur.fetchone()[0]
    
    def update_plan_row_from_client(self, row_id: int, vals: dict):
        """
        Aggiorna gli unici campi che il cliente è autorizzato a toccare.
        `vals` è un dict con (eventualmente) repetitions, sets, exec_time_s,
        rest_s, suggested_kg – tutti opzionali, possono valere None.
        """
        self.conn.execute(
            """UPDATE workout_plan_exercises
                SET repetitions  = ?,
                    sets         = ?,
                    exec_time_s  = ?,
                    rest_s       = ?,
                    suggested_kg = ?
                WHERE id = ?""",
            (
                vals.get("repetitions"),
                vals.get("sets"),
                vals.get("exec_time_s"),
                vals.get("rest_s"),
                vals.get("suggested_kg"),
                row_id
            )
        )
        self.conn.commit()
    
if __name__ == "__main__":
    db = GymDatabaseManager()
    
    db.main()
    
    