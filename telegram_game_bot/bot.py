import logging
import asyncio
import nest_asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import os
TOKEN = os.environ.get("BOT_TOKEN")


users = {}
logging.basicConfig(level=logging.INFO)

langs = {
    "ru": {"play_bot": "🤖 Играть с ботом", "play_online": "🌐 Играть онлайн", "back": "🔙 Назад",
           "choose_language": "Выберите язык / Choose language / Dil seçin",
           "level_easy": "🟢 Лёгкий", "level_medium": "🟡 Средний", "level_hard": "🔴 Сложный",
           "create_room": "➕ Создать комнату", "join_room": "🔗 Подключиться", "find_enemy": "🎯 Найти соперника",
           "profile": "👤 Ваш профиль:\nМонеты: 💰{}\nКубки: 🏆{}"},
    "en": {"play_bot": "🤖 Play with bot", "play_online": "🌐 Play online", "back": "🔙 Back",
           "choose_language": "Choose language / Выберите язык / Dil seçin",
           "level_easy": "🟢 Easy", "level_medium": "🟡 Medium", "level_hard": "🔴 Hard",
           "create_room": "➕ Create room", "join_room": "🔗 Join room", "find_enemy": "🎯 Find opponent",
           "profile": "👤 Your profile:\nCoins: 💰{}\nCups: 🏆{}"},
    "az": {"play_bot": "🤖 Botla oynamaq", "play_online": "🌐 Onlayn oynamaq", "back": "🔙 Geri",
           "choose_language": "Dil seçin / Choose language / Выберите язык",
           "level_easy": "🟢 Asan", "level_medium": "🟡 Orta", "level_hard": "🔴 Çətin",
           "create_room": "➕ Otaq yarat", "join_room": "🔗 Qoşulmaq", "find_enemy": "🎯 Rəqib tap",
           "profile": "👤 Profiliniz:\nPul: 💰{}\nKuboklar: 🏆{}"}
}

def lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="lang_az")]
    ])

def menu_kb(lang):
    t = langs[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["play_bot"], callback_data="play_bot")],
        [InlineKeyboardButton(t["play_online"], callback_data="play_online")]
    ])

def levels_kb(lang):
    t = langs[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["level_easy"], callback_data="level_easy")],
        [InlineKeyboardButton(t["level_medium"], callback_data="level_medium")],
        [InlineKeyboardButton(t["level_hard"], callback_data="level_hard")],
        [InlineKeyboardButton(t["back"], callback_data="main_menu")]
    ])

def online_kb(lang):
    t = langs[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["create_room"], callback_data="create_room")],
        [InlineKeyboardButton(t["join_room"], callback_data="join_room")],
        [InlineKeyboardButton(t["find_enemy"], callback_data="find_enemy")],
        [InlineKeyboardButton(t["back"], callback_data="main_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        users[uid] = {"lang": "ru", "coins": 0, "cups": 1000}
        await update.message.reply_text(langs["ru"]["choose_language"], reply_markup=lang_kb())
    else:
        lang = users[uid]["lang"]
        await update.message.reply_text("📋 Меню:", reply_markup=menu_kb(lang))

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = users.get(uid, {"lang": "ru", "coins": 0, "cups": 1000})
    users[uid] = user
    msg = langs[user["lang"]]["profile"].format(user["coins"], user["cups"])
    await update.message.reply_text(msg)

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(langs["ru"]["choose_language"], reply_markup=lang_kb())

async def baltop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💬 Пример: /baltop cash или /baltop cups")
        return
    param = context.args[0]
    if param not in ("cash", "cups"):
        await update.message.reply_text("❗ Только 'cash' или 'cups'")
        return
    key = "coins" if param == "cash" else "cups"
    top = sorted(users.items(), key=lambda x: x[1][key], reverse=True)[:10]
    msg = f"🏆 Топ по {param}:\n"
    for i, (uid, data) in enumerate(top, 1):
        msg += f"{i}. ID {uid} — 💰{data['coins']} / 🏆{data['cups']}\n"
    await update.message.reply_text(msg)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = str(query.from_user.id)
    data = query.data
    user = users.setdefault(uid, {"lang": "ru", "coins": 0, "cups": 1000})
    lang = user["lang"]
    t = langs[lang]

    await query.answer()

    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        user["lang"] = lang_code
        await query.edit_message_text("📋 Меню:", reply_markup=menu_kb(lang_code))
    elif data == "play_bot":
        await query.edit_message_text("🎮 Выберите уровень:", reply_markup=levels_kb(lang))
    elif data == "play_online":
        await query.edit_message_text("🌐 Онлайн режим:", reply_markup=online_kb(lang))
    elif data == "main_menu":
        await query.edit_message_text("📋 Меню:", reply_markup=menu_kb(lang))
    elif data in ("level_easy", "level_medium", "level_hard"):
        await query.edit_message_text(f"✅ Режим {t[data]} выбран! (Игра в разработке)")
    elif data == "create_room":
        room_id = random.randint(1000, 9999)
        await query.edit_message_text(f"🆕 Комната создана! ID: {room_id}")
    elif data == "join_room":
        await query.edit_message_text("🔗 Введите ID комнаты (будет реализовано позже)")
    elif data == "find_enemy":
        await query.edit_message_text("🔍 Поиск соперника... (будет позже)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — запустить бота\n"
        "/language — сменить язык\n"
        "/profile — ваш профиль\n"
        "/baltop cash — топ по монетам\n"
        "/baltop cups — топ по кубкам"
    )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("baltop", baltop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))

    await app.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("language", "Сменить язык"),
        BotCommand("profile", "Профиль игрока"),
        BotCommand("baltop", "Топ игроков"),
        BotCommand("help", "Помощь")
    ])

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
