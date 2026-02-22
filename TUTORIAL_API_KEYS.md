# 🔑 TUTORIEL : Obtenir vos Clés API

Ce guide vous explique **étape par étape** comment obtenir vos clés API gratuitement.

---

## 🛫 PARTIE 1 : Amadeus API (GRATUIT)

### Étape 1 : Créer un compte

1. Allez sur **https://developers.amadeus.com**
2. Cliquez sur **"Register"** en haut à droite
3. Remplissez le formulaire :
   - Prénom / Nom
   - Email
   - Mot de passe
   - Acceptez les conditions
4. Validez votre email

### Étape 2 : Créer une application

1. Connectez-vous sur https://developers.amadeus.com
2. Allez dans **"My Self-Service Workspace"**
3. Cliquez sur **"Create new app"**
4. Remplissez :
   - **App name** : Flight Deal Tracker
   - **App description** : Recherche de vols à bas prix
5. Cliquez sur **"Create"**

### Étape 3 : Récupérer les clés

1. Dans votre application, vous verrez :
   - **API Key** (commence généralement par des lettres/chiffres)
   - **API Secret** (chaîne plus longue)
2. **COPIEZ CES DEUX VALEURS** - vous en aurez besoin

### Étape 4 : Configuration dans .env

Ouvrez votre fichier `.env` et remplissez :

```env
AMADEUS_API_KEY=votre_cle_copiee
AMADEUS_API_SECRET=votre_secret_copie
AMADEUS_API_URL=https://test.api.amadeus.com
```

⚠️ **IMPORTANT** : Utilisez **https://test.api.amadeus.com** pour commencer.
L'environnement de test a des quotas plus généreux (2000 appels/mois).

### ✅ Vérification

Pour tester que vos clés fonctionnent :

```bash
curl -X POST "https://test.api.amadeus.com/v1/security/oauth2/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=VOTRE_API_KEY" \
  -d "client_secret=VOTRE_API_SECRET"
```

Si ça fonctionne, vous recevrez un `access_token`.

---

## 🤖 PARTIE 2 : Discord Webhook (GRATUIT)

### Prérequis

Vous devez avoir :
- Un compte Discord
- Un serveur Discord (ou créez-en un)
- Les droits d'administrateur sur ce serveur

### Étape 1 : Accéder aux paramètres du serveur

1. **Ouvrez Discord** (application ou web)
2. **Sélectionnez votre serveur** (dans la liste à gauche)
3. **Clic droit** sur le nom du serveur en haut
4. Cliquez sur **"Paramètres du serveur"**

### Étape 2 : Créer un webhook

1. Dans le menu de gauche, cliquez sur **"Intégrations"**
2. Cliquez sur **"Webhooks"**
3. Cliquez sur **"Créer un webhook"** (ou "New Webhook")
4. Configurez :
   - **Nom** : Flight Deals (ou ce que vous voulez)
   - **Canal** : Sélectionnez le canal où vous voulez recevoir les notifications
   - **Avatar** : Optionnel (vous pouvez mettre une icône d'avion)

### Étape 3 : Copier l'URL du webhook

1. Dans la configuration du webhook, cliquez sur **"Copier l'URL du Webhook"**
2. L'URL ressemble à ça :
   ```
   https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz
   ```
3. **COPIEZ CETTE URL COMPLÈTE**

### Étape 4 : Configuration dans .env

Ouvrez votre fichier `.env` et remplissez :

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz
```

### ✅ Vérification

Pour tester que votre webhook fonctionne :

```bash
curl -X POST "VOTRE_URL_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test de webhook - ça marche !"}'
```

Si ça fonctionne, vous verrez un message dans votre canal Discord.

---

## 📝 RÉCAPITULATIF : Votre fichier .env final

Après avoir suivi ce tutoriel, votre `.env` doit ressembler à ça :

```env
# Base de données (SQLite pour commencer)
DATABASE_URL=sqlite:///./flight_deals.db

# Amadeus API
AMADEUS_API_KEY=abc123def456ghi789
AMADEUS_API_SECRET=xyz789uvw456rst123
AMADEUS_API_URL=https://test.api.amadeus.com

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

# Paramètres (déjà configurés)
DEPARTURE_AIRPORT=GVA
DESTINATIONS=NRT,HND,PVG,HAN,BKK,KUL,CGK
SEARCH_WINDOW_DAYS=180
MIN_STAY_DAYS=7
MAX_STAY_DAYS=14
MAX_STOPS=1
CURRENCY=EUR
ADULTS=1
SCORE_THRESHOLD=70
SEARCH_INTERVAL_HOURS=6
PORT=8000
DEBUG=True
```

---

## 🚀 Prêt à lancer !

Une fois votre `.env` configuré :

1. **Windows** : Double-cliquez sur `start.bat`
2. **Mac/Linux** : Exécutez `./start.sh`

L'application devrait démarrer et vous verrez :
```
✅ Application prête !
🌐 Interface web : http://localhost:8000
```

---

## ❓ FAQ

### "Invalid API key"
- Vérifiez que vous avez bien copié l'API Key ET l'API Secret
- Assurez-vous qu'il n'y a pas d'espaces avant/après
- Vérifiez que votre application Amadeus est bien créée

### "Webhook URL is invalid"
- L'URL doit commencer par `https://discord.com/api/webhooks/`
- Vérifiez qu'elle est complète (avec le token à la fin)
- Testez avec la commande curl ci-dessus

### "Quota exceeded"
- Vous avez dépassé les 2000 appels/mois gratuits
- Attendez le mois prochain
- OU passez à l'environnement de production (payant)

### "Cannot connect to database"
- Pour SQLite : Vérifiez que le chemin est correct
- Pour PostgreSQL : Vérifiez que PostgreSQL est installé et lancé

---

## 🆘 Besoin d'aide ?

Si vous rencontrez un problème :

1. **Vérifiez les logs** : L'application affiche des messages d'erreur détaillés
2. **Consultez la FAQ** ci-dessus
3. **Relisez ce tutoriel** étape par étape
4. **Ouvrez une issue** sur GitHub avec :
   - Le message d'erreur complet
   - Votre configuration (SANS les clés API)
   - Les logs de l'application

---

**Bon développement ! 🚀**
