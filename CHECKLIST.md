# ✅ CHECKLIST DE VÉRIFICATION

Utilisez cette checklist pour vous assurer que tout est bien configuré.

## 📦 1. Installation

- [ ] Python 3.11+ installé (`python --version`)
- [ ] Environnement virtuel créé (`python -m venv venv`)
- [ ] Environnement virtuel activé (vous voyez `(venv)` dans le terminal)
- [ ] Dépendances installées (`pip install -r requirements.txt`)

## 🔑 2. Configuration API

### Amadeus API
- [ ] Compte créé sur https://developers.amadeus.com
- [ ] Application créée dans "My Self-Service Workspace"
- [ ] API Key copiée
- [ ] API Secret copié
- [ ] Clés ajoutées dans `.env`
- [ ] URL de test utilisée : `https://test.api.amadeus.com`

### Discord Webhook
- [ ] Serveur Discord créé ou accessible
- [ ] Webhook créé (Paramètres > Intégrations > Webhooks)
- [ ] URL du webhook copiée
- [ ] URL ajoutée dans `.env`

## ⚙️ 3. Fichier .env

- [ ] Fichier `.env` créé (copié depuis `.env.example`)
- [ ] `AMADEUS_API_KEY` rempli
- [ ] `AMADEUS_API_SECRET` rempli
- [ ] `AMADEUS_API_URL` = `https://test.api.amadeus.com`
- [ ] `DISCORD_WEBHOOK_URL` rempli
- [ ] `DATABASE_URL` configuré (SQLite par défaut : OK)
- [ ] `DEPARTURE_AIRPORT` = `GVA` (ou modifié selon vos besoins)

## 🧪 4. Tests de Connexion

### Test Amadeus
```bash
curl -X POST "https://test.api.amadeus.com/v1/security/oauth2/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=VOTRE_API_KEY" \
  -d "client_secret=VOTRE_API_SECRET"
```
- [ ] Vous recevez un `access_token`

### Test Discord
```bash
curl -X POST "VOTRE_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test de webhook"}'
```
- [ ] Vous voyez un message dans votre canal Discord

## 🚀 5. Lancement de l'Application

- [ ] Application lancée (`python app/main.py` ou `./start.sh` ou `start.bat`)
- [ ] Pas d'erreur au démarrage
- [ ] Message "✅ Application prête !" affiché
- [ ] Tables de base de données créées

## 🌐 6. Vérification Web

- [ ] Interface web accessible sur http://localhost:8000
- [ ] Page charge correctement (même si aucun deal)
- [ ] Documentation API accessible sur http://localhost:8000/docs
- [ ] Swagger UI s'affiche correctement

## 📊 7. Vérification API

Testez chaque endpoint :

- [ ] GET http://localhost:8000/health → `{"status": "healthy"}`
- [ ] GET http://localhost:8000/deals/ → Liste (vide au début)
- [ ] GET http://localhost:8000/deals/stats/summary → Statistiques

## 🔍 8. Test de Recherche Manuelle

Lancez une recherche manuellement pour tester :

```python
import asyncio
from app.scheduler.tasks import run_search_now
asyncio.run(run_search_now())
```

Vérifiez :
- [ ] Logs "🔍 Recherche de vols..." affichés
- [ ] Appels API Amadeus réussis
- [ ] Vols trouvés et enregistrés en BDD
- [ ] Notifications Discord reçues (si deals avec bon score)

## 📁 9. Fichiers Présents

Vérifiez que tous les fichiers sont là :

```
✅ README.md
✅ QUICKSTART.md
✅ ARCHITECTURE.md
✅ TUTORIAL_API_KEYS.md
✅ CHECKLIST.md (ce fichier)
✅ PROJECT_STRUCTURE.txt
✅ requirements.txt
✅ .env.example
✅ .env.template
✅ .gitignore
✅ start.bat
✅ start.sh
✅ app/main.py
✅ app/config.py
✅ app/database.py
✅ app/models/flight.py
✅ app/schemas/flight.py
✅ app/services/flight_api.py
✅ app/services/scoring.py
✅ app/services/deduplication.py
✅ app/services/discord_notifier.py
✅ app/routers/deals.py
✅ app/scheduler/tasks.py
✅ app/templates/index.html
✅ app/*/__init__.py (tous les packages)
```

## 🎯 10. Fonctionnement Automatique

- [ ] Scheduler démarré (message "⏰ Scheduler configuré")
- [ ] Première recherche prévue dans X heures (selon config)
- [ ] Application tourne en continu sans erreur

## 🔧 11. Personnalisation (Optionnel)

Si vous voulez personnaliser :

- [ ] Destinations modifiées dans `.env`
- [ ] Score threshold ajusté dans `.env`
- [ ] Intervalle de recherche modifié dans `.env`
- [ ] Formule de scoring personnalisée dans `app/services/scoring.py`

## 📈 12. Monitoring

Pour suivre le fonctionnement :

- [ ] Logs affichés dans le terminal (mode DEBUG=True)
- [ ] Notifications Discord reçues pour les bons deals
- [ ] Base de données se remplit (`flight_deals.db` si SQLite)
- [ ] Interface web se met à jour avec les nouveaux deals

## 🚨 Problèmes Courants

### "ModuleNotFoundError"
→ Environnement virtuel pas activé OU dépendances pas installées
→ Solution : `pip install -r requirements.txt`

### "Invalid API credentials"
→ Mauvaises clés Amadeus
→ Solution : Vérifiez `.env` et refaites le tutoriel

### "Webhook failed"
→ Mauvaise URL Discord
→ Solution : Testez avec curl, vérifiez l'URL complète

### "No flights found"
→ Quotas API dépassés OU pas de vols disponibles
→ Solution : Attendez ou vérifiez les logs

### "Port already in use"
→ Une autre application utilise le port 8000
→ Solution : Changez `PORT=8001` dans `.env`

## ✅ Validation Finale

Tous les points cochés ?

→ 🎉 **Votre application est prête !**

Prochaines étapes :
1. Laissez l'application tourner
2. Attendez les notifications Discord
3. Consultez l'interface web régulièrement
4. Déployez en production (voir README.md)

---

**Besoin d'aide ?** Relisez la documentation ou ouvrez une issue !
