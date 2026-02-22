# 🚀 COMMENCEZ ICI !

Bienvenue dans votre application **Flight Deal Tracker** !

Ce fichier vous guide dans les **premiers pas**.

---

## 📚 Quelle documentation lire ?

Voici les fichiers dans **l'ordre recommandé** :

### 1️⃣ **VOUS ÊTES ICI** → `START_HERE.md`
   Lisez ce fichier en premier !

### 2️⃣ `QUICKSTART.md` ⚡
   **Guide de démarrage rapide** (5 minutes)
   - Installation en 5 étapes
   - Lancement immédiat
   - Pour les pressés !

### 3️⃣ `TUTORIAL_API_KEYS.md` 🔑
   **Obtenir vos clés API** (15 minutes)
   - Créer un compte Amadeus (gratuit)
   - Créer un webhook Discord (gratuit)
   - Captures d'écran et explications détaillées

### 4️⃣ `CHECKLIST.md` ✅
   **Vérifier votre installation**
   - Liste de tous les points à vérifier
   - Troubleshooting des problèmes courants
   - À utiliser pendant l'installation

### 5️⃣ `README.md` 📖
   **Documentation complète**
   - Fonctionnalités détaillées
   - Configuration avancée
   - Déploiement en production

### 6️⃣ `ARCHITECTURE.md` 🏗️
   **Comprendre l'application** (pour approfondir)
   - Comment ça marche en détail
   - Flow de données
   - Architecture technique

### 7️⃣ `PROJECT_STRUCTURE.txt` 📁
   **Structure des fichiers**
   - Arborescence visuelle
   - Rôle de chaque fichier
   - Référence rapide

---

## 🎯 Parcours Rapide (30 minutes)

### Pour démarrer en 30 minutes :

1. **Lisez** `QUICKSTART.md` (5 min)
2. **Suivez** `TUTORIAL_API_KEYS.md` (15 min)
3. **Configurez** votre `.env` (5 min)
4. **Lancez** l'application avec `start.bat` ou `start.sh`
5. **Vérifiez** avec `CHECKLIST.md` (5 min)

✅ **C'est tout !** Votre application tourne.

---

## 🛠️ Fichiers Utilitaires

### `test_config.py` 🧪
Script Python pour tester votre configuration.
```bash
python test_config.py
```

### `start.bat` / `start.sh` 🚀
Scripts de lancement automatique.
- Windows : Double-cliquez sur `start.bat`
- Mac/Linux : `./start.sh`

### `.env.example` / `.env.template` ⚙️
Templates pour créer votre fichier `.env`

---

## 🆘 En cas de problème

1. **Consultez** `CHECKLIST.md` → Section "Problèmes Courants"
2. **Lancez** `python test_config.py` pour diagnostiquer
3. **Relisez** `TUTORIAL_API_KEYS.md` étape par étape
4. **Vérifiez** les logs dans le terminal

---

## 📊 Ce que fait l'application

En résumé :

1. 🔍 **Recherche** des vols depuis Genève vers l'Asie (via API Amadeus)
2. 📈 **Calcule** un score pour chaque vol (prix + durée + escales)
3. 💾 **Stocke** les meilleurs deals en base de données
4. 📨 **Notifie** sur Discord quand un bon deal apparaît
5. 🌐 **Affiche** tous les deals sur une interface web

**Automatiquement, toutes les 6 heures !**

---

## 🎓 Pour les Débutants

### Vous débutez en programmation ?

Ne vous inquiétez pas ! Le code est **très commenté** et **pédagogique**.

Chaque fichier Python contient :
- ✅ Des explications ligne par ligne
- ✅ Des exemples d'utilisation
- ✅ Des commentaires "Pourquoi ?" et "Comment ?"

### Ordre de lecture du code (si vous voulez apprendre) :

1. `app/config.py` → Variables de configuration
2. `app/models/flight.py` → Structure des données
3. `app/services/scoring.py` → Logique simple
4. `app/services/flight_api.py` → Appels API
5. `app/main.py` → Application principale

---

## 🚀 Prochaines Étapes

Une fois l'application lancée :

1. **Attendez** les premières notifications Discord (6h max)
2. **Consultez** http://localhost:8000 pour voir les deals
3. **Personnalisez** les paramètres dans `.env`
4. **Déployez** en production (voir `README.md`)

---

## 📞 Support

- 📖 Documentation complète : `README.md`
- 🏗️ Architecture détaillée : `ARCHITECTURE.md`
- ✅ Vérification : `CHECKLIST.md`
- 🔑 Aide API : `TUTORIAL_API_KEYS.md`

---

**Bon voyage avec vos deals de vols ! ✈️🌏**
