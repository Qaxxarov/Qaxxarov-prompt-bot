"""
Agro AI — ✍️ SSENARIY + 🎞 VEO PROMPTLAR handlers
Real engines: StorytellingEngine + VeoEngine.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.storytelling import StorytellingEngine
from app.ai.veo import VeoEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions

logger = logging.getLogger("agro_ai.bot.ssenariy")


@register("ss")
@error_handler
async def handle_ssenariy(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """✍️ SSENARIY handler — StorytellingEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = StorytellingEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    titles = {
        "reel": "🎤 REEL SSENARIY",
        "kadr": "🎥 KADRLAR REJASI",
        "story": "🎭 EMOTSIONAL STORY",
        "cta": "📢 CTA YARATISH",
        "full": "📝 TO'LIQ PAKET",
    }

    if action not in titles:
        await send_message(update, "❓ Noma'lum ssenariy turi.", keyboard=back_button())
        return

    # Loading message
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *{titles[action]}* yaratilmoqda...\n"
            "_(Cinematic ssenariy tayyorlanmoqda)_",
            parse_mode="Markdown",
        )

    # Route to specific StorytellingEngine methods
    if action == "reel":
        result = await engine.generate_story(
            arc_type="transformation",
            topic="urug' parvarishi yoki hosil ko'paytirish",
            stats=stats,
        )
    elif action == "kadr":
        result = await engine.generate_shot_plan(
            scene_count=10,
            style="cinematic",
            stats=stats,
        )
    elif action == "story":
        result = await engine.generate_emotional_script(
            trigger="pride",
            stats=stats,
        )
    elif action == "cta":
        # CTA uses base generate with specific task
        result = await engine.generate(
            task=(
                "10 ta kuchli CTA (call-to-action) yarat.\n\n"
                "Kategoriyalar:\n"
                "• LIKE uchun (2 ta)\n"
                "• COMMENT uchun (2 ta)\n"
                "• SHARE uchun (2 ta)\n"
                "• FOLLOW uchun (2 ta)\n"
                "• SOTUV uchun (2 ta)\n\n"
                "Har biri: emoji + matn. Qishloq xo'jaligi auditoriyasi uchun.\n"
                "Kuchli, aniq, harakat chaqiruvchi."
            ),
            max_tokens=600,
        )
    elif action == "full":
        result = await engine.generate(
            task=(
                "To'liq reel paketi yarat:\n\n"
                "1. 🎣 HOOK (birinchi 3 soniya — 1 kuchli jumla)\n"
                "2. 🎬 SSENARIY (to'liq voiceover matni, 25 soniyalik)\n"
                "3. 🎥 KADRLAR (5 ta asosiy kadr tavsifi)\n"
                "4. 📝 CAPTION (CTA bilan, 3-4 qator)\n"
                "5. #️⃣ HASHTAGLAR (7 ta)\n"
                "6. 🎵 MUSIQA tavsiyasi\n\n"
                "Mavzu: urug' yoki hosil. Cinematic uslubda."
            ),
            max_tokens=1200,
        )
    else:
        result = "❓ Noma'lum."

    text = f"✍️ *{titles[action]}*\n\n{result}"
    await send_message(update, text, keyboard=back_button())


@register("veo")
@error_handler
async def handle_veo(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🎞 VEO PROMPTLAR handler — VeoEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = VeoEngine(acc)

    titles = {
        "agro": "🌾 Agro Cinematic",
        "fermer": "🚜 Fermer Sahna",
        "yomgir": "🌧 Yomg'irli Sahna",
        "ekin": "🌱 Ekin O'sishi",
        "ultra": "🎬 Ultra Realistik",
    }

    if action not in titles:
        await send_message(update, "❓ Noma'lum sahna turi.", keyboard=back_button())
        return

    # Loading
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *{titles[action]}* promptlari yaratilmoqda...\n"
            "_(Cinematic video promptlar tayyorlanmoqda)_",
            parse_mode="Markdown",
        )

    # Map to VeoEngine scene types
    scene_map = {
        "agro": "golden_harvest",
        "fermer": "farmer_hands",
        "yomgir": "rain_on_crops",
        "ekin": "seed_germination",
        "ultra": "greenhouse_morning",
    }

    style_map = {
        "agro": "cinematic",
        "fermer": "documentary",
        "yomgir": "cinematic",
        "ekin": "timelapse",
        "ultra": "epic",
    }

    scene_type = scene_map.get(action, "golden_harvest")
    style = style_map.get(action, "cinematic")

    # Generate using VeoEngine
    result = await engine.generate_scene_prompt(
        scene_type=scene_type,
        style=style,
        custom_details=f"Uzbekistan agriculture, {titles[action]} theme",
    )

    # Also get the static library prompt as bonus
    scene_info = engine.SCENE_LIBRARY.get(scene_type)
    bonus = ""
    if scene_info:
        bonus = (
            f"\n\n📌 *Tayyor prompt (kutubxonadan):*\n"
            f"`{scene_info['visual']}`\n"
            f"_Mood: {scene_info['mood']} | {scene_info['duration']}_"
        )

    text = f"🎞 *{titles[action]} — VEO PROMPTLAR*\n\n{result}{bonus}"
    await send_message(update, text, keyboard=back_button())
