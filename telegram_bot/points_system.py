from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db
from datetime import datetime, timedelta

class PointsSystem:
    def __init__(self):
        self.db = db
    
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'points_menu': '⭐ النقاط والجوائز',
                'current_points': 'نقاطك الحالية: {} نقطة',
                'points_history': '📊 تاريخ النقاط',
                'referral_system': '👥 نظام الإحالة',
                'achievements': '🏆 الإنجازات',
                'leaderboard': '🥇 لوحة المتصدرين',
                'your_referral_code': 'كود الإحالة الخاص بك:',
                'referral_instructions': 'شارك هذا الكود مع أصدقائك واحصل على 50 نقطة لكل صديق يسجل!',
                'total_referrals': 'إجمالي الإحالات: {}',
                'referral_earnings': 'النقاط من الإحالات: {}',
                'recent_transactions': 'المعاملات الأخيرة:',
                'no_transactions': 'لا توجد معاملات حتى الآن',
                'earned': 'مكتسب',
                'spent': 'مصروف',
                'main_menu': '🏠 القائمة الرئيسية',
                'back': '🔙 رجوع',
                'achievement_unlocked': '🎉 تم فتح إنجاز جديد!',
                'first_lesson': '📚 أول درس',
                'first_lesson_desc': 'أكمل درسك الأول',
                'five_lessons': '📚 خمسة دروس',
                'five_lessons_desc': 'أكمل 5 دروس',
                'first_referral': '👥 أول إحالة',
                'first_referral_desc': 'احصل على أول إحالة',
                'points_collector': '💰 جامع النقاط',
                'points_collector_desc': 'اجمع 100 نقطة',
                'week_streak': '🔥 أسبوع متواصل',
                'week_streak_desc': 'ادخل لمدة 7 أيام متتالية'
            },
            'en': {
                'points_menu': '⭐ Points & Rewards',
                'current_points': 'Your current points: {} points',
                'points_history': '📊 Points History',
                'referral_system': '👥 Referral System',
                'achievements': '🏆 Achievements',
                'leaderboard': '🥇 Leaderboard',
                'your_referral_code': 'Your referral code:',
                'referral_instructions': 'Share this code with friends and get 50 points for each friend who registers!',
                'total_referrals': 'Total referrals: {}',
                'referral_earnings': 'Points from referrals: {}',
                'recent_transactions': 'Recent transactions:',
                'no_transactions': 'No transactions yet',
                'earned': 'Earned',
                'spent': 'Spent',
                'main_menu': '🏠 Main Menu',
                'back': '🔙 Back',
                'achievement_unlocked': '🎉 New achievement unlocked!',
                'first_lesson': '📚 First Lesson',
                'first_lesson_desc': 'Complete your first lesson',
                'five_lessons': '📚 Five Lessons',
                'five_lessons_desc': 'Complete 5 lessons',
                'first_referral': '👥 First Referral',
                'first_referral_desc': 'Get your first referral',
                'points_collector': '💰 Points Collector',
                'points_collector_desc': 'Collect 100 points',
                'week_streak': '🔥 Week Streak',
                'week_streak_desc': 'Login for 7 consecutive days'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def create_points_menu(self, user_id):
        """إنشاء قائمة النقاط والجوائز"""
        user_info = self.db.get_user_info(user_id)
        points = user_info[5] if user_info else 0
        
        text = f"{self.get_text(user_id, 'points_menu')}\n\n"
        text += f"{self.get_text(user_id, 'current_points').format(points)}"
        
        keyboard = [
            [
                InlineKeyboardButton(self.get_text(user_id, 'points_history'), callback_data='points_history'),
                InlineKeyboardButton(self.get_text(user_id, 'referral_system'), callback_data='referral_system')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'achievements'), callback_data='achievements'),
                InlineKeyboardButton(self.get_text(user_id, 'leaderboard'), callback_data='leaderboard')
            ],
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_points_history(self, user_id, limit=10):
        """الحصول على تاريخ النقاط"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT points, reason, transaction_type, date 
            FROM points_history 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT ?
        ''', (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        
        if not history:
            return self.get_text(user_id, 'no_transactions')
        
        text = f"{self.get_text(user_id, 'recent_transactions')}\n\n"
        
        for points, reason, transaction_type, date in history:
            emoji = "📈" if transaction_type == 'earned' else "📉"
            sign = "+" if transaction_type == 'earned' else "-"
            type_text = self.get_text(user_id, transaction_type)
            
            # تنسيق التاريخ
            date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
            
            text += f"{emoji} {sign}{abs(points)} - {reason}\n"
            text += f"   {type_text} | {formatted_date}\n\n"
        
        return text
    
    def create_points_history_menu(self, user_id):
        """إنشاء قائمة تاريخ النقاط"""
        text = self.get_points_history(user_id)
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back'), callback_data='points')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_referral_info(self, user_id):
        """الحصول على معلومات الإحالة"""
        user_info = self.db.get_user_info(user_id)
        referral_code = user_info[8] if user_info else None
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # عدد الإحالات
        cursor.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ?', (user_id,))
        total_referrals = cursor.fetchone()[0]
        
        # النقاط من الإحالات
        cursor.execute('SELECT SUM(points_awarded) FROM referrals WHERE referrer_id = ?', (user_id,))
        referral_points = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'referral_code': referral_code,
            'total_referrals': total_referrals,
            'referral_points': referral_points
        }
    
    def create_referral_menu(self, user_id):
        """إنشاء قائمة نظام الإحالة"""
        referral_info = self.get_referral_info(user_id)
        
        text = f"{self.get_text(user_id, 'referral_system')}\n\n"
        text += f"{self.get_text(user_id, 'your_referral_code')}\n"
        text += f"`{referral_info['referral_code']}`\n\n"
        text += f"{self.get_text(user_id, 'referral_instructions')}\n\n"
        text += f"{self.get_text(user_id, 'total_referrals').format(referral_info['total_referrals'])}\n"
        text += f"{self.get_text(user_id, 'referral_earnings').format(referral_info['referral_points'])}"
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back'), callback_data='points')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_achievements(self, user_id):
        """الحصول على الإنجازات"""
        user_info = self.db.get_user_info(user_id)
        total_lessons = user_info[10] if user_info else 0
        points = user_info[5] if user_info else 0
        
        referral_info = self.get_referral_info(user_id)
        total_referrals = referral_info['total_referrals']
        
        achievements = [
            {
                'id': 'first_lesson',
                'name': self.get_text(user_id, 'first_lesson'),
                'description': self.get_text(user_id, 'first_lesson_desc'),
                'unlocked': total_lessons >= 1,
                'emoji': '📚'
            },
            {
                'id': 'five_lessons',
                'name': self.get_text(user_id, 'five_lessons'),
                'description': self.get_text(user_id, 'five_lessons_desc'),
                'unlocked': total_lessons >= 5,
                'emoji': '📚'
            },
            {
                'id': 'first_referral',
                'name': self.get_text(user_id, 'first_referral'),
                'description': self.get_text(user_id, 'first_referral_desc'),
                'unlocked': total_referrals >= 1,
                'emoji': '👥'
            },
            {
                'id': 'points_collector',
                'name': self.get_text(user_id, 'points_collector'),
                'description': self.get_text(user_id, 'points_collector_desc'),
                'unlocked': points >= 100,
                'emoji': '💰'
            }
        ]
        
        return achievements
    
    def create_achievements_menu(self, user_id):
        """إنشاء قائمة الإنجازات"""
        achievements = self.get_achievements(user_id)
        
        text = f"{self.get_text(user_id, 'achievements')}\n\n"
        
        for achievement in achievements:
            status = "✅" if achievement['unlocked'] else "🔒"
            text += f"{status} {achievement['emoji']} {achievement['name']}\n"
            text += f"   {achievement['description']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back'), callback_data='points')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_leaderboard(self, user_id, limit=10):
        """الحصول على لوحة المتصدرين"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, first_name, points, total_lessons_completed
            FROM users 
            ORDER BY points DESC, total_lessons_completed DESC
            LIMIT ?
        ''', (limit,))
        leaderboard = cursor.fetchall()
        conn.close()
        
        return leaderboard
    
    def create_leaderboard_menu(self, user_id):
        """إنشاء قائمة لوحة المتصدرين"""
        leaderboard = self.get_leaderboard(user_id)
        
        text = f"{self.get_text(user_id, 'leaderboard')}\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (uid, name, points, lessons) in enumerate(leaderboard):
            rank = i + 1
            medal = medals[i] if i < 3 else f"{rank}."
            
            # إخفاء الأسماء الطويلة
            display_name = name[:15] + "..." if len(name) > 15 else name
            
            # تمييز المستخدم الحالي
            if uid == user_id:
                text += f"👤 {medal} {display_name} - {points} نقطة\n"
            else:
                text += f"{medal} {display_name} - {points} نقطة\n"
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back'), callback_data='points')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def check_new_achievements(self, user_id):
        """فحص الإنجازات الجديدة"""
        # هذه الدالة يمكن استخدامها لإشعار المستخدم بالإنجازات الجديدة
        # يمكن تطويرها لاحقاً لحفظ الإنجازات المفتوحة في قاعدة البيانات
        pass
    
    def process_referral(self, referral_code, new_user_id):
        """معالجة الإحالة"""
        referrer_id = self.db.get_user_by_referral_code(referral_code)
        
        if referrer_id and referrer_id != new_user_id:
            # تحديث المستخدم الجديد
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', 
                          (referrer_id, new_user_id))
            
            # إضافة سجل الإحالة
            cursor.execute('''
                INSERT INTO referrals (referrer_id, referred_id, points_awarded)
                VALUES (?, ?, ?)
            ''', (referrer_id, new_user_id, 50))
            
            # إضافة نقاط للمحيل
            cursor.execute('UPDATE users SET points = points + 50 WHERE user_id = ?', (referrer_id,))
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (referrer_id, 50, f'Referral bonus for user {new_user_id}', 'earned'))
            
            conn.commit()
            conn.close()
            
            return True
        
        return False

# إنشاء مثيل من نظام النقاط
points_system = PointsSystem()

