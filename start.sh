#!/bin/bash

echo "========================================"
echo "Flight Deal Tracker - Lancement"
echo "========================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    echo ""
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate
echo ""

# Installer les dépendances si nécessaire
echo "Installation des dépendances..."
pip install -q -r requirements.txt
echo ""

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "ATTENTION: Le fichier .env n'existe pas!"
    echo "Copiez .env.example vers .env et configurez vos clés API."
    echo ""
    exit 1
fi

# Lancer l'application
echo "Lancement de l'application..."
echo "Interface web: http://localhost:8000"
echo "Documentation API: http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'application."
echo ""
python app/main.py
