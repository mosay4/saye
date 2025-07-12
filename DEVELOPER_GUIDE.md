# دليل المطور - CyberBot AI 🛠️

## مرحباً بك في فريق التطوير!

هذا الدليل مخصص للمطورين الذين يريدون المساهمة في تطوير CyberBot AI أو تخصيصه لاحتياجاتهم.

---

## 🏗️ هيكل المشروع

### نظرة عامة على البنية
```
cyberbot_ai/
├── telegram_bot/              # البوت الرئيسي
│   ├── main_bot.py           # نقطة الدخول الرئيسية
│   ├── database.py           # طبقة قاعدة البيانات
│   ├── lessons.py            # نظام الدروس التعليمية
│   ├── ai_chat.py            # نظام الذكاء الاصطناعي
│   ├── news_system.py        # نظام الأخبار
│   ├── shop_system.py        # نظام المتجر
│   ├── points_system.py      # نظام النقاط والإحالات
│   ├── analytics_system.py   # نظام التحليلات
│   ├── notification_system.py # نظام الإشعارات
│   ├── requirements.txt      # متطلبات Python
│   └── .env                  # متغيرات البيئة
├── backend/                  # API الخلفي
│   ├── src/
│   │   ├── main.py          # خادم Flask الرئيسي
│   │   └── admin_api.py     # واجهة برمجة التطبيقات الإدارية
│   └── requirements.txt     # متطلبات Backend
├── frontend/                 # واجهة الإدارة
│   ├── src/
│   │   ├── App.jsx          # التطبيق الرئيسي
│   │   ├── components/      # مكونات React
│   │   └── ...
│   ├── package.json         # متطلبات Node.js
│   └── ...
├── docs/                     # التوثيق
├── tests/                    # الاختبارات
└── scripts/                  # سكريبتات مساعدة
```

---

## 🔧 إعداد بيئة التطوير

### 1. متطلبات التطوير
```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Git
git --version

# محرر النصوص (VS Code مُوصى به)
code --version
```

### 2. استنساخ المشروع
```bash
git clone https://github.com/your-username/cyberbot-ai.git
cd cyberbot-ai

# إنشاء branch جديد للتطوير
git checkout -b feature/new-feature
```

### 3. إعداد البيئة الافتراضية
```bash
# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# تثبيت المكتبات
pip install -r telegram_bot/requirements.txt
pip install -r backend/requirements.txt

# تثبيت مكتبات التطوير الإضافية
pip install pytest black flake8 mypy
```

### 4. إعداد Frontend
```bash
cd frontend
npm install --legacy-peer-deps

# تثبيت أدوات التطوير
npm install -D eslint prettier
```

### 5. إعداد متغيرات البيئة للتطوير
```bash
# نسخ ملف المثال
cp telegram_bot/.env.example telegram_bot/.env

# تحرير الملف وإضافة قيم التطوير
TELEGRAM_BOT_TOKEN=your_test_bot_token
OPENAI_API_KEY=your_openai_key
DEBUG=True
DATABASE_URL=sqlite:///test_cyberbot.db
```

---

## 📊 قاعدة البيانات

### هيكل قاعدة البيانات

#### الجداول الرئيسية

##### جدول المستخدمين
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
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_lessons_completed INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    is_vip BOOLEAN DEFAULT FALSE,
    vip_expires TIMESTAMP,
    newsletter_subscribed BOOLEAN DEFAULT TRUE
);
```

##### جدول الدروس
```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_ar TEXT NOT NULL,
    title_en TEXT NOT NULL,
    content_ar TEXT NOT NULL,
    content_en TEXT NOT NULL,
    level TEXT NOT NULL,
    points_reward INTEGER DEFAULT 10,
    quiz_questions TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### إدارة قاعدة البيانات

#### إضافة جدول جديد
```python
# في ملف database.py
def create_new_table(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
```

#### إجراء Migration
```python
# إنشاء ملف migration جديد
# migrations/001_add_new_column.py

def upgrade():
    """إضافة عمود جديد"""
    conn = sqlite3.connect('cyberbot.db')
    cursor = conn.cursor()
    
    cursor.execute('ALTER TABLE users ADD COLUMN new_column TEXT')
    
    conn.commit()
    conn.close()

def downgrade():
    """التراجع عن التغيير"""
    # SQLite لا يدعم DROP COLUMN
    # يجب إعادة إنشاء الجدول
    pass
```

---

