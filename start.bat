@echo off
echo ========================================
echo Flight Deal Tracker - Lancement
echo ========================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    echo.
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.

REM Installer les dépendances si nécessaire
echo Installation des dependances...
pip install -q -r requirements.txt
echo.

REM Vérifier si .env existe
if not exist ".env" (
    echo ATTENTION: Le fichier .env n'existe pas!
    echo Copiez .env.example vers .env et configurez vos cles API.
    echo.
    pause
    exit /b 1
)

REM Lancer l'application
echo Lancement de l'application...
echo Interface web: http://localhost:8000
echo Documentation API: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter l'application.
echo.
python app/main.py

pause
