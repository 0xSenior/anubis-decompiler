# Discord Bot Configuration
import os

# استخدام المتغيرات البيئية أو القيم الافتراضية
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '1364595716227596349'))  # تأكد من تحويل القيمة إلى رقم
