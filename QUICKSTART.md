# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## ⚡ Configuration en 5 minutes

### 1️⃣ Installer Python 3.11+

Vérifiez votre version :
```bash
python --version
```

Si < 3.11, téléchargez Python sur https://www.python.org/downloads/

### 2️⃣ Créer l'environnement virtuel

```bash
cd flight-deal-tracker
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer l'application

Copiez le fichier d'exemple :
```bash
cp .env.example .env
```

Éditez `.env` et remplissez **au minimum** :

```env
# API Amadeus (OBLIGATOIRE)
AMADEUS_API_KEY=votre_cle_ici
AMADEUS_API_SECRET=votre_secret_ici

# Discord Webhook (OBLIGATOIRE)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Base de données (optionnel, SQLite par défaut)
DATABASE_URL=sqlite:///./flight_deals.db
```

#### 🔑 Obtenir une clé API Amadeus (GRATUIT)

1. Allez sur https://developers.amadeus.com
2. Créez un compte
3. Créez une application (Self-Service)
4. Copiez votre **API Key** et **API Secret**
5. Utilisez l'URL de **TEST** : `https://test.api.amadeus.com`

#### 🤖 Créer un Webhook Discord

1. Sur votre serveur Discord, faites clic droit sur un canal
2. **Modifier le canal** → **Intégrations** → **Webhooks**
3. **Créer un webhook**
4. Copiez l'**URL du webhook**
5. Collez-la dans `.env`

### 5️⃣ Lancer l'application

```bash
python app/main.py
```

Vous devriez voir :
```
🚀 DÉMARRAGE DE L'APPLICATION
✅ Tables de base de données créées
⏰ Scheduler configuré
✅ Application prête !
🌐 Interface web : http://localhost:8000
```

### 6️⃣ Tester l'application

Ouvrez votre navigateur sur :
- **Interface web** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🧪 Test Manuel

Pour lancer une recherche immédiatement (sans attendre le scheduler) :

```bash
python -c "
import asyncio
from app.scheduler.tasks import run_search_now
asyncio.run(run_search_now())
"
```

## ⚠️ Problèmes Courants

### "Module not found"
```bash
# Assurez-vous que l'environnement virtuel est activé
# Vous devriez voir (venv) au début de votre terminal
pip install -r requirements.txt
```

### "Aucun vol trouvé"
- Vérifiez vos identifiants Amadeus dans `.env`
- Utilisez l'URL de **TEST** : `https://test.api.amadeus.com`
- Les quotas gratuits : 2000 appels/mois

### "Discord webhook failed"
- Vérifiez l'URL du webhook (doit commencer par `https://discord.com/api/webhooks/`)
- Testez avec curl :
  ```bash
  curl -X POST "VOTRE_URL_WEBHOOK" -H "Content-Type: application/json" -d '{"content": "Test"}'
  ```

## 📊 Prochaines Étapes

1. ✅ L'application tourne localement
2. ✅ Les recherches s'exécutent toutes les 6 heures (configurable dans `.env`)
3. ✅ Les deals sont notifiés sur Discord
4. ✅ Consultez l'interface web pour voir tous les deals

Pour **déployer en production** (gratuit) :
- Suivez le guide dans `README.md` section "Déploiement"
- Render.com ou Railway.app recommandés

## 🎯 Configuration Recommandée

Pour de meilleurs résultats, ajustez dans `.env` :

```env
# Recherche toutes les 6 heures (4 fois par jour)
SEARCH_INTERVAL_HOURS=6

# Accepter uniquement les très bons deals (score > 75)
SCORE_THRESHOLD=75

# Maximum 1 escale
MAX_STOPS=1

# Séjours de 7 à 14 jours
MIN_STAY_DAYS=7
MAX_STAY_DAYS=14
```

## 🆘 Besoin d'Aide ?

- Documentation complète : `README.md`
- Problème technique : Ouvrez une issue sur GitHub
- Questions : Consultez les commentaires dans le code (très détaillés)

**Bon voyage ! ✈️**
