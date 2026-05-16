"""
Agro AI — Telegram Klaviaturalar (v2)
Barcha menyu va tugmalar.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


# ════════════════════════════════════════════════════════
# 🏠 ASOSIY MENYU (15 bo'lim)
# ════════════════════════════════════════════════════════

def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ["📊 TAHLIL",         "💡 G'OYALAR"],
        ["🎣 HOOKLAR",        "✍️ SSENARIY"],
        ["🎞 VEO PROMPTLAR",  "🎬 PIPELINE"],
        ["📅 REJA",           "📡 TRENDLAR"],
        ["📦 SOTUV AI",       "🧠 AUDIENCE AI"],
        ["🏆 VIRAL SCORE",    "📈 O'SISH"],
        ["🎯 KONKURENT",      "📋 OPS MANAGER"],
        ["📸 MEDIA AI",       "🧪 A/B TEST"],
        ["🕵️ MONITORING",     "🛒 MAHSULOTLAR"],
        ["🔔 ALERTLAR",       "📮 POST NAVBAT"],
        ["🌐 TARJIMA",        "💬 DM JAVOB"],
        ["📊 MULTI-ACCOUNT",  "🔄 AKKAUNTLAR"],
        ["🧠 XOTIRA",         "📤 EXPORT"],
        ["👥 FOYDALANUVCHILAR", "⚙️ SOZLAMALAR"],
        ["👑 ADMIN"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ════════════════════════════════════════════════════════
# 📊 TAHLIL
# ════════════════════════════════════════════════════════

def tahlil_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Eng Kuchli Reels", callback_data="tahlil:top")],
        [InlineKeyboardButton("📈 Viral Tahlil", callback_data="tahlil:viral")],
        [InlineKeyboardButton("👀 Aktivlik Tahlili", callback_data="tahlil:aktivlik")],
        [InlineKeyboardButton("📉 Kuchsiz Kontent", callback_data="tahlil:kuchsiz")],
        [InlineKeyboardButton("🧠 Viral Sirlar", callback_data="tahlil:sirlar")],
        [InlineKeyboardButton("🔄 Yangi Tahlil", callback_data="tahlil:yangi")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 💡 G'OYALAR
# ════════════════════════════════════════════════════════

def goyalar_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Viral G'oyalar", callback_data="goya:viral")],
        [InlineKeyboardButton("📖 Story Kontent", callback_data="goya:story")],
        [InlineKeyboardButton("⚡ Trend G'oyalar", callback_data="goya:trend")],
        [InlineKeyboardButton("😱 Shok Kontent", callback_data="goya:shok")],
        [InlineKeyboardButton("🌾 Agro G'oyalar", callback_data="goya:agro")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🎣 HOOKLAR
# ════════════════════════════════════════════════════════

def hooklar_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Viral Hooklar", callback_data="hook:viral")],
        [InlineKeyboardButton("😱 Qo'rquv Hooklar", callback_data="hook:fear")],
        [InlineKeyboardButton("🤔 Qiziqish Hooklar", callback_data="hook:curiosity")],
        [InlineKeyboardButton("💰 Foyda Hooklar", callback_data="hook:benefit")],
        [InlineKeyboardButton("🎯 Niche Hooklar", callback_data="hook:niche")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# ✍️ SSENARIY
# ════════════════════════════════════════════════════════

def ssenariy_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎤 Reel Ssenariy", callback_data="ss:reel")],
        [InlineKeyboardButton("🎥 Kadrlar Rejasi", callback_data="ss:kadr")],
        [InlineKeyboardButton("🎭 Emotsional Story", callback_data="ss:story")],
        [InlineKeyboardButton("📢 CTA Yaratish", callback_data="ss:cta")],
        [InlineKeyboardButton("📝 Caption + Script", callback_data="ss:full")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🎞 VEO PROMPTLAR
# ════════════════════════════════════════════════════════

def veo_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌾 Agro Cinematic", callback_data="veo:agro")],
        [InlineKeyboardButton("🚜 Fermer Sahna", callback_data="veo:fermer")],
        [InlineKeyboardButton("🌧 Yomg'irli Sahna", callback_data="veo:yomgir")],
        [InlineKeyboardButton("🌱 Ekin O'sishi", callback_data="veo:ekin")],
        [InlineKeyboardButton("🎬 Ultra Realistik", callback_data="veo:ultra")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📅 REJA
# ════════════════════════════════════════════════════════

def reja_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📆 7 Kunlik Reja", callback_data="reja:7kun")],
        [InlineKeyboardButton("📆 30 Kunlik Reja", callback_data="reja:30kun")],
        [InlineKeyboardButton("⏰ Eng Yaxshi Vaqt", callback_data="reja:vaqt")],
        [InlineKeyboardButton("🧠 Viral Strategiya", callback_data="reja:strategiya")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📡 TRENDLAR
# ════════════════════════════════════════════════════════

def trendlar_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Trend Mavzular", callback_data="trend:mavzu")],
        [InlineKeyboardButton("🎵 Trend Audio", callback_data="trend:audio")],
        [InlineKeyboardButton("🎬 Trend Formatlar", callback_data="trend:format")],
        [InlineKeyboardButton("⚡ Hook Trendlari", callback_data="trend:hook")],
        [InlineKeyboardButton("🔮 Trend Bashorat", callback_data="trend:predict")],
        [InlineKeyboardButton("📋 Kunlik Hisobot", callback_data="trend:daily")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📦 SOTUV AI
# ════════════════════════════════════════════════════════

def sotuv_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌱 Urug' Sotuv G'oya", callback_data="sotuv:urug")],
        [InlineKeyboardButton("💰 Sotuv Strategiya", callback_data="sotuv:strategiya")],
        [InlineKeyboardButton("🎯 Mahsulot Reklama", callback_data="sotuv:reklama")],
        [InlineKeyboardButton("📢 Agro Marketing", callback_data="sotuv:marketing")],
        [InlineKeyboardButton("🔄 Sales Funnel", callback_data="sotuv:funnel")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🧠 AUDIENCE AI
# ════════════════════════════════════════════════════════

def audience_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Auditoriya Profili", callback_data="aud:profil")],
        [InlineKeyboardButton("🧠 Psixologik Tahlil", callback_data="aud:psych")],
        [InlineKeyboardButton("💬 Comment Tahlil", callback_data="aud:comments")],
        [InlineKeyboardButton("📊 Engagement Pattern", callback_data="aud:pattern")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🏆 VIRAL SCORE
# ════════════════════════════════════════════════════════

def viral_score_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Joriy Score", callback_data="vscore:current")],
        [InlineKeyboardButton("🔮 Bashorat", callback_data="vscore:predict")],
        [InlineKeyboardButton("📈 Retention Tahlil", callback_data="vscore:retention")],
        [InlineKeyboardButton("🏅 Top Performers", callback_data="vscore:top")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📈 O'SISH ANALIZI
# ════════════════════════════════════════════════════════

def osish_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 O'sish Statistika", callback_data="osish:stats")],
        [InlineKeyboardButton("🎯 Maqsadlar", callback_data="osish:goals")],
        [InlineKeyboardButton("💡 O'sish Tavsiyalar", callback_data="osish:tips")],
        [InlineKeyboardButton("📅 Haftalik Hisobot", callback_data="osish:weekly")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🎯 KONKURENT TAHLILI
# ════════════════════════════════════════════════════════

def konkurent_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Konkurent Tahlil", callback_data="konk:analyze")],
        [InlineKeyboardButton("📊 Solishtirish", callback_data="konk:compare")],
        [InlineKeyboardButton("💡 Ulardan O'rganish", callback_data="konk:learn")],
        [InlineKeyboardButton("🎯 Ustunlik Topish", callback_data="konk:advantage")],
        [InlineKeyboardButton("🎣 Konkurent Hooklar", callback_data="konk:hooks")],
        [InlineKeyboardButton("📊 Viral Pattern'lar", callback_data="konk:patterns")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🎬 CONTENT PIPELINE
# ════════════════════════════════════════════════════════

def pipeline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌱 Urug' Parvarish", callback_data="pipe:urug")],
        [InlineKeyboardButton("🌾 Hosil Ko'paytirish", callback_data="pipe:hosil")],
        [InlineKeyboardButton("🏠 Issiqxona", callback_data="pipe:issiqxona")],
        [InlineKeyboardButton("🦠 Kasallik Davolash", callback_data="pipe:kasallik")],
        [InlineKeyboardButton("🌍 Tuproq Tayyorlash", callback_data="pipe:tuproq")],
        [InlineKeyboardButton("⚡ Tezkor Paket", callback_data="pipe:quick")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🧠 MEMORY (xotira tizimi)
# ════════════════════════════════════════════════════════

def memory_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Xotira Statistika", callback_data="mem:stats")],
        [InlineKeyboardButton("🎣 Top Hooklar", callback_data="mem:hooks")],
        [InlineKeyboardButton("🎭 Top Hikoyalar", callback_data="mem:stories")],
        [InlineKeyboardButton("📈 Viral Pattern'lar", callback_data="mem:patterns")],
        [InlineKeyboardButton("📉 Ishlamagan Pattern'lar", callback_data="mem:failed")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📋 OPS MANAGER
# ════════════════════════════════════════════════════════

def ops_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Tezkor Holat", callback_data="ops:status")],
        [InlineKeyboardButton("🌅 Ertalabki Brifing", callback_data="ops:morning")],
        [InlineKeyboardButton("🌙 Kechki Hisobot", callback_data="ops:evening")],
        [InlineKeyboardButton("📋 Intizom Hisoboti", callback_data="ops:discipline")],
        [InlineKeyboardButton("📅 Haftalik Hisobot", callback_data="ops:weekly")],
        [InlineKeyboardButton("🔄 Yangi Skan", callback_data="ops:scan")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📤 EXPORT
# ════════════════════════════════════════════════════════

def export_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Excel Hisobot", callback_data="export:excel")],
        [InlineKeyboardButton("📄 PDF Strategiya", callback_data="export:pdf")],
        [InlineKeyboardButton("📁 JSON Export", callback_data="export:json")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# ⚙️ SOZLAMALAR
# ════════════════════════════════════════════════════════

def sozlamalar_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Akkaunt Almashtirish", callback_data="soz:switch")],
        [InlineKeyboardButton("📋 Akkauntlar Ro'yxati", callback_data="soz:list")],
        [InlineKeyboardButton("🔍 Chrome Diagnostika", callback_data="soz:chrome")],
        [InlineKeyboardButton("📊 Tizim Holati", callback_data="soz:status")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 👑 ADMIN PANEL
# ════════════════════════════════════════════════════════

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Tizim Statistika", callback_data="admin:stats")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin:users")],
        [InlineKeyboardButton("➕ Akkaunt Qo'shish", callback_data="admin:add_acc")],
        [InlineKeyboardButton("🗑 Akkaunt O'chirish", callback_data="admin:del_acc")],
        [InlineKeyboardButton("🔄 Bot Restart", callback_data="admin:restart")],
        [InlineKeyboardButton("📋 Loglar", callback_data="admin:logs")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📸 MEDIA AI
# ════════════════════════════════════════════════════════

def media_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ℹ️ Qanday Ishlaydi", callback_data="media:info")],
        [InlineKeyboardButton("📜 Tarix", callback_data="media:history")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🧪 A/B TEST
# ════════════════════════════════════════════════════════

def abtest_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 Yangi Test", callback_data="abtest:new")],
        [InlineKeyboardButton("📋 Faol Testlar", callback_data="abtest:active")],
        [InlineKeyboardButton("📊 Natijalar", callback_data="abtest:results")],
        [InlineKeyboardButton("📈 Statistika", callback_data="abtest:stats")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🕵️ COMPETITOR MONITORING
# ════════════════════════════════════════════════════════

def compmon_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Raqobatchi Qo'shish", callback_data="compmon:add")],
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="compmon:list")],
        [InlineKeyboardButton("🔔 Alertlar", callback_data="compmon:alerts")],
        [InlineKeyboardButton("📊 Monitoring Holati", callback_data="compmon:status")],
        [InlineKeyboardButton("🔄 Hozir Skanerlash", callback_data="compmon:scan")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🛒 MAHSULOTLAR
# ════════════════════════════════════════════════════════

def product_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Mahsulot Qo'shish", callback_data="product:add")],
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="product:list")],
        [InlineKeyboardButton("💰 Narx Yangilash", callback_data="product:price")],
        [InlineKeyboardButton("📝 Sotuv Post Yaratish", callback_data="product:sales_post")],
        [InlineKeyboardButton("📦 Katalog Post", callback_data="product:catalog_post")],
        [InlineKeyboardButton("🌱 Mavsumiy Post", callback_data="product:seasonal")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🔔 ALERTLAR
# ════════════════════════════════════════════════════════

def alert_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Alert Sozlamalari", callback_data="alert:settings")],
        [InlineKeyboardButton("📜 Alert Tarixi", callback_data="alert:history")],
        [InlineKeyboardButton("🟢 Barchasini Yoqish", callback_data="alert:enable_all")],
        [InlineKeyboardButton("🔴 Barchasini O'chirish", callback_data="alert:disable_all")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📮 POST NAVBAT
# ════════════════════════════════════════════════════════

def post_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Navbatga Qo'shish", callback_data="post:add")],
        [InlineKeyboardButton("📋 Navbatni Ko'rish", callback_data="post:queue")],
        [InlineKeyboardButton("📅 Bugun", callback_data="post:today")],
        [InlineKeyboardButton("📮 Hozir Post Qil", callback_data="post:now")],
        [InlineKeyboardButton("📜 Tarix", callback_data="post:history")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🌐 TARJIMA
# ════════════════════════════════════════════════════════

def translate_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿→🇷🇺 O'zbekchadan Ruschaga", callback_data="translate:uz_ru")],
        [InlineKeyboardButton("🇷🇺→🇺🇿 Ruschadan O'zbekchaga", callback_data="translate:ru_uz")],
        [InlineKeyboardButton("🌐 Ikki Tilda Yaratish", callback_data="translate:bilingual")],
        [InlineKeyboardButton("🎣 Hook Tarjima", callback_data="translate:hooks")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 💬 DM JAVOB
# ════════════════════════════════════════════════════════

def dm_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 FAQ Ro'yxati", callback_data="dm:list")],
        [InlineKeyboardButton("➕ FAQ Qo'shish", callback_data="dm:add")],
        [InlineKeyboardButton("🧪 Test Qilish", callback_data="dm:test")],
        [InlineKeyboardButton("📊 Statistika", callback_data="dm:stats")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 👥 FOYDALANUVCHILAR
# ════════════════════════════════════════════════════════

def users_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="users:list")],
        [InlineKeyboardButton("➕ Qo'shish", callback_data="users:add")],
        [InlineKeyboardButton("🔄 Rol O'zgartirish", callback_data="users:role")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data="users:remove")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 📊 MULTI-ACCOUNT
# ════════════════════════════════════════════════════════

def multi_account_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Barchasini Tahlil Qil", callback_data="multi:analyze_all")],
        [InlineKeyboardButton("📋 Barcha Uchun Kontent", callback_data="multi:content_all")],
        [InlineKeyboardButton("📈 Umumiy Holat", callback_data="multi:status")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# 🔄 AKKAUNTLAR BOSHQARUVI
# ════════════════════════════════════════════════════════

def acc_manage_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi Akkaunt", callback_data="accmgr:new")],
        [InlineKeyboardButton("✏️ Tahrirlash", callback_data="accmgr:edit")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data="accmgr:delete")],
        [InlineKeyboardButton("📋 Batafsil Ro'yxat", callback_data="accmgr:details")],
        [_back_btn()],
    ])


# ════════════════════════════════════════════════════════
# YORDAMCHI
# ════════════════════════════════════════════════════════

def _back_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_back_btn()]])


def confirm_keyboard(yes_data: str, no_data: str = "nav:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ha", callback_data=yes_data),
            InlineKeyboardButton("❌ Yo'q", callback_data=no_data),
        ]
    ])


def webapp_keyboard(base_url: str) -> InlineKeyboardMarkup:
    """Telegram Mini App tugmalari."""
    from telegram import WebAppInfo
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Dashboard Ochish", web_app=WebAppInfo(url=f"{base_url}/miniapp"))],
        [
            InlineKeyboardButton("📈 Analytics", web_app=WebAppInfo(url=f"{base_url}/miniapp")),
            InlineKeyboardButton("🤖 AI Center", web_app=WebAppInfo(url=f"{base_url}/miniapp")),
        ],
        [
            InlineKeyboardButton("📡 Trend Radar", web_app=WebAppInfo(url=f"{base_url}/miniapp")),
            InlineKeyboardButton("🎬 Pipeline", web_app=WebAppInfo(url=f"{base_url}/miniapp")),
        ],
    ])


def account_switch_keyboard(accounts: list) -> InlineKeyboardMarkup:
    """Akkaunt tanlash klaviaturasi."""
    buttons = []
    for acc in accounts:
        label = f"{'✅' if acc.active else '⬜'} {acc.instagram}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"switch:{acc.id}")])
    buttons.append([_back_btn()])
    return InlineKeyboardMarkup(buttons)
