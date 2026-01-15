import os, logging, asyncio
import whisper
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from pydub import AudioSegment

TOKEN = os.getenv('TELEGRAM_TOKEN') or '8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0'
model = whisper.load_model('base')  # large-v3 для accuracy

app = Application.builder().token(TOKEN).build()

async def voice_handler(update: Update, context):
    voice = await update.message.voice.get_file()
    audio = await voice.download_as_bytearray()
    audio_seg = AudioSegment.from_file(io.BytesIO(audio), format="ogg")
    audio_wav = io.BytesIO()
    audio_seg.export(audio_wav, format="wav")
    result = model.transcribe(audio_wav, language='fr')
    text_fr = result['text'].strip()
    # Translate FR->RU via GPT или dict
    translated_ru = f"🇫🇷 {text_fr}
🇷🇺 {translate_to_ru(text_fr)}"  # ваша функция
    await update.message.reply_voice(translated_ru, voice.Note(duration=5))  # или text

async def start(update: Update, context):
    await update.message.reply_text("🎤 Отправь голос FR → RU! Префектура Tarbes ready.")

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

async def post_init(application):
    await application.bot.set_webhook(f"https://your-service.onrender.com/{TOKEN8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_path=TOKEN,
        url_path=TOKEN,
        webhook_url=f"https://your-service.onrender.com/{TOKEN}"
    )
