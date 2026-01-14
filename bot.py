import os, logging, whisper, io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0")  # Environment!

DICT_FR_RU = {'bonjour':'привет', 'merci':'спасибо', 'passeport':'паспорт', 'préfecture':'префектура'}

def translate_fr_ru(text):
    return ' '.join([DICT_FR_RU.get(w.lower(), w) for w in text.split()])

model = None

async def start(update: Update, context):
    await update.message.reply_text("🎤 Голос FR→RU webhook!")

async def voice_handler(update: Update, context):
    global model
    try:
        voice_file = await update.message.voice.get_file()
        ogg_bytes = await voice_file.download_as_bytearray()
        audio = AudioSegment.from_ogg(io.BytesIO(ogg_bytes))
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav"); wav_bytes.seek(0)
        
        if model is None: model = whisper.load_model("tiny")
        result = model.transcribe(wav_bytes, language="fr")
        text_ru = translate_fr_ru(result["text"])
        await update.message.reply_text(f"🇫🇷: {result['text']}\n🇷🇺: {text_ru}")
    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    # WEBHOOK для Render Web Service!
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://translatorlourdes65.onrender.com/{TOKEN}",
        webhook_path=TOKEN
    )

if __name__ == '__main__':
    main()