## 🤖 تطوير البوت

### إضافة أمر جديد

#### 1. إنشاء معالج الأمر
```python
# في ملف main_bot.py
async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر جديد"""
    user_id = update.effective_user.id
    
    # منطق الأمر هنا
    text = "هذا أمر جديد!"
    keyboard = [[InlineKeyboardButton("زر", callback_data='new_action')]]
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# إضافة المعالج في setup_handlers
def setup_handlers(self):
    self.application.add_handler(CommandHandler("new", self.new_command))
    # باقي المعالجات...
```

#### 2. إضافة معالج الأزرار
```python
# في button_callback
elif data == 'new_action':
    # منطق الزر الجديد
    text = "تم الضغط على الزر الجديد!"
    keyboard = [[InlineKeyboardButton("العودة", callback_data='main_menu')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
```

### إضافة نظام جديد

#### 1. إنشاء ملف النظام
```python
# إنشاء ملف new_system.py
import logging
from database import db

logger = logging.getLogger(__name__)

class NewSystem:
    def __init__(self):
        self.db = db
    
    def create_menu(self, user_id):
        """إنشاء قائمة النظام الجديد"""
        text = "مرحباً بك في النظام الجديد!"
        keyboard = [
            [InlineKeyboardButton("خيار 1", callback_data='new_option1')],
            [InlineKeyboardButton("خيار 2", callback_data='new_option2')],
            [InlineKeyboardButton("العودة", callback_data='main_menu')]
        ]
        return text, InlineKeyboardMarkup(keyboard)
    
    def process_option1(self, user_id):
        """معالجة الخيار الأول"""
        # منطق المعالجة
        return "تم تنفيذ الخيار الأول!"

# إنشاء مثيل من النظام
new_system = NewSystem()
```

#### 2. دمج النظام في البوت الرئيسي
```python
# في main_bot.py
from new_system import new_system

class CyberBotAI:
    def __init__(self):
        # الأنظمة الموجودة...
        self.new_system = new_system
    
    # في button_callback
    elif data == 'new_system':
        text, keyboard = self.new_system.create_menu(user_id)
        await query.edit_message_text(text, reply_markup=keyboard)
```

---

## 🎨 تطوير Frontend

### إضافة صفحة جديدة

#### 1. إنشاء مكون الصفحة
```jsx
// src/components/NewPage.jsx
import { useState, useEffect } from 'react';

const NewPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await fetch('/api/new-endpoint');
            const result = await response.json();
            setData(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>جاري التحميل...</div>;
    }

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">صفحة جديدة</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.map(item => (
                    <div key={item.id} className="bg-white p-4 rounded-lg shadow">
                        <h3 className="font-semibold">{item.title}</h3>
                        <p className="text-gray-600">{item.description}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NewPage;
```

#### 2. إضافة الصفحة للتوجيه
```jsx
// src/App.jsx
import NewPage from './components/NewPage';

// في مكون App
<Route path="/new-page" element={<NewPage />} />
```

#### 3. إضافة رابط في الشريط الجانبي
```jsx
// src/components/Sidebar.jsx
<Link 
    to="/new-page" 
    className={`flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 ${
        location.pathname === '/new-page' ? 'bg-blue-100 text-blue-700' : ''
    }`}
>
    <Icon className="w-5 h-5 mr-3" />
    صفحة جديدة
</Link>
```

### إضافة API endpoint جديد

#### 1. في Backend (Flask)
```python
# backend/src/admin_api.py
@app.route('/api/new-endpoint', methods=['GET'])
def get_new_data():
    try:
        # منطق جلب البيانات
        data = [
            {'id': 1, 'title': 'عنصر 1', 'description': 'وصف العنصر 1'},
            {'id': 2, 'title': 'عنصر 2', 'description': 'وصف العنصر 2'},
        ]
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/new-endpoint', methods=['POST'])
def create_new_item():
    try:
        data = request.get_json()
        
        # منطق إنشاء عنصر جديد
        new_item = {
            'id': generate_id(),
            'title': data.get('title'),
            'description': data.get('description')
        }
        
        # حفظ في قاعدة البيانات
        save_to_database(new_item)
        
        return jsonify({
            'success': True,
            'data': new_item
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## 🧪 الاختبارات

### إعداد بيئة الاختبار

#### 1. تثبيت مكتبات الاختبار
```bash
pip install pytest pytest-asyncio pytest-mock
```

#### 2. إنشاء ملف إعدادات الاختبار
```python
# tests/conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock
from telegram_bot.database import Database

