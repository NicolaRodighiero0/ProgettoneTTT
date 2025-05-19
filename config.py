import os

# Percorso al database SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'db', 'gym_database.db')

# Chiave segreta di Flask per sessioni
SECRET_KEY = os.environ.get('SECRET_KEY', 'una_chiave_casuale_sicura_e_privata')

# Configurazione JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'una_chiave_lunga_e_casuale_per_jwt')
# Durata del token di accesso (in secondi)
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 ora

# Configurazioni CORS (API)
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# DEBUG mode
DEBUG = True