# دليل التثبيت والإعداد - CyberBot AI

## 📋 المتطلبات الأساسية

### متطلبات النظام
- **نظام التشغيل**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **الذاكرة**: 4GB RAM كحد أدنى (8GB مُوصى به)
- **التخزين**: 2GB مساحة فارغة
- **الاتصال**: إنترنت مستقر

### البرامج المطلوبة

#### Python 3.11+
```bash
# التحقق من الإصدار
python --version
python3 --version

# تحميل Python (إذا لم يكن مثبتاً)
# Windows: https://python.org/downloads/
# macOS: brew install python@3.11
# Ubuntu: sudo apt update && sudo apt install python3.11
```

#### Node.js 18+
```bash
# التحقق من الإصدار
node --version
npm --version

# تحميل Node.js (إذا لم يكن مثبتاً)
# Windows/macOS: https://nodejs.org/
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
#         sudo apt-get install -y nodejs
```

#### Git
```bash
# التحقق من التثبيت
git --version

# تثبيت Git (إذا لم يكن مثبتاً)
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Ubuntu: sudo apt install git
```

---

## 🔑 الحصول على المفاتيح المطلوبة

### 1. مفتاح بوت التيليجرام

#### إنشاء البوت
1. افتح التيليجرام وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اختر اسماً للبوت (مثل: CyberBot AI)
4. اختر username للبوت (مثل: cyberbot_ai_bot)
5. احفظ الـ Token المُرسل

#### إعدادات البوت
```bash
# أرسل هذه الأوامر لـ BotFather
/setdescription - وصف البوت
/setabouttext - نبذة عن البوت
/setuserpic - صورة البوت
/setcommands - قائمة الأوامر
```

### 2. مفتاح OpenAI API

#### الحصول على المفتاح
1. انتقل إلى https://platform.openai.com/
2. سجل الدخول أو أنشئ حساباً جديداً
3. اذهب إلى API Keys
4. اضغط "Create new secret key"
5. احفظ المفتاح في مكان آمن

#### إعداد الفوترة
- أضف طريقة دفع في Billing
- ضع حد أقصى للإنفاق الشهري
- راقب الاستخدام بانتظام

### 3. مفتاح Stripe (اختياري)

#### للمدفوعات الإلكترونية
1. انتقل إلى https://stripe.com/
2. أنشئ حساباً جديداً
3. اذهب إلى Developers > API Keys
4. احفظ Secret Key و Publishable Key

---

## 📥 تحميل وإعداد المشروع

### 1. استنساخ المشروع
```bash
# استنساخ من GitHub
git clone https://github.com/your-username/cyberbot-ai.git
cd cyberbot-ai

# أو تحميل الملف المضغوط وفك الضغط
unzip cyberbot-ai.zip
cd cyberbot-ai
```

### 2. إعداد البيئة الافتراضية
```bash
# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# التحقق من التفعيل (يجب أن ترى (venv) في بداية السطر)
which python
```

### 3. تثبيت مكتبات Python
```bash
# الانتقال لمجلد البوت
cd telegram_bot

# تثبيت المكتبات
pip install --upgrade pip
pip install -r requirements.txt

# التحقق من التثبيت
pip list
```

### 4. إعداد ملف المتغيرات البيئية
```bash
# نسخ ملف المثال
cp .env.example .env

# تحرير الملف (استخدم محرر النصوص المفضل لديك)
nano .env
# أو
vim .env
# أو
code .env
```

#### محتوى ملف .env
```env
# مفتاح بوت التيليجرام (مطلوب)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# مفتاح OpenAI (مطلوب)
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz

# مفاتيح Stripe (اختياري)
STRIPE_SECRET_KEY=sk_test_abcdefghijklmnopqrstuvwxyz
STRIPE_PUBLISHABLE_KEY=pk_test_abcdefghijklmnopqrstuvwxyz

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///cyberbot.db

# إعدادات الأمان
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# إعدادات البوت
BOT_WEBHOOK_URL=https://your-domain.com/webhook
DEBUG=True
```

---

## 🖥️ إعداد لوحة التحكم

### 1. إعداد Backend (Flask)
```bash
# الانتقال لمجلد Backend
cd ../backend

# تثبيت المكتبات
pip install -r requirements.txt

# اختبار التشغيل
cd src
python admin_api.py
```

### 2. إعداد Frontend (React)
```bash
# الانتقال لمجلد Frontend
cd ../../frontend

# تثبيت المكتبات
npm install --legacy-peer-deps

# أو باستخدام yarn
yarn install

# اختبار التشغيل
npm run dev
```

---

## 🚀 تشغيل النظام

### 1. تشغيل البوت
```bash
# في terminal منفصل
cd telegram_bot
source ../venv/bin/activate  # تفعيل البيئة الافتراضية
python main_bot.py
```

### 2. تشغيل API الخلفي
```bash
# في terminal منفصل
cd backend/src
source ../../venv/bin/activate
python admin_api.py
```

### 3. تشغيل واجهة الإدارة
```bash
# في terminal منفصل
cd frontend
npm run dev
```

