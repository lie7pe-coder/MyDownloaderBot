import os
import telebot
from yt_dlp import YoutubeDL

# التوكن الخاص بك
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"
bot = telebot.TeleBot(TOKEN)

# 1. رد الترحيب (بلمستك الخاصة)
@bot.message_handler(func=lambda m: m.text == "بوت" or m.text == "/start")
def welcome(message):
    welcome_text = (
        "هنء بنياشي شلون عيرك\n"
        "دز رابط الميديا التريدها 🫦💅🏻"
    )
    bot.reply_to(message, welcome_text)

# 2. معالجة الروابط بأعلى كواليتي وسلاسة
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(message):
    url = message.text
    
    # رسالة الانتظار
    status_text = (
        "يتم استدعاء عملائك\n"
        "لينفذو طلبك 🫦🎀"
    )
    status = bot.reply_to(message, status_text)

    # إعدادات سحب أعلى نسخة مدمجة جاهزة (تضمن الجودة والسلاسة بدون FFmpeg)
    ydl_opts = {
        'format': 'best[ext=mp4]/best', 
        'outtmpl': 'file_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            ext = info.get('ext', '').lower()
            # فحص إذا كان الرابط لصورة
            is_image = ext in ['jpg', 'jpeg', 'png', 'webp', 'heic']

        with open(filename, 'rb') as f:
            if is_image:
                # إرسال الصورة أولاً
                bot.send_photo(message.chat.id, f, reply_to_message_id=message.message_id)
                # ثم الرد المنفصل
                bot.send_message(message.chat.id, "وهاي الصورة بافضل كواليتي\nبدون مشاكل ✅")
            else:
                # إرسال الفيديو بأعلى سلاسة للمشاهدة والتحويل لـ GIF
                bot.send_video(
                    message.chat.id, 
                    f, 
                    reply_to_message_id=message.message_id, 
                    supports_streaming=True,
                    width=info.get('width'),
                    height=info.get('height'),
                    duration=info.get('duration')
                )
                # ثم الرد المنفصل
                bot.send_message(message.chat.id, "وهذا الفيديو بافضل كواليتي\nبدون مشاكل ✅")
        
        # تنظيف الملفات الزائدة
        os.remove(filename)
        bot.delete_message(message.chat.id, status.message_id)

    except Exception:
        # رد الفشل
        bot.edit_message_text("فشل استدعاء الميديا\nاسفةة دادي 💅🏻", message.chat.id, status.message_id)

# تشغيل البوت
bot.polling()
