"""
Service de communication avec l'API Amadeus pour rechercher des vols.

API Amadeus :
- Endpoint : Flight Offers Search
- Documentation : https://developers.amadeus.com/self-service/category/flights

Authentification :
- OAuth2 : récupération d'un access token avec API key + secret
- Le token expire après 30 minutes

Stratégie de recherche :
- Échantillonnage intelligent des dates (mercredis + samedis)
- Limitation des requêtes pour respecter les quotas
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.config import settings


class AmadeusAPI:
    """
    Client pour l'API Amadeus Flight Offers Search.
    
    Usage:
        api = AmadeusAPI()
        offers = api.search_flights("GVA", "TYO", "2026-03-15", "2026-03-25")
    """
    
    BASE_URL = "https://test.api.amadeus.com"  # URL de test
    # Pour production : "https://api.amadeus.com"
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _get_access_token(self) -> str:
        """
        Récupère un token d'accès OAuth2.
        
        Le token est valide 30 minutes.
        On le réutilise si encore valide.
        
        Returns:
            Access token valide
        """
        
        # Réutiliser le token si encore valide
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Récupérer un nouveau token
        url = f"{self.BASE_URL}/v1/security/oauth2/token"
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": settings.amadeus_api_key,
            "client_secret": settings.amadeus_api_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            
            # Le token expire dans 1800 secondes (30 min)
            # On le fait expirer 5 min avant pour être sûr
            expires_in = data.get("expires_in", 1800) - 300
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Token Amadeus obtenu (expire dans {expires_in//60} min)")
            return self.access_token
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du token Amadeus : {e}")
            raise
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str,
        adults: int = 1,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recherche des vols aller-retour.
        
        Args:
            origin: Code IATA de départ (ex: "GVA")
            destination: Code IATA d'arrivée (ex: "TYO")
            departure_date: Date de départ (format: "YYYY-MM-DD")
            return_date: Date de retour (format: "YYYY-MM-DD")
            adults: Nombre d'adultes (défaut: 1)
            max_results: Nombre max de résultats (défaut: 5)
        
        Returns:
            Liste de dictionnaires contenant les offres de vols
        
        Exemple de retour (simplifié) :
            [
                {
                    "price": {"total": "425.50", "currency": "EUR"},
                    "itineraries": [...],
                    "validatingAirlineCodes": ["AF"]
                }
            ]
        """
        
        token = self._get_access_token()
        
        url = f"{self.BASE_URL}/v2/shopping/flight-offers"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": adults,
            "currencyCode": "EUR",
            "max": max_results,
            "nonStop": "false",  # Autorise les escales
            "maxPrice": 1500     # Prix max en EUR (ajustable)
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data:
                print(f"✅ Amadeus : {len(data['data'])} vols trouvés {origin}→{destination} ({departure_date})")
                return data["data"]
            else:
                print(f"⚠️  Amadeus : Aucun vol trouvé {origin}→{destination}")
                return []
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print(f"⚠️  Requête invalide pour {origin}→{destination} : {e.response.text}")
            else:
                print(f"❌ Erreur HTTP Amadeus : {e}")
            return []
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche de vols : {e}")
            return []


def generate_search_dates(
    start_date: datetime,
    end_date: datetime,
    min_duration: int,
    max_duration: int
) -> List[tuple]:
    """
    Génère des paires de dates (départ, retour) à rechercher.
    
    Stratégie : 2 départs par semaine (mercredi + samedi)
    pour limiter le nombre de requêtes API.
    
    Args:
        start_date: Date de début de la fenêtre de recherche
        end_date: Date de fin de la fenêtre de recherche
        min_duration: Durée min du séjour en jours
        max_duration: Durée max du séjour en jours
    
    Returns:
        Liste de tuples (date_depart, date_retour)
    
    Exemple:
        >>> from datetime import datetime
        >>> generate_search_dates(
        ...     datetime(2026, 3, 1),
        ...     datetime(2026, 4, 1),
        ...     7,
        ...     14
        ... )
        [
            (datetime(2026, 3, 4), datetime(2026, 3, 11)),   # Mercredi → 7j
            (datetime(2026, 3, 4), datetime(2026, 3, 18)),   # Mercredi → 14j
            (datetime(2026, 3, 7), datetime(2026, 3, 14)),   # Samedi → 7j
            ...
        ]
    """
    
    date_pairs = []
    current_date = start_date
    
    while current_date <= end_date:
        weekday = current_date.weekday()
        
        # Mercredi (2) ou Samedi (5)
        if weekday in [2, 5]:
            # Tester durée min et max
            for duration in [min_duration, max_duration]:
                return_date = current_date + timedelta(days=duration)
                
                # Vérifier que la date de retour est dans la fenêtre
                if return_date <= end_date:
                    date_pairs.append((current_date, return_date))
        
        current_date += timedelta(days=1)
    
    return date_pairs


# === FONCTION DE TEST ===
def test_amadeus_api():
    """
    Teste l'API Amadeus avec une recherche réelle.
    
    Exécuter avec : python -c "from app.services.flight_api import test_amadeus_api; test_amadeus_api()"
    """
    
    print("\n" + "="*70)
    print("🧪 TEST DE L'API AMADEUS")
    print("="*70)
    
    api = AmadeusAPI()
    
    # Date de test : dans 30 jours
    test_dep = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    test_ret = (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d")
    
    print(f"\n🔍 Recherche : GVA → TYO")
    print(f"   Départ : {test_dep}")
    print(f"   Retour : {test_ret}")
    
    offers = api.search_flights(
        origin="GVA",
        destination="TYO",
        departure_date=test_dep,
        return_date=test_ret,
        max_results=3
    )
    
    if offers:
        print(f"\n✅ {len(offers)} offres trouvées :\n")
        for i, offer in enumerate(offers, 1):
            price = offer.get("price", {}).get("total", "N/A")
            currency = offer.get("price", {}).get("currency", "EUR")
            print(f"   {i}. Prix : {price} {currency}")
    else:
        print("\n⚠️  Aucune offre trouvée (peut-être un problème de token ou de dates)")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_amadeus_api()
