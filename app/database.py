"""
Gestion de la connexion à la base de données avec SQLAlchemy.

SQLAlchemy est un ORM (Object-Relational Mapping) qui permet de :
- Manipuler la base de données avec des objets Python au lieu de SQL brut
- Changer facilement de moteur de BDD (SQLite → PostgreSQL)
- Gérer automatiquement les migrations

Concepts clés :
- Engine : Connexion à la base de données
- SessionLocal : Fabrique de sessions pour interagir avec la BDD
- Base : Classe de base pour tous les modèles
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# === CRÉATION DU MOTEUR DE BASE DE DONNÉES ===

# Pour SQLite, on ajoute check_same_thread=False pour permettre l'usage multi-thread
# Pour PostgreSQL, ces arguments ne sont pas nécessaires
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug  # Affiche les requêtes SQL en mode debug
)

# === SESSION FACTORY ===
# Chaque fois qu'on veut interagir avec la BDD, on crée une session

SessionLocal = sessionmaker(
    autocommit=False,  # On gère manuellement les commits
    autoflush=False,   # On gère manuellement les flush
    bind=engine
)

# === CLASSE DE BASE POUR LES MODÈLES ===
# Tous les modèles (tables) hériteront de cette classe

Base = declarative_base()


# === FONCTION UTILITAIRE : RÉCUPÉRER UNE SESSION ===
def get_db():
    """
    Générateur de session de base de données.
    
    Utilisation dans FastAPI :
    
    @app.get("/deals")
    def get_deals(db: Session = Depends(get_db)):
        return db.query(Flight).all()
    
    Le 'yield' permet de :
    1. Créer une session
    2. La passer à la fonction
    3. Fermer automatiquement la session après usage
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === FONCTION : CRÉER LES TABLES ===
def create_tables():
    """
    Crée toutes les tables définies dans les modèles.
    
    À appeler au démarrage de l'application.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tables de base de données créées avec succès")


# === FONCTION : VIDER LA BASE (ATTENTION !) ===
def drop_all_tables():
    """
    Supprime toutes les tables (utile pour reset en développement).
    
    ⚠️ NE JAMAIS UTILISER EN PRODUCTION !
    """
    Base.metadata.drop_all(bind=engine)
    print("🗑️  Toutes les tables ont été supprimées")
