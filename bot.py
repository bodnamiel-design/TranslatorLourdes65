import os, logging, io, asyncio, gc
import torch
import whisper
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from pydub import AudioSegment

TOKEN = os.getenv('TELEGRAM_TOKEN')  # УБРАЛ ХАРДКОД! Задай в Render Environment

# Загрузка ТINY модели (250MB RAM)
print("Загружаем Whisper tiny...")
model = whisper.load_model('tiny')  # tiny.en для ENG, base → OOM!
print("Модель загружена")
gc.collect()

app = Application.builder().token(TOKEN).build()

async def voice_handler(update: Update, context):
    try:
        voice = await update.message.voice.get_file()
        audio = await voice.download_as_bytearray()
        
        # pydub → WAV в памяти
        audio_seg = AudioSegment.from_file(io.BytesIO(audio), format="ogg")
        audio_wav = io.BytesIO()
        audio_seg.export(audio_wav, format="wav")
        audio_wav.seek(0)
        
        # Транскрипция FR
        result = model.transcribe(audio_wav, language='fr')
        text_fr = result['text'].strip()
        
        if not text_fr:
            await update.message.reply_text("🤐 Не разобрал аудио. Говори громче! 🔊")
            return
        
        # FAKE перевод (замени на OpenAI/GPT)
        translated_ru = f"🇫🇷 {text_fr}\n🇷🇺 {text_fr[::-1][:50]}..."  # Реверс для теста
        
        await update.message.reply_text(translated_ru)  # TEXT, не voice!
        
        # Очистка памяти
        del audio_seg, audio_wav, result
        gc.collect()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
        logging.error(f"Voice error: {e}")

async def start(update: Update, context):
    await update.message.reply_text("🎤 Голос FR→RU! Tarbes65 Translator ready. Отправь voice!")

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"  # Render var!
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_path=TOKEN,
        url_path=TOKEN,
        webhook_url=webhook_url
    )
