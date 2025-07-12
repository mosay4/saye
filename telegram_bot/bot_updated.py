import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from database import db
from lessons import lessons_manager
from points_system import points_system
from datetime import datetime

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دالة للحصول على النصوص حسب اللغة
def get_text(user_id, key):
    user_info = db.get_user_info(user_id)
    lang = user_info[4] if user_info else 'ar'
    
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
            'english': '🇺🇸 English',
            'under_development': '🚧 قيد التطوير\n\nسيتم إضافة هذه الميزة قريباً!'
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
            'english': '🇺🇸 English',
            'under_development': '🚧 Under Development\n\nThis feature will be added soon!'
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

# معالج أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    # معالجة كود الإحالة إذا وجد
    referral_code = None
    if context.args:
        referral_code = context.args[0]
    
    # تسجيل المستخدم إذا لم يكن مسجلاً
    referred_by = None
    if referral_code:
        referred_by = db.get_user_by_referral_code(referral_code)
    
    is_new, message = db.register_user(user_id, user.username, user.first_name, user.last_name, referred_by)
    
    if is_new:
        welcome_text = get_text(user_id, 'registration_success') + '\n\n' + get_text(user_id, 'welcome')
    else:
        welcome_text = get_text(user_id, 'welcome')
    
    reply_markup = create_main_menu(user_id)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# متغيرات لحفظ حالة الاختبار
user_quiz_state = {}

# معالج الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    try:
        if data == 'main_menu':
            text = get_text(user_id, 'welcome')
            reply_markup = create_main_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == 'profile':
            user_info = db.get_user_info(user_id)
            if user_info:
                points = user_info[5]
                level = user_info[6]
                lessons_completed = user_info[10] if len(user_info) > 10 else 0
                
                text = f"👤 {get_text(user_id, 'profile')}\n\n"
                text += f"{get_text(user_id, 'points_balance').format(points)}\n"
                text += f"{get_text(user_id, 'level_status').format(level)}\n"
                text += f"📚 الدروس المكتملة: {lessons_completed}"
                
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
            db.update_user_language(user_id, lang)
            
            text = get_text(user_id, 'language_changed')
            keyboard = [[InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # معالجة الدروس
        elif data == 'lessons':
            text = lessons_manager.get_text(user_id, 'choose_level')
            reply_markup = lessons_manager.create_levels_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data.startswith('level_'):
            level = data.split('_')[1]
            text = f"{lessons_manager.get_text(user_id, 'lessons_menu')} - {lessons_manager.get_text(user_id, level)}"
            reply_markup = lessons_manager.create_lessons_menu(user_id, level)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data.startswith('lesson_'):
            lesson_id = int(data.split('_')[1])
            lesson_content = lessons_manager.get_lesson_content(user_id, lesson_id)
            
            if lesson_content:
                text = f"📚 {lesson_content['title']}\n\n{lesson_content['content']}"
                await query.edit_message_text(text, reply_markup=lesson_content['keyboard'])
        
        elif data.startswith('quiz_'):
            lesson_id = int(data.split('_')[1])
            quiz_data = lessons_manager.create_quiz_question(user_id, lesson_id, 0)
            
            if quiz_data:
                # حفظ حالة الاختبار
                user_quiz_state[user_id] = {
                    'lesson_id': lesson_id,
                    'current_question': 0,
                    'score': 0,
                    'total_questions': quiz_data['total_questions']
                }
                
                await query.edit_message_text(quiz_data['text'], reply_markup=quiz_data['keyboard'])
        
        elif data.startswith('answer_'):
            parts = data.split('_')
            lesson_id = int(parts[1])
            question_index = int(parts[2])
            user_answer = parts[3]
            
            if user_id in user_quiz_state:
                quiz_state = user_quiz_state[user_id]
                
                # الحصول على السؤال الحالي للتحقق من الإجابة
                quiz_data = lessons_manager.create_quiz_question(user_id, lesson_id, question_index)
                
                if quiz_data:
                    is_correct = user_answer == quiz_data['correct_answer']
                    
                    if is_correct:
                        quiz_state['score'] += 1
                        feedback = lessons_manager.get_text(user_id, 'correct_answer')
                    else:
                        feedback = lessons_manager.get_text(user_id, 'wrong_answer')
                    
                    feedback += f"\n\n{quiz_data['explanation']}"
                    
                    # الانتقال للسؤال التالي أو إنهاء الاختبار
                    next_question = question_index + 1
                    
                    if next_question < quiz_state['total_questions']:
                        # السؤال التالي
                        quiz_state['current_question'] = next_question
                        next_quiz_data = lessons_manager.create_quiz_question(user_id, lesson_id, next_question)
                        
                        keyboard = [
                            [InlineKeyboardButton("➡️ السؤال التالي", callback_data=f"next_question_{lesson_id}_{next_question}")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(feedback, reply_markup=reply_markup)
                    else:
                        # إنهاء الاختبار
                        score = quiz_state['score']
                        total = quiz_state['total_questions']
                        
                        # إكمال الدرس ومنح النقاط
                        completed, points_earned = lessons_manager.complete_lesson(user_id, lesson_id, score)
                        
                        result_text = lessons_manager.get_text(user_id, 'quiz_completed').format(score, total, points_earned)
                        
                        keyboard = [
                            [InlineKeyboardButton(lessons_manager.get_text(user_id, 'back_to_lessons'), 
                                                callback_data='lessons')],
                            [InlineKeyboardButton(lessons_manager.get_text(user_id, 'main_menu'), 
                                                callback_data='main_menu')]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(result_text, reply_markup=reply_markup)
                        
                        # حذف حالة الاختبار
                        del user_quiz_state[user_id]
        
        elif data.startswith('next_question_'):
            parts = data.split('_')
            lesson_id = int(parts[2])
            question_index = int(parts[3])
            
            quiz_data = lessons_manager.create_quiz_question(user_id, lesson_id, question_index)
            if quiz_data:
                await query.edit_message_text(quiz_data['text'], reply_markup=quiz_data['keyboard'])
        
        # معالجة النقاط
        elif data == 'points':
            text, reply_markup = points_system.create_points_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == 'points_history':
            text, reply_markup = points_system.create_points_history_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == 'referral_system':
            text, reply_markup = points_system.create_referral_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
        elif data == 'achievements':
            text, reply_markup = points_system.create_achievements_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == 'leaderboard':
            text, reply_markup = points_system.create_leaderboard_menu(user_id)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # الميزات قيد التطوير
        elif data in ['news', 'shop', 'ai_chat', 'help']:
            text = get_text(user_id, 'under_development')
            keyboard = [[InlineKeyboardButton(get_text(user_id, 'main_menu'), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        # في حالة الخطأ، العودة للقائمة الرئيسية
        text = get_text(user_id, 'welcome')
        reply_markup = create_main_menu(user_id)
        await query.edit_message_text(text, reply_markup=reply_markup)

# دالة رئيسية
def main():
    # إنشاء قاعدة البيانات وإدراج البيانات التجريبية
    db.init_database()
    db.insert_sample_lessons()
    lessons_manager.create_sample_quizzes()
    
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

