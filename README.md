
# saye
=======
# CyberBot AI 🤖🔒

## نظام تعليمي ذكي شامل للأمن السيبراني

CyberBot AI هو بوت تيليجرام تعليمي متطور يجمع بين التعلم التفاعلي والذكاء الاصطناعي لتقديم تجربة تعليمية فريدة في مجال الأمن السيبراني.

---

## 🌟 الميزات الرئيسية

### 📚 النظام التعليمي التفاعلي
- **دروس منظمة حسب المستوى**: مبتدئ، متوسط، متقدم
- **اختبارات تفاعلية**: تقييم فوري مع نقاط مكافآت
- **تتبع التقدم**: مراقبة مستمرة لإنجازات المتعلم
- **شهادات إتمام**: شهادات رسمية للدورات المكتملة

### 🤖 الذكاء الاصطناعي المتقدم
- **محادثة ذكية**: إجابات فورية على استفسارات الأمن السيبراني
- **دعم متعدد اللغات**: العربية والإنجليزية
- **ذاكرة المحادثة**: تتبع السياق عبر المحادثات
- **أسئلة مقترحة**: توجيه المستخدمين للمواضيع المهمة

### 📰 النشرة الإخبارية الذكية
- **أخبار يومية**: تحديثات أمنية من مصادر موثوقة
- **تصنيف ذكي**: تنظيم الأخبار حسب الأهمية والفئة
- **تلخيص تلقائي**: ملخصات مفيدة باستخدام الذكاء الاصطناعي
- **تنبيهات حرجة**: إشعارات فورية للتهديدات الخطيرة

### 🛒 المتجر الإلكتروني المتكامل
- **نظام نقاط**: كسب واستخدام النقاط للمشتريات
- **اشتراكات VIP**: مميزات حصرية للأعضاء المميزين
- **دورات متقدمة**: محتوى تعليمي متخصص
- **دفع آمن**: دعم Stripe للمدفوعات الخارجية

### 📊 لوحة التحكم الإدارية
- **إدارة المستخدمين**: مراقبة وإدارة حسابات المستخدمين
- **إحصائيات شاملة**: تحليلات مفصلة للاستخدام والأداء
- **إدارة المحتوى**: تحكم كامل في الدروس والأخبار
- **نظام الإشعارات**: إرسال تنبيهات مخصصة

---

## 🏗️ البنية التقنية

### المكونات الأساسية

```
cyberbot_ai/
├── telegram_bot/          # بوت التيليجرام الرئيسي
│   ├── main_bot.py       # الملف الرئيسي للبوت
│   ├── database.py       # إدارة قاعدة البيانات
│   ├── lessons.py        # نظام الدروس التعليمية
│   ├── ai_chat.py        # نظام الذكاء الاصطناعي
│   ├── news_system.py    # نظام الأخبار
│   ├── shop_system.py    # نظام المتجر
│   ├── points_system.py  # نظام النقاط والإحالات
│   ├── analytics_system.py    # نظام التحليلات
│   └── notification_system.py # نظام الإشعارات
├── backend/              # API الخلفي للوحة التحكم
│   └── src/
│       ├── admin_api.py  # واجهة برمجة التطبيقات الإدارية
│       └── main.py       # خادم Flask الرئيسي
└── frontend/             # واجهة لوحة التحكم
    └── src/
        ├── App.jsx       # التطبيق الرئيسي
        ├── components/   # مكونات React
        └── ...
```

### التقنيات المستخدمة

#### Backend
- **Python 3.11+**: لغة البرمجة الأساسية
- **python-telegram-bot**: مكتبة بوت التيليجرام
- **SQLite**: قاعدة البيانات المحلية
- **Flask**: إطار عمل الويب للAPI
- **OpenAI GPT-4**: الذكاء الاصطناعي
- **Stripe**: معالجة المدفوعات

#### Frontend
- **React 18**: مكتبة واجهة المستخدم
- **Tailwind CSS**: إطار عمل التصميم
- **Shadcn/UI**: مكونات واجهة المستخدم
- **React Router**: التنقل بين الصفحات
- **Lucide Icons**: الأيقونات

---

## 🚀 التثبيت والإعداد

### المتطلبات الأساسية

