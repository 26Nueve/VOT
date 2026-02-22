"""
Script de lancement de l'application.

Usage :
    python run.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.debug,  # Auto-reload en mode debug
        log_level="info"
    )
