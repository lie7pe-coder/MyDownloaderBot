import os
import telebot
from yt_dlp import YoutubeDL

# التوكن الخاص بك تم وضعه هنا مباشرة
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"
bot = telebot.TeleBot(TOKEN)

# 1. رد الترحيب
@bot.message_handler(func=lambda m: m.text == "بوت" or m.text == "/start")
def welcome(message):
    welcome_text = (
        "هنء بنياشي شلون عيرك\n"
        "دز رابط الميديا التريدها 🫦💅🏻"
    )
    bot.reply_to(message, welcome_text)

# 2. معالجة الروابط
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(message):
    url = message.text
    
    status_text = (
        "يتم استدعاء عملائك\n"
        "لينفذو طلبك 🫦🎀"
    )
    status = bot.reply_to(message, status_text)

    # إعدادات الجودة القصوى والتخفي كإنسان
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', 
        'outtmpl': 'file_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': url,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + ".mp4"
            
            ext = info.get('ext', '').lower()
            is_image = ext in ['jpg', 'jpeg', 'png', 'webp', 'heic']

        with open(filename, 'rb') as f:
            if is_image:
                # 3. رد نجاح الصورة
                bot.send_photo(
                    message.chat.id, 
                    f, 
                    caption="وهاي الصورة بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id
                )
            else:
                # 4. رد نجاح الفيديو
                bot.send_document(
                    message.chat.id, 
                    f, 
                    caption="وهذا الفيديو بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id
                )
        
        os.remove(filename)
        bot.delete_message(message.chat.id, status.message_id)

    except Exception:
        # 5. رد الخطأ
        bot.edit_message_text("فشل استدعاء الميديا\nاسفةة دادي 💅🏻", message.chat.id, status.message_id)

bot.polling()
