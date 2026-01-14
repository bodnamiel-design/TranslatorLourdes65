import os, logging, whisper, io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0")

DICT_FR_RU = {
    'bonjour': 'привет', 'merci': 'спасибо', 'passeport': 'паспорт',
    'préfecture': 'префектура', 'rendez-vous': 'встреча', 'demande': 'заявка',
    'documents': 'документы', 'carte': 'карта', 'identité': 'личность'
}

def translate_fr_ru(text):
    words = text.lower().split()
    return ' '.join([DICT_FR_RU.get(word, word) for word in words])

model = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Голос/текст FR→RU! Tarbes 2026 🚀")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_fr = update.message.text
    text_ru = translate_fr_ru(text_fr)
    await update.message.reply_text(f"🇫🇷: {text_fr}\n🇷🇺: {text_ru}")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global model
    try:
        voice_file = await update.message.voice.get_file()
        ogg_bytes = await voice_file.download_as_bytearray()
        audio = AudioSegment.from_ogg(io.BytesIO(ogg_bytes))
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)
        
        if model is None:
            model = whisper.load_model("tiny")  # Быстрее!
        
        result = model.transcribe(wav_bytes, language="fr")
        text_fr = result["text"].strip()
        text_ru = translate_fr_ru(text_fr)
        
        await update.message.reply_text(f"🎤 🇫🇷: {text_fr}\n🇷🇺: {text_ru}")
    except Exception as e:
        await update.message.reply_text(f"❌ Голос ошибка: {str(e)[:100]}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    # WEBHOOK для Render Web Service!
    port = int(os.environ.get("PORT", 10000))
    webhook_url = f"http://translatorlourdes65.onrender.com/{TOKEN}"
    
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url,
        webhook_path=TOKEN
    )

if __name__ == '__main__':
    main()

