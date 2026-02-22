"""
Tâches planifiées pour la recherche automatique de vols.

APScheduler exécute périodiquement la recherche de vols
et envoie des notifications pour les nouveaux deals.

Fréquence configurable dans .env (SEARCH_FREQUENCY_HOURS)
"""

from datetime import datetime, timedelta
from typing import List
import json

from app.config import settings
from app.database import SessionLocal
from app.models.flight import Flight
from app.services.flight_api import AmadeusAPI, generate_search_dates
from app.services.scoring import calculate_flight_score
from app.services.deduplication import generate_flight_hash, is_duplicate
from app.services.discord_notifier import send_flight_notification


def parse_flight_offer(offer: dict) -> dict:
    """
    Parse une offre de vol de l'API Amadeus et extrait les infos essentielles.
    
    Args:
        offer: Dictionnaire brut de l'API Amadeus
    
    Returns:
        Dictionnaire avec les informations structurées
    """
    
    # === PRIX ===
    price = float(offer.get("price", {}).get("total", 0))
    currency = offer.get("price", {}).get("currency", "EUR")
    
    # === ITINÉRAIRES (aller + retour) ===
    itineraries = offer.get("itineraries", [])
    
    if not itineraries or len(itineraries) < 2:
        return None  # Pas un aller-retour valide
    
    # Itinéraire aller (premier)
    outbound = itineraries[0]
    # Itinéraire retour (dernier)
    inbound = itineraries[-1]
    
    # === SEGMENTS (vols individuels) ===
    outbound_segments = outbound.get("segments", [])
    inbound_segments = inbound.get("segments", [])
    
    if not outbound_segments or not inbound_segments:
        return None
    
    # === DATES ===
    # Premier segment de l'aller = date de départ
    departure_date = datetime.fromisoformat(
        outbound_segments[0].get("departure", {}).get("at", "").replace("Z", "+00:00")
    )
    
    # Premier segment du retour = date de retour
    return_date = datetime.fromisoformat(
        inbound_segments[0].get("departure", {}).get("at", "").replace("Z", "+00:00")
    )
    
    # === AÉROPORTS ===
    departure_airport = outbound_segments[0].get("departure", {}).get("iataCode", "")
    arrival_airport = outbound_segments[-1].get("arrival", {}).get("iataCode", "")
    
    # === DURÉE TOTALE ===
    # Format ISO 8601 : "PT14H30M"
    outbound_duration = outbound.get("duration", "PT0H")
    inbound_duration = inbound.get("duration", "PT0H")
    
    def parse_duration(iso_duration: str) -> float:
        """Convertit PT14H30M en heures décimales"""
        import re
        hours = re.search(r'(\d+)H', iso_duration)
        minutes = re.search(r'(\d+)M', iso_duration)
        h = int(hours.group(1)) if hours else 0
        m = int(minutes.group(1)) if minutes else 0
        return h + (m / 60)
    
    total_duration_hours = parse_duration(outbound_duration) + parse_duration(inbound_duration)
    
    # === ESCALES ===
    # Nombre de segments - 1 = nombre d'escales
    num_stops = max(len(outbound_segments) - 1, len(inbound_segments) - 1)
    
    # === COMPAGNIE ===
    airline_codes = offer.get("validatingAirlineCodes", [])
    airline = airline_codes[0] if airline_codes else "Unknown"
    
    # === NUMÉROS DE VOL ===
    flight_numbers = []
    for seg in outbound_segments + inbound_segments:
        carrier = seg.get("carrierCode", "")
        number = seg.get("number", "")
        if carrier and number:
            flight_numbers.append(f"{carrier}{number}")
    
    flight_numbers_str = ",".join(flight_numbers)
    
    # === LIEN DE RÉSERVATION ===
    # Amadeus ne fournit pas de lien direct, on peut construire un lien générique
    booking_link = f"https://www.google.com/flights?q={departure_airport}+to+{arrival_airport}+{departure_date.strftime('%Y-%m-%d')}"
    
    return {
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
        "departure_date": departure_date,
        "return_date": return_date,
        "price": price,
        "currency": currency,
        "airline": airline,
        "flight_numbers": flight_numbers_str,
        "num_stops": num_stops,
        "total_duration_hours": total_duration_hours,
        "booking_link": booking_link,
        "raw_data": json.dumps(offer)
    }


def search_and_save_flights():
    """
    Tâche principale : recherche les vols et sauvegarde les deals.
    
    Cette fonction est appelée périodiquement par le scheduler.
    
    Workflow:
    1. Générer les dates à rechercher
    2. Pour chaque destination :
        - Rechercher les vols
        - Calculer le score
        - Vérifier les doublons
        - Sauvegarder en base
        - Notifier si bon deal
    """
    
    print("\n" + "="*70)
    print(f"🔍 RECHERCHE DE VOLS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    db = SessionLocal()
    api = AmadeusAPI()
    
    # === GÉNÉRER LES DATES À RECHERCHER ===
    start_date = datetime.now()
    end_date = start_date + timedelta(days=settings.search_window_months * 30)
    
    date_pairs = generate_search_dates(
        start_date,
        end_date,
        settings.min_trip_duration,
        settings.max_trip_duration
    )
    
    print(f"\n📅 {len(date_pairs)} combinaisons de dates à tester")
    print(f"🌏 {len(settings.destinations_list)} destinations")
    print(f"📊 Total de recherches : {len(date_pairs) * len(settings.destinations_list)}\n")
    
    total_found = 0
    total_saved = 0
    total_notified = 0
    
    # === PARCOURIR CHAQUE DESTINATION ===
    for destination in settings.destinations_list:
        
        print(f"\n🎯 Destination : {destination}")
        
        # Limiter à 3 dates par destination pour éviter trop de requêtes
        selected_dates = date_pairs[:3]
        
        for dep_date, ret_date in selected_dates:
            
            # Rechercher les vols
            offers = api.search_flights(
                origin=settings.departure_airport,
                destination=destination,
                departure_date=dep_date.strftime("%Y-%m-%d"),
                return_date=ret_date.strftime("%Y-%m-%d"),
                max_results=5
            )
            
            total_found += len(offers)
            
            # === TRAITER CHAQUE OFFRE ===
            for offer in offers:
                
                # Parser l'offre
                flight_data = parse_flight_offer(offer)
                
                if not flight_data:
                    continue
                
                # Vérifier le nombre d'escales
                if flight_data["num_stops"] > settings.max_stopovers:
                    continue
                
                # === CALCULER LE SCORE ===
                score = calculate_flight_score(
                    price=flight_data["price"],
                    total_duration_hours=flight_data["total_duration_hours"],
                    num_stops=flight_data["num_stops"],
                    destination=destination
                )
                
                flight_data["score"] = score
                
                # Filtrer les mauvais deals
                if score < settings.min_score_threshold:
                    continue
                
                # === GÉNÉRER LE HASH ===
                flight_hash = generate_flight_hash(
                    departure_date=flight_data["departure_date"],
                    return_date=flight_data["return_date"],
                    price=flight_data["price"],
                    flight_numbers=flight_data["flight_numbers"]
                )
                
                # Vérifier les doublons
                if is_duplicate(db, flight_hash):
                    continue
                
                # === SAUVEGARDER EN BASE ===
                new_flight = Flight(
                    unique_hash=flight_hash,
                    departure_airport=flight_data["departure_airport"],
                    arrival_airport=flight_data["arrival_airport"],
                    destination_city=destination,  # On pourrait améliorer avec un mapping
                    departure_date=flight_data["departure_date"],
                    return_date=flight_data["return_date"],
                    price=flight_data["price"],
                    currency=flight_data["currency"],
                    airline=flight_data["airline"],
                    flight_numbers=flight_data["flight_numbers"],
                    num_stops=flight_data["num_stops"],
                    total_duration_hours=flight_data["total_duration_hours"],
                    score=score,
                    booking_link=flight_data["booking_link"],
                    raw_data=flight_data["raw_data"],
                    notified=False
                )
                
                db.add(new_flight)
                db.commit()
                total_saved += 1
                
                print(f"   ✅ Nouveau deal : {flight_data['price']}€ (score {score:.0f})")
                
                # === NOTIFIER VIA DISCORD ===
                notification_sent = send_flight_notification(
                    departure_airport=flight_data["departure_airport"],
                    arrival_airport=flight_data["arrival_airport"],
                    destination_city=destination,
                    departure_date=flight_data["departure_date"],
                    return_date=flight_data["return_date"],
                    price=flight_data["price"],
                    currency=flight_data["currency"],
                    airline=flight_data["airline"],
                    flight_numbers=flight_data["flight_numbers"],
                    num_stops=flight_data["num_stops"],
                    total_duration_hours=flight_data["total_duration_hours"],
                    score=score,
                    booking_link=flight_data["booking_link"]
                )
                
                if notification_sent:
                    new_flight.notified = True
                    db.commit()
                    total_notified += 1
    
    db.close()
    
    # === RÉSUMÉ ===
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA RECHERCHE")
    print("="*70)
    print(f"✈️  Offres trouvées : {total_found}")
    print(f"💾 Deals sauvegardés : {total_saved}")
    print(f"💬 Notifications envoyées : {total_notified}")
    print("="*70 + "\n")


# === FONCTION DE TEST MANUELLE ===
def test_search():
    """
    Lance une recherche manuelle pour tester.
    
    Usage : python -c "from app.scheduler.tasks import test_search; test_search()"
    """
    search_and_save_flights()


if __name__ == "__main__":
    test_search()
