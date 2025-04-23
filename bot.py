import discord
from discord.ext import commands
import os
import subprocess
import logging
from config import BOT_TOKEN, CHANNEL_ID

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bot')

# إعداد البوت مع الصلاحيات المطلوبة
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# مسار ملف unluac.jar
UNLUAC_PATH = "unluac.jar"

@bot.event
async def on_ready():
    """يتم تنفيذ هذه الدالة عند تشغيل البوت"""
    logger.info(f'تم تشغيل البوت بنجاح: {bot.user}')
    logger.info(f'البوت يراقب الروم: {CHANNEL_ID}')
    
    # التحقق من وجود ملف unluac.jar
    if not os.path.exists(UNLUAC_PATH):
        logger.error(f'ملف {UNLUAC_PATH} غير موجود!')
    else:
        logger.info(f'تم العثور على ملف {UNLUAC_PATH}')

@bot.event
async def on_message(message):
    """التعامل مع الرسائل الواردة"""
    # تجاهل رسائل البوت نفسه
    if message.author.bot:
        return

    # التحقق من أن الرسالة في الروم المحدد
    if message.channel.id != CHANNEL_ID:
        return

    # التحقق من وجود ملفات مرفقة
    if message.attachments:
        logger.info(f'تم استلام رسالة من {message.author} تحتوي على {len(message.attachments)} ملفات')
        
        for attachment in message.attachments:
            logger.info(f'معالجة الملف: {attachment.filename}')
            
            if attachment.filename.endswith('.luac') or attachment.filename.endswith('.lua'):
                # إرسال رسالة تأكيد
                status_message = await message.channel.send(f'⏳ جاري معالجة الملف: {attachment.filename}')
                
                try:
                    # تحميل الملف
                    await attachment.save(attachment.filename)
                    
                    # تحضير اسم الملف الناتج
                    output_file = 'Anubis.lua'
                    
                    # تنفيذ عملية فك التشفير
                    logger.info('تشغيل unluac...')
                    process = subprocess.run(
                        ['java', '-jar', UNLUAC_PATH, attachment.filename],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if process.returncode == 0:
                        # إضافة رسالة في بداية الملف
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write('-- Decompiled by Anubis Group\n')
                            f.write(process.stdout)
                    
                    # التحقق من نجاح العملية
                    if process.returncode == 0:
                        logger.info('تم فك التشفير بنجاح')
                        # إرسال الملف المفكك كرد على الرسالة الأصلية
                        await message.reply(
                            '✅ تم فك تشفير الملف بنجاح:',
                            file=discord.File(output_file)
                        )
                    else:
                        error = process.stderr.strip()
                        logger.error(f'خطأ في فك التشفير: {error}')
                        # إرسال رسالة خطأ في الروم
                        await message.reply(f'❌ حدث خطأ أثناء فك التشفير:\n```\n{error}\n```')
                    
                except Exception as e:
                    # إرسال رسالة خطأ مؤقتة لصاحب الرسالة فقط
                    error_msg = await message.reply(
                        f'حدث خطأ: {str(e)}',
                        ephemeral=True
                    )
                    # إضافة زر لحذف رسالة الخطأ
                    await error_msg.add_reaction('❌')
                
                finally:
                    # تنظيف الملفات المؤقتة
                    try:
                        if os.path.exists(attachment.filename):
                            os.remove(attachment.filename)
                            logger.info(f'تم حذف الملف المؤقت: {attachment.filename}')
                        if 'output_file' in locals() and os.path.exists(output_file):
                            os.remove(output_file)
                            logger.info(f'تم حذف الملف المؤقت: {output_file}')
                        # حذف رسالة الحالة
                        await status_message.delete()
                    except Exception as e:
                        logger.error(f'خطأ في حذف الملفات المؤقتة: {e}')

@bot.event
async def on_reaction_add(reaction, user):
    """التعامل مع الردود على الرسائل"""
    # تجاهل ردود البوت
    if user.bot:
        return

    # إذا كان الرد هو ❌ وكان المستخدم هو صاحب الرسالة الأصلية
    if str(reaction.emoji) == '❌' and reaction.message.author == bot.user:
        if reaction.message.reference and reaction.message.reference.message_id:
            original_msg = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
            if original_msg.author == user:
                await reaction.message.delete()

# تشغيل البوت
if __name__ == '__main__':
    if not os.path.exists(UNLUAC_PATH):
        print(f'تحذير: ملف {UNLUAC_PATH} غير موجود!')
        print('يرجى تحميل الملف من: https://sourceforge.net/projects/unluac/')
    bot.run(BOT_TOKEN)
