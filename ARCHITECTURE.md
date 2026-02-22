# 🏗️ ARCHITECTURE DÉTAILLÉE

Ce document explique en détail comment l'application fonctionne.

## 📊 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEDULER (APScheduler)                  │
│              Exécution toutes les 6 heures                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              SERVICE: flight_api.py                         │
│              Appel API Amadeus                              │
│              - Authentification OAuth                       │
│              - Recherche multi-destinations                 │
│              - Parsing des résultats                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              SERVICE: scoring.py                            │
│              Calcul du score (0-100)                        │
│              - Pénalité prix (50%)                          │
│              - Pénalité durée (30%)                         │
│              - Pénalité escales (20%)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              SERVICE: deduplication.py                      │
│              Génération hash MD5                            │
│              - Hash = f(dates, prix, vol)                   │
│              - Vérification en base de données              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              BASE DE DONNÉES (PostgreSQL/SQLite)            │
│              Table: flights                                 │
│              - Sauvegarde du vol                            │
│              - Marquage notified=False                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              SERVICE: discord_notifier.py                   │
│              Envoi notification Discord                     │
│              - Embed formaté                                │
│              - Bouton de réservation                        │
│              - Update notified=True                         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Structure des Fichiers

### 🔧 Configuration (`app/config.py`)

**Rôle** : Centralise toutes les variables d'environnement.

**Principe** : Utilise Pydantic pour valider automatiquement que toutes les variables nécessaires sont présentes et du bon type.

**Exemple** :
```python
from app.config import settings
print(settings.departure_airport)  # "GVA"
```

### 🗄️ Base de Données (`app/database.py`)

**Rôle** : Gère la connexion à PostgreSQL/SQLite avec SQLAlchemy.

**Composants** :
- `engine` : Connexion à la base de données
- `SessionLocal` : Factory pour créer des sessions
- `Base` : Classe parent de tous les modèles
- `get_db()` : Générateur de session pour FastAPI

**ORM SQLAlchemy** :
Au lieu de :
```sql
SELECT * FROM flights WHERE price < 500;
```

On écrit :
```python
db.query(Flight).filter(Flight.price < 500).all()
```

### 📊 Modèles (`app/models/flight.py`)

**Rôle** : Définit la structure de la table `flights`.

**Colonnes principales** :
- `id` : Clé primaire auto-incrémentée
- `flight_hash` : Hash unique pour déduplication
- `departure_airport` / `destination_airport` : Codes IATA
- `departure_date` / `return_date` : Dates du vol
- `price` : Prix en EUR
- `score` : Score calculé (0-100)
- `notified` : Booléen (déjà notifié ou non)

**Index** : Créés sur les colonnes fréquemment filtrées (price, score, destination)

### ✅ Schémas (`app/schemas/flight.py`)

**Rôle** : Valide les données entrantes/sortantes de l'API avec Pydantic.

**Différence Modèle vs Schéma** :
- **Modèle** : Structure de la table en BDD (SQLAlchemy)
- **Schéma** : Validation des données API (Pydantic)

**Types de schémas** :
- `FlightBase` : Champs communs
- `FlightCreate` : Pour créer un vol
- `FlightUpdate` : Pour modifier un vol
- `FlightResponse` : Pour renvoyer un vol au client

### 🛫 Service API Amadeus (`app/services/flight_api.py`)

**Rôle** : Communication avec l'API Amadeus.

**Workflow** :
1. **Authentification OAuth** :
   - Demande un token avec API key/secret
   - Cache le token (expire après ~30 min)
   - Régénère automatiquement si expiré

2. **Recherche de vols** :
   - Génère des dates sur 6 mois glissants
   - Teste plusieurs durées de séjour (7, 10, 13 jours)
   - Recherche pour chaque destination
   - Parse les résultats complexes

3. **Parsing** :
   - Extrait prix, dates, compagnie, escales, durée
   - Simplifie la structure JSON Amadeus

