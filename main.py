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
    status = await update.message.reply_text("⏳ جاري معالجة الرابط...")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'vid_{chat_id}_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'user_agent': random.choice(USER_AGENTS),
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + ".mp4"

            # إنشاء الزر أسفل الفيديو
            keyboard = [[InlineKeyboardButton("🎬 إرسال كمتحركة (بدون صوت)", callback_data=f"gif|{filename}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(filename, 'rb') as vf:
                await update.message.reply_video(
                    video=vf, 
                    caption="✅ تم تحميل الفيديو بنجاح",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )
            
            # ملاحظة: لا نحذف الملف هنا فوراً لأننا قد نحتاجه إذا ضغط المستخدم على زر GIF
            # سيتم الحذف بعد فترة أو عند الضغط على الزر
            await status.delete()
            
    except Exception as e:
        await status.edit_text(f"❌ فشل: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    if data[0] == "gif":
        filename = data[1]
        if os.path.exists(filename):
            await query.message.reply_animation(
                animation=open(filename, 'rb'),
                caption="🎥 تم الإرسال بصيغة متحركة"
            )
            # الآن يمكن حذف الملف بعد تلبية الطلبين
            os.remove(filename)
        else:
            await query.message.reply_text("⚠️ عذراً، الملف انتهت صلاحيته من السيرفر.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 سورس الأزرار التفاعلية يعمل...")
    app.run_polling()

if __name__ == '__main__':
    main()
