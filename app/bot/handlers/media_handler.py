"""
Agro AI — 📸 MEDIA HANDLER
Video/Rasm qabul qilish → AI orqali kontent paket yaratish.
"""

import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.memory.manager import memory
from app.settings import AI_ENABLED, OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger("agro_ai.bot.media")


@register("media")
@error_handler
async def handle_media_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """Media bo'limi callback handler."""
    await send_typing(update, context)

    if action == "info":
        text = (
            "📸 *MEDIA → KONTENT*\n\n"
            "Botga rasm yoki video yuboring:\n"
            "• 📷 Rasm → AI tavsiflab, kontent paket yaratadi\n"
            "• 🎬 Video → Thumbnail olib, AI tahlil qiladi\n\n"
            "Natija:\n"
            "🎣 3 ta hook varianti\n"
            "📝 Tayyor caption\n"
            "#️⃣ 15 ta optimal hashtag\n"
            "🏆 Viral Score (0-100)\n"
            "⏰ Post vaqti tavsiyasi"
        )
        await send_message(update, text, keyboard=back_button())
    elif action == "history":
        acc = accounts.active
        entries = memory.search_memory(acc.id, category="media_content", limit=5)
        if entries:
            lines = ["📸 *OXIRGI MEDIA KONTENTLAR*\n"]
            for i, e in enumerate(entries, 1):
                lines.append(f"*{i}.* {e.content[:100]}...")
            text = "\n".join(lines)
        else:
            text = "📸 *MEDIA TARIX*\n\n_(Hali media kontent yaratilmagan.)_"
        await send_message(update, text, keyboard=back_button())
    else:
        await send_message(update, "❓ Noma'lum media buyrug'i.", keyboard=back_button())


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Foydalanuvchi rasm yoki video yuborganda ishga tushadi.
    AI orqali kontent paket yaratadi.
    """
    await send_typing(update, context)
    acc = accounts.active

    if not AI_ENABLED:
        await update.message.reply_text(
            "⚠️ AI o'chirilgan (OPENAI_API_KEY kerak).\n"
            "Media tahlil qilish uchun AI yoqilgan bo'lishi kerak."
        )
        return

    # Rasm yoki video ekanligini aniqlash
    is_photo = bool(update.message.photo)
    is_video = bool(update.message.video)

    if not is_photo and not is_video:
        return

    await update.message.reply_text("⏳ *Media tahlil qilinmoqda...* AI ishlayapti.", parse_mode="Markdown")

    try:
        description = ""

        if is_photo:
            # Eng katta rasmni olish
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            file_url = file.file_path

            # OpenAI Vision API orqali tavsif
            description = await _analyze_image_with_vision(file_url, acc)

        elif is_video:
            # Video thumbnail olish
            video = update.message.video
            if video.thumbnail:
                file = await context.bot.get_file(video.thumbnail.file_id)
                file_url = file.file_path
                description = await _analyze_image_with_vision(file_url, acc, is_video=True)
            else:
                description = "Video (thumbnail mavjud emas — umumiy agro kontent)"

        # Kontent paket yaratish
        content_pack = await _generate_content_pack(description, acc)

        # Memory'ga saqlash
        memory.save_memory(
            account_id=acc.id,
            category="media_content",
            content=content_pack[:200],
            tags=["media", "photo" if is_photo else "video", "auto"],
            score=7.0,
            source="generated",
            metadata={"description": description[:100], "type": "photo" if is_photo else "video"},
        )

        await send_message(update, content_pack, keyboard=back_button())

    except Exception as e:
        logger.error(f"Media handler xatosi: {e}")
        await update.message.reply_text(
            "❌ Media tahlilida xato yuz berdi. Qayta urinib ko'ring."
        )


async def _analyze_image_with_vision(file_url: str, acc, is_video: bool = False) -> str:
    """OpenAI Vision API orqali rasm/video thumbnail tavsifi."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        media_type = "video thumbnail" if is_video else "rasm"
        prompt = (
            f"Bu {media_type}ni tavsifla. Niche: {acc.niche}. "
            f"Instagram kontent uchun qanday ishlatish mumkin? "
            f"Qisqa, aniq tavsif ber (2-3 gap)."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": file_url}},
                    ],
                }
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Vision API xatosi: {e}")
        return "Agro mahsulot/ekin rasmi (AI tavsif mavjud emas)"


async def _generate_content_pack(description: str, acc) -> str:
    """AI orqali to'liq kontent paket yaratish."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        # Memory'dan o'rganish konteksti
        learning = memory.get_learning_context(acc.id, "hook", limit=3)
        avoid = memory.avoid_repetition_context(acc.id, "media_content", limit=5)

        system_prompt = acc.get_system_prompt()
        user_prompt = (
            f"Media tavsifi: {description}\n\n"
            f"Shu media asosida Instagram kontent paket yarat:\n\n"
            f"1. 3 ta HOOK varianti (qisqa, kuchli, viral)\n"
            f"2. Tayyor CAPTION (150-200 so'z, emoji bilan)\n"
            f"3. 15 ta optimal HASHTAG (niche + viral mix)\n"
            f"4. VIRAL SCORE (0-100) va sababi\n"
            f"5. Eng yaxshi POST VAQTI tavsiyasi\n\n"
            f"Format:\n"
            f"📸 KONTENT PAKET\n"
            f"🎣 Hook 1: ...\n"
            f"🎣 Hook 2: ...\n"
            f"🎣 Hook 3: ...\n"
            f"📝 Caption: ...\n"
            f"#️⃣ Hashtags: ...\n"
            f"🏆 Viral Score: .../100\n"
            f"⏰ Post vaqti: ...\n"
        )

        if learning:
            user_prompt += f"\n\n{learning}"
        if avoid:
            user_prompt += f"\n\n{avoid}"

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Content pack generation xatosi: {e}")
        return (
            "📸 *KONTENT PAKET*\n\n"
            "⚠️ AI javob yaratishda xato.\n"
            f"Media tavsifi: {description}\n\n"
            "Qayta urinib ko'ring."
        )
