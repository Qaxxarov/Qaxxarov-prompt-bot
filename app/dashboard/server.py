"""
Agro AI — Dashboard Server
Run with: python -m app.dashboard.server
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import uvicorn
from app.settings import logger


def run_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Dashboard serverni ishga tushirish."""
    logger.info(f"🌐 Dashboard ishga tushmoqda: http://localhost:{port}")
    print(f"\n{'═' * 50}")
    print(f"  🌿 Agro AI Dashboard")
    print(f"  🌐 http://localhost:{port}")
    print(f"  🔑 Parol: .env dagi DASHBOARD_PASSWORD")
    print(f"  To'xtatish: Ctrl+C")
    print(f"{'═' * 50}\n")

    uvicorn.run(
        "app.dashboard.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run_dashboard()
