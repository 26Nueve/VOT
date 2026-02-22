"""
Schémas Pydantic pour la validation des données.

Différence entre Model (SQLAlchemy) et Schema (Pydantic) :
- Model : Structure de la table en base de données
- Schema : Validation des données entrantes/sortantes dans l'API

Exemple d'usage :
- Créer un vol : FlightCreate (sans id, sans created_at)
- Lire un vol : FlightResponse (avec tous les champs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FlightBase(BaseModel):
    """Schéma de base partagé entre toutes les variations"""
    
    departure_airport: str = Field(..., min_length=3, max_length=3, description="Code IATA de départ (ex: GVA)")
    arrival_airport: str = Field(..., min_length=3, max_length=3, description="Code IATA d'arrivée (ex: TYO)")
    destination_city: Optional[str] = None
    
    departure_date: datetime
    return_date: datetime
    
    price: float = Field(..., gt=0, description="Prix en EUR")
    currency: str = "EUR"
    
    airline: Optional[str] = None
    flight_numbers: Optional[str] = None
    
    num_stops: int = Field(default=0, ge=0, le=3)
    total_duration_hours: Optional[float] = None
    
    score: Optional[float] = None
    booking_link: Optional[str] = None


class FlightCreate(FlightBase):
    """
    Schéma pour créer un nouveau vol.
    
    Hérite de FlightBase mais ajoute le hash unique.
    """
    unique_hash: str = Field(..., min_length=32, max_length=32)
    raw_data: Optional[str] = None


class FlightResponse(FlightBase):
    """
    Schéma pour renvoyer un vol via l'API.
    
    Inclut les champs générés automatiquement (id, created_at, etc.)
    """
    id: int
    unique_hash: str
    notified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Configuration Pydantic"""
        from_attributes = True  # Permet de convertir depuis un modèle SQLAlchemy


class FlightFilter(BaseModel):
    """
    Schéma pour filtrer les vols dans l'API.
    
    Tous les champs sont optionnels.
    """
    destination: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_score: Optional[float] = None
    only_not_notified: Optional[bool] = False
    limit: int = Field(default=50, le=200)
    
    
class FlightStats(BaseModel):
    """Statistiques sur les vols en base"""
    total_flights: int
    total_notified: int
    average_price: float
    best_score: float
    destinations_count: dict