@pytest.fixture
def mock_database():
    """قاعدة بيانات وهمية للاختبار"""
    db = Database()
    db.db_path = ':memory:'  # استخدام قاعدة بيانات في الذاكرة
    db.create_tables()
    return db

@pytest.fixture
def mock_bot():
    """بوت وهمي للاختبار"""
    return AsyncMock()

@pytest.fixture
def event_loop():
    """حلقة الأحداث للاختبارات غير المتزامنة"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### كتابة اختبارات الوحدة

#### 1. اختبار قاعدة البيانات
```python
# tests/test_database.py
import pytest
from telegram_bot.database import Database

def test_register_user(mock_database):
    """اختبار تسجيل مستخدم جديد"""
    user_id = 12345
    username = "test_user"
    
    # تسجيل المستخدم
    result = mock_database.register_user(
        user_id=user_id,
        username=username,
        first_name="Test",
        last_name="User",
        language="ar"
    )
    
    assert result == True
    
    # التحقق من وجود المستخدم
    user_info = mock_database.get_user_info(user_id)
    assert user_info is not None
    assert user_info[1] == username

def test_add_points(mock_database):
    """اختبار إضافة نقاط"""
    user_id = 12345
    
    # تسجيل المستخدم أولاً
    mock_database.register_user(user_id, "test", "Test", "User")
    
    # إضافة نقاط
    result = mock_database.add_points(user_id, 50, "Test points")
    assert result == True
    
    # التحقق من النقاط
    user_info = mock_database.get_user_info(user_id)
    assert user_info[5] == 50  # النقاط في العمود السادس
```

#### 2. اختبار البوت
```python
# tests/test_bot.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram_bot.main_bot import CyberBotAI

@pytest.mark.asyncio
async def test_start_command(mock_bot, mock_database):
    """اختبار أمر البداية"""
    # إعداد البوت
    bot = CyberBotAI()
    bot.db = mock_database
    
    # إعداد update وهمي
    update = AsyncMock()
    update.effective_user.id = 12345
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.message.reply_text = AsyncMock()
    
    context = AsyncMock()
    
    # تنفيذ الأمر
    await bot.start_command(update, context)
    
    # التحقق من استدعاء reply_text
    update.message.reply_text.assert_called_once()
    
    # التحقق من تسجيل المستخدم
    user_info = mock_database.get_user_info(12345)
    assert user_info is not None
```

### اختبارات التكامل

#### 1. اختبار API
```python
# tests/test_api.py
import pytest
import json
from backend.src.admin_api import app

@pytest.fixture
def client():
    """عميل اختبار Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """اختبار endpoint الصحة"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_get_users(client):
    """اختبار جلب المستخدمين"""
    response = client.get('/api/users')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'users' in data
    assert isinstance(data['users'], list)
```

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# تشغيل اختبارات محددة
pytest tests/test_database.py

# تشغيل مع تغطية الكود
pytest --cov=telegram_bot

# تشغيل مع تقرير مفصل
pytest -v --tb=short
```

---

## 📈 المراقبة والتسجيل

### إعداد نظام التسجيل

#### 1. إعداد Logger
```python
# telegram_bot/logger_config.py
import logging
import logging.handlers
import os

def setup_logger(name, log_file, level=logging.INFO):
    """إعداد logger مخصص"""
    
    # إنشاء مجلد السجلات
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # إعداد formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # إعداد file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # إعداد console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # إعداد logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# استخدام Logger
bot_logger = setup_logger('bot', 'logs/bot.log')
api_logger = setup_logger('api', 'logs/api.log')
```

#### 2. استخدام Logger في الكود
```python
# في أي ملف
import logging

logger = logging.getLogger('bot')

def some_function():
    try:
        logger.info("بدء تنفيذ الوظيفة")
        # منطق الوظيفة
        logger.info("انتهاء تنفيذ الوظيفة بنجاح")
    except Exception as e:
        logger.error(f"خطأ في تنفيذ الوظيفة: {e}")
        raise
```

### مراقبة الأداء

#### 1. إضافة مقاييس الأداء
```python
# telegram_bot/metrics.py
import time
import functools
from collections import defaultdict

class PerformanceMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def time_function(self, func_name):
        """decorator لقياس وقت تنفيذ الوظائف"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self.metrics[func_name].append(execution_time)
            return wrapper
        return decorator
    
    def get_average_time(self, func_name):
        """الحصول على متوسط وقت التنفيذ"""
        times = self.metrics[func_name]
        return sum(times) / len(times) if times else 0