**Optimisation** :
- Recherches espacées (tous les 7 jours) pour ne pas saturer les quotas
- Async/await pour paralléliser les requêtes

### 📈 Service Scoring (`app/services/scoring.py`)

**Rôle** : Calcule un score pour chaque vol.

**Formule** :
```python
score = 100 - (
    pénalité_prix * 0.50 +
    pénalité_durée * 0.30 +
    pénalité_escales * 0.20
)
```

**Pénalités** :
- **Prix** : 0€-200€ = 0%, 500€ = 30%, 1000€+ = 80%+
- **Durée** : <8h = 0%, 12h = 20%, 20h = 60%, 30h+ = 100%
- **Escales** : Direct = 0%, 1 escale = 40%, 2+ = 80%+

**Personnalisation** :
Modifiez les constantes `WEIGHT_PRICE`, `WEIGHT_DURATION`, `WEIGHT_STOPS` selon vos priorités.

### 🔒 Service Déduplication (`app/services/deduplication.py`)

**Rôle** : Évite les notifications en double.

**Hash MD5** :
```python
hash_string = f"{date_depart}|{date_retour}|{prix}|{num_vol}|{compagnie}"
hash_md5 = hashlib.md5(hash_string.encode()).hexdigest()
```

**Vérifications** :
1. `is_duplicate()` : Le vol existe-t-il en BDD ?
2. `should_notify()` : Doit-on notifier (nouveau OU pas encore notifié) ?

### 📨 Service Discord (`app/services/discord_notifier.py`)

**Rôle** : Envoie des notifications formatées sur Discord.

**Embeds Discord** :
- Titre coloré selon le score
- Champs structurés (dates, prix, durée, etc.)
- Bouton "Réserver" cliquable

**Codes couleur** :
- Score 90+ : 🔥 Rouge (exceptionnel)
- Score 80-89 : ⭐ Orange (excellent)
- Score 70-79 : ✅ Vert (bon)

### ⏰ Scheduler (`app/scheduler/tasks.py`)

**Rôle** : Exécute automatiquement la recherche toutes les X heures.

**APScheduler** :
- `AsyncIOScheduler` : Compatible avec async/await
- `IntervalTrigger` : Exécution périodique
- `max_instances=1` : Une seule exécution à la fois

**Tâche principale** : `search_and_notify_deals()`
1. Recherche tous les vols
2. Calcule les scores
3. Filtre par seuil
4. Vérifie les doublons
5. Sauvegarde en BDD
6. Notifie sur Discord
7. Log le résumé

### 🌐 Routes API (`app/routers/deals.py`)

**Rôle** : Définit les endpoints HTTP.

**Endpoints disponibles** :
- `GET /deals/` : Liste tous les deals (avec filtres)
- `GET /deals/{id}` : Récupère un deal par ID
- `GET /deals/destination/{code}` : Filtre par destination
- `GET /deals/best/` : Meilleur deal disponible
- `GET /deals/stats/summary` : Statistiques globales

**Filtres** :
- `min_score` : Score minimum
- `destination` : Code IATA
- `sort_by` : Tri (price, score, date)
- `order` : Ordre (asc, desc)

### 🖥️ Interface Web (`app/templates/index.html`)

**Rôle** : Interface utilisateur pour consulter les deals.

**Fonctionnalités** :
- Affichage des statistiques (total, prix moyen, etc.)
- Filtres interactifs
- Tri dynamique
- Cartes de deals cliquables
- Bouton "Réserver" redirigeant vers le booking

**JavaScript** :
- Appels fetch() vers l'API
- Rendu dynamique des résultats
- Gestion des filtres

### 🚀 Application Principale (`app/main.py`)

**Rôle** : Point d'entrée de FastAPI.

**Lifespan** :
- **Démarrage** : Init BDD + Démarrage scheduler
- **Arrêt** : Arrêt propre du scheduler

**Middlewares** :
- Gestionnaires d'erreurs 404/500
- Templates Jinja2 pour HTML
- Inclusion des routers

