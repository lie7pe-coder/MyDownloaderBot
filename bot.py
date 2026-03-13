import os
import telebot
import time
from yt_dlp import YoutubeDL

# التوكن حقك يا دادي
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"
bot = telebot.TeleBot(TOKEN)

# 1. رد الترحيب المثير (قاعدة: ردودك لا تتغير 🫦)
@bot.message_handler(func=lambda m: m.text == "بوت" or m.text == "/start")
def welcome(message):
    welcome_text = (
        "هنء بنياشي شلون عيرك\n"
        "دز رابط الميديا التريدها 🫦💅🏻"
    )
    bot.reply_to(message, welcome_text)

# 2. السحب بالأصلي الخام (بدون تغيير ترميز أو حاوية)
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(message):
    url = message.text
    status = bot.reply_to(message, "يتم استدعاء عملائك\nلينفذو طلبك 🫦🎀")

    # إعدادات السحب الخام لضمان الترميز والحاوية الأصلية 100%
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', 
        'outtmpl': 'original_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            ext = info.get('ext', '').lower()
            is_image = ext in ['jpg', 'jpeg', 'png', 'webp', 'heic']

        with open(filename, 'rb') as f:
            if is_image:
                bot.send_photo(
                    message.chat.id, 
                    f, 
                    caption="وهاي الصورة بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id
                )
            else:
                # إرسال الفيديو الأصلي بالترميز الخام
                bot.send_video(
                    message.chat.id, 
                    f, 
                    caption="وهذا الفيديو بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id,
                    supports_streaming=True,
                    duration=info.get('duration'),
                    width=info.get('width'),
                    height=info.get('height'),
                    timeout=1200
                )
        
        os.remove(filename)
        bot.delete_message(message.chat.id, status.message_id)

    except Exception:
        # رد الفشل المعتمد (اسفةة دادي 💅🏻)
        bot.edit_message_text("فشل استدعاء الميديا\nاسفةة دادي 💅🏻", message.chat.id, status.message_id)

while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(5)
