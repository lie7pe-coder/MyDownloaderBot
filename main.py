import os
import asyncio
import yt_dlp
import random
from telegram import Update, constants
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1'
]

def format_caption(text, words_per_line=3):
    """دالة لإنزال سطر جديد بعد كل عدد معين من الكلمات"""
    words = text.split()
    lines = []
    for i in range(0, len(words), words_per_line):
        lines.append(" ".join(words[i:i+words_per_line]))
    return "\n".join(lines)

async def live_typing(message, full_text, step=3):
    """تأثير الكتابة الحية (3 أحرف بـ 3 أحرف) والسرعة 0.3"""
    display_text = ""
    for i in range(0, len(full_text), step):
        display_text = full_text[:i+step]
        try:
            await message.edit_text(display_text)
            await asyncio.sleep(0.3) 
        except:
            continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return
    chat_id = update.message.chat_id

    # التعامل مع كلمة "بوت"
    if "بوت" in text:
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
        main_msg = await update.message.reply_text("ه")
        await live_typing(main_msg, "هلو بنياشي اهء فدوا العيرك 🫦💅🏻", step=3)
        
        extra_replies = ["عءقعءقءعق ءواعق", "ءواعق عءقعءقءعق", "عءقعءقءعق ءواعق"]
        for reply in extra_replies:
            m = await update.message.reply_text("ء")
            await live_typing(m, reply, step=3)
        return

    # كود تحميل الفيديو مع الكابشن "المنظم"
    if "http" in text:
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
        status = await update.message.reply_text("تم")
        await live_typing(status, "تم استلام الرابط وبدء العمل 🫦💅🏻", step=3)
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'vid_{chat_id}_%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
            'user_agent': random.choice(USER_AGENTS),
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.UPLOAD_VIDEO)
                info = await asyncio.to_thread(ydl.extract_info, text, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'): filename = os.path.splitext(filename)[0] + ".mp4"

                # تنسيق الرد لينزل سطر بعد كل 3 كلمات
                raw_caption = "الفيديو كدامك مثل ماردته بافضل كواليتي 👈🏻👉🏻"
                final_caption = format_caption(raw_caption, words_per_line=3)

                with open(filename, 'rb') as vf:
                    await update.message.reply_video(
                        video=vf, 
                        caption=final_caption,
                        supports_streaming=True
                    )
                if os.path.exists(filename): os.remove(filename)
            await status.delete()
        except:
            await status.edit_text("هذا")
            await live_typing(status, "هذا الرابط غير مدعوم 🎀", step=3)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
