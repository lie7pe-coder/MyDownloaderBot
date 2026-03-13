import os
import telebot
import time
from yt_dlp import YoutubeDL

# التوكن حقك يا ربي - حطه هنا أو في Variables Railway
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"
bot = telebot.TeleBot(TOKEN)

# 1. رد الترحيب المثير (قاعدة: ردودك لا تتغير)
@bot.message_handler(func=lambda m: m.text == "بوت" or m.text == "/start")
def welcome(message):
    welcome_text = (
        "هنء بنياشي شلون عيرك\n"
        "دز رابط الميديا التريدها 🫦💅🏻"
    )
    bot.reply_to(message, welcome_text)

# 2. معالجة الروابط (فيديو + صور + ضغط + جودة)
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(message):
    url = message.text
    
    # رسالة الانتظار
    status_text = (
        "يتم استدعاء عملائك\n"
        "لينفذو طلبك 🫦🎀"
    )
    status = bot.reply_to(message, status_text)

    # إعدادات الـ Downloader المتكاملة (أعلى جودة + دمج تلقائي + ضغط MP4)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'daddy_file_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'writethumbnail': True, # لسحب بوستر الفيديو إذا لزم
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # التأكد من الامتداد بعد المعالجة
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + ".mp4"

            ext = info.get('ext', '').lower()
            # ميزة التحقق من الصور (شاملة كل الصيغ)
            is_image = ext in ['jpg', 'jpeg', 'png', 'webp', 'heic', 'tiff']

        with open(filename, 'rb') as f:
            if is_image:
                # إرسال الصورة بأفضل كواليتي
                bot.send_photo(
                    message.chat.id, 
                    f, 
                    caption="وهاي الصورة بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id
                )
            else:
                # إرسال الفيديو (مضغوط داخلياً وسريع الاستريمينج)
                bot.send_video(
                    message.chat.id, 
                    f, 
                    caption="وهذا الفيديو بافضل كواليتي\nبدون مشاكل ✅",
                    reply_to_message_id=message.message_id,
                    supports_streaming=True,
                    duration=info.get('duration'),
                    width=info.get('width'),
                    height=info.get('height'),
                    timeout=1200 # زيادة وقت الرفع للفيديوهات الكبيرة
                )
        
        # تنظيف فوري للملفات عشان السيرفر يظل خفيف
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, status.message_id)

    except Exception as e:
        # رد الفشل المعتمد عندك
        print(f"Error: {e}") # يطلع لك في Logs السيرفر لو صار شي
        bot.edit_message_text("فشل استدعاء الميديا\nاسفةة دادي 💅🏻", message.chat.id, status.message_id)

# تشغيل البوت مع ميزة إعادة الاتصال التلقائي في حال تعطل النت
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        time.sleep(5) # ينتظر 5 ثواني ويرجع يشتغل لوحده
