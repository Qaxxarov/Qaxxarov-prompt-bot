"""
Agro AI — 👥 FOYDALANUVCHILAR Telegram handler
Foydalanuvchilarni boshqarish (faqat admin).
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.bot.keyboards import back_button
from app.bot.middleware import admin_only, error_handler, send_message, send_typing
from app.bot.router import register
from app.users.manager import user_manager

logger = logging.getLogger("agro_ai.bot.users")


def users_menu() -> InlineKeyboardMarkup:
    """Foydalanuvchilar menyusi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="users:list")],
        [InlineKeyboardButton("➕ Qo'shish", callback_data="users:add")],
        [InlineKeyboardButton("🔄 Rol O'zgartirish", callback_data="users:role")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data="users:remove")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("users")
@admin_only
@error_handler
async def handle_users(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """👥 FOYDALANUVCHILAR handler (faqat admin)."""
    await send_typing(update, context)
    admin_id = update.effective_user.id

    if action == "list":
        text = f"👥 *FOYDALANUVCHILAR*\n\n{user_manager.format_user_list()}"
        await send_message(update, text, keyboard=users_menu())
        return

    if action == "add":
        text = (
            "➕ *FOYDALANUVCHI QO'SHISH*\n\n"
            "Telegram ID yoki @username yuboring:\n\n"
            "Masalan:\n"
            "• `123456789`\n"
            "• `123456789 manager`\n"
            "• `123456789 viewer Ism`\n\n"
            "Format: `ID [rol] [ism]`\n"
            "Rollar: admin, manager, viewer"
        )
        context.user_data["awaiting_user_add"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "role":
        users = user_manager.list_users()
        if users:
            buttons = []
            for u in users:
                role_emoji = {"admin": "👑", "manager": "📋", "viewer": "👁"}.get(u.role, "👤")
                buttons.append([InlineKeyboardButton(
                    f"{role_emoji} {u.name or u.username} ({u.role})",
                    callback_data=f"users:setrole_{u.user_id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "🔄 *ROL O'ZGARTIRISH*\n\nFoydalanuvchini tanlang:", keyboard=kb)
        else:
            await send_message(update, "_(Foydalanuvchi yo'q.)_", keyboard=users_menu())
        return

    if action == "remove":
        users = user_manager.list_users()
        # Admin o'zini ko'rsatmasin
        users = [u for u in users if u.user_id != admin_id]
        if users:
            buttons = []
            for u in users:
                buttons.append([InlineKeyboardButton(
                    f"🗑 {u.name or u.username} ({u.role})",
                    callback_data=f"users:del_{u.user_id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "🗑 *O'CHIRISH*\n\nFoydalanuvchini tanlang:", keyboard=kb)
        else:
            await send_message(update, "_(O'chirish uchun foydalanuvchi yo'q.)_", keyboard=users_menu())
        return

    # Set role for specific user
    if action.startswith("setrole_"):
        target_id = int(action[8:])
        user = user_manager.get_user(target_id)
        if user:
            buttons = [
                [InlineKeyboardButton("👑 Admin", callback_data=f"users:dorole_{target_id}_admin")],
                [InlineKeyboardButton("📋 Manager", callback_data=f"users:dorole_{target_id}_manager")],
                [InlineKeyboardButton("👁 Viewer", callback_data=f"users:dorole_{target_id}_viewer")],
                [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
            ]
            kb = InlineKeyboardMarkup(buttons)
            text = (
                f"🔄 *ROL O'ZGARTIRISH*\n\n"
                f"👤 {user.name or user.username}\n"
                f"Hozirgi rol: *{user.role}*\n\n"
                f"Yangi rolni tanlang:"
            )
            await send_message(update, text, keyboard=kb)
        else:
            await send_message(update, "❌ Foydalanuvchi topilmadi.", keyboard=users_menu())
        return

    # Execute role change
    if action.startswith("dorole_"):
        parts = action[7:].rsplit("_", 1)
        if len(parts) == 2:
            target_id = int(parts[0])
            new_role = parts[1]
            success, msg = user_manager.set_role(target_id, new_role, changed_by=admin_id)
            await send_message(update, msg, keyboard=users_menu())
        return

    # Delete specific user
    if action.startswith("del_"):
        target_id = int(action[4:])
        success, msg = user_manager.remove_user(target_id, removed_by=admin_id)
        await send_message(update, msg, keyboard=users_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=users_menu())


async def handle_user_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Foydalanuvchi qo'shish uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    if not context.user_data.get("awaiting_user_add"):
        return False

    text = update.message.text.strip()
    parts = text.split()

    if not parts:
        await update.message.reply_text("❌ ID yuboring.")
        return True

    try:
        user_id = int(parts[0])
    except ValueError:
        await update.message.reply_text("❌ ID raqam bo'lishi kerak.")
        return True

    role = parts[1] if len(parts) > 1 else "viewer"
    name = " ".join(parts[2:]) if len(parts) > 2 else ""

    if role not in ("admin", "manager", "viewer"):
        role = "viewer"

    context.user_data["awaiting_user_add"] = False

    admin_id = update.effective_user.id
    user = user_manager.add_user(
        user_id=user_id,
        username="",
        name=name or f"User {user_id}",
        role=role,
        added_by=str(admin_id),
    )

    await update.message.reply_text(
        f"✅ Foydalanuvchi qo'shildi!\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"👤 Ism: {user.name}\n"
        f"🔑 Rol: {user.role}",
        parse_mode="Markdown",
    )

    # Foydalanuvchiga xabar yuborish
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Sizga botga kirish ruxsati berildi!\n\n/start buyrug'ini yuboring.",
        )
    except Exception:
        pass  # Foydalanuvchi botni start qilmagan bo'lishi mumkin

    return True
