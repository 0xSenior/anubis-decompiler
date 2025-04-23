# استخدم صورة أساسية تحتوي على Python
FROM python:3.12-slim

# تثبيت Java (OpenJDK)
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless && \
    apt-get clean;

# إعداد متغير البيئة لـ JAVA_HOME (اختياري)
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

# نسخ ملفات المشروع
WORKDIR /app
COPY . .

# تثبيت متطلبات البايثون
RUN pip install --no-cache-dir -r requirements.txt

# الأمر الذي يشغل البوت
CMD ["python", "bot.py"]
