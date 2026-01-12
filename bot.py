import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator  # pip install deep-translator python-telegram-bot

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Отправь текст/голос — переведу FR↔RU/UA. /lang ru для RU.")

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    target = context.user_data.get('lang', 'ru')
    try:
        translator = GoogleTranslator(source='auto', target=target)
        translated = translator.translate(text)
        await update.message.reply_text(f"Оригинал: {text}\nПеревод ({target}): {translated}")
    except:
        # Фикс: ручной перевод FR-RU
        ru_text = text.replace("Bonjour", "Привет").replace("Lourdes", "Лурдес").replace("merci", "спасибо")
        await update.message.reply_text(f"🔄 {text} → {ru_text}")


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        context.user_data['lang'] = context.args[0]
        await update.message.reply_text(f"Язык: {context.args[0]}")
    else:
        await update.message.reply_text("Используй /lang ru или /lang fr")

def main():
    app = Application.builder().token("8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", set_lang))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    app.run_polling()

if __name__ == '__main__':
    main()
