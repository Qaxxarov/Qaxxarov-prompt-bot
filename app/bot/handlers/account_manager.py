"""
Agro AI — AKKAUNT CRUD Handler
Bot ichidan step-by-step akkaunt yaratish, tahrirlash, o'chirish.
ConversationHandler o'rniga context.user_data bilan multi-step dialog.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import Account, accounts
from app.bot.keyboards import back_button
from app.bot.middleware import admin_only, error_handler, send_message, send_typing
from app.bot.router import register

logger = logging.getLogger("agro_ai.bot.account_mgr")


def _acc_manage_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi Akkaunt", callback_data="accmgr:new")],
        [InlineKeyboardButton("✏️ Tahrirlash", callback_data="accmgr:edit")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data="accmgr:delete")],
        [InlineKeyboardButton("📋 Batafsil Ro'yxat", callback_data="accmgr:details")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("accmgr")
@admin_only
@error_handler
async def handle_accmgr(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """Akkaunt boshqaruvi handler."""
    await send_typing(update, context)

    if action == "new":
        text = (
            "➕ *YANGI AKKAUNT*\n\n"
            "Instagram username yuboring (@ bilan):\n"
            "Masalan: `@my_new_account`"
        )
        context.user_data["acc_step"] = "username"
        context.user_data["acc_draft"] = {}
        await send_message(update, text, keyboard=back_button())
        return

    if action == "edit":
        all_accs = accounts.all_accounts
        buttons = []
        for acc in all_accs:
            buttons.append([InlineKeyboardButton(
                f"✏️ {acc.instagram}", callback_data=f"accmgr:ed_{acc.id}"
            )])
        buttons.append([InlineKeyboardButton("🏠 Orqaga", callback_data="nav:main")])
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, "✏️ *TAHRIRLASH*\n\nAkkauntni tanlang:", keyboard=kb)
        return

    if action == "delete":
        all_accs = accounts.all_accounts
        if len(all_accs) <= 1:
            await send_message(update, "❌ Oxirgi akkauntni o'chirib bo'lmaydi.", keyboard=_acc_manage_menu())
            return
        buttons = []
        for acc in all_accs:
            if acc.id != accounts.active.id:
                buttons.append([InlineKeyboardButton(
                    f"🗑 {acc.instagram}", callback_data=f"accmgr:confirmdel_{acc.id}"
                )])
        buttons.append([InlineKeyboardButton("🏠 Orqaga", callback_data="nav:main")])
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, "🗑 *O'CHIRISH*\n\nTanlang:", keyboard=kb)
        return

    if action == "details":
        lines = ["📋 *AKKAUNTLAR BATAFSIL*\n"]
        for acc in accounts.all_accounts:
            lines.append(accounts.format_account_full(acc))
            lines.append("")
        await send_message(update, "\n".join(lines), keyboard=_acc_manage_menu())
        return

    # Edit specific account — show edit menu
    if action.startswith("ed_"):
        acc_id = action[3:]
        acc = accounts.get(acc_id)
        if not acc:
            await send_message(update, "❌ Akkaunt topilmadi.", keyboard=_acc_manage_menu())
            return
        buttons = [
            [InlineKeyboardButton("🎯 Niche", callback_data=f"accmgr:setniche_{acc_id}")],
            [InlineKeyboardButton("👥 Auditoriya", callback_data=f"accmgr:setaud_{acc_id}")],
            [InlineKeyboardButton("#️⃣ Hashtags", callback_data=f"accmgr:sethash_{acc_id}")],
            [InlineKeyboardButton("⏰ Post vaqtlari", callback_data=f"accmgr:settime_{acc_id}")],
            [InlineKeyboardButton("🎭 AI Tone", callback_data=f"accmgr:settone_{acc_id}")],
            [InlineKeyboardButton("🕵️ Raqobatchilar", callback_data=f"accmgr:setcomp_{acc_id}")],
            [InlineKeyboardButton("📊 Post chastotasi", callback_data=f"accmgr:setfreq_{acc_id}")],
            [InlineKeyboardButton("🏠 Orqaga", callback_data="nav:main")],
        ]
        kb = InlineKeyboardMarkup(buttons)
        text = f"✏️ *TAHRIRLASH: {acc.instagram}*\n\nNimani o'zgartirmoqchisiz?"
        await send_message(update, text, keyboard=kb)
        return

    # Set fields
    if action.startswith("setniche_"):
        acc_id = action[9:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "niche"
        await send_message(update, "🎯 Yangi niche yozing:", keyboard=back_button())
        return

    if action.startswith("setaud_"):
        acc_id = action[7:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "target_audience"
        await send_message(update, "👥 Yangi auditoriya yozing:", keyboard=back_button())
        return

    if action.startswith("sethash_"):
        acc_id = action[8:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "hashtags"
        await send_message(update, "#️⃣ Hashtag'larni vergul bilan yozing:\n`#agro, #fermer, #hosil`", keyboard=back_button())
        return

    if action.startswith("settime_"):
        acc_id = action[8:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "posting_times"
        await send_message(update, "⏰ Post vaqtlarini vergul bilan yozing:\n`19:00, 20:00, 07:00`", keyboard=back_button())
        return

    if action.startswith("settone_"):
        acc_id = action[8:]
        buttons = [
            [InlineKeyboardButton("🎩 Professional", callback_data=f"accmgr:dotone_{acc_id}_professional")],
            [InlineKeyboardButton("😊 Casual", callback_data=f"accmgr:dotone_{acc_id}_casual")],
            [InlineKeyboardButton("🎉 Fun", callback_data=f"accmgr:dotone_{acc_id}_fun")],
        ]
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, "🎭 AI tone tanlang:", keyboard=kb)
        return

    if action.startswith("dotone_"):
        parts = action[7:].rsplit("_", 1)
        acc_id, tone = parts[0], parts[1]
        accounts.update(acc_id, ai_tone=tone)
        await send_message(update, f"✅ AI tone: *{tone}*", keyboard=_acc_manage_menu())
        return

    if action.startswith("setcomp_"):
        acc_id = action[8:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "competitors"
        await send_message(update, "🕵️ Raqobatchilar (vergul bilan):\n`competitor1, competitor2`", keyboard=back_button())
        return

    if action.startswith("setfreq_"):
        acc_id = action[8:]
        context.user_data["acc_edit_id"] = acc_id
        context.user_data["acc_edit_field"] = "posting_frequency"
        await send_message(update, "📊 Kuniga nechta post? (raqam yozing: 1, 2, 3...)", keyboard=back_button())
        return

    # Confirm delete
    if action.startswith("confirmdel_"):
        acc_id = action[11:]
        acc = accounts.get(acc_id)
        if not acc:
            await send_message(update, "❌ Topilmadi.", keyboard=_acc_manage_menu())
            return
        buttons = [
            [InlineKeyboardButton("✅ Ha, o'chir", callback_data=f"accmgr:dodel_{acc_id}")],
            [InlineKeyboardButton("❌ Bekor", callback_data="nav:main")],
        ]
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, f"🗑 *{acc.instagram}* ni o'chirmoqchimisiz?", keyboard=kb)
        return

    if action.startswith("dodel_"):
        acc_id = action[6:]
        if accounts.remove(acc_id):
            await send_message(update, "✅ Akkaunt o'chirildi.", keyboard=_acc_manage_menu())
        else:
            await send_message(update, "❌ O'chirib bo'lmadi.", keyboard=_acc_manage_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=_acc_manage_menu())


async def handle_account_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Multi-step akkaunt yaratish/tahrirlash uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    # ── YANGI AKKAUNT YARATISH (step-by-step) ──
    step = context.user_data.get("acc_step")
    if step:
        draft = context.user_data.get("acc_draft", {})
        text = update.message.text.strip()

        if step == "username":
            username = text.lstrip("@").strip()
            if len(username) < 2:
                await update.message.reply_text("❌ Username juda qisqa. Qayta yozing.")
                return True
            draft["instagram"] = f"@{username}"
            draft["id"] = username.replace(".", "_").lower()
            context.user_data["acc_draft"] = draft
            context.user_data["acc_step"] = "niche"
            await update.message.reply_text(
                "✅ Username: " + draft["instagram"] + "\n\n"
                "🎯 Endi *niche* yozing:\n"
                "Masalan: `Texnologiya va gadgetlar`",
                parse_mode="Markdown",
            )
            return True

        if step == "niche":
            draft["niche"] = text
            context.user_data["acc_draft"] = draft
            context.user_data["acc_step"] = "audience"
            await update.message.reply_text(
                "✅ Niche: " + text + "\n\n"
                "👥 Endi *maqsadli auditoriya* yozing:\n"
                "Masalan: `Yosh dasturchilar, IT mutaxassislar`",
                parse_mode="Markdown",
            )
            return True

        if step == "audience":
            draft["target_audience"] = text
            context.user_data["acc_draft"] = draft
            context.user_data["acc_step"] = "hashtags"
            await update.message.reply_text(
                "✅ Auditoriya: " + text + "\n\n"
                "#️⃣ Endi *hashtag'lar* yozing (vergul bilan):\n"
                "Masalan: `#tech, #coding, #gadget`",
                parse_mode="Markdown",
            )
            return True

        if step == "hashtags":
            tags = [t.strip() for t in text.replace(",", " ").split() if t.strip()]
            draft["hashtags"] = tags
            context.user_data["acc_draft"] = draft
            context.user_data["acc_step"] = "chrome"
            await update.message.reply_text(
                "✅ Hashtags: " + ", ".join(tags[:5]) + "\n\n"
                "📁 Chrome profil nomi yozing:\n"
                "Masalan: `Profile 1` yoki `Default`\n\n"
                "_(Bilmasangiz `Default` yozing)_",
                parse_mode="Markdown",
            )
            return True

        if step == "chrome":
            draft["chrome_profile"] = text
            context.user_data["acc_step"] = None

            # Akkaunt yaratish
            new_acc = Account(
                id=draft.get("id", "new_account"),
                instagram=draft.get("instagram", "@new"),
                niche=draft.get("niche", ""),
                target_audience=draft.get("target_audience", ""),
                hashtags=draft.get("hashtags", []),
                chrome_profile=text,
            )
            accounts.add(new_acc)
            context.user_data["acc_draft"] = {}

            await update.message.reply_text(
                f"✅ *AKKAUNT YARATILDI!*\n\n"
                f"🌿 {new_acc.instagram}\n"
                f"🎯 {new_acc.niche}\n"
                f"👥 {new_acc.target_audience}\n"
                f"📁 {new_acc.chrome_profile}\n\n"
                f"Almashtirish uchun ⚙️ SOZLAMALAR → Akkaunt Almashtirish",
                parse_mode="Markdown",
            )
            return True

    # ── AKKAUNT TAHRIRLASH ──
    edit_field = context.user_data.get("acc_edit_field")
    edit_id = context.user_data.get("acc_edit_id")
    if edit_field and edit_id:
        text = update.message.text.strip()
        context.user_data["acc_edit_field"] = None
        context.user_data["acc_edit_id"] = None

        if edit_field == "hashtags":
            value = [t.strip() for t in text.replace(",", " ").split() if t.strip()]
        elif edit_field == "posting_times":
            value = [t.strip() for t in text.split(",") if t.strip()]
        elif edit_field == "competitors":
            value = [c.strip().lstrip("@") for c in text.split(",") if c.strip()]
        elif edit_field == "posting_frequency":
            try:
                value = int(text)
            except ValueError:
                await update.message.reply_text("❌ Raqam yozing.")
                return True
        else:
            value = text

        if accounts.update(edit_id, **{edit_field: value}):
            await update.message.reply_text(f"✅ *{edit_field}* yangilandi!", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Yangilashda xato.")
        return True

    return False