```bash
# Python 3.11 أو أحدث
python --version

# Node.js 18 أو أحدث
node --version

# npm أو yarn
npm --version
```

### 1. إعداد البوت

```bash
# استنساخ المشروع
git clone <repository-url>
cd cyberbot_ai

# إعداد البيئة الافتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# تثبيت المتطلبات
cd telegram_bot
pip install -r requirements.txt
```

### 2. إعداد المتغيرات البيئية

```bash
# إنشاء ملف .env
cp .env.example .env

# تحرير الملف وإضافة المفاتيح المطلوبة
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### 3. إعداد لوحة التحكم

```bash
# تثبيت مكتبات Frontend
cd ../frontend
npm install --legacy-peer-deps

# تثبيت مكتبات Backend
cd ../backend
pip install -r requirements.txt
```

### 4. تشغيل النظام

```bash
# تشغيل البوت
cd telegram_bot
python main_bot.py

# تشغيل API الخلفي (في terminal منفصل)
cd backend/src
python admin_api.py

# تشغيل واجهة الإدارة (في terminal منفصل)
cd frontend
npm run dev
```

---

## 📖 دليل الاستخدام

### للمستخدمين

#### البدء مع البوت
1. ابحث عن البوت في التيليجرام: `@your_bot_username`
2. اضغط `/start` لبدء التفاعل
3. اختر لغتك المفضلة (العربية/الإنجليزية)
4. استكشف القائمة الرئيسية

#### كسب النقاط
- **إكمال الدروس**: 10-50 نقطة لكل درس
- **النجاح في الاختبارات**: نقاط إضافية حسب النتيجة
- **الإحالات**: 50 نقطة لكل صديق مدعو
- **النشاط اليومي**: نقاط مكافآت للاستخدام المنتظم

#### استخدام الذكاء الاصطناعي
- اختر "🤖 الذكاء الاصطناعي" من القائمة
- اطرح أسئلتك حول الأمن السيبراني
- استخدم الأسئلة المقترحة للبدء
- **ملاحظة**: المستخدمون العاديون لديهم حد يومي، أعضاء VIP لديهم استخدام غير محدود

### للمشرفين

#### الوصول للوحة التحكم
1. افتح المتصفح وانتقل إلى `http://localhost:3000`
2. سجل الدخول باستخدام:
   - **اسم المستخدم**: admin
   - **كلمة المرور**: admin123
3. استكشف الإحصائيات والإعدادات

#### إدارة المستخدمين
- عرض قائمة المستخدمين مع إمكانية البحث
- تعديل نقاط المستخدمين (إضافة/خصم)
- مراقبة نشاط المستخدمين وتقدمهم
- إدارة اشتراكات VIP

---

## 🔧 التطوير والتخصيص

### إضافة دروس جديدة

```python
# في ملف lessons.py
def add_new_lesson(self, title_ar, title_en, content_ar, content_en, level, quiz_questions):
    conn = self.db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lessons (title_ar, title_en, content_ar, content_en, level, quiz_questions)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title_ar, title_en, content_ar, content_en, level, json.dumps(quiz_questions)))
    
    conn.commit()
    conn.close()
```

### إضافة منتجات للمتجر

```python
# في ملف shop_system.py
def add_shop_item(self, name_ar, name_en, description_ar, description_en, 
                  price_points, price_usd, category):
    conn = self.db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO shop_items (name_ar, name_en, description_ar, description_en,
                              price_points, price_usd, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name_ar, name_en, description_ar, description_en, 
          price_points, price_usd, category))
    
    conn.commit()
    conn.close()
```

### تخصيص الذكاء الاصطناعي

```python
# في ملف ai_chat.py
def get_system_prompt(self, user_id):
    # تخصيص prompt النظام حسب احتياجاتك
    return """أنت خبير في الأمن السيبراني..."""
```

---

## 📊 قاعدة البيانات

### الجداول الرئيسية

#### جدول المستخدمين (users)
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT DEFAULT 'ar',
    points INTEGER DEFAULT 0,
    level TEXT DEFAULT 'beginner',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_vip BOOLEAN DEFAULT FALSE,
    vip_expires TIMESTAMP
);
```

#### جدول الدروس (lessons)
```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_ar TEXT NOT NULL,
    title_en TEXT NOT NULL,
    content_ar TEXT NOT NULL,
    content_en TEXT NOT NULL,
    level TEXT NOT NULL,
    points_reward INTEGER DEFAULT 10,
    quiz_questions TEXT
);
```

#### جدول النقاط (points_history)
```sql
CREATE TABLE points_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    points INTEGER,
    reason TEXT,
    transaction_type TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 الأمان والخصوصية

