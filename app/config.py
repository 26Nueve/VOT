"""
Configuration centralisée de l'application.

Ce fichier charge toutes les variables d'environnement depuis le fichier .env
et les rend accessibles partout dans l'application.

Pourquoi utiliser pydantic-settings ?
- Validation automatique des types
- Valeurs par défaut
- Documentation intégrée
- Détection des variables manquantes
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Classe de configuration de l'application.
    
    Toutes les variables sont chargées depuis .env automatiquement.
    Si une variable obligatoire manque, une erreur sera levée au démarrage.
    """
    
    # === API AMADEUS ===
    amadeus_api_key: str
    amadeus_api_secret: str
    
    # === DISCORD ===
    discord_webhook_url: str
    
    # === BASE DE DONNÉES ===
    database_url: str = "sqlite:///./flight_deals.db"
    
    # === PARAMÈTRES DE RECHERCHE ===
    departure_airport: str = "GVA"
    
    # Convertit automatiquement la chaîne "TYO,PEK,HAN" en liste ["TYO", "PEK", "HAN"]
    destinations: str = "TYO,PEK,HAN,BKK,KUL,CGK"
    
    min_trip_duration: int = 7
    max_trip_duration: int = 14
    search_window_months: int = 6
    max_stopovers: int = 1
    
    # === SCORING ===
    min_score_threshold: float = 70.0
    
    # === SCHEDULER ===
    search_frequency_hours: int = 6
    
    # === APPLICATION ===
    app_port: int = 8000
    debug: bool = True
    
    class Config:
        """Configuration de Pydantic"""
        env_file = ".env"  # Charge automatiquement le fichier .env
        env_file_encoding = "utf-8"
        case_sensitive = False  # Les variables peuvent être en majuscules ou minuscules
    
    @property
    def destinations_list(self) -> List[str]:
        """
        Convertit la chaîne de destinations en liste.
        
        Exemple: "TYO,PEK,HAN" → ["TYO", "PEK", "HAN"]
        """
        return [dest.strip() for dest in self.destinations.split(",")]


# Instance unique de configuration accessible partout dans l'app
settings = Settings()


# Fonction utilitaire pour afficher la config (masque les secrets)
def display_config():
    """Affiche la configuration au démarrage (masque les secrets)"""
    print("=" * 60)
    print("📋 CONFIGURATION DE L'APPLICATION")
    print("=" * 60)
    print(f"🛫 Aéroport de départ : {settings.departure_airport}")
    print(f"🌏 Destinations : {', '.join(settings.destinations_list)}")
    print(f"📅 Durée séjour : {settings.min_trip_duration}-{settings.max_trip_duration} jours")
    print(f"🔍 Fenêtre recherche : {settings.search_window_months} mois")
    print(f"✈️  Escales max : {settings.max_stopovers}")
    print(f"⭐ Score min notification : {settings.min_score_threshold}")
    print(f"⏱️  Fréquence recherche : toutes les {settings.search_frequency_hours}h")
    print(f"💾 Base de données : {settings.database_url.split(':')[0].upper()}")
    print(f"🔑 Amadeus API : {'✅ Configurée' if settings.amadeus_api_key else '❌ Manquante'}")
    print(f"💬 Discord Webhook : {'✅ Configuré' if settings.discord_webhook_url else '❌ Manquant'}")
    print("=" * 60)
