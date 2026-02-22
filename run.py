"""
Script de lancement de l'application.

Usage :
    python run.py
"""

import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.app_port))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info"
    )