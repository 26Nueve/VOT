"""
Service de notification Discord via webhook.

Envoie des messages formatés (embeds) vers un canal Discord
pour alerter des nouveaux deals de vols.

Format du message :
- Embed coloré avec toutes les infos du vol
- Bouton "Réserver" cliquable
- Emoji selon le score
"""

import requests
from datetime import datetime
from typing import Optional
from app.config import settings
from app.services.scoring import get_score_interpretation


def send_flight_notification(
    departure_airport: str,
    arrival_airport: str,
    destination_city: str,
    departure_date: datetime,
    return_date: datetime,
    price: float,
    currency: str,
    airline: str,
    flight_numbers: str,
    num_stops: int,
    total_duration_hours: float,
    score: float,
    booking_link: Optional[str] = None
) -> bool:
    """
    Envoie une notification Discord pour un nouveau deal de vol.
    
    Args:
        Tous les détails du vol (voir modèle Flight)
    
    Returns:
        True si la notification a été envoyée avec succès, False sinon
    
    Format du message Discord :
        🔥 Nouveau Deal : Genève → Tokyo
        ━━━━━━━━━━━━━━━━━━━━━━━━
        💰 Prix : 450.00€
        📅 Départ : 15 mars 2026
        🔙 Retour : 25 mars 2026
        ⏱️ Durée : 12h30
        ✈️ Compagnie : Air France
        🔄 Escales : 1
        ⭐ Score : 85/100 - Très bon deal
        
        [Bouton : Réserver ce vol]
    """
    
    # Vérifier que le webhook est configuré
    if not settings.discord_webhook_url or settings.discord_webhook_url == "https://discord.com/api/webhooks/your_webhook_url":
        print("⚠️  Discord webhook non configuré, notification ignorée")
        return False
    
    # === FORMATER LES DATES ===
    dep_str = departure_date.strftime("%d %B %Y")
    ret_str = return_date.strftime("%d %B %Y")
    
    # Calculer la durée du séjour
    trip_days = (return_date - departure_date).days
    
    # === FORMATER LA DURÉE DU VOL ===
    hours = int(total_duration_hours)
    minutes = int((total_duration_hours - hours) * 60)
    duration_str = f"{hours}h{minutes:02d}" if minutes > 0 else f"{hours}h"
    
    # === INTERPRÉTER LE SCORE ===
    interpretation = get_score_interpretation(score)
    
    # === DÉTERMINER LA COULEUR DE L'EMBED ===
    # Excellent = Vert, Très bon = Bleu, Bon = Orange, Moyen = Gris
    color_mapping = {
        "excellent": 0x00FF00,  # Vert
        "very_good": 0x0099FF,  # Bleu
        "good": 0xFF9900,       # Orange
        "average": 0x999999,    # Gris
        "poor": 0xFF0000        # Rouge
    }
    embed_color = color_mapping.get(interpretation["level"], 0x0099FF)
    
    # === CONSTRUIRE LE MESSAGE EMBED ===
    embed = {
        "title": f"{interpretation['emoji']} Nouveau Deal : {departure_airport} → {destination_city}",
        "color": embed_color,
        "fields": [
            {
                "name": "💰 Prix",
                "value": f"**{price:.2f} {currency}**",
                "inline": True
            },
            {
                "name": "⭐ Score",
                "value": f"**{score:.0f}/100**\n{interpretation['description']}",
                "inline": True
            },
            {
                "name": "\u200b",  # Champ vide pour la mise en page
                "value": "\u200b",
                "inline": True
            },
            {
                "name": "📅 Départ",
                "value": dep_str,
                "inline": True
            },
            {
                "name": "🔙 Retour",
                "value": ret_str,
                "inline": True
            },
            {
                "name": "🗓️ Durée séjour",
                "value": f"{trip_days} jours",
                "inline": True
            },
            {
                "name": "⏱️ Temps de vol",
                "value": duration_str,
                "inline": True
            },
            {
                "name": "✈️ Compagnie",
                "value": airline or "N/A",
                "inline": True
            },
            {
                "name": "🔄 Escales",
                "value": f"{num_stops} {'escale' if num_stops <= 1 else 'escales'}",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Vols : {flight_numbers} • Trouvé le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        }
    }
    
    # Ajouter le lien de réservation si disponible
    if booking_link:
        embed["url"] = booking_link
        embed["description"] = f"[🔗 Cliquez ici pour réserver]({booking_link})"
    
    # === CONSTRUIRE LA PAYLOAD DISCORD ===
    payload = {
        "username": "Flight Deal Tracker",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3097/3097180.png",  # Icône d'avion
        "embeds": [embed]
    }
    
    # === ENVOYER LA REQUÊTE ===
    try:
        response = requests.post(
            settings.discord_webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 204:
            print(f"✅ Notification Discord envoyée : {departure_airport}→{destination_city} ({price}€)")
            return True
        else:
            print(f"❌ Erreur Discord (code {response.status_code}) : {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi Discord : {str(e)}")
        return False


def send_test_notification() -> bool:
    """
    Envoie une notification de test pour vérifier la configuration Discord.
    
    Returns:
        True si le test réussit
    
    Usage:
        python -c "from app.services.discord_notifier import send_test_notification; send_test_notification()"
    """
    from datetime import timedelta
    
    print("\n🧪 Envoi d'une notification de test Discord...\n")
    
    test_date = datetime.now() + timedelta(days=30)
    
    success = send_flight_notification(
        departure_airport="GVA",
        arrival_airport="TYO",
        destination_city="Tokyo",
        departure_date=test_date,
        return_date=test_date + timedelta(days=10),
        price=425.50,
        currency="EUR",
        airline="Air France",
        flight_numbers="AF274, AF275",
        num_stops=1,
        total_duration_hours=14.5,
        score=87.5,
        booking_link="https://www.example.com/book"
    )
    
    if success:
        print("✅ Notification de test envoyée avec succès !")
        print("   Vérifiez votre canal Discord.")
    else:
        print("❌ Échec de l'envoi de la notification de test.")
        print("   Vérifiez votre DISCORD_WEBHOOK_URL dans le fichier .env")
    
    return success


if __name__ == "__main__":
    send_test_notification()
