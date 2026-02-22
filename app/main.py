"""
Application FastAPI principale.

Point d'entrée de l'application :
- Initialise FastAPI
- Configure les routes
- Démarre le scheduler
- Sert l'interface web
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings, display_config
from app.database import create_tables
from app.routers import deals
from app.scheduler.tasks import search_and_save_flights


# === GESTION DU LIFECYCLE (SCHEDULER) ===
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application.
    
    Au démarrage :
    - Affiche la configuration
    - Crée les tables de BDD
    - Démarre le scheduler
    
    À l'arrêt :
    - Arrête le scheduler proprement
    """
    
    # === DÉMARRAGE ===
    print("\n🚀 Démarrage de l'application...")
    
    # Afficher la config
    display_config()
    
    # Créer les tables
    create_tables()
    
    # Démarrer le scheduler
    print(f"\n⏰ Démarrage du scheduler (recherche toutes les {settings.search_frequency_hours}h)...")
    
    # Ajouter la tâche de recherche
    scheduler.add_job(
        search_and_save_flights,
        'interval',
        hours=settings.search_frequency_hours,
        id='search_flights',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler démarré\n")
    
    yield  # L'application tourne ici
    
    # === ARRÊT ===
    print("\n🛑 Arrêt de l'application...")
    scheduler.shutdown()
    print("✅ Scheduler arrêté\n")


# === CRÉATION DE L'APPLICATION FASTAPI ===
app = FastAPI(
    title="Flight Deal Tracker",
    description="Surveillance automatique des meilleurs deals de vols",
    version="1.0.0",
    lifespan=lifespan
)


# === CONFIGURATION DES TEMPLATES ===
templates = Jinja2Templates(directory="app/templates")


# === ROUTES ===

# Inclure les routes API
app.include_router(deals.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Page d'accueil avec l'interface web.
    
    Affiche la liste des deals avec filtres.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que l'app fonctionne.
    
    Utile pour les déploiements (Render, Railway, etc.)
    """
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "next_search": scheduler.get_jobs()[0].next_run_time.isoformat() if scheduler.get_jobs() else None
    }


@app.get("/api/info")
async def app_info():
    """
    Informations sur la configuration de l'application.
    
    Retourne les paramètres (sans les secrets).
    """
    return {
        "departure_airport": settings.departure_airport,
        "destinations": settings.destinations_list,
        "trip_duration": f"{settings.min_trip_duration}-{settings.max_trip_duration} jours",
        "search_window": f"{settings.search_window_months} mois",
        "max_stopovers": settings.max_stopovers,
        "min_score_threshold": settings.min_score_threshold,
        "search_frequency": f"{settings.search_frequency_hours} heures"
    }


# === GESTION DES ERREURS ===

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Gestion des erreurs 404"""
    return {"error": "Route non trouvée", "path": str(request.url)}


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Gestion des erreurs 500"""
    return {"error": "Erreur serveur", "detail": str(exc)}


# === MESSAGE DE BIENVENUE ===
@app.on_event("startup")
async def startup_message():
    """Affiche un message au démarrage"""
    print("\n" + "="*70)
    print("✅ APPLICATION DÉMARRÉE AVEC SUCCÈS")
    print("="*70)
    print(f"🌐 Interface web : http://localhost:{settings.app_port}")
    print(f"📚 Documentation API : http://localhost:{settings.app_port}/docs")
    print(f"🔄 Prochaine recherche : dans {settings.search_frequency_hours}h")
    print("="*70 + "\n")
