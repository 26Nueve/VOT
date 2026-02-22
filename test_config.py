#!/usr/bin/env python3
"""
Script de vérification de la configuration.

Ce script teste que :
- Le fichier .env existe et est valide
- Les clés API Amadeus sont correctes
- Le webhook Discord fonctionne
- La base de données est accessible
"""

import os
import sys
from pathlib import Path

print("=" * 80)
print("🔍 VÉRIFICATION DE LA CONFIGURATION")
print("=" * 80)
print()

# Vérifier que nous sommes dans le bon dossier
if not Path("app").exists():
    print("❌ ERREUR : Ce script doit être exécuté depuis la racine du projet")
    print("   Utilisez : python test_config.py")
    sys.exit(1)

# Test 1 : Fichier .env
print("1️⃣ Vérification du fichier .env...")
if not Path(".env").exists():
    print("   ❌ Le fichier .env n'existe pas !")
    print("   📝 Créez-le avec : cp .env.example .env")
    print("   📝 Puis remplissez vos clés API")
    sys.exit(1)
else:
    print("   ✅ Fichier .env trouvé")

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✅ Variables d'environnement chargées")
except ImportError:
    print("   ❌ Module python-dotenv non installé")
    print("   📝 Installez avec : pip install python-dotenv")
    sys.exit(1)

print()

# Test 2 : Variables obligatoires
print("2️⃣ Vérification des variables obligatoires...")
required_vars = {
    "AMADEUS_API_KEY": "Clé API Amadeus",
    "AMADEUS_API_SECRET": "Secret API Amadeus",
    "DISCORD_WEBHOOK_URL": "URL du webhook Discord"
}

missing_vars = []
for var, description in required_vars.items():
    value = os.getenv(var)
    if not value or value.startswith("votre_") or value.startswith("REMPLACEZ"):
        print(f"   ❌ {description} ({var}) manquante ou invalide")
        missing_vars.append(var)
    else:
        # Masquer les valeurs sensibles
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"   ✅ {description} : {masked}")

if missing_vars:
    print()
    print("   ⚠️  Variables manquantes. Consultez TUTORIAL_API_KEYS.md")
    sys.exit(1)

print()

# Test 3 : Test de connexion Amadeus
print("3️⃣ Test de connexion à l'API Amadeus...")
try:
    import httpx
    import asyncio
    
    async def test_amadeus():
        api_url = os.getenv("AMADEUS_API_URL", "https://test.api.amadeus.com")
        api_key = os.getenv("AMADEUS_API_KEY")
        api_secret = os.getenv("AMADEUS_API_SECRET")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{api_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": api_key,
                    "client_secret": api_secret
                }
            )
            
            if response.status_code == 200:
                print("   ✅ Connexion à Amadeus API réussie !")
                data = response.json()
                print(f"   ℹ️  Token d'accès obtenu (expire dans {data.get('expires_in', 0)}s)")
                return True
            else:
                print(f"   ❌ Erreur {response.status_code} : {response.text[:100]}")
                return False
    
    result = asyncio.run(test_amadeus())
    if not result:
        print("   ⚠️  Vérifiez vos identifiants Amadeus")
except ImportError:
    print("   ⚠️  Module httpx non installé, test ignoré")
except Exception as e:
    print(f"   ❌ Erreur lors du test : {e}")

print()

# Test 4 : Test du webhook Discord
print("4️⃣ Test du webhook Discord...")
try:
    import httpx
    import asyncio
    
    async def test_discord():
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json={
                    "content": "✅ Test de configuration - Webhook Discord fonctionnel !"
                }
            )
            
            if response.status_code == 204:
                print("   ✅ Webhook Discord fonctionnel !")
                print("   ℹ️  Vérifiez votre canal Discord")
                return True
            else:
                print(f"   ❌ Erreur {response.status_code}")
                return False
    
    result = asyncio.run(test_discord())
    if not result:
        print("   ⚠️  Vérifiez l'URL de votre webhook Discord")
except Exception as e:
    print(f"   ❌ Erreur lors du test : {e}")

print()

# Test 5 : Test de la base de données
print("5️⃣ Vérification de la base de données...")
try:
    from app.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("   ✅ Connexion à la base de données réussie !")
except ImportError:
    print("   ⚠️  Modules SQLAlchemy non installés, test ignoré")
except Exception as e:
    print(f"   ❌ Erreur : {e}")

print()

# Résumé
print("=" * 80)
print("📊 RÉSUMÉ")
print("=" * 80)
print()
print("Si tous les tests sont ✅, vous pouvez lancer l'application !")
print()
print("Commandes de lancement :")
print("  • Windows : start.bat")
print("  • Linux/Mac : ./start.sh")
print("  • Manuel : python app/main.py")
print()
print("Interface web : http://localhost:8000")
print("Documentation API : http://localhost:8000/docs")
print()
print("=" * 80)
