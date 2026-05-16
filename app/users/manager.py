"""
Agro AI — User Manager
Foydalanuvchilarni boshqarish: qo'shish, o'chirish, rol berish.
Rollar: admin, manager, viewer.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import ADMIN_IDS, DATA_DIR

logger = logging.getLogger("agro_ai.users.manager")

USERS_FILE = DATA_DIR / "users.json"


@dataclass
class User:
    """Bitta foydalanuvchi."""
    user_id: int
    username: str = ""
    name: str = ""
    role: str = "viewer"  # admin, manager, viewer
    added_by: str = "system"
    added_at: str = ""
    active: bool = True

    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat()


class UserManager:
    """
    Foydalanuvchilarni boshqarish.
    - add_user, remove_user, list_users
    - is_allowed, is_admin, set_role
    - Har bir o'zgarishda data/users.json ga saqlash
    """

    def __init__(self):
        self._users: Dict[int, User] = {}
        self._load()

    def _load(self) -> None:
        """users.json dan yuklash yoki ADMIN_IDS dan migrate qilish."""
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for u_data in data.get("allowed_users", []):
                    user = User(**u_data)
                    self._users[user.user_id] = user
                logger.info(f"✅ {len(self._users)} ta foydalanuvchi yuklandi")
            except Exception as e:
                logger.error(f"users.json yuklashda xato: {e}")
                self._migrate_from_env()
        else:
            self._migrate_from_env()

    def _migrate_from_env(self) -> None:
        """
        Birinchi ishga tushganda .env dagi ALLOWED_USER_IDS ni users.json ga migrate qilish.
        """
        logger.info("📦 ADMIN_IDS dan users.json ga migrate qilinmoqda...")
        for i, uid in enumerate(ADMIN_IDS):
            role = "admin" if i == 0 else "manager"
            user = User(
                user_id=uid,
                username="admin" if i == 0 else f"user_{uid}",
                name="Admin" if i == 0 else f"User {uid}",
                role=role,
                added_by="system",
            )
            self._users[uid] = user
        self._save()
        logger.info(f"✅ {len(self._users)} ta foydalanuvchi migrate qilindi")

    def _save(self) -> None:
        """users.json ga saqlash."""
        try:
            data = {
                "admin_ids": [u.user_id for u in self._users.values() if u.role == "admin"],
                "allowed_users": [asdict(u) for u in self._users.values()],
            }
            USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"users.json saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def add_user(
        self,
        user_id: int,
        username: str = "",
        name: str = "",
        role: str = "viewer",
        added_by: str = "admin",
    ) -> User:
        """Yangi foydalanuvchi qo'shish."""
        if user_id in self._users:
            # Mavjud foydalanuvchini yangilash
            self._users[user_id].active = True
            self._users[user_id].role = role
            self._save()
            return self._users[user_id]

        user = User(
            user_id=user_id,
            username=username,
            name=name,
            role=role,
            added_by=added_by,
        )
        self._users[user_id] = user
        self._save()
        logger.info(f"➕ Foydalanuvchi qo'shildi: {user_id} ({role})")
        return user

    def remove_user(self, user_id: int, removed_by: int = 0) -> tuple:
        """
        Foydalanuvchini o'chirish.
        Returns: (success: bool, message: str)
        """
        if user_id not in self._users:
            return False, "Foydalanuvchi topilmadi."

        user = self._users[user_id]

        # Admin o'zini o'chira olmasin
        if user_id == removed_by:
            return False, "O'zingizni o'chira olmaysiz."

        # Oxirgi adminni o'chirib bo'lmasin
        if user.role == "admin":
            admin_count = sum(1 for u in self._users.values() if u.role == "admin" and u.active)
            if admin_count <= 1:
                return False, "Oxirgi adminni o'chirib bo'lmaydi."

        user.active = False
        self._save()
        logger.info(f"🗑 Foydalanuvchi o'chirildi: {user_id} (by {removed_by})")
        return True, f"✅ {user.name or user.username} o'chirildi."

    def list_users(self, active_only: bool = True) -> List[User]:
        """Barcha foydalanuvchilar ro'yxati."""
        users = list(self._users.values())
        if active_only:
            users = [u for u in users if u.active]
        return users

    def get_user(self, user_id: int) -> Optional[User]:
        """Foydalanuvchini olish."""
        return self._users.get(user_id)

    # ─────────────────────────────────────────────────────
    # AUTH
    # ─────────────────────────────────────────────────────

    def is_allowed(self, user_id: int) -> bool:
        """Foydalanuvchiga ruxsat bormi?"""
        user = self._users.get(user_id)
        if user and user.active:
            return True
        # Fallback: ADMIN_IDS dan tekshirish (backward compatibility)
        if user_id in ADMIN_IDS:
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        """Admin ekanligini tekshirish."""
        user = self._users.get(user_id)
        if user and user.active and user.role == "admin":
            return True
        # Fallback
        if ADMIN_IDS and user_id == ADMIN_IDS[0]:
            return True
        return False

    def is_manager_or_above(self, user_id: int) -> bool:
        """Manager yoki admin ekanligini tekshirish."""
        user = self._users.get(user_id)
        if user and user.active and user.role in ("admin", "manager"):
            return True
        if user_id in ADMIN_IDS:
            return True
        return False

    # ─────────────────────────────────────────────────────
    # ROLE MANAGEMENT
    # ─────────────────────────────────────────────────────

    def set_role(self, user_id: int, role: str, changed_by: int = 0) -> tuple:
        """
        Rol o'zgartirish.
        Returns: (success: bool, message: str)
        """
        if role not in ("admin", "manager", "viewer"):
            return False, "Noto'g'ri rol. admin/manager/viewer bo'lishi kerak."

        if user_id not in self._users:
            return False, "Foydalanuvchi topilmadi."

        user = self._users[user_id]

        # Oxirgi admin rolini o'zgartirib bo'lmasin
        if user.role == "admin" and role != "admin":
            admin_count = sum(1 for u in self._users.values() if u.role == "admin" and u.active)
            if admin_count <= 1:
                return False, "Oxirgi admin rolini o'zgartirib bo'lmaydi."

        old_role = user.role
        user.role = role
        self._save()
        logger.info(f"🔄 Rol o'zgartirildi: {user_id} ({old_role} → {role}) by {changed_by}")
        return True, f"✅ {user.name or user.username}: {old_role} → {role}"

    # ─────────────────────────────────────────────────────
    # FORMATTING
    # ─────────────────────────────────────────────────────

    def format_user_list(self) -> str:
        """Foydalanuvchilar ro'yxatini formatlash."""
        users = self.list_users()
        if not users:
            return "_(Foydalanuvchi yo'q.)_"

        role_emoji = {"admin": "👑", "manager": "📋", "viewer": "👁"}
        lines = []
        for i, u in enumerate(users, 1):
            emoji = role_emoji.get(u.role, "👤")
            lines.append(
                f"*{i}.* {emoji} `{u.user_id}`\n"
                f"   {u.name or u.username} | {u.role}"
            )
        return "\n".join(lines)


# Global instance
user_manager = UserManager()
