import logging
import os
import asyncio
import whisper
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import io

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ТВОЙ TELEGRAM_TOKEN
TOKEN = "8508774998:AAGTo190LCDz65VPvRBt8VtDLqLacPgnL_0"

# FR → RU словарь (расширь!)
DICT_FR_RU = {
    'bonjour': 'привет',
    'merci': 'спасибо',
    'passeport': 'паспорт',
    'préfecture': 'префектура',
    'rendez-vous': 'встреча',
    'demande': 'заявка',
    'documents': 'документы'
}

def translate_fr_ru(text):
    """Простой FR→RU через словарь"""
    words = text.lower().split()
    translated = []
    for word in words:
        translated.append(DICT_FR_RU.get(word, word))
    return ' '.join(translated)

# Whisper модель (загружается 1 раз)
model = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Голосовой перевод FR→RU!\n📝 Отправь текст или голосовое.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_fr = update.message.text
    text_ru = translate_fr_ru(text_fr)
    await update.message.reply_text(f"🇫🇷: {text_fr}\n🇷🇺: {text_ru}")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global model
    
    try:
        # Скачиваем голосовое (OGG → WAV)
        voice_file = await update.message.voice.get_file()
        ogg_bytes = await voice_file.download_as_bytearray()
        
        # Конверт OGG → WAV
        audio = AudioSegment.from_ogg(io.BytesIO(ogg_bytes))
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)
        
        # Загружаем Whisper (base модель ~50MB)
        if model is None:
            model = whisper.load_model("base")
            logger.info("Whisper model loaded!")
        
        # Транскрипция FR
        result = model.transcribe(wav_bytes, language="fr")
        text_fr = result["text"].strip()
        
        if text_fr:
            text_ru = translate_fr_ru(text_fr)
            await update.message.reply_text(f"🎤 FR: {text_fr}\n🇷🇺 RU: {text_ru}")
        else:
            await update.message.reply_text("❌ Не разобрал голос. Говори громче! 🔊")
            
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await update.message.reply_text("❌ Ошибка голоса. Попробуй текст.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
