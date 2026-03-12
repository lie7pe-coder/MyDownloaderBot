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
    status = await update.message.reply_text("🚀 جاري سحب الفيديو بأعلى جودة...")
    
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
            v_file = ydl.prepare_filename(info)
            if not v_file.endswith('.mp4'): v_file = os.path.splitext(v_file)[0] + ".mp4"

            # الزر الآن يشير إلى نفس الملف المحمل محلياً
            keyboard = [[InlineKeyboardButton("🔇 إرسال كمتحركة (بدون صوت)", callback_data=f"gif|{v_file}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(v_file, 'rb') as vf:
                await update.message.reply_video(
                    video=vf, 
                    caption="✅ الفيديو الأصلي بجودة كاملة",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )
            
            # ملاحظة: لن نحذف الملف فوراً لنسمح للمستخدم بالضغط على زر المتحركة
            # سيتم الحذف بواسطة مهمة مجدولة أو عند الضغط على الزر
            await status.delete()
            
    except Exception as e:
        await status.edit_text(f"❌ فشل التحميل: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    if data[0] == "gif":
        v_file = data[1]
        
        if os.path.exists(v_file):
            # إرسال كـ animation يزيل الصوت تلقائياً في تليجرام
            with open(v_file, 'rb') as mf:
                await query.message.reply_animation(
                    animation=mf, 
                    caption="🎥 نسخة متحركة (بدون تراك صوتي)"
                )
            # الآن نحذف الملف بعد الإرسال بنجاح
            os.remove(v_file)
        else:
            await query.edit_message_caption(caption="⚠️ عذراً، الملف حُذف من السيرفر. أرسل الرابط مجدداً.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
