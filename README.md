# ✈️ Flight Deal Tracker

Application automatisée de surveillance des meilleurs deals de vols depuis Genève vers l'Asie.

## 🎯 Fonctionnalités

- ✅ Recherche automatique de vols via l'API Amadeus
- ✅ Calcul intelligent du score de chaque deal
- ✅ Déduplication pour éviter les doublons
- ✅ Notifications Discord pour les meilleurs deals
- ✅ Interface web moderne pour consulter les deals
- ✅ API REST complète
- ✅ Scheduler intégré (recherche toutes les 6h par défaut)

## 📋 Prérequis

- Python 3.11+
- Compte Amadeus API (gratuit)
- Webhook Discord (optionnel)

## 🚀 Installation Locale

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd flight-deal-tracker
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
# Copier le template
cp .env.example .env

# Éditer le fichier .env avec vos vraies valeurs
nano .env  # ou votre éditeur préféré
```

#### 📝 Obtenir les clés API Amadeus

1. Aller sur https://developers.amadeus.com
2. Créer un compte gratuit
3. Créer une application dans "My Self-Service Workspace"
4. Copier votre **API Key** et **API Secret**
5. Coller dans le fichier `.env`

#### 💬 Configurer le Webhook Discord

1. Dans Discord, aller dans **Paramètres du salon** → **Intégrations** → **Webhooks**
2. Cliquer sur **Nouveau Webhook**
3. Personnaliser le nom et l'avatar (optionnel)
4. Copier l'URL du webhook
5. Coller dans le fichier `.env`

### 5. Lancer l'application

```bash
python run.py
```

L'application sera accessible sur : **http://localhost:8000**

## 📚 Utilisation

### Interface Web

Ouvrez votre navigateur sur `http://localhost:8000`

- **Filtrer** les deals par destination, prix, score
- **Trier** automatiquement par meilleurs deals
- **Réserver** via le bouton direct

### API REST

Documentation automatique : `http://localhost:8000/docs`

**Endpoints principaux :**

```bash
# Liste tous les deals
GET /api/deals

# Filtrer par destination
GET /api/deals?destination=TYO

# Filtrer par score minimum
GET /api/deals?min_score=80

# Statistiques globales
GET /api/stats

# Déclencher une recherche manuelle
POST /api/trigger-search
```

### Tests Manuels

#### Tester l'API Amadeus

```bash
python -c "from app.services.flight_api import test_amadeus_api; test_amadeus_api()"
```

#### Tester le système de scoring

```bash
python -c "from app.services.scoring import test_scoring; test_scoring()"
```

#### Tester Discord

```bash
python -c "from app.services.discord_notifier import send_test_notification; send_test_notification()"
```

#### Lancer une recherche manuelle

```bash
python -c "from app.scheduler.tasks import test_search; test_search()"
```

## ⚙️ Configuration Avancée

### Modifier les destinations

Éditer le fichier `.env` :

```env
DESTINATIONS=TYO,PEK,HAN,BKK,KUL,CGK,SIN,HKG
```

**Codes IATA courants :**
- TYO : Tokyo
- PEK : Pékin
- HAN : Hanoi
- BKK : Bangkok
- KUL : Kuala Lumpur
- CGK : Jakarta
- SIN : Singapour
- HKG : Hong Kong

### Ajuster le scoring

Modifier `app/services/scoring.py` ligne 42 :

```python
# Exemple : favoriser le prix à 70%
price_score = max(0, 70 - (price / 15))
duration_score = max(0, 20 - (total_duration_hours / 2))
stops_score = stops_mapping.get(num_stops, 0) * 10
```

### Changer la fréquence de recherche

Dans `.env` :

```env
# Recherche toutes les 3 heures
SEARCH_FREQUENCY_HOURS=3

# Recherche toutes les 12 heures
SEARCH_FREQUENCY_HOURS=12
```

## 🚢 Déploiement en Production

### Option 1 : Render.com (Recommandé)