## 🔄 Flow Complet d'une Recherche

```
1. SCHEDULER déclenche search_and_notify_deals()
   └─> Toutes les 6 heures

2. AMADEUS API : Recherche des vols
   ├─> Authentification OAuth
   ├─> Recherche multi-destinations
   └─> Parse des résultats

3. SCORING : Pour chaque vol trouvé
   ├─> Calcul score = f(prix, durée, escales)
   └─> Filtrage si score < seuil

4. DÉDUPLICATION : Génère hash unique
   ├─> Hash = MD5(dates + prix + vol)
   └─> Vérifie si déjà en BDD

5. BASE DE DONNÉES : Sauvegarde
   ├─> INSERT nouveau vol
   └─> Marqué notified=False

6. DISCORD : Notification
   ├─> Envoi embed formaté
   ├─> Update notified=True
   └─> Log succès/échec

7. RÉSUMÉ : Logger les statistiques
   ├─> Nombre de deals trouvés
   ├─> Nombre de notifications envoyées
   └─> Meilleur deal du jour
```

## 🎯 Points Clés pour Débutants

### 1. **Async/Await**
Permet de faire plusieurs choses en même temps :
```python
# Au lieu d'attendre chaque appel séquentiellement
result1 = appel_api_1()  # Attend 2s
result2 = appel_api_2()  # Attend 2s
# Total : 4s

# Avec async, en parallèle
result1, result2 = await asyncio.gather(
    appel_api_1(),  # 2s
    appel_api_2()   # 2s
)
# Total : 2s
```

### 2. **ORM SQLAlchemy**
Traduit Python → SQL automatiquement :
```python
# Python
flights = db.query(Flight).filter(Flight.price < 500).all()

# SQL généré automatiquement
# SELECT * FROM flights WHERE price < 500;
```

### 3. **Dependency Injection (FastAPI)**
FastAPI injecte automatiquement les dépendances :
```python
@app.get("/deals")
def get_deals(db: Session = Depends(get_db)):
    # FastAPI crée automatiquement la session BDD
    # et la ferme après l'exécution
```

### 4. **Pydantic Validation**
Vérifie automatiquement les types :
```python
class FlightBase(BaseModel):
    price: float = Field(gt=0)  # Prix > 0

# Si quelqu'un envoie price=-100, Pydantic rejette
```

## 🔧 Extensibilité

### Ajouter une nouvelle destination
1. Modifier `.env` :
```env
DESTINATIONS=NRT,HND,PVG,HAN,BKK,KUL,CGK,SIN  # +Singapour
```

2. Mettre à jour `index.html` (optionnel) :
```html
<option value="SIN">Singapour</option>
```

### Modifier la formule de scoring
Éditer `app/services/scoring.py` :
```python
# Donner plus d'importance au prix
WEIGHT_PRICE = 0.70      # 70%
WEIGHT_DURATION = 0.20   # 20%
WEIGHT_STOPS = 0.10      # 10%
```

### Ajouter une nouvelle API de vols
1. Créer `app/services/skyscanner_api.py`
2. Implémenter la même interface que `amadeus_api.py`
3. Combiner les résultats dans `search_and_notify_deals()`

## 📚 Ressources Complémentaires

- **FastAPI** : https://fastapi.tiangolo.com
- **SQLAlchemy** : https://docs.sqlalchemy.org
- **Pydantic** : https://docs.pydantic.dev
- **Amadeus API** : https://developers.amadeus.com
- **Discord Webhooks** : https://discord.com/developers/docs/resources/webhook

---

**Cette architecture est conçue pour être :**
- ✅ **Maintenable** : Code bien organisé en modules
- ✅ **Évolutive** : Facile d'ajouter de nouvelles fonctionnalités
- ✅ **Pédagogique** : Commentaires détaillés partout
- ✅ **Robuste** : Gestion d'erreurs, logging, validation