### 4. التحقق من التشغيل
- **البوت**: أرسل `/start` للبوت في التيليجرام
- **API**: افتح http://localhost:5000/health
- **واجهة الإدارة**: افتح http://localhost:3000

---

## 🔧 إعدادات متقدمة

### 1. إعداد Webhook (للإنتاج)
```bash
# تعيين webhook للبوت
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/webhook"}'
```

### 2. إعداد SSL (للإنتاج)
```bash
# باستخدام Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d your-domain.com
```

### 3. إعداد قاعدة بيانات خارجية
```python
# في ملف database.py
# استبدال SQLite بـ PostgreSQL
import psycopg2

DATABASE_URL = "postgresql://user:password@localhost:5432/cyberbot"
```

### 4. إعداد Redis للتخزين المؤقت
```bash
# تثبيت Redis
sudo apt install redis-server

# في Python
pip install redis
```

---

## 🐳 النشر باستخدام Docker

### 1. إنشاء Dockerfile للبوت
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY telegram_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_bot/ .

CMD ["python", "main_bot.py"]
```

### 2. إنشاء docker-compose.yml
```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    restart: unless-stopped
```

### 3. تشغيل Docker
```bash
# بناء وتشغيل الحاويات
docker-compose up -d

# مراقبة السجلات
docker-compose logs -f

# إيقاف الخدمات
docker-compose down
```

---

## 🔍 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في مفتاح التيليجرام
```
Error: Invalid token
```
**الحل**: تحقق من صحة TELEGRAM_BOT_TOKEN في ملف .env

#### 2. خطأ في مفتاح OpenAI
```
Error: Invalid API key
```
**الحل**: تحقق من صحة OPENAI_API_KEY وتأكد من وجود رصيد

#### 3. خطأ في قاعدة البيانات
```
Error: Database locked
```
**الحل**: تأكد من عدم تشغيل عدة نسخ من البوت

#### 4. خطأ في المنافذ
```
Error: Port already in use
```
**الحل**: غير المنفذ أو أوقف العملية المستخدمة للمنفذ

### سجلات الأخطاء
```bash
# عرض سجلات البوت
tail -f telegram_bot/logs/bot.log

# عرض سجلات API
tail -f backend/logs/api.log

# عرض سجلات النظام
journalctl -u cyberbot -f
```

---

## 📊 مراقبة الأداء

### 1. مراقبة استخدام الموارد
```bash
# استخدام الذاكرة والمعالج
htop
# أو
top

# مساحة القرص
df -h

# حالة الشبكة
netstat -tulpn
```

### 2. مراقبة قاعدة البيانات
```bash
# حجم قاعدة البيانات
ls -lh telegram_bot/cyberbot.db

# عدد المستخدمين
sqlite3 telegram_bot/cyberbot.db "SELECT COUNT(*) FROM users;"
```

### 3. مراقبة API
```bash
# اختبار صحة API
curl http://localhost:5000/health

# إحصائيات الاستخدام
curl http://localhost:5000/api/stats
```

---

## 🔄 التحديث والصيانة

### 1. تحديث المشروع
```bash
# سحب آخر التحديثات
git pull origin main

# تحديث مكتبات Python
pip install --upgrade -r requirements.txt

# تحديث مكتبات Node.js
npm update
```

### 2. النسخ الاحتياطية
```bash
# نسخ احتياطي لقاعدة البيانات
cp telegram_bot/cyberbot.db backups/cyberbot_$(date +%Y%m%d).db

# نسخ احتياطي للملفات
tar -czf backup_$(date +%Y%m%d).tar.gz cyberbot_ai/
```

### 3. إعادة التشغيل
```bash
# إعادة تشغيل البوت
pkill -f main_bot.py
python telegram_bot/main_bot.py &

# إعادة تشغيل الخدمات
sudo systemctl restart cyberbot
```

---

## 📞 الدعم الفني

### في حالة مواجهة مشاكل:

1. **تحقق من السجلات**: راجع ملفات السجلات للأخطاء
2. **راجع التوثيق**: تأكد من اتباع التعليمات بدقة
3. **ابحث في المشاكل المعروفة**: راجع GitHub Issues
4. **اطلب المساعدة**: تواصل معنا عبر:
   - البريد الإلكتروني: support@cyberbot.ai
   - التيليجرام: @cyberbot_support
   - GitHub Issues: https://github.com/your-repo/issues

---

## ✅ قائمة التحقق النهائية

- [ ] تثبيت Python 3.11+
- [ ] تثبيت Node.js 18+
- [ ] الحصول على مفتاح بوت التيليجرام
- [ ] الحصول على مفتاح OpenAI API
- [ ] استنساخ المشروع
- [ ] إعداد البيئة الافتراضية
- [ ] تثبيت مكتبات Python
- [ ] إعداد ملف .env
- [ ] تثبيت مكتبات Node.js
- [ ] اختبار تشغيل البوت
- [ ] اختبار تشغيل API
- [ ] اختبار تشغيل واجهة الإدارة
- [ ] إرسال رسالة اختبار للبوت
- [ ] الوصول للوحة التحكم

**تهانينا! 🎉 CyberBot AI جاهز للاستخدام**

