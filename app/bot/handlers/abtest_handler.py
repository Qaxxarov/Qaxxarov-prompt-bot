"""
Agro AI — 🧪 A/B TEST Telegram handler
A/B test yaratish, boshqarish va natijalar.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register

logger = logging.getLogger("agro_ai.bot.abtest")


def abtest_menu() -> InlineKeyboardMarkup:
    """A/B Test menyusi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 Yangi Test", callback_data="abtest:new")],
        [InlineKeyboardButton("📋 Faol Testlar", callback_data="abtest:active")],
        [InlineKeyboardButton("📊 Natijalar", callback_data="abtest:results")],
        [InlineKeyboardButton("📈 Statistika", callback_data="abtest:stats")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("abtest")
@error_handler
async def handle_abtest(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🧪 A/B TEST handler."""
    await send_typing(update, context)
    acc = accounts.active

    from app.ai.ab_test import ABTestEngine
    engine = ABTestEngine(acc)

    if action == "new":
        text = (
            "🆕 *YANGI A/B TEST*\n\n"
            "Mavzuni yuboring va AI 3 ta variant yaratadi.\n\n"
            "Masalan:\n"
            "• `Pomidor parvarishi haqida reel`\n"
            "• `Yangi urug' sotuvga chiqdi`\n"
            "• `Issiqxona qurilishi`\n\n"
            "Mavzuni yozing 👇"
        )
        context.user_data["awaiting_abtest_topic"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "active":
        active_tests = engine.get_active_tests()
        if active_tests:
            lines = ["📋 *FAOL TESTLAR*\n"]
            for test in active_tests[:5]:
                lines.append(engine.format_test(test))
                lines.append("")
                # Variant tanlash tugmalari
            text = "\n".join(lines)

            # Tugmalar
            buttons = []
            for test in active_tests[:5]:
                for v in test.variants:
                    buttons.append([InlineKeyboardButton(
                        f"✅ {test.topic[:15]}... → {v.label}",
                        callback_data=f"abtest:select_{test.id}_{v.id}",
                    )])
            buttons.append([InlineKeyboardButton("📊 Natija Kiritish", callback_data="abtest:input_result")])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, text, keyboard=kb)
        else:
            text = "📋 *FAOL TESTLAR*\n\n_(Hozirda faol test yo'q.)_\n\n🆕 Yangi test yarating!"
            await send_message(update, text, keyboard=abtest_menu())
        return

    if action == "results":
        all_tests = engine.get_all_tests(limit=10)
        completed = [t for t in all_tests if t.status == "completed"]
        if completed:
            lines = ["📊 *TEST NATIJALARI*\n"]
            for test in completed[-5:]:
                lines.append(engine.format_test(test))
                lines.append("")
            text = "\n".join(lines)
        else:
            text = "📊 *NATIJALAR*\n\n_(Hali tugallangan test yo'q.)_"
        await send_message(update, text, keyboard=abtest_menu())
        return

    if action == "stats":
        stats = engine.get_stats()
        text = (
            "📈 *A/B TEST STATISTIKA*\n\n"
            f"📋 Jami testlar: {stats['total_tests']}\n"
            f"🟢 Faol: {stats['active']}\n"
            f"✅ Tugallangan: {stats['completed']}\n"
            f"⏰ Muddati o'tgan: {stats['expired']}\n\n"
            f"🏆 Eng ko'p g'olib stil: *{stats['top_winning_style']}*\n"
            f"   ({stats['win_count']} marta g'olib)"
        )
        await send_message(update, text, keyboard=abtest_menu())
        return

    if action == "input_result":
        text = (
            "📊 *NATIJA KIRITISH*\n\n"
            "Quyidagi formatda yuboring:\n"
            "`test_id variant_id score`\n\n"
            "Masalan: `test_abc123 var_def456 8`\n\n"
            "Score: 1-10 (10 = eng yaxshi)"
        )
        context.user_data["awaiting_abtest_result"] = True
        await send_message(update, text, keyboard=back_button())
        return

    # Variant tanlash
    if action.startswith("select_"):
        parts = action[7:].split("_", 2)
        if len(parts) >= 2:
            test_id = parts[0] + "_" + parts[1] if len(parts) == 3 else parts[0]
            variant_id = parts[-1]
            # Reconstruct proper IDs
            # Format: select_test_abc123_var_def456
            full_action = action[7:]  # test_abc123_var_def456
            # Find test
            for test in engine.get_all_tests():
                for v in test.variants:
                    if full_action.endswith(v.id):
                        test_id = test.id
                        variant_id = v.id
                        break

            if engine.select_variant(test_id, variant_id):
                text = f"✅ Variant tanlandi! Shu variantni ishlatib ko'ring.\n\n48 soat ichida natijani kiriting."
            else:
                text = "❌ Variant topilmadi."
            await send_message(update, text, keyboard=abtest_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=abtest_menu())


async def handle_abtest_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    A/B test uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    # Yangi test mavzusi
    if context.user_data.get("awaiting_abtest_topic"):
        topic = update.message.text.strip()
        if len(topic) < 3:
            await update.message.reply_text("❌ Mavzu juda qisqa. Qayta yozing.")
            return True

        context.user_data["awaiting_abtest_topic"] = False
        await update.message.reply_text("⏳ *A/B test yaratilmoqda...* AI ishlayapti.", parse_mode="Markdown")

        acc = accounts.active
        from app.ai.ab_test import ABTestEngine
        engine = ABTestEngine(acc)

        test = await engine.create_test(topic, num_variants=3)
        text = engine.format_test(test)
        text += "\n\n✅ Test yaratildi! Variantlardan birini tanlang va ishlatib ko'ring."

        await send_message(update, text, keyboard=abtest_menu())
        return True

    # Natija kiritish
    if context.user_data.get("awaiting_abtest_result"):
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) < 3:
            await update.message.reply_text("❌ Format: `test_id variant_id score`", parse_mode="Markdown")
            return True

        test_id = parts[0]
        variant_id = parts[1]
        try:
            score = float(parts[2])
        except ValueError:
            await update.message.reply_text("❌ Score raqam bo'lishi kerak (1-10).")
            return True

        context.user_data["awaiting_abtest_result"] = False

        acc = accounts.active
        from app.ai.ab_test import ABTestEngine
        engine = ABTestEngine(acc)

        if engine.record_result(test_id, variant_id, score):
            test = engine.get_test(test_id)
            if test and test.status == "completed":
                await update.message.reply_text(
                    f"✅ Natija saqlandi!\n\n🏆 Test tugadi — g'olib aniqlandi!",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text("✅ Natija saqlandi!")
        else:
            await update.message.reply_text("❌ Test yoki variant topilmadi.")
        return True

    return False
