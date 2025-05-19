import sqlite3
import bcrypt
import os
class GymDatabaseManager:
    def __init__(self, db_name='gym_database.db'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(base_dir, db_name)
        self.conn = None
        self.cursor = None


    def open_connection(self):
        self.conn = sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None  


    def create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('trainer', 'client')) NOT NULL
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
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
    """)


    def create_muscle_groups_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS muscle_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)

    def create_objectives_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)     

    def create_difficulty_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_difficulty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL UNIQUE CHECK(level IN ('Facile', 'Medio', 'Difficile'))
            );
        """)

    def create_machines_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)

    def create_media_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL
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
                media_id INTEGER,
                FOREIGN KEY (objective_id) REFERENCES exercise_objectives(id),
                FOREIGN KEY (difficulty_id) REFERENCES exercise_difficulty(id),
                FOREIGN KEY (media_id) REFERENCES media(id)
            );
        """)   


    def create_exercise_parameters_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_parameters (
                exercise_id INTEGER PRIMARY KEY,
                duration_seconds INTEGER,        
                repetitions INTEGER,             
                rest_seconds INTEGER,            
                sets INTEGER,                    
                weight_kg REAL,                  
                uses_machine BOOLEAN,            
                FOREIGN KEY (exercise_id) REFERENCES exercise(id)
            );
        """)


    def create_workout_plans_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                trainer_id INTEGER,
                date_created DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (client_id) REFERENCES users(id),
                FOREIGN KEY (trainer_id) REFERENCES users(id)
            );
        """)


    def create_workout_exercises_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_plan_id INTEGER,
                exercise_id INTEGER,
                machine_id INTEGER,
                repetitions INTEGER,
                execution_time INTEGER,
                sets INTEGER,
                rest_time INTEGER,
                suggested_weight REAL,
                FOREIGN KEY (workout_plan_id) REFERENCES workout_plans(id),
                FOREIGN KEY (exercise_id) REFERENCES exercise(id),
                FOREIGN KEY (machine_id) REFERENCES machines(id)
            );
        """)

    def create_all_tables(self):
        self.create_users_table()
        self.create_jwt_sessions_table()
        self.create_muscle_groups_table()
        self.create_objectives_table()
        self.create_machines_table()
        self.create_difficulty_table()
        self.create_media_table()
        self.create_exercises_table()
        self.create_exercise_parameters_table()
        self.create_workout_plans_table()
        self.create_workout_exercises_table()
        


        

        print("Tutte le tabelle sono state create")

    
    def get_user_by_username(self, username: str):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def insert_user(self, username: str, password: str, role: str):
        # Controllo se l'utente esiste già
        if self.get_user_by_username(username):
            print(f"L'utente '{username}' esiste già.")
            return None

        # Hash della password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserimento nel database
        self.cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, hashed_password.decode('utf-8'), role))

        self.conn.commit()
        print(f"Utente '{username}' inserito con successo.")
        return self.cursor.lastrowid



    def main(self):
        self.open_connection()
        self.create_all_tables()
        

        existing_trainer = self.get_user_by_username("trainer")
        if not existing_trainer:
            trainer_id = self.insert_user("trainer", "trainerpass", "trainer")
            print(f"Trainer inserito con ID: {trainer_id}")
        else:
            print("Trainer già presente nel database.")

        self.close_connection()    

if __name__ == "__main__":
    db = GymDatabaseManager()
    db.main()
    