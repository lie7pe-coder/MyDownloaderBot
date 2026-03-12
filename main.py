import os
import asyncio
import yt_dlp
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# التوكن الخاص بك
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1'
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url: return
    
    chat_id = update.message.chat_id
    status = await update.message.reply_text("⏳ جاري التحميل (سيتم توفير نسخة بدون صوت)...")
    
    # تحميل الفيديو الأصلي (بصوت)
    v_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'vid_{chat_id}_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'user_agent': random.choice(USER_AGENTS),
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(v_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            v_file = ydl.prepare_filename(info)
            if not v_file.endswith('.mp4'): v_file = os.path.splitext(v_file)[0] + ".mp4"

            # إنشاء أزرار الخيارات
            keyboard = [[InlineKeyboardButton("🔇 إرسال كمتحركة (بدون تراك صوتي)", callback_data=f"mute|{url}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(v_file, 'rb') as vf:
                await update.message.reply_video(video=vf, caption="🎬 الفيديو الأصلي", reply_markup=reply_markup)
            
            os.remove(v_file)
            await status.delete()
            
    except Exception as e:
        await status.edit_text(f"❌ خطأ: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    if data[0] == "mute":
        url = data[1]
        chat_id = query.message.chat_id
        
        # تحميل الفيديو "بدون تراك صوتي" نهائياً من المصدر
        mute_opts = {
            'format': 'bestvideo', # نطلب الفيديو فقط بدون Audio
            'outtmpl': f'mute_{chat_id}_%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
            'user_agent': random.choice(USER_AGENTS),
            'quiet': True,
        }
        
        status_msg = await query.message.reply_text("🔄 جاري معالجة النسخة الصامتة (بدون تراك)...")
        
        try:
            with yt_dlp.YoutubeDL(mute_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                m_file = ydl.prepare_filename(info)
                if not m_file.endswith('.mp4'): m_file = os.path.splitext(m_file)[0] + ".mp4"

                with open(m_file, 'rb') as mf:
                    await query.message.reply_animation(animation=mf, caption="🎥 تم الإرسال كمتحركة صامتة نهائياً")
                
                os.remove(m_file)
                await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text("❌ فشل في معالجة النسخة الصامتة.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
