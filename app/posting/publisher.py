"""
Agro AI — Instagram Publisher
Instagram Graph API orqali post publish qilish.

ESLATMA: Instagram Graph API Business account talab qiladi.
Fallback: API bo'lmasa — Telegram'ga reminder + tayyor caption yuborish.
"""

import logging
from typing import Optional

from app.settings import ADMIN_IDS

logger = logging.getLogger("agro_ai.posting.publisher")


class InstagramPublisher:
    """
    Instagram'ga post publish qilish.

    Hozircha fallback rejimda ishlaydi:
    - Instagram Graph API Business account talab qiladi
    - API mavjud bo'lmasa — Telegram'ga reminder yuboradi
    - Tayyor caption + hashtag + media path ko'rsatadi

    Keyinroq Graph API integratsiya qo'shiladi.
    """

    def __init__(self, access_token: str = ""):
        self.access_token = access_token
        self._api_available = bool(access_token)

    async def publish(
        self,
        caption: str,
        media_path: str = "",
        hashtags: list = None,
    ) -> dict:
        """
        Post publish qilish.
        Returns: {"success": bool, "method": str, "message": str}
        """
        if self._api_available:
            return await self._publish_via_api(caption, media_path, hashtags)
        else:
            return self._prepare_reminder(caption, media_path, hashtags)

    async def _publish_via_api(
        self,
        caption: str,
        media_path: str,
        hashtags: list,
    ) -> dict:
        """
        Instagram Graph API orqali publish.
        TODO: Business account bilan integratsiya.
        """
        # Placeholder — keyinroq implement qilinadi
        logger.warning("Instagram Graph API hali ulangan emas")
        return {
            "success": False,
            "method": "api",
            "message": "Instagram Graph API hali sozlanmagan. Business account kerak.",
        }

    def _prepare_reminder(
        self,
        caption: str,
        media_path: str,
        hashtags: list,
    ) -> dict:
        """
        Fallback: Telegram'ga reminder tayyorlash.
        """
        full_caption = caption
        if hashtags:
            full_caption += "\n\n" + " ".join(f"#{h}" for h in hashtags)

        reminder_text = (
            "📱 *POST VAQTI KELDI!*\n\n"
            "Tayyor kontent:\n\n"
            f"📝 *Caption:*\n{full_caption[:500]}\n"
        )

        if media_path:
            reminder_text += f"\n📁 Media: `{media_path}`\n"

        reminder_text += (
            "\n💡 *Qadamlar:*\n"
            "1. Instagram'ni oching\n"
            "2. Yangi post/reel yarating\n"
            "3. Yuqoridagi caption'ni nusxalang\n"
            "4. Post qiling! ✅"
        )

        return {
            "success": True,
            "method": "reminder",
            "message": reminder_text,
        }

    def format_for_copy(self, caption: str, hashtags: list = None) -> str:
        """Nusxalash uchun tayyor format."""
        text = caption
        if hashtags:
            text += "\n\n" + " ".join(f"#{h}" for h in hashtags)
        return text
