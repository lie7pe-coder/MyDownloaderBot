import os
import asyncio
import yt_dlp
import random
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ضع التوكن الخاص بك هنا
TOKEN = "ضع_التوكن_هنا"

# إعدادات التمويه لتجنب الحظر
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
]

# إعدادات الجودة العالية مع هوية مزورة
def get_opts(mode, chat_id):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': random.choice(USER_AGENTS),
        'referer': 'https://www.google.com/', # تمويه المصدر
        'nocheckcertificate': True,
    }
    
    if mode == 'video':
        opts.update({
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'v_{chat_id}_%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        })
    else: # audio
        opts.update({
            'format': 'bestaudio/best',
            'outtmpl': f'a_{chat_id}_%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        })
    return opts

async def download_item(opts, url):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return await asyncio.to_thread(ydl.extract_info, url, download=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url: return
    
    chat_id = update.message.chat_id
    status = await update.message.reply_text("⏳ جاري التحميل بأمان وأعلى جودة...")
    
    try:
        # فحص الرابط أولاً مع هوية عشوائية
        with yt_dlp.YoutubeDL({'quiet': True, 'user_agent': random.choice(USER_AGENTS)}) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
        
        # إذا كان الرابط صورة مباشرة
        if info.get('ext') in ['jpg', 'png', 'jpeg', 'webp'] or not info.get('vcodec'):
            await update.message.reply_photo(url)
        else:
            # تحميل الفيديو والصوت في نفس الوقت
            v_opts = get_opts('video', chat_id)
            a_opts = get_opts('audio', chat_id)
            
            res = await asyncio.gather(download_item(v_opts, url), download_item(a_opts, url))
            
            # جلب أسماء الملفات التي تم تحميلها
            v_file = v_opts['outtmpl'].replace('%(id)s', res[0]['id']).replace('%(ext)s', 'mp4')
            a_file = a_opts['outtmpl'].replace('%(id)s', res[1]['id']).replace('%(ext)s', 'mp3')

            # إرسال الملفات
            with open(v_file, 'rb') as vf, open(a_file, 'rb') as af:
                await update.message.reply_video(vf, caption="🎬 فيديو دقة كاملة")
                await update.message.reply_audio(af, caption="🎵 صوت عالي النقاوة 320kbps")
            
            # تنظيف السيرفر
            os.remove(v_file)
            os.remove(a_file)
            
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ خطأ: الرابط محمي أو السيرفر محظور.\n{str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 البوت شغال بنظام تخطي الحظر...")
    app.run_polling()

if __name__ == '__main__':
    main()
