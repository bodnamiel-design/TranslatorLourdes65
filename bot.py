import os, logging, io, asyncio
import whisper
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TELEGRAM_TOKEN') or "8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0"

model = whisper.load_model("tiny")

FR_RU = {'bonjour':'привет', 'merci':'спасибо', 'préfecture':'префектура', 'rendez-vous':'встреча', 
         'passeport':'паспорт', 'tarbes':'Тарб', 'phonothèque':'фонотека'}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Голос/текст FR→RU! Tarbes 2026 🚀")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    ru = ' '.join(FR_RU.get(w, w) for w in text.split())
    await update.message.reply_text(ru)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info("Voice!")
        file = await update.message.voice.get_file()
        path = await file.download_to_drive('voice.ogg')
        audio = AudioSegment.from_ogg(path)
        audio.export('temp.wav', format='wav')
        result = model.transcribe('temp.wav', language='fr')
        text_fr = result['text'].lower()
        ru = ' '.join(FR_RU.get(w, w) for w in text_fr.split())
        await update.message.reply_text(f"🎤 {text_fr} 🇷🇺 {ru}")
        os.remove('temp.wav')
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    print("🚀 Polling started! Tarbes Translator Live!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