# استخدام المقاييس
metrics = PerformanceMetrics()

@metrics.time_function('start_command')
async def start_command(self, update, context):
    # منطق الأمر
    pass
```

---

## 🚀 النشر والإنتاج

### إعداد متغيرات الإنتاج

#### 1. ملف .env للإنتاج
```env
# Production Environment Variables
TELEGRAM_BOT_TOKEN=your_production_bot_token
OPENAI_API_KEY=your_production_openai_key
STRIPE_SECRET_KEY=your_production_stripe_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cyberbot_prod

# Security
SECRET_KEY=your_very_secure_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=very_secure_password

# Performance
DEBUG=False
MAX_WORKERS=4
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

### Docker للإنتاج

#### 1. Dockerfile للبوت
```dockerfile
FROM python:3.11-slim

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ متطلبات Python
COPY telegram_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY telegram_bot/ .

# إنشاء مستخدم غير root
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# تشغيل البوت
CMD ["python", "main_bot.py"]
```

#### 2. docker-compose للإنتاج
```yaml
version: '3.8'

services:
  bot:
    build: 
      context: .
      dockerfile: Dockerfile.bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=cyberbot_prod
      - POSTGRES_USER=cyberbot
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

---

## 🔧 أدوات التطوير

### إعداد VS Code

#### 1. ملف settings.json
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/node_modules": true
    }
}
```

#### 2. ملف launch.json للتصحيح
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/telegram_bot/main_bot.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Debug API",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/src/admin_api.py",
            "console": "integratedTerminal"
        }
    ]
}
```

### أدوات الجودة

#### 1. إعداد Black للتنسيق
```bash
# تثبيت Black
pip install black

# تنسيق الملفات
black telegram_bot/
black backend/

# إعداد pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

#### 2. إعداد Flake8 للفحص
```bash
# تثبيت Flake8
pip install flake8

# إعداد .flake8
[flake8]
max-line-length = 88
exclude = venv,__pycache__,.git
ignore = E203,W503
```

#### 3. إعداد MyPy للتحقق من الأنواع
```bash
# تثبيت MyPy
pip install mypy

# إعداد mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

## 📚 أفضل الممارسات

### كتابة الكود

#### 1. تسمية المتغيرات والوظائف
```python
# جيد
def get_user_points(user_id: int) -> int:
    """الحصول على نقاط المستخدم"""
    pass

def calculate_lesson_reward(lesson_level: str, quiz_score: int) -> int:
    """حساب مكافأة الدرس"""
    pass

# سيء
def get_pts(uid):
    pass

def calc_reward(lvl, score):
    pass
```

#### 2. التعامل مع الأخطاء
```python
# جيد
async def send_message_safe(bot, chat_id: int, text: str):
    """إرسال رسالة مع معالجة الأخطاء"""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Message sent to {chat_id}")
    except TelegramError as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        # معالجة الخطأ حسب النوع
        if "blocked" in str(e).lower():
            # المستخدم حظر البوت
            mark_user_as_blocked(chat_id)
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        raise

# سيء
async def send_message(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)
```

#### 3. استخدام Type Hints
```python
from typing import List, Dict, Optional, Union
from datetime import datetime

def get_user_lessons(
    user_id: int, 
    level: Optional[str] = None
) -> List[Dict[str, Union[str, int]]]:
    """الحصول على دروس المستخدم"""
    pass

def update_user_activity(
    user_id: int, 
    activity_type: str, 
    timestamp: Optional[datetime] = None
) -> bool:
    """تحديث نشاط المستخدم"""
    pass
```

### الأمان

#### 1. التحقق من المدخلات
```python
def validate_user_input(text: str) -> bool:
    """التحقق من صحة مدخلات المستخدم"""
    if not text or len(text.strip()) == 0:
        return False
    
    if len(text) > 1000:  # حد أقصى للطول
        return False
    
    # منع الأكواد الخبيثة
    dangerous_patterns = ['<script>', 'javascript:', 'eval(']
    for pattern in dangerous_patterns:
        if pattern.lower() in text.lower():
            return False
    
    return True

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رسالة المستخدم"""
    message_text = update.message.text
    
    if not validate_user_input(message_text):
        await update.message.reply_text("رسالة غير صالحة")
        return
    
    # معالجة الرسالة...
```

#### 2. حماية API
```python
from functools import wraps
import jwt

def require_auth(f):
    """decorator للتحقق من المصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # إزالة "Bearer " من بداية التوكن
            token = token.replace('Bearer ', '')
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/api/admin/users')
@require_auth
def get_users():
    """جلب المستخدمين (يتطلب مصادقة)"""
    pass
