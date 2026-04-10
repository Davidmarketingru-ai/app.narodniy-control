"""
Telegram Bot for Народный Контроль
- User notifications about app events
- Admin commands with role-based access
- Account linking via code
"""
import os
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

logger = logging.getLogger("telegram_bot")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

ADMIN_PERMISSIONS = {
    "manage_reviews": "Управление отзывами",
    "manage_orgs": "Управление организациями",
    "manage_councils": "Управление советами",
    "manage_users": "Управление пользователями",
    "view_stats": "Просмотр статистики",
    "send_notifications": "Отправка уведомлений",
    "moderate_news": "Модерация новостей",
}


async def handle_update(update_data: dict, db):
    """Process incoming Telegram update."""
    if not bot:
        return
    try:
        update = Update.de_json(update_data, bot)
        if update.message and update.message.text:
            await _handle_message(update.message, db)
        elif update.callback_query:
            await _handle_callback(update.callback_query, db)
    except Exception as e:
        logger.error(f"Telegram update error: {e}")


async def _handle_message(message, db):
    chat_id = message.chat_id
    text = message.text.strip()
    tg_user = message.from_user

    # Upsert telegram user info
    await db.telegram_users.update_one(
        {"chat_id": chat_id},
        {"$set": {
            "chat_id": chat_id,
            "tg_username": tg_user.username or "",
            "tg_first_name": tg_user.first_name or "",
            "last_active": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )

    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1:
            # Deep link with linking code
            code = parts[1]
            await _link_account(chat_id, code, db)
        else:
            await _cmd_start(chat_id, db)
    elif text == "/help":
        await _cmd_help(chat_id, db)
    elif text == "/link":
        await _cmd_link_info(chat_id, db)
    elif text == "/unlink":
        await _cmd_unlink(chat_id, db)
    elif text == "/settings":
        await _cmd_settings(chat_id, db)
    elif text == "/admin":
        await _cmd_admin(chat_id, db)
    elif text == "/stats":
        await _cmd_stats(chat_id, db)
    elif text.startswith("/notify"):
        await _cmd_notify(chat_id, text, db)
    else:
        await bot.send_message(chat_id=chat_id, text="Используйте /help для списка команд.")


async def _cmd_start(chat_id, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    linked = tg_user and tg_user.get("app_user_id")
    if linked:
        user = await db.users.find_one({"user_id": tg_user["app_user_id"]}, {"_id": 0, "name": 1})
        name = user.get("name", "Пользователь") if user else "Пользователь"
        text = f"Добро пожаловать, {name}!\n\nВаш аккаунт привязан. Вы будете получать уведомления о событиях в приложении.\n\n/help — список команд\n/settings — настройки уведомлений"
    else:
        text = "Добро пожаловать в Народный Контроль!\n\nЧтобы получать уведомления, привяжите аккаунт:\n1. Откройте приложение → Профиль\n2. Нажмите «Привязать Telegram»\n3. Скопируйте код и отправьте его сюда\n\nИли используйте /link для получения инструкции."
    await bot.send_message(chat_id=chat_id, text=text)


async def _cmd_help(chat_id, db):
    text = ("Команды:\n"
            "/start — Начало\n"
            "/link — Привязать аккаунт\n"
            "/unlink — Отвязать аккаунт\n"
            "/settings — Настройки уведомлений\n"
            "/admin — Панель администратора\n"
            "/stats — Статистика платформы\n"
            "/help — Эта справка")
    await bot.send_message(chat_id=chat_id, text=text)


async def _cmd_link_info(chat_id, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    if tg_user and tg_user.get("app_user_id"):
        await bot.send_message(chat_id=chat_id, text="Ваш аккаунт уже привязан. /unlink для отвязки.")
        return
    text = ("Чтобы привязать аккаунт:\n"
            "1. Откройте приложение → Профиль\n"
            "2. Нажмите «Привязать Telegram»\n"
            "3. Нажмите на кнопку-ссылку или отправьте код боту")
    await bot.send_message(chat_id=chat_id, text=text)


async def _link_account(chat_id, code, db):
    link = await db.telegram_links.find_one({"code": code, "used": False})
    if not link:
        await bot.send_message(chat_id=chat_id, text="Код недействителен или уже использован. Получите новый в приложении.")
        return
    user_id = link["user_id"]
    # Link telegram to app user
    await db.telegram_users.update_one(
        {"chat_id": chat_id},
        {"$set": {"app_user_id": user_id, "linked_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    await db.users.update_one({"user_id": user_id}, {"$set": {"telegram_chat_id": chat_id}})
    await db.telegram_links.update_one({"code": code}, {"$set": {"used": True}})
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "name": 1})
    name = user.get("name", "") if user else ""
    await bot.send_message(chat_id=chat_id, text=f"Аккаунт привязан! Привет, {name}.\nТеперь вы будете получать уведомления здесь.")


async def _cmd_unlink(chat_id, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    if not tg_user or not tg_user.get("app_user_id"):
        await bot.send_message(chat_id=chat_id, text="Аккаунт не привязан.")
        return
    await db.users.update_one({"user_id": tg_user["app_user_id"]}, {"$unset": {"telegram_chat_id": ""}})
    await db.telegram_users.update_one({"chat_id": chat_id}, {"$unset": {"app_user_id": ""}})
    await bot.send_message(chat_id=chat_id, text="Аккаунт отвязан. Уведомления больше не будут приходить.")


async def _cmd_settings(chat_id, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    if not tg_user or not tg_user.get("app_user_id"):
        await bot.send_message(chat_id=chat_id, text="Сначала привяжите аккаунт. /link")
        return
    prefs = tg_user.get("notification_prefs", {})
    keyboard = []
    for key, label in [
        ("council_news", "Новости советов"),
        ("council_discussions", "Обсуждения"),
        ("council_votes", "Голосования"),
        ("reviews", "Отзывы"),
        ("system", "Системные"),
    ]:
        enabled = prefs.get(key, True)
        icon = "ON" if enabled else "OFF"
        keyboard.append([InlineKeyboardButton(f"{icon} {label}", callback_data=f"toggle_{key}")])
    await bot.send_message(
        chat_id=chat_id,
        text="Настройки уведомлений:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def _handle_callback(callback_query, db):
    chat_id = callback_query.message.chat_id
    data = callback_query.data
    if data.startswith("toggle_"):
        key = data[7:]
        tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
        prefs = tg_user.get("notification_prefs", {}) if tg_user else {}
        current = prefs.get(key, True)
        prefs[key] = not current
        await db.telegram_users.update_one({"chat_id": chat_id}, {"$set": {"notification_prefs": prefs}})
        await callback_query.answer(f"{'Включено' if not current else 'Выключено'}")
        await _cmd_settings(chat_id, db)


async def _cmd_admin(chat_id, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    if not tg_user or not tg_user.get("app_user_id"):
        await bot.send_message(chat_id=chat_id, text="Привяжите аккаунт. /link")
        return
    user = await db.users.find_one({"user_id": tg_user["app_user_id"]}, {"_id": 0, "role": 1})
    is_admin = user and user.get("role") == "admin"
    staff = await db.telegram_staff.find_one({"telegram_user_id": str(chat_id), "active": True})
    if not is_admin and not staff:
        await bot.send_message(chat_id=chat_id, text="Нет доступа к админ-панели.")
        return
    if is_admin:
        perms = list(ADMIN_PERMISSIONS.keys())
    else:
        perms = staff.get("permissions", [])
    lines = ["Админ-панель Народный Контроль\n\nДоступные функции:"]
    if "view_stats" in perms:
        lines.append("/stats — Статистика")
    if "manage_reviews" in perms:
        lines.append("Управление отзывами — через приложение")
    if "manage_councils" in perms:
        lines.append("Управление советами — через приложение")
    if "send_notifications" in perms:
        lines.append("/notify [текст] — Массовая рассылка")
    if "moderate_news" in perms:
        lines.append("Модерация новостей — через приложение")
    lines.append("\nПолное управление доступно в веб-приложении.")
    await bot.send_message(chat_id=chat_id, text="\n".join(lines))


async def _cmd_stats(chat_id, db):
    # Check permissions
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    total_users = await db.users.count_documents({})
    total_reviews = await db.reviews.count_documents({})
    active_councils = await db.councils.count_documents({"status": "active"})
    tg_linked = await db.telegram_users.count_documents({"app_user_id": {"$exists": True, "$ne": None}})
    text = (f"Статистика Народный Контроль\n\n"
            f"Пользователей: {total_users}\n"
            f"Отзывов: {total_reviews}\n"
            f"Активных советов: {active_councils}\n"
            f"Привязано к Telegram: {tg_linked}")
    await bot.send_message(chat_id=chat_id, text=text)


async def _cmd_notify(chat_id, text, db):
    tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
    if not tg_user or not tg_user.get("app_user_id"):
        return
    user = await db.users.find_one({"user_id": tg_user["app_user_id"]}, {"_id": 0, "role": 1})
    staff = await db.telegram_staff.find_one({"telegram_user_id": str(chat_id), "active": True})
    has_perm = (user and user.get("role") == "admin") or (staff and "send_notifications" in staff.get("permissions", []))
    if not has_perm:
        await bot.send_message(chat_id=chat_id, text="Нет прав для рассылки.")
        return
    msg = text.replace("/notify", "").strip()
    if not msg:
        await bot.send_message(chat_id=chat_id, text="Использование: /notify текст сообщения")
        return
    # Send to all linked users
    linked = await db.telegram_users.find({"app_user_id": {"$exists": True}}, {"chat_id": 1}).to_list(10000)
    sent = 0
    for u in linked:
        try:
            await bot.send_message(chat_id=u["chat_id"], text=f"Объявление:\n\n{msg}")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await bot.send_message(chat_id=chat_id, text=f"Отправлено {sent} пользователям.")


# ==================== Notification Functions ====================
async def notify_user(user_id: str, title: str, body: str, db, category: str = "system"):
    """Send notification to a user via Telegram if linked and enabled."""
    if not bot:
        return
    try:
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "telegram_chat_id": 1})
        if not user or not user.get("telegram_chat_id"):
            return
        chat_id = user["telegram_chat_id"]
        # Check notification preferences
        tg_user = await db.telegram_users.find_one({"chat_id": chat_id})
        if tg_user:
            prefs = tg_user.get("notification_prefs", {})
            if not prefs.get(category, True):
                return
        await bot.send_message(chat_id=chat_id, text=f"{title}\n\n{body}")
    except Exception as e:
        logger.error(f"Telegram notify error for {user_id}: {e}")


async def notify_council_members(council_id: str, title: str, body: str, db, exclude_user_id: str = None, category: str = "council_news"):
    """Notify all members of a council."""
    if not bot:
        return
    try:
        council = await db.councils.find_one({"council_id": council_id}, {"_id": 0, "members": 1})
        if not council:
            return
        for member in council.get("members", []):
            if member["user_id"] != exclude_user_id:
                await notify_user(member["user_id"], title, body, db, category)
                await asyncio.sleep(0.05)
    except Exception as e:
        logger.error(f"Council notify error: {e}")


async def setup_webhook(base_url: str):
    """Set webhook URL for the bot."""
    if not bot or not BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return
    webhook_secret = uuid.uuid4().hex[:16]
    webhook_url = f"{base_url}/api/telegram/webhook/{webhook_secret}"
    try:
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Telegram webhook set: {webhook_url}")
        return webhook_secret
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return None
