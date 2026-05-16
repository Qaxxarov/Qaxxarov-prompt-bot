"""
Agro AI — Proaktiv Alert Tizimi
Muhim hodisalarda real-time Telegram alert.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import ADMIN_IDS, DATA_DIR

logger = logging.getLogger("agro_ai.ops.alerts")

ALERTS_DIR = DATA_DIR / "alerts"
ALERTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Alert:
    """Bitta alert."""
    id: str = ""
    alert_type: str = ""  # follower_milestone, viral_reel, er_drop, er_spike, no_post, best_time
    message: str = ""
    data: Dict = field(default_factory=dict)
    sent: bool = False
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"alert_{int(time.time() * 1000)}"
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class AlertSettings:
    """Foydalanuvchi alert sozlamalari."""
    enabled: bool = True
    follower_milestone: bool = True
    viral_reel: bool = True
    er_drop: bool = True
    er_spike: bool = True
    no_post: bool = True
    best_time: bool = True


class AlertManager:
    """
    Proaktiv alert tizimi.
    Trigger'lar:
    - follower_milestone: 1000, 5000, 10000, 50000 ga yetganda
    - viral_reel: views > 3x o'rtacha
    - er_drop: ER 20%+ tushganda
    - er_spike: ER 50%+ ko'tarilganda
    - no_post: 48 soat post qilinmaganda
    - best_time: Eng yaxshi post vaqti 30 min oldin
    """

    MILESTONES = [1000, 5000, 10000, 25000, 50000, 100000]

    def __init__(self, account_id: str):
        self.account_id = account_id
        self._alerts_path = ALERTS_DIR / f"{account_id}_alerts.json"
        self._settings_path = ALERTS_DIR / f"{account_id}_settings.json"
        self._alerts: List[Alert] = []
        self._settings: AlertSettings = AlertSettings()
        self._load()

    def _load(self) -> None:
        """Ma'lumotlarni yuklash."""
        if self._alerts_path.exists():
            try:
                with open(self._alerts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._alerts = [Alert(**a) for a in data]
            except Exception as e:
                logger.error(f"Alerts yuklashda xato: {e}")

        if self._settings_path.exists():
            try:
                with open(self._settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._settings = AlertSettings(**data)
            except Exception as e:
                logger.error(f"Alert settings yuklashda xato: {e}")

    def _save(self) -> None:
        """Saqlash."""
        try:
            # Faqat oxirgi 500 alert
            self._alerts = self._alerts[-500:]
            with open(self._alerts_path, "w", encoding="utf-8") as f:
                json.dump([asdict(a) for a in self._alerts], f, ensure_ascii=False, indent=2)
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self._settings), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Alerts saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # TRIGGER CHECKS
    # ─────────────────────────────────────────────────────

    def check_follower_milestone(self, current_followers: int, prev_followers: int) -> Optional[Alert]:
        """Follower milestone tekshirish."""
        if not self._settings.follower_milestone:
            return None

        for milestone in self.MILESTONES:
            if prev_followers < milestone <= current_followers:
                alert = Alert(
                    alert_type="follower_milestone",
                    message=f"🎉 TABRIKLAYMIZ! {current_followers:,} follower'ga yetdingiz! 🏆",
                    data={"milestone": milestone, "current": current_followers},
                )
                self._alerts.append(alert)
                self._save()
                return alert
        return None

    def check_viral_reel(self, reel_views: int, avg_views: int) -> Optional[Alert]:
        """Viral reel tekshirish (views > 3x o'rtacha)."""
        if not self._settings.viral_reel:
            return None

        if avg_views > 0 and reel_views > avg_views * 3:
            multiplier = round(reel_views / avg_views, 1)
            alert = Alert(
                alert_type="viral_reel",
                message=(
                    f"🚀 VIRAL REEL! {reel_views:,} views!\n"
                    f"O'rtachadan {multiplier}x ko'p! 🔥"
                ),
                data={"views": reel_views, "avg": avg_views, "multiplier": multiplier},
            )
            self._alerts.append(alert)
            self._save()
            return alert
        return None

    def check_er_drop(self, current_er: float, prev_er: float) -> Optional[Alert]:
        """ER 20%+ tushganda."""
        if not self._settings.er_drop:
            return None

        if prev_er > 0 and current_er > 0:
            drop_pct = ((prev_er - current_er) / prev_er) * 100
            if drop_pct >= 20:
                alert = Alert(
                    alert_type="er_drop",
                    message=(
                        f"⚠️ ER TUSHDI! {prev_er:.1f}% → {current_er:.1f}%\n"
                        f"({drop_pct:.0f}% pasayish)\n"
                        f"💡 Kontent sifatini tekshiring!"
                    ),
                    data={"prev_er": prev_er, "current_er": current_er, "drop_pct": drop_pct},
                )
                self._alerts.append(alert)
                self._save()
                return alert
        return None

    def check_er_spike(self, current_er: float, prev_er: float) -> Optional[Alert]:
        """ER 50%+ ko'tarilganda."""
        if not self._settings.er_spike:
            return None

        if prev_er > 0 and current_er > 0:
            spike_pct = ((current_er - prev_er) / prev_er) * 100
            if spike_pct >= 50:
                alert = Alert(
                    alert_type="er_spike",
                    message=(
                        f"📈 ER OSHDI! {prev_er:.1f}% → {current_er:.1f}%\n"
                        f"(+{spike_pct:.0f}% o'sish) 🎉\n"
                        f"💡 Shu uslubda davom eting!"
                    ),
                    data={"prev_er": prev_er, "current_er": current_er, "spike_pct": spike_pct},
                )
                self._alerts.append(alert)
                self._save()
                return alert
        return None

    def check_no_post(self, hours_since_last_post: float) -> Optional[Alert]:
        """48 soat post qilinmaganda."""
        if not self._settings.no_post:
            return None

        if hours_since_last_post >= 48:
            # Kuniga 1 marta alert
            recent = [a for a in self._alerts if a.alert_type == "no_post"]
            if recent:
                last = recent[-1]
                if time.time() - last.timestamp < 24 * 3600:
                    return None

            alert = Alert(
                alert_type="no_post",
                message=(
                    f"🚨 48 SOAT POST QILINMADI!\n"
                    f"⏰ Oxirgi post: {int(hours_since_last_post)} soat oldin\n"
                    f"💡 Streak yo'qolmasin — hozir post qiling!"
                ),
                data={"hours": hours_since_last_post},
            )
            self._alerts.append(alert)
            self._save()
            return alert
        return None

    def check_best_time(self, best_hour: int = 19) -> Optional[Alert]:
        """Eng yaxshi post vaqti 30 min oldin."""
        if not self._settings.best_time:
            return None

        now = datetime.now()
        # 30 min oldin = best_hour - 0:30
        if now.hour == best_hour - 1 and now.minute >= 30:
            # Bugun allaqachon alert yuborilganmi?
            today = now.strftime("%Y-%m-%d")
            recent = [
                a for a in self._alerts
                if a.alert_type == "best_time" and
                datetime.fromtimestamp(a.timestamp).strftime("%Y-%m-%d") == today
            ]
            if recent:
                return None

            alert = Alert(
                alert_type="best_time",
                message=(
                    f"⏰ POST VAQTI YAQINLASHDI!\n"
                    f"🕐 30 daqiqadan keyin eng yaxshi vaqt ({best_hour}:00)\n"
                    f"💡 Tayyor kontentni post qiling!"
                ),
                data={"best_hour": best_hour},
            )
            self._alerts.append(alert)
            self._save()
            return alert
        return None

    # ─────────────────────────────────────────────────────
    # SETTINGS
    # ─────────────────────────────────────────────────────

    def get_settings(self) -> AlertSettings:
        """Joriy sozlamalar."""
        return self._settings

    def toggle_alert(self, alert_type: str) -> bool:
        """Alert turini yoqish/o'chirish."""
        if hasattr(self._settings, alert_type):
            current = getattr(self._settings, alert_type)
            setattr(self._settings, alert_type, not current)
            self._save()
            return not current
        return False

    def toggle_all(self, enabled: bool) -> None:
        """Barcha alertlarni yoqish/o'chirish."""
        self._settings.enabled = enabled
        self._save()

    # ─────────────────────────────────────────────────────
    # HISTORY
    # ─────────────────────────────────────────────────────

    def get_history(self, limit: int = 20) -> List[Alert]:
        """Alert tarixi."""
        return self._alerts[-limit:]

    def get_unsent(self) -> List[Alert]:
        """Yuborilmagan alertlar."""
        return [a for a in self._alerts if not a.sent]

    def mark_sent(self, alert_id: str) -> None:
        """Alertni yuborilgan deb belgilash."""
        for a in self._alerts:
            if a.id == alert_id:
                a.sent = True
                break
        self._save()

    def format_settings(self) -> str:
        """Sozlamalarni formatlash."""
        s = self._settings
        on = "✅"
        off = "❌"
        enabled_text = "Yoqilgan" if s.enabled else "O'chirilgan"
        enabled_emoji = "🟢" if s.enabled else "🔴"
        return (
            f"🔔 *ALERT SOZLAMALARI*\n\n"
            f"{enabled_emoji} Umumiy: {enabled_text}\n\n"
            f"{on if s.follower_milestone else off} Follower milestone\n"
            f"{on if s.viral_reel else off} Viral reel\n"
            f"{on if s.er_drop else off} ER tushishi\n"
            f"{on if s.er_spike else off} ER o'sishi\n"
            f"{on if s.no_post else off} Post qilinmagan (48h)\n"
            f"{on if s.best_time else off} Post vaqti eslatma"
        )

    def format_history(self, limit: int = 10) -> str:
        """Tarixni formatlash."""
        history = self.get_history(limit)
        if not history:
            return "_(Alert tarixi bo'sh.)_"

        lines = ["🔔 *ALERT TARIXI*\n"]
        for a in reversed(history):
            dt = datetime.fromtimestamp(a.timestamp).strftime("%d.%m %H:%M")
            sent_mark = "✅" if a.sent else "⏳"
            lines.append(f"{sent_mark} [{dt}] {a.message[:60]}")
        return "\n".join(lines)