```

### الأداء

#### 1. استخدام التخزين المؤقت
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    """decorator للتخزين المؤقت"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # البحث في التخزين المؤقت
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # تنفيذ الوظيفة وحفظ النتيجة
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key, 
                expiration, 
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)  # 10 دقائق
def get_user_statistics(user_id: int):
    """الحصول على إحصائيات المستخدم"""
    # استعلام قاعدة البيانات...
    pass
```

---

## 🤝 المساهمة في المشروع

### عملية المساهمة

#### 1. Fork المشروع
```bash
# Fork المشروع على GitHub
# ثم استنساخ النسخة المنسوخة
git clone https://github.com/your-username/cyberbot-ai.git
cd cyberbot-ai

# إضافة المستودع الأصلي كـ upstream
git remote add upstream https://github.com/original-username/cyberbot-ai.git
```

#### 2. إنشاء Branch جديد
```bash
# إنشاء branch للميزة الجديدة
git checkout -b feature/new-awesome-feature

# أو لإصلاح خطأ
git checkout -b bugfix/fix-important-bug
```

#### 3. تطوير الميزة
```bash
# إجراء التغييرات
# كتابة الاختبارات
# تشغيل الاختبارات
pytest

# فحص جودة الكود
black .
flake8 .
mypy .
```

#### 4. Commit التغييرات
```bash
# إضافة الملفات
git add .

# Commit مع رسالة واضحة
git commit -m "feat: add new lesson management system

- Add CRUD operations for lessons
- Implement lesson categorization
- Add unit tests for lesson system
- Update documentation"
```

#### 5. Push وإنشاء Pull Request
```bash
# Push للـ branch
git push origin feature/new-awesome-feature

# إنشاء Pull Request على GitHub
# مع وصف مفصل للتغييرات
```

### معايير المراجعة

#### 1. قائمة التحقق للكود
- [ ] الكود يتبع معايير التنسيق (Black, Flake8)
- [ ] جميع الوظائف لها Type Hints
- [ ] الكود موثق بشكل جيد
- [ ] الاختبارات تغطي الوظائف الجديدة
- [ ] لا توجد أخطاء أمنية واضحة
- [ ] الأداء مقبول

#### 2. قائمة التحقق للميزات
- [ ] الميزة تعمل كما هو متوقع
- [ ] واجهة المستخدم سهلة الاستخدام
- [ ] التوثيق محدث
- [ ] لا تكسر الميزات الموجودة
- [ ] متوافقة مع جميع المتصفحات المدعومة

---

## 📞 الدعم والمساعدة

### الحصول على المساعدة

#### 1. التوثيق
- راجع هذا الدليل أولاً
- اقرأ README.md
- راجع التعليقات في الكود

#### 2. المجتمع
- GitHub Discussions للأسئلة العامة
- GitHub Issues للأخطاء والميزات
- Discord/Telegram للدردشة المباشرة

#### 3. التواصل المباشر
- البريد الإلكتروني: dev@cyberbot.ai
- التيليجرام: @cyberbot_dev

### الإبلاغ عن الأخطاء

#### قالب تقرير الخطأ
```markdown
## وصف الخطأ
وصف واضح ومختصر للخطأ.

## خطوات إعادة الإنتاج
1. اذهب إلى '...'
2. اضغط على '....'
3. مرر إلى '....'
4. شاهد الخطأ

## السلوك المتوقع
وصف واضح لما كنت تتوقع حدوثه.

## لقطات الشاشة
إذا أمكن، أضف لقطات شاشة لتوضيح المشكلة.

## معلومات البيئة
- نظام التشغيل: [مثل iOS]
- المتصفح: [مثل chrome, safari]
- إصدار Python: [مثل 3.11.0]
- إصدار البوت: [مثل 1.0.0]

## معلومات إضافية
أي معلومات أخرى حول المشكلة.
```

---

**مرحباً بك في فريق تطوير CyberBot AI! 🚀**

نتطلع لمساهماتك في جعل التعلم الأمني أكثر متعة وفعالية.

