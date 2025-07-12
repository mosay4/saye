import sqlite3
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'cyberbot.db')
        self.create_tables()
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = self.get_connection()
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
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_lessons_completed INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                is_vip BOOLEAN DEFAULT FALSE,
                vip_expires TIMESTAMP,
                newsletter_subscribed BOOLEAN DEFAULT TRUE
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
                quiz_questions TEXT,
                is_premium BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول تقدم المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_id INTEGER,
                completed BOOLEAN DEFAULT FALSE,
                quiz_score INTEGER DEFAULT 0,
                completion_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        # جدول تاريخ النقاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                points INTEGER,
                reason TEXT,
                transaction_type TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الأخبار
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_ar TEXT NOT NULL,
                title_en TEXT NOT NULL,
                content_ar TEXT NOT NULL,
                content_en TEXT NOT NULL,
                summary_ar TEXT,
                summary_en TEXT,
                source_url TEXT,
                category TEXT,
                severity TEXT DEFAULT 'medium',
                published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # جدول منتجات المتجر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                description_ar TEXT,
                description_en TEXT,
                price_points INTEGER DEFAULT 0,
                price_usd REAL DEFAULT 0,
                category TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المشتريات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                item_id INTEGER,
                payment_method TEXT,
                amount_points INTEGER DEFAULT 0,
                amount_usd REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (item_id) REFERENCES shop_items (id)
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                referral_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points_awarded INTEGER DEFAULT 50,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول أنشطة المستخدمين (للتحليلات)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإشعارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'normal',
                scheduled_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent BOOLEAN DEFAULT FALSE,
                sent_at TIMESTAMP,
                failed BOOLEAN DEFAULT FALSE,
                error_message TEXT,
                is_broadcast BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول تفضيلات الإشعارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notification_preferences (
                user_id INTEGER PRIMARY KEY,
                notification_types TEXT,
                quiet_hours_start TIME,
                quiet_hours_end TIME,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول تقارير التحليلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT,
                period TEXT,
                data TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, user_id, username, first_name, last_name, language='ar'):
        """تسجيل مستخدم جديد"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # التحقق من وجود المستخدم
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            if cursor.fetchone():
                conn.close()
                return False
            
            # إنشاء رمز الإحالة
            import uuid
            referral_code = str(uuid.uuid4())[:8].upper()
            
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, language, referral_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, language, referral_code))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def get_user_info(self, user_id):
        """الحصول على معلومات المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def add_points(self, user_id, points, reason):
        """إضافة نقاط للمستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points, user_id))
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, points, reason, 'earned'))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            return False
    
    def spend_points(self, user_id, points, reason):
        """خصم نقاط من المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # التحقق من الرصيد
            cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
            current_points = cursor.fetchone()[0]
            
            if current_points < points:
                conn.close()
                return False, "نقاطك غير كافية"
            
            cursor.execute('UPDATE users SET points = points - ? WHERE user_id = ?', (points, user_id))
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, -points, reason, 'spent'))
            
            conn.commit()
            conn.close()
            return True, "تم خصم النقاط بنجاح"
        except Exception as e:
            logger.error(f"Error spending points: {e}")
            return False, "حدث خطأ"
    
    def update_user_language(self, user_id, language):
        """تحديث لغة المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating language: {e}")
            return False
    
    def get_newsletter_subscribers(self):
        """الحصول على المشتركين في النشرة الإخبارية"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE newsletter_subscribed = TRUE')
            subscribers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return subscribers
        except Exception as e:
            logger.error(f"Error getting newsletter subscribers: {e}")
            return []

# إنشاء مثيل من قاعدة البيانات
db = Database()

