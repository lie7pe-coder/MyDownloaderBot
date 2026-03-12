import os
import asyncio
import yt_dlp
import random
import re
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# التوكن الخاص بك
TOKEN = "8650672657:AAHKkLKrMYIVrWbD5nrOT99QKDKLnJPgmZ4"

custom_db = {}
user_state = {}

def format_caption(text, words_per_line=3):
    emoji_pattern = r'[\u2600-\u27BF]|[\u1f300-\u1f64f]|[\u1f680-\u1f6ff]|[\u1f1e0-\u1f1ff]'
    emojis = "".join(re.findall(emoji_pattern, text))
    pure_text = re.sub(emoji_pattern, '', text).strip()
    words = pure_text.split()
    lines = [" ".join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
    formatted_text = "\n".join(lines)
    return f"{formatted_text}\n{emojis}" if emojis else formatted_text

async def live_typing(message, full_text, step=5):
    display_text = ""
    for i in range(0, len(full_text), step):
        display_text = full_text[:i+step]
        try:
            await message.edit_text(display_text)
            await asyncio.sleep(0.1) 
        except: continue

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "finish_adding":
        if user_id in user_state and "trigger" in user_state[user_id]:
            data = user_state[user_id]
            trigger = data["trigger"]
            replies = data["replies"]
            
            if replies:
                custom_db[trigger] = replies
                await query.edit_message_text(f"تم إضافة {len(replies)} ردود للكلمة: ({trigger}) ✅")
            else:
                await query.edit_message_text("تم إلغاء العملية، لم تضف أي ردود.")
            
            if user_id in user_state: del user_state[user_id]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.message.chat_id
    text = update.message.text
    user_id = update.message.from_user.id

    # 1. نظام إضافة رد متعدد
    if text == "أضف رد متعدد":
        user_state[user_id] = {"state": "waiting_for_trigger", "replies": []}
        await update.message.reply_text("ارسل الرد المتعدد (الكلمة التي تشغل الردود)")
        return

    if user_id in user_state:
        state_data = user_state[user_id]
        
        if state_data["state"] == "waiting_for_trigger":
            user_state[user_id]["trigger"] = text
            user_state[user_id]["state"] = "waiting_for_replies"
            await update.message.reply_text(f"تم تحديد الكلمة: ({text})\nالآن ارسل الردود (نصوص أو متحركات) واحداً تلو الآخر.")
            return

        if state_data["state"] == "waiting_for_replies":
            # إضافة الرد الحالي للقائمة
            if update.message.animation:
                user_state[user_id]["replies"].append({"type": "gif", "file_id": update.message.animation.file_id})
            elif text:
                user_state[user_id]["replies"].append({"type": "text", "content": text})
            
            keyboard = [[InlineKeyboardButton("اضغط لإنهاء الاضافة 🏁", callback_data="finish_adding")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"تم تسجيل الرد رقم {len(user_state[user_id]['replies'])}.. ارسل الرد التالي أو اضغط إنهاء:", reply_markup=reply_markup)
            return

    # 2. الأوامر العامة (الردود، مسح رد)
    if text == "الردود":
        if not custom_db:
            await update.message.reply_text("لا توجد ردود حالياً ❄️")
            return
        report = "📋 **الردود المضافة:**\n"
        for t in custom_db: report += f"🔹 {t} ({len(custom_db[t])} رد)\n"
        await update.message.reply_text(report, parse_mode='Markdown')
        return

    if text and text.startswith("مسح رد "):
        word = text.replace("مسح رد ", "").strip()
        if word in custom_db:
            del custom_db[word]
            await update.message.reply_text(f"تم مسح الردود لـ ({word})")
        return

    # 3. تنفيذ الردود (يرسل كل الردود المضافة للكلمة)
    if text in custom_db:
        for res in custom_db[text]:
            if res["type"] == "gif":
                await update.message.reply_animation(animation=res["file_id"])
            else:
                formatted = format_caption(res["content"])
                m = await update.message.reply_text(formatted[:1])
                await live_typing(m, formatted)
        return

    # 4. تحميل الفيديو
    if text and "http" in text:
        status = await update.message.reply_text("ت")
        await live_typing(status, "جاري معالجة الرابط 🫦💅🏻")
        ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': f'vid_{chat_id}.%(ext)s', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, text, download=True)
                filename = ydl.prepare_filename(info)
                with open(filename, 'rb') as vf:
                    await update.message.reply_video(video=vf, supports_streaming=True)
                raw_cap = "الفيديو كدامك مثل ماردته بافضل كواليتي 👈🏻👉🏻"
                final_cap = format_caption(raw_cap)
                cap_msg = await update.message.reply_text("ا")
                await live_typing(cap_msg, final_cap)
                if os.path.exists(filename): os.remove(filename)
            await status.delete()
        except:
            await status.edit_text("هذا الرابط غير مدعوم 🎀")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
