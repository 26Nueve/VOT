"""
Routes API pour consulter les deals de vols.

Endpoints disponibles :
- GET /deals : Liste tous les deals (avec filtres)
- GET /deals/{id} : Détails d'un deal spécifique
- GET /stats : Statistiques globales
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.flight import Flight
from app.schemas.flight import FlightResponse, FlightStats

router = APIRouter(prefix="/api", tags=["deals"])


@router.get("/deals", response_model=List[FlightResponse])
def get_deals(
    destination: Optional[str] = Query(None, description="Filtrer par code IATA destination"),
    min_score: Optional[float] = Query(None, description="Score minimum"),
    max_price: Optional[float] = Query(None, description="Prix maximum"),
    only_not_notified: bool = Query(False, description="Uniquement les non-notifiés"),
    limit: int = Query(50, le=200, description="Nombre maximum de résultats"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des deals avec filtres optionnels.
    
    Exemples d'utilisation :
    - /api/deals : Tous les deals
    - /api/deals?destination=TYO : Seulement Tokyo
    - /api/deals?min_score=80 : Seulement les excellents deals
    - /api/deals?max_price=500 : Maximum 500€
    """
    
    query = db.query(Flight)
    
    # Appliquer les filtres
    if destination:
        query = query.filter(Flight.arrival_airport == destination.upper())
    
    if min_score is not None:
        query = query.filter(Flight.score >= min_score)
    
    if max_price is not None:
        query = query.filter(Flight.price <= max_price)
    
    if only_not_notified:
        query = query.filter(Flight.notified == False)
    
    # Trier par score décroissant (meilleurs deals en premier)
    query = query.order_by(Flight.score.desc())
    
    # Limiter les résultats
    flights = query.limit(limit).all()
    
    return flights


@router.get("/deals/{flight_id}", response_model=FlightResponse)
def get_deal(flight_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails d'un deal spécifique.
    
    Args:
        flight_id: ID du vol
    
    Returns:
        Détails complets du vol
    
    Raises:
        404 si le vol n'existe pas
    """
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    
    if not flight:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vol non trouvé")
    
    return flight


@router.get("/stats", response_model=FlightStats)
def get_stats(db: Session = Depends(get_db)):
    """
    Récupère des statistiques globales sur les deals.
    
    Returns:
        Statistiques : total, moyenne prix, meilleur score, etc.
    """
    
    total_flights = db.query(Flight).count()
    total_notified = db.query(Flight).filter(Flight.notified == True).count()
    
    # Moyenne des prix
    avg_price = db.query(func.avg(Flight.price)).scalar() or 0
    
    # Meilleur score
    best_score = db.query(func.max(Flight.score)).scalar() or 0
    
    # Comptage par destination
    destinations = db.query(
        Flight.arrival_airport,
        func.count(Flight.id)
    ).group_by(Flight.arrival_airport).all()
    
    destinations_count = {dest: count for dest, count in destinations}
    
    return FlightStats(
        total_flights=total_flights,
        total_notified=total_notified,
        average_price=round(avg_price, 2),
        best_score=round(best_score, 2),
        destinations_count=destinations_count
    )


@router.post("/trigger-search")
def trigger_search_manually(db: Session = Depends(get_db)):
    """
    Déclenche manuellement une recherche de vols.
    
    ⚠️ Utiliser avec précaution pour ne pas dépasser les quotas API.
    
    Returns:
        Message de confirmation
    """
    
    from app.scheduler.tasks import search_and_save_flights
    
    # Lancer la recherche dans un thread séparé pour ne pas bloquer
    import threading
    thread = threading.Thread(target=search_and_save_flights)
    thread.start()
    
    return {
        "message": "Recherche lancée en arrière-plan",
        "status": "processing"
    }
