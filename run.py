"""
╔══════════════════════════════════════════════════════╗
║   AGRO AI v2.0 — Unified Entry Point                ║
║                                                      ║
║   Ishlatish:                                         ║
║     python run.py              (Telegram bot)        ║
║     python run.py --dashboard  (Web dashboard)       ║
║     python run.py --both       (Bot + Dashboard)     ║
║     python run.py --check      (Diagnostika)         ║
╚══════════════════════════════════════════════════════╝
"""

import argparse
import signal
import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def handle_shutdown(signum, frame):
    print("\n🛑 Graceful shutdown...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def main():
    parser = argparse.ArgumentParser(description="Agro AI v3.0")
    parser.add_argument("--check", action="store_true", help="Diagnostika va chiqish")
    parser.add_argument("--dashboard", action="store_true", help="Faqat web dashboard")
    parser.add_argument("--both", action="store_true", help="Bot + Dashboard birga")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")), help="Dashboard port")
    args = parser.parse_args()

    from app.settings import print_status, validate, TELEGRAM_BOT_TOKEN

    print_status()

    if args.check:
        issues = validate()
        if issues:
            print(f"\n❌ {len(issues)} ta muammo topildi.")
            sys.exit(1)
        else:
            print("\n✅ Barcha tekshiruvlar o'tdi. Tizim tayyor.")
            sys.exit(0)

    from app.accounts import accounts
    acc = accounts.active
    print(f"\n🌿 Faol akkaunt: {acc.instagram} ({acc.niche[:40]})")

    if args.dashboard:
        # Faqat dashboard
        from app.dashboard.server import run_dashboard
        run_dashboard(port=args.port)

    elif args.both:
        # Bot + Dashboard parallel (auto-restart bilan)
        print("\n🚀 Bot + Dashboard birga ishga tushmoqda...\n")

        def start_dashboard_with_restart():
            """Dashboard crash bo'lsa 5 soniyada qayta ishga tushadi."""
            from app.dashboard.server import run_dashboard
            while True:
                try:
                    run_dashboard(port=args.port)
                except Exception as e:
                    print(f"\n⚠️ Dashboard crash: {e}")
                    print("🔄 5 soniyada qayta ishga tushadi...\n")
                    import time
                    time.sleep(5)

        dash_thread = threading.Thread(target=start_dashboard_with_restart, daemon=True)
        dash_thread.start()

        # Bot asosiy thread'da
        from app.bot.main import run_bot
        run_bot()

    else:
        # Faqat bot (default)
        issues = validate()
        critical = [i for i in issues if "TELEGRAM_BOT_TOKEN" in i]
        if critical:
            print("\n❌ TELEGRAM_BOT_TOKEN o'rnatilmagan. Bot ishga tushmaydi.")
            sys.exit(1)

        print("\n🚀 Telegram bot ishga tushmoqda...\n")
        from app.bot.main import run_bot
        run_bot()


if __name__ == "__main__":
    main()
