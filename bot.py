
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

app = Flask(__name__)

@app.get("/")
def home():
    return "Anime AI Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 Создать образ", callback_data="create")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="help")],
    ]
    await update.message.reply_text(
        "Привет! Я Anime AI Bot 🤖\n\n"
        "Я помогаю создавать реалистичные образы "
        "вымышленных совершеннолетних персонажей.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["waiting_photo"] = True
        await query.message.reply_text(
            "Отправь рисунок персонажа. Затем напиши, "
            "какой новый костюм или образ хочешь создать."
        )
    elif query.data == "help":
        await query.message.reply_text(
            "1. Отправь рисунок.\n"
            "2. Опиши желаемую одежду.\n"
            "3. Получи обработанный образ после подключения "
            "сервиса генерации."
        )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo_id"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "Фото получено! Теперь опиши желаемый новый образ."
    )

async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("photo_id"):
        await update.message.reply_text(
            "Сначала отправь рисунок персонажа."
        )
        return

    description = update.message.text
    await update.message.reply_text(
        "Описание принято:\n"
        f"{description}\n\n"
        "Интерфейс бота готов. Для генерации изображения "
        "нужно подключить отдельный ИИ-сервис."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Действие отменено.")

def run_bot():
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("cancel", cancel))
    bot.add_handler(CallbackQueryHandler(buttons))
    bot.add_handler(MessageHandler(filters.PHOTO, photo))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prompt))
    bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
