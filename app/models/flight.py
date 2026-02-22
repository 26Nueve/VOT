"""
Modèle de base de données pour les vols.

Ce fichier définit la structure de la table "flights" en base de données.
SQLAlchemy traduit automatiquement cette classe Python en table SQL.

Champs importants :
- unique_hash : Pour éviter les doublons
- notified : Pour savoir si on a déjà envoyé une notification Discord
- score : Pour filtrer les meilleurs deals
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class Flight(Base):
    """
    Modèle représentant un vol dans la base de données.
    
    Correspond à la table SQL "flights".
    """
    
    __tablename__ = "flights"
    
    # === IDENTIFIANT UNIQUE ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === HASH UNIQUE (anti-doublon) ===
    unique_hash = Column(String(32), unique=True, index=True, nullable=False)
    # MD5 de : date_depart + date_retour + prix + numero_vol
    
    # === INFORMATIONS DE VOL ===
    departure_airport = Column(String(3), nullable=False)  # Ex: "GVA"
    arrival_airport = Column(String(3), nullable=False)    # Ex: "TYO"
    destination_city = Column(String(100))                 # Ex: "Tokyo"
    
    departure_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)
    
    # === DÉTAILS DU VOL ===
    price = Column(Float, nullable=False)                  # Prix en EUR
    currency = Column(String(3), default="EUR")
    
    airline = Column(String(100))                          # Compagnie aérienne
    flight_numbers = Column(Text)                          # Ex: "AF274,AF275"
    
    num_stops = Column(Integer, default=0)                 # Nombre d'escales
    total_duration_hours = Column(Float)                   # Durée totale en heures
    
    # === SCORING ===
    score = Column(Float, index=True)                      # Score calculé (0-100)
    
    # === NOTIFICATION ===
    notified = Column(Boolean, default=False, index=True)  # Déjà notifié ?
    
    # === LIEN DE RÉSERVATION ===
    booking_link = Column(Text)                            # URL pour réserver
    
    # === DONNÉES BRUTES ===
    raw_data = Column(Text)                                # JSON complet de l'API
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        """Représentation lisible d'un vol (pour le debugging)"""
        return (
            f"<Flight {self.departure_airport}→{self.arrival_airport} "
            f"{self.departure_date.date()} | {self.price}€ | Score:{self.score:.1f}>"
        )
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire (pour l'API)"""
        return {
            "id": self.id,
            "departure_airport": self.departure_airport,
            "arrival_airport": self.arrival_airport,
            "destination_city": self.destination_city,
            "departure_date": self.departure_date.isoformat() if self.departure_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "price": self.price,
            "currency": self.currency,
            "airline": self.airline,
            "flight_numbers": self.flight_numbers,
            "num_stops": self.num_stops,
            "total_duration_hours": self.total_duration_hours,
            "score": round(self.score, 2) if self.score else None,
            "notified": self.notified,
            "booking_link": self.booking_link,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