### حماية البيانات
- **تشفير كلمات المرور**: استخدام SHA-256
- **JWT Tokens**: للمصادقة الآمنة في لوحة التحكم
- **CORS Protection**: حماية من الطلبات غير المصرح بها
- **Rate Limiting**: منع إساءة الاستخدام

### النسخ الاحتياطية
- **نسخ تلقائية**: يومياً في الساعة 2:00 صباحاً
- **تشفير النسخ**: حماية ملفات النسخ الاحتياطية
- **استرداد سريع**: إمكانية الاستعادة في دقائق

---

## 📈 المراقبة والتحليلات

### الإحصائيات المتاحة
- **إحصائيات المستخدمين**: العدد الكلي، الجدد، النشطين
- **تحليلات التعلم**: معدلات الإكمال، الدروس الصعبة
- **إحصائيات الإيرادات**: المبيعات، الإيرادات اليومية
- **استخدام الذكاء الاصطناعي**: عدد الاستفسارات، المستخدمين النشطين

### التقارير التلقائية
- **تقارير أسبوعية**: ملخص شامل للأداء
- **تنبيهات الأداء**: إشعارات عند تجاوز حدود معينة
- **تحليل السلوك**: فهم أنماط استخدام المستخدمين

---

## 🚀 النشر والاستضافة

### خيارات النشر

#### 1. الخادم المحلي
```bash
# تشغيل جميع الخدمات محلياً
python main_bot.py &
python admin_api.py &
npm run dev
```

#### 2. الخدمات السحابية
- **Heroku**: للبوت والAPI
- **Vercel**: لواجهة الإدارة
- **Railway**: للنشر الشامل
- **DigitalOcean**: للخوادم المخصصة

#### 3. Docker (قريباً)
```dockerfile
# Dockerfile للبوت
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main_bot.py"]
```

---

## 🤝 المساهمة والدعم

### كيفية المساهمة
1. Fork المشروع
2. إنشاء branch جديد للميزة
3. Commit التغييرات
4. Push إلى Branch
5. إنشاء Pull Request

### الإبلاغ عن المشاكل
- استخدم GitHub Issues
- قدم وصفاً مفصلاً للمشكلة
- أرفق logs إذا أمكن
- حدد خطوات إعادة الإنتاج

### طلب الميزات
- اقترح ميزات جديدة عبر Issues
- اشرح الفائدة المتوقعة
- قدم أمثلة للاستخدام

---

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للتفاصيل.

---

## 📞 التواصل والدعم

- **البريد الإلكتروني**: support@cyberbot.ai
- **التيليجرام**: @cyberbot_support
- **الموقع الإلكتروني**: https://cyberbot.ai
- **التوثيق**: https://docs.cyberbot.ai

---

## 🙏 شكر وتقدير

نشكر جميع المساهمين والمطورين الذين ساعدوا في تطوير هذا المشروع:

- فريق OpenAI لتوفير GPT-4
- مجتمع Python Telegram Bot
- مطوري React و Tailwind CSS
- جميع المختبرين والمستخدمين الأوائل

---

## 🔄 سجل التحديثات

### الإصدار 1.0.0 (2024)
- ✅ إطلاق النسخة الأولى
- ✅ النظام التعليمي الكامل
- ✅ الذكاء الاصطناعي المتقدم
- ✅ المتجر الإلكتروني
- ✅ لوحة التحكم الإدارية
- ✅ نظام الإشعارات والتحليلات

### الميزات القادمة
- 🔄 تطبيق الهاتف المحمول
- 🔄 دعم المزيد من اللغات
- 🔄 تكامل مع منصات التعلم الأخرى
- 🔄 نظام الشهادات المتقدم
- 🔄 الواقع المعزز للتدريب

---

**CyberBot AI** - تعلم الأمن السيبراني بذكاء 🚀

 971f16f (Initial commit for CyberBot AI)