1. **Créer un compte sur Render.com**

2. **Créer un nouveau Web Service**
   - Repository : votre dépôt GitHub
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python run.py`

3. **Configurer les variables d'environnement**
   - Ajouter toutes les variables du fichier `.env`
   - Pour PostgreSQL : ajouter une base de données PostgreSQL sur Render

4. **Déployer**
   - Render détectera les changements et redéploiera automatiquement

### Option 2 : Railway

1. **Créer un compte sur Railway.app**

2. **Créer un nouveau projet**
   - Import depuis GitHub
   - Railway détecte automatiquement Python

3. **Ajouter PostgreSQL**
   - Cliquer sur "+ New" → PostgreSQL
   - Copier l'URL de connexion

4. **Variables d'environnement**
   - Ajouter toutes vos variables
   - `DATABASE_URL` = URL PostgreSQL de Railway

5. **Déployer**
   - Railway déploie automatiquement

### Passage à PostgreSQL en Production

Modifier `.env` :

```env
# Remplacer SQLite par PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Rien d'autre à changer ! SQLAlchemy gère automatiquement.

## 📊 Structure du Projet

```
flight-deal-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── config.py            # Configuration
│   ├── database.py          # Connexion BDD
│   ├── models/
│   │   └── flight.py        # Modèle SQLAlchemy
│   ├── schemas/
│   │   └── flight.py        # Schémas Pydantic
│   ├── services/
│   │   ├── flight_api.py    # API Amadeus
│   │   ├── scoring.py       # Calcul de score
│   │   ├── deduplication.py # Anti-doublon
│   │   └── discord_notifier.py # Notifications
│   ├── routers/
│   │   └── deals.py         # Routes API
│   ├── scheduler/
│   │   └── tasks.py         # Tâches automatiques
│   └── templates/
│       └── index.html       # Interface web
├── .env                     # Variables d'environnement
├── .env.example             # Template de config
├── requirements.txt         # Dépendances Python
├── run.py                   # Script de lancement
└── README.md                # Documentation
```

## 🔧 Dépannage

### L'API Amadeus ne fonctionne pas

```bash
# Vérifier les clés API
python -c "from app.config import settings; print(settings.amadeus_api_key)"

# Tester la connexion
python -c "from app.services.flight_api import test_amadeus_api; test_amadeus_api()"
```

### Discord ne reçoit pas les notifications

```bash
# Tester le webhook
python -c "from app.services.discord_notifier import send_test_notification; send_test_notification()"

# Vérifier l'URL du webhook
python -c "from app.config import settings; print(settings.discord_webhook_url)"
```

### Aucun deal ne s'affiche

```bash
# Vérifier la base de données
python -c "from app.database import SessionLocal; from app.models.flight import Flight; db = SessionLocal(); print(f'{db.query(Flight).count()} vols en base'); db.close()"

# Lancer une recherche manuelle
python -c "from app.scheduler.tasks import test_search; test_search()"
```

### Erreur "Module not found"

```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

## 🎓 Extensions Possibles

### 1. Ajouter plus de destinations

Modifier `.env` et ajouter les codes IATA souhaités.

### 2. Créer des alertes par email

Créer un nouveau fichier `app/services/email_notifier.py` inspiré de `discord_notifier.py`.

### 3. Améliorer le scoring

Ajouter des critères :
- Horaires de vol (préférer les horaires de jour)
- Compagnies aériennes favorites
- Bonus pour les vols directs

### 4. Interface mobile

Utiliser FastAPI + React Native ou créer une PWA.

### 5. Multi-utilisateurs

Ajouter un système d'authentification et des préférences personnalisées.

## 📄 Licence

Ce projet est à usage personnel et éducatif.

## 💬 Support

Pour toute question :
1. Lire attentivement ce README
2. Vérifier les fonctions de test
3. Consulter la documentation API : `/docs`

---

**Créé avec ❤️ pour trouver les meilleurs deals de vols !**
