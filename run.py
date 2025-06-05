from app import create_app
from app.models.gym_database import GymDatabaseManager

# prima di creare l'app facciamo partire la creazione delle tabelle
db = GymDatabaseManager()
db.open_connection()
db.drop_all_tables()
db.create_all_tables()
db.seed_initial_exercises()

db.seed_default_machines()
db.seed_clients_for_trainer(1, [
    ('alice', 'alicepass'),
    ('bob',   'bobpass'),
]) 
db.close_connection()

#utenti di debug



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)