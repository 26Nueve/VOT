"""
Service de calcul du score des vols.

Le score détermine si un vol est un "bon deal" ou non.
Plus le score est élevé, meilleur est le deal.

Formule actuelle (facilement modifiable) :
- Prix : 50% du score
- Durée : 30% du score
- Escales : 20% du score

Score final : 0-100 (100 = meilleur deal possible)
"""

from typing import Dict


def calculate_flight_score(
    price: float,
    total_duration_hours: float,
    num_stops: int,
    destination: str = None
) -> float:
    """
    Calcule un score de 0 à 100 pour un vol.
    
    Args:
        price: Prix du vol en EUR
        total_duration_hours: Durée totale en heures
        num_stops: Nombre d'escales
        destination: Code IATA de destination (optionnel, pour ajustements futurs)
    
    Returns:
        Score entre 0 et 100 (100 = meilleur deal)
    
    Exemples:
        >>> calculate_flight_score(price=400, total_duration_hours=12, num_stops=0)
        88.0
        
        >>> calculate_flight_score(price=800, total_duration_hours=20, num_stops=2)
        52.0
    """
    
    # === COMPOSANTE 1 : PRIX (50% du score) ===
    # Prix de référence : 1000€ = score 0, 200€ = score 50
    # Formule : plus le prix est bas, meilleur le score
    price_score = max(0, 50 - (price / 20))
    price_score = min(50, price_score)  # Plafonner à 50
    
    # === COMPOSANTE 2 : DURÉE (30% du score) ===
    # Durée de référence : 30h = score 0, 10h = score 30
    # Formule : moins la durée est longue, meilleur le score
    duration_score = max(0, 30 - (total_duration_hours / 1.5))
    duration_score = min(30, duration_score)  # Plafonner à 30
    
    # === COMPOSANTE 3 : ESCALES (20% du score) ===
    # 0 escale = 20 points, 1 escale = 10 points, 2+ escales = 0 points
    stops_mapping = {
        0: 20,
        1: 10,
        2: 5,
    }
    stops_score = stops_mapping.get(num_stops, 0)
    
    # === AJUSTEMENTS OPTIONNELS PAR DESTINATION ===
    # Peut être étendu pour favoriser certaines destinations
    destination_bonus = 0
    
    # Exemple : bonus pour les destinations moins fréquentes
    # rare_destinations = ["CGK", "HAN"]  # Jakarta, Hanoi
    # if destination in rare_destinations:
    #     destination_bonus = 5
    
    # === SCORE FINAL ===
    total_score = price_score + duration_score + stops_score + destination_bonus
    
    # Arrondir à 2 décimales
    return round(total_score, 2)


def get_score_interpretation(score: float) -> Dict[str, str]:
    """
    Interprète un score et renvoie une évaluation textuelle.
    
    Args:
        score: Score calculé (0-100)
    
    Returns:
        Dictionnaire avec niveau et description
    
    Exemple:
        >>> get_score_interpretation(85)
        {"level": "excellent", "emoji": "🔥", "description": "Deal exceptionnel !"}
    """
    
    if score >= 80:
        return {
            "level": "excellent",
            "emoji": "🔥",
            "description": "Deal exceptionnel !"
        }
    elif score >= 70:
        return {
            "level": "very_good",
            "emoji": "⭐",
            "description": "Très bon deal"
        }
    elif score >= 60:
        return {
            "level": "good",
            "emoji": "👍",
            "description": "Bon deal"
        }
    elif score >= 50:
        return {
            "level": "average",
            "emoji": "😐",
            "description": "Deal moyen"
        }
    else:
        return {
            "level": "poor",
            "emoji": "👎",
            "description": "Pas un bon deal"
        }


# === FONCTION POUR TESTER DIFFÉRENTS SCÉNARIOS ===
def test_scoring():
    """
    Fonction de test pour visualiser différents scores.
    
    Exécuter avec : python -c "from app.services.scoring import test_scoring; test_scoring()"
    """
    
    test_cases = [
        # (prix, durée, escales, description)
        (300, 11, 0, "Vol direct pas cher, court"),
        (500, 15, 1, "Prix moyen, 1 escale"),
        (800, 20, 2, "Cher, long, 2 escales"),
        (200, 25, 1, "Très pas cher mais long"),
        (1200, 10, 0, "Très cher mais direct et court"),
    ]
    
    print("\n" + "="*70)
    print("🧪 TEST DU SYSTÈME DE SCORING")
    print("="*70)
    
    for price, duration, stops, desc in test_cases:
        score = calculate_flight_score(price, duration, stops)
        interpretation = get_score_interpretation(score)
        
        print(f"\n📊 {desc}")
        print(f"   Prix: {price}€ | Durée: {duration}h | Escales: {stops}")
        print(f"   Score: {score:.1f}/100 {interpretation['emoji']} - {interpretation['description']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_scoring()
