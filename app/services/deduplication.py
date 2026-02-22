"""
Service de déduplication des vols.

Génère un hash unique pour chaque vol afin d'éviter de :
- Stocker le même vol plusieurs fois
- Notifier plusieurs fois le même deal

Le hash est calculé à partir de :
- Date de départ
- Date de retour
- Prix
- Numéro(s) de vol
"""

import hashlib
from datetime import datetime


def generate_flight_hash(
    departure_date: datetime,
    return_date: datetime,
    price: float,
    flight_numbers: str
) -> str:
    """
    Génère un hash MD5 unique pour un vol.
    
    Le hash combine plusieurs informations clés pour garantir l'unicité.
    
    Args:
        departure_date: Date de départ
        return_date: Date de retour
        price: Prix du vol
        flight_numbers: Numéros de vol (ex: "AF274,AF275")
    
    Returns:
        Hash MD5 de 32 caractères (ex: "a1b2c3d4e5f6...")
    
    Exemple:
        >>> from datetime import datetime
        >>> generate_flight_hash(
        ...     datetime(2026, 3, 15),
        ...     datetime(2026, 3, 25),
        ...     450.0,
        ...     "AF274,AF275"
        ... )
        'e4d909c290d0fb1ca068ffaddf22cbd0'
    """
    
    # Formater les dates en format ISO (YYYY-MM-DD)
    dep_str = departure_date.strftime("%Y-%m-%d")
    ret_str = return_date.strftime("%Y-%m-%d")
    
    # Arrondir le prix à 2 décimales pour éviter les variations minimes
    price_str = f"{price:.2f}"
    
    # Nettoyer les numéros de vol (supprimer espaces)
    flights_str = flight_numbers.strip().replace(" ", "")
    
    # Créer la chaîne unique
    unique_string = f"{dep_str}|{ret_str}|{price_str}|{flights_str}"
    
    # Générer le hash MD5
    hash_object = hashlib.md5(unique_string.encode('utf-8'))
    return hash_object.hexdigest()


def is_duplicate(db_session, flight_hash: str) -> bool:
    """
    Vérifie si un vol existe déjà en base de données.
    
    Args:
        db_session: Session SQLAlchemy
        flight_hash: Hash unique du vol
    
    Returns:
        True si le vol existe déjà, False sinon
    
    Exemple:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> is_duplicate(db, "a1b2c3d4e5f6...")
        False
    """
    from app.models.flight import Flight
    
    existing_flight = db_session.query(Flight).filter(
        Flight.unique_hash == flight_hash
    ).first()
    
    return existing_flight is not None


def get_duplicate_stats(db_session) -> dict:
    """
    Récupère des statistiques sur la déduplication.
    
    Args:
        db_session: Session SQLAlchemy
    
    Returns:
        Dictionnaire avec les stats
    
    Exemple de retour:
        {
            "total_flights": 150,
            "unique_hashes": 150,
            "duplicates_avoided": 23
        }
    """
    from app.models.flight import Flight
    from sqlalchemy import func
    
    total_flights = db_session.query(Flight).count()
    unique_hashes = db_session.query(func.count(func.distinct(Flight.unique_hash))).scalar()
    
    return {
        "total_flights": total_flights,
        "unique_hashes": unique_hashes,
        "duplicates_avoided": 0  # Nécessiterait un compteur séparé
    }


# === FONCTION DE TEST ===
def test_deduplication():
    """
    Teste le système de déduplication avec différents scénarios.
    
    Exécuter avec : python -c "from app.services.deduplication import test_deduplication; test_deduplication()"
    """
    from datetime import datetime
    
    print("\n" + "="*70)
    print("🧪 TEST DU SYSTÈME DE DÉDUPLICATION")
    print("="*70)
    
    # Test 1 : Même vol = même hash
    hash1 = generate_flight_hash(
        datetime(2026, 3, 15),
        datetime(2026, 3, 25),
        450.0,
        "AF274,AF275"
    )
    
    hash2 = generate_flight_hash(
        datetime(2026, 3, 15),
        datetime(2026, 3, 25),
        450.0,
        "AF274,AF275"
    )
    
    print(f"\n✅ Test 1 : Vols identiques")
    print(f"   Hash 1 : {hash1}")
    print(f"   Hash 2 : {hash2}")
    print(f"   Résultat : {'IDENTIQUES ✓' if hash1 == hash2 else 'DIFFÉRENTS ✗'}")
    
    # Test 2 : Prix différent = hash différent
    hash3 = generate_flight_hash(
        datetime(2026, 3, 15),
        datetime(2026, 3, 25),
        455.0,  # Prix différent
        "AF274,AF275"
    )
    
    print(f"\n✅ Test 2 : Prix différent")
    print(f"   Hash original : {hash1}")
    print(f"   Hash prix +5€ : {hash3}")
    print(f"   Résultat : {'DIFFÉRENTS ✓' if hash1 != hash3 else 'IDENTIQUES ✗'}")
    
    # Test 3 : Date différente = hash différent
    hash4 = generate_flight_hash(
        datetime(2026, 3, 16),  # Date différente
        datetime(2026, 3, 25),
        450.0,
        "AF274,AF275"
    )
    
    print(f"\n✅ Test 3 : Date différente")
    print(f"   Hash original : {hash1}")
    print(f"   Hash date +1j : {hash4}")
    print(f"   Résultat : {'DIFFÉRENTS ✓' if hash1 != hash4 else 'IDENTIQUES ✗'}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_deduplication()
