import os
import logging
import schedule
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# استيراد الأنظمة المطورة
from database import db
from lessons import lesson_system
from points_system import points_system
from news_system import news_system
from ai_chat import ai_chat_system
from shop_system import shop_system

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CyberBotAI:
    def __init__(self):
        self.db = db
        self.lesson_system = lesson_system
        self.points_system = points_system
        self.news_system = news_system
        self.ai_chat_system = ai_chat_system
        self.shop_system = shop_system
        
        # إعداد البوت
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        # إعداد المهام المجدولة
        self.setup_scheduled_tasks()
    
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'welcome': '🤖 مرحباً بك في CyberBot AI!\n\nبوتك التعليمي الذكي للأمن السيبراني',
                'main_menu': '🏠 القائمة الرئيسية',
                'lessons': '📚 الدروس التعليمية',
                'news': '📰 الأخبار الأمنية',
                'ai_chat': '🤖 الذكاء الاصطناعي',
                'shop': '🛒 المتجر',
                'profile': '👤 ملفي الشخصي',
                'settings': '⚙️ الإعدادات',
                'help': '❓ المساعدة',
                'points': 'نقاطك: {} نقطة',
                'level': 'مستواك: {}',
                'vip_status': '👑 عضو VIP',
                'regular_status': '👤 عضو عادي',
                'choose_option': 'اختر من القائمة أدناه:',
                'language_changed': '✅ تم تغيير اللغة بنجاح',
                'error_occurred': '❌ حدث خطأ، حاول مرة أخرى'
            },
            'en': {
                'welcome': '🤖 Welcome to CyberBot AI!\n\nYour smart educational bot for cybersecurity',
                'main_menu': '🏠 Main Menu',
                'lessons': '📚 Educational Lessons',
                'news': '📰 Security News',
                'ai_chat': '🤖 AI Chat',
                'shop': '🛒 Shop',
                'profile': '👤 My Profile',
                'settings': '⚙️ Settings',
                'help': '❓ Help',
                'points': 'Your points: {} points',
                'level': 'Your level: {}',
                'vip_status': '👑 VIP Member',
                'regular_status': '👤 Regular Member',
                'choose_option': 'Choose from the menu below:',
                'language_changed': '✅ Language changed successfully',
                'error_occurred': '❌ An error occurred, please try again'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def create_main_menu(self, user_id):
        """إنشاء القائمة الرئيسية"""
        user_info = self.db.get_user_info(user_id)
        points = user_info[5] if user_info else 0
        level = user_info[6] if user_info else 'beginner'
        is_vip = user_info[11] if len(user_info) > 11 else False
        
        # ترجمة المستوى
        level_text = {
            'beginner': 'مبتدئ' if user_info[4] == 'ar' else 'Beginner',
            'intermediate': 'متوسط' if user_info[4] == 'ar' else 'Intermediate',
            'advanced': 'متقدم' if user_info[4] == 'ar' else 'Advanced'
        }.get(level, level)
        
        text = f"{self.get_text(user_id, 'welcome')}\n\n"
        text += f"📊 {self.get_text(user_id, 'points').format(points)}\n"
        text += f"🎯 {self.get_text(user_id, 'level').format(level_text)}\n"
        text += f"💎 {self.get_text(user_id, 'vip_status') if is_vip else self.get_text(user_id, 'regular_status')}\n\n"
        text += f"{self.get_text(user_id, 'choose_option')}"
        
        keyboard = [
            [
                InlineKeyboardButton(self.get_text(user_id, 'lessons'), callback_data='lessons'),
                InlineKeyboardButton(self.get_text(user_id, 'news'), callback_data='news')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'ai_chat'), callback_data='ai_chat'),
                InlineKeyboardButton(self.get_text(user_id, 'shop'), callback_data='shop')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'profile'), callback_data='profile'),
                InlineKeyboardButton(self.get_text(user_id, 'settings'), callback_data='settings')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'help'), callback_data='help')
            ]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        user_id = user.id
        
        # تسجيل المستخدم في قاعدة البيانات
        self.db.register_user(
            user_id=user_id,
            username=user.username or '',
            first_name=user.first_name or '',
            last_name=user.last_name or '',
            language='ar'  # افتراضي
        )
        
        # إنشاء القائمة الرئيسية
        text, keyboard = self.create_main_menu(user_id)
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        try:
            if data == 'main_menu':
                text, keyboard = self.create_main_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'lessons':
                text, keyboard = self.lesson_system.create_lessons_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('lesson_'):
                lesson_id = int(data.split('_')[1])
                text, keyboard = self.lesson_system.create_lesson_details(user_id, lesson_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('quiz_'):
                lesson_id = int(data.split('_')[1])
                text, keyboard = self.lesson_system.start_quiz(user_id, lesson_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('answer_'):
                parts = data.split('_')
                lesson_id = int(parts[1])
                question_index = int(parts[2])
                answer_index = int(parts[3])
                
                result = self.lesson_system.submit_quiz_answer(user_id, lesson_id, question_index, answer_index)
                
                if result['completed']:
                    # إضافة النقاط
                    self.db.add_points(user_id, result['points'], f"Completed lesson {lesson_id}")
                    
                    text = f"🎉 تهانينا! لقد أكملت الدرس بنجاح!\n\n"
                    text += f"📊 النتيجة: {result['score']}/{result['total']}\n"
                    text += f"⭐ النقاط المكتسبة: {result['points']}\n\n"
                    
                    keyboard = [[InlineKeyboardButton("🔙 العودة للدروس", callback_data='lessons')]]
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    # السؤال التالي
                    text, keyboard = self.lesson_system.get_next_question(user_id, lesson_id, question_index + 1)
                    await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'news':
                text, keyboard = self.news_system.create_news_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('news_'):
                if data == 'news_latest':
                    text, keyboard = self.news_system.show_latest_news(user_id)
                elif data == 'news_critical':
                    text, keyboard = self.news_system.show_critical_news(user_id)
                elif data == 'news_categories':
                    text, keyboard = self.news_system.show_categories(user_id)
                else:
                    news_id = int(data.split('_')[1])
                    text, keyboard = self.news_system.show_news_details(user_id, news_id)
                
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'ai_chat':
                text, keyboard = self.ai_chat_system.create_ai_chat_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('ai_'):
                if data == 'ai_clear':
                    self.ai_chat_system.clear_conversation(user_id)
                    text = self.ai_chat_system.get_text(user_id, 'chat_cleared')
                    keyboard = self.ai_chat_system.create_ai_response_menu(user_id)
                    await query.edit_message_text(text, reply_markup=keyboard)
                elif data.startswith('ai_ask_'):
                    question_type = data.split('_')[2]
                    answer = self.ai_chat_system.get_predefined_answer(user_id, question_type)
                    keyboard = self.ai_chat_system.create_ai_response_menu(user_id)
                    await query.edit_message_text(answer, reply_markup=keyboard)
            
            elif data == 'shop':
                text, keyboard = self.shop_system.create_shop_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('shop_'):
                if data.startswith('shop_category_'):
                    category = data.split('_')[2]
                    text, keyboard = self.shop_system.create_category_menu(user_id, category)
                elif data.startswith('shop_item_'):
                    item_id = int(data.split('_')[2])
                    text, keyboard = self.shop_system.create_item_details_menu(user_id, item_id)
                elif data.startswith('shop_buy_'):
                    parts = data.split('_')
                    payment_method = parts[2]
                    item_id = int(parts[3])
                    text, keyboard = self.shop_system.create_purchase_confirmation(user_id, item_id, payment_method)
                elif data.startswith('shop_confirm_'):
                    parts = data.split('_')
                    payment_method = parts[2]
                    item_id = int(parts[3])
                    
                    if payment_method == 'points':
                        success, message = self.shop_system.process_points_purchase(user_id, item_id)
                        text = f"✅ {message}" if success else f"❌ {message}"
                        keyboard = [[InlineKeyboardButton("🔙 العودة للمتجر", callback_data='shop')]]
                    else:  # card payment
                        payment_url = self.shop_system.create_stripe_payment_link(user_id, item_id)
                        if payment_url:
                            text = f"💳 {self.shop_system.get_text(user_id, 'payment_link')}\n\n{payment_url}"
                        else:
                            text = "❌ فشل في إنشاء رابط الدفع"
                        keyboard = [[InlineKeyboardButton("🔙 العودة للمتجر", callback_data='shop')]]
                elif data == 'shop_purchases':
                    text, keyboard = self.shop_system.create_purchases_menu(user_id)
                
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'profile':
                text, keyboard = self.points_system.create_profile_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'settings':
                text, keyboard = self.create_settings_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data.startswith('lang_'):
                lang = data.split('_')[1]
                self.db.update_user_language(user_id, lang)
                text = self.get_text(user_id, 'language_changed')
                text, keyboard = self.create_main_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
            
            elif data == 'help':
                text, keyboard = self.create_help_menu(user_id)
                await query.edit_message_text(text, reply_markup=keyboard)
        
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            await query.edit_message_text(
                self.get_text(user_id, 'error_occurred'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')
                ]])
            )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # التحقق من حالة المحادثة مع الذكاء الاصطناعي
        if user_id in context.user_data and context.user_data[user_id].get('ai_chat_mode'):
            # إرسال السؤال للذكاء الاصطناعي
            thinking_msg = await update.message.reply_text(
                self.ai_chat_system.get_text(user_id, 'thinking')
            )
            
            answer = self.ai_chat_system.ask_ai(user_id, message_text)
            keyboard = self.ai_chat_system.create_ai_response_menu(user_id)
            
            await thinking_msg.edit_text(answer, reply_markup=keyboard)
        else:
            # عرض القائمة الرئيسية
            text, keyboard = self.create_main_menu(user_id)
            await update.message.reply_text(text, reply_markup=keyboard)
    
    def create_settings_menu(self, user_id):
        """إنشاء قائمة الإعدادات"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        text = "⚙️ الإعدادات\n\n" if lang == 'ar' else "⚙️ Settings\n\n"
        text += f"🌐 اللغة الحالية: {'العربية' if lang == 'ar' else 'English'}\n\n"
        text += "اختر الإعداد الذي تريد تغييره:" if lang == 'ar' else "Choose the setting you want to change:"
        
        keyboard = [
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar'),
                InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
            ],
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def create_help_menu(self, user_id):
        """إنشاء قائمة المساعدة"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        if lang == 'ar':
            text = """❓ المساعدة والدعم

🤖 **حول CyberBot AI:**
بوت تعليمي ذكي متخصص في الأمن السيبراني

📚 **الميزات الرئيسية:**
• دروس تفاعلية في الأمن السيبراني
• نشرة إخبارية يومية ذكية
• محادثة مع الذكاء الاصطناعي
• نظام نقاط ومكافآت
• متجر إلكتروني للمحتوى المميز

🎯 **كيفية الاستخدام:**
1. ابدأ بالدروس التعليمية لكسب النقاط
2. تابع الأخبار الأمنية اليومية
3. اسأل الذكاء الاصطناعي عن أي استفسار
4. استخدم النقاط للشراء من المتجر

💎 **اشتراك VIP:**
• استخدام الذكاء الاصطناعي بلا حدود
• دروس حصرية متقدمة
• أولوية في الدعم الفني

📞 **التواصل:**
للدعم الفني: @support_cyberbot"""
        else:
            text = """❓ Help & Support

🤖 **About CyberBot AI:**
Smart educational bot specialized in cybersecurity

📚 **Main Features:**
• Interactive cybersecurity lessons
• Smart daily newsletter
• AI chat conversations
• Points and rewards system
• E-commerce store for premium content

🎯 **How to Use:**
1. Start with educational lessons to earn points
2. Follow daily security news
3. Ask AI about any questions
4. Use points to purchase from store

💎 **VIP Subscription:**
• Unlimited AI usage
• Exclusive advanced lessons
• Priority technical support

📞 **Contact:**
Technical support: @support_cyberbot"""
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def setup_handlers(self):
        """إعداد معالجات البوت"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    def setup_scheduled_tasks(self):
        """إعداد المهام المجدولة"""
        # النشرة اليومية في الساعة 8 مساءً
        schedule.every().day.at("20:00").do(self.send_daily_newsletter)
        
        # نسخ احتياطي يومي في الساعة 2 صباحاً
        schedule.every().day.at("02:00").do(self.backup_database)
        
        # تشغيل المجدول في thread منفصل
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def send_daily_newsletter(self):
        """إرسال النشرة اليومية"""
        try:
            logger.info("Starting daily newsletter...")
            
            # جمع الأخبار وإنشاء النشرة
            newsletter = self.news_system.generate_daily_newsletter()
            
            if newsletter:
                # الحصول على جميع المستخدمين المشتركين
                subscribers = self.db.get_newsletter_subscribers()
                
                for user_id in subscribers:
                    try:
                        # إرسال النشرة للمستخدم
                        self.application.bot.send_message(
                            chat_id=user_id,
                            text=newsletter,
                            parse_mode='Markdown'
                        )
                        time.sleep(0.1)  # تجنب حدود التيليجرام
                    except Exception as e:
                        logger.error(f"Failed to send newsletter to {user_id}: {e}")
                
                logger.info(f"Newsletter sent to {len(subscribers)} subscribers")
            
        except Exception as e:
            logger.error(f"Error in daily newsletter: {e}")
    
    def backup_database(self):
        """نسخ احتياطي لقاعدة البيانات"""
        try:
            logger.info("Starting database backup...")
            
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(os.path.dirname(__file__), 'backups', backup_filename)
            
            # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # نسخ قاعدة البيانات
            import shutil
            shutil.copy2(self.db.db_path, backup_path)
            
            logger.info(f"Database backup created: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error in database backup: {e}")
    
    def run(self):
        """تشغيل البوت"""
        logger.info("Starting CyberBot AI...")
        
        # إنشاء الجداول وإعداد البيانات الافتراضية
        self.db.create_tables()
        self.lesson_system.init_default_lessons()
        self.shop_system.init_shop_items()
        
        # تشغيل البوت
        self.application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        bot = CyberBotAI()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

