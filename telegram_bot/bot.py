import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعداد قاعدة البيانات
def init_database():
    conn = sqlite3.connect('cyberbot.db')
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'ar',
            points INTEGER DEFAULT 0,
            level TEXT DEFAULT 'beginner',
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            is_vip BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # جدول الدروس
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_ar TEXT NOT NULL,
            title_en TEXT NOT NULL,
            content_ar TEXT NOT NULL,
            content_en TEXT NOT NULL,
            level TEXT NOT NULL,
            points_reward INTEGER DEFAULT 10,
            is_premium BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # جدول تقدم المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            lesson_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            completion_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # جدول النقاط
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS points_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            points INTEGER,
            reason TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# دالة للحصول على النصوص حسب اللغة
def get_text(user_id, key):
    conn = sqlite3.connect('cyberbot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    lang = result[0] if result else 'ar'
    
    texts = {
        'ar': {
            'welcome': '🔐 مرحباً بك في CyberBot AI!\n\nبوت تعليمي متقدم للأمن السيبراني مدعوم بالذكاء الاصطناعي.\n\nاختر ما تريد فعله:',
            'main_menu': '🏠 القائمة الرئيسية',
            'lessons': '📚 الدروس التعليمية',
            'news': '📰 الأخبار اليومية',
            'points': '⭐ النقاط والجوائز',
            'shop': '🛒 المتجر',
            'ai_chat': '🤖 الذكاء الاصطناعي',
            'settings': '⚙️ الإعدادات',
            'profile': '👤 الملف الشخصي',
            'language': '🌐 اللغة',
            'help': '❓ المساعدة',
            'points_balance': 'رصيد النقاط: {} نقطة',
            'level_status': 'المستوى: {}',
            'registration_success': '✅ تم تسجيلك بنجاح!\nحصلت على 10 نقاط كمكافأة ترحيب.',
            'choose_language': 'اختر لغتك المفضلة:',
            'language_changed': '✅ تم تغيير اللغة بنجاح!',
            'arabic': '🇸🇦 العربية',
            'english': '🇺🇸 English'
        },
        'en': {
            'welcome': '🔐 Welcome to CyberBot AI!\n\nAdvanced cybersecurity educational bot powered by AI.\n\nChoose what you want to do:',
            'main_menu': '🏠 Main Menu',
            'lessons': '📚 Educational Lessons',
            'news': '📰 Daily News',
            'points': '⭐ Points & Rewards',
            'shop': '🛒 Shop',
            'ai_chat': '🤖 AI Chat',
            'settings': '⚙️ Settings',
            'profile': '👤 Profile',
            'language': '🌐 Language',
            'help': '❓ Help',
            'points_balance': 'Points Balance: {} points',
            'level_status': 'Level: {}',
            'registration_success': '✅ Registration successful!\nYou received 10 points as welcome bonus.',
            'choose_language': 'Choose your preferred language:',
            'language_changed': '✅ Language changed successfully!',
            'arabic': '🇸🇦 العربية',
            'english': '🇺🇸 English'
        }
    }
    
    return texts.get(lang, texts['ar']).get(key, key)

# دالة لإنشاء القائمة الرئيسية
def create_main_menu(user_id):
    keyboard = [
        [
            InlineKeyboardButton(get_text(user_id, 'lessons'), callback_data='lessons'),
            InlineKeyboardButton(get_text(user_id, 'news'), callback_data='news')
        ],
        [
            InlineKeyboardButton(get_text(user_id, 'points'), callback_data='points'),
            InlineKeyboardButton(get_text(user_id, 'shop'), callback_data='shop')
        ],
        [
            InlineKeyboardButton(get_text(user_id, 'ai_chat'), callback_data='ai_chat'),
            InlineKeyboardButton(get_text(user_id, 'profile'), callback_data='profile')
        ],
        [
            InlineKeyboardButton(get_text(user_id, 'settings'), callback_data='settings'),
            InlineKeyboardButton(get_text(user_id, 'help'), callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# دالة لتسجيل المستخدم
def register_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('cyberbot.db')
    cursor = conn.cursor()
    
    # التحقق من وجود المستخدم
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if cursor.fetchone():
        conn.close()
        return False
    
    # إنشاء كود الإحالة
    referral_code = f"CB{user_id}"
    
    # إدراج المستخدم الجديد
    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, referral_code, points)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, referral_code, 10))
    
    # إضافة نقاط الترحيب
    cursor.execute('''
        INSERT INTO points_history (user_id, points, reason)
        VALUES (?, ?, ?)
    ''', (user_id, 10, 'Welcome bonus'))
    
    conn.commit()
    conn.close()
    return True

# دالة للحصول على معلومات المستخدم
def get_user_info(user_id):
    conn = sqlite3.connect('cyberbot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# معالج أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    # تسجيل المستخدم إذا لم يكن مسجلاً
    is_new = register_user(user_id, user.username, user.first_name, user.last_name)
    
    if is_new:
        welcome_text = get_text(user_id, 'registration_success') + '\n\n' + get_text(user_id, 'welcome')
    else:
        welcome_text = get_text(user_id, 'welcome')
    
    reply_markup = create_main_menu(user_id)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# معالج الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'main_menu':
        text = get_text(user_id, 'welcome')
        reply_markup = create_main_menu(user_id)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    elif data == 'profile':
        user_info = get_user_info(user_id)
        if user_info:
            points = user_info[5]
            level = user_info[6]
            text = f"👤 {get_text(user_id, 'profile')}\n\n"
            text += f"{get_text(user_id, 'points_balance').format(points)}\n"
            text += f"{get_text(user_id, 'level_status').format(level)}"
            
            keyboard = [[InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    elif data == 'settings':
        text = get_text(user_id, 'choose_language')
        keyboard = [
            [
                InlineKeyboardButton(get_text(user_id, 'arabic'), callback_data='lang_ar'),
                InlineKeyboardButton(get_text(user_id, 'english'), callback_data='lang_en')
            ],
            [InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    elif data.startswith('lang_'):
        lang = data.split('_')[1]
        conn = sqlite3.connect('cyberbot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
        conn.commit()
        conn.close()
        
        text = get_text(user_id, 'language_changed')
        keyboard = [[InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    elif data in ['lessons', 'news', 'points', 'shop', 'ai_chat', 'help']:
        text = f"🚧 {get_text(user_id, data)} - قيد التطوير\n\nسيتم إضافة هذه الميزة قريباً!"
        keyboard = [[InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)

# دالة رئيسية
def main():
    # إنشاء قاعدة البيانات
    init_database()
    
    # إنشاء التطبيق
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # تشغيل البوت
    print("🤖 CyberBot AI is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

