import sqlite3
from datetime import datetime
import random
import string

class DatabaseManager:
    def __init__(self, db_path='cyberbot.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
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
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                is_vip BOOLEAN DEFAULT FALSE,
                total_lessons_completed INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_activity_date DATE
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
                level TEXT NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
                points_reward INTEGER DEFAULT 10,
                is_premium BOOLEAN DEFAULT FALSE,
                category TEXT,
                duration_minutes INTEGER DEFAULT 15,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الاختبارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                question_ar TEXT NOT NULL,
                question_en TEXT NOT NULL,
                option_a_ar TEXT NOT NULL,
                option_a_en TEXT NOT NULL,
                option_b_ar TEXT NOT NULL,
                option_b_en TEXT NOT NULL,
                option_c_ar TEXT NOT NULL,
                option_c_en TEXT NOT NULL,
                option_d_ar TEXT NOT NULL,
                option_d_en TEXT NOT NULL,
                correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
                explanation_ar TEXT,
                explanation_en TEXT,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
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
                time_spent_minutes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                UNIQUE(user_id, lesson_id)
            )
        ''')
        
        # جدول تاريخ النقاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                points INTEGER,
                reason TEXT,
                transaction_type TEXT CHECK (transaction_type IN ('earned', 'spent')),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
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
        
        # جدول الأخبار
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_ar TEXT NOT NULL,
                title_en TEXT NOT NULL,
                content_ar TEXT NOT NULL,
                content_en TEXT NOT NULL,
                source_url TEXT,
                category TEXT,
                severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # جدول المتجر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                description_ar TEXT,
                description_en TEXT,
                price_points INTEGER NOT NULL,
                price_usd REAL,
                category TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                stock_quantity INTEGER DEFAULT -1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المشتريات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id INTEGER,
                payment_method TEXT,
                amount_points INTEGER,
                amount_usd REAL,
                status TEXT DEFAULT 'pending',
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (item_id) REFERENCES shop_items (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, user_id, username, first_name, last_name, referred_by=None):
        """تسجيل مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود المستخدم
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            conn.close()
            return False, "User already exists"
        
        # إنشاء كود الإحالة
        referral_code = f"CB{user_id}"
        
        # نقاط الترحيب
        welcome_points = 10
        if referred_by:
            welcome_points += 20  # مكافأة إضافية للإحالة
        
        try:
            # إدراج المستخدم الجديد
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, referral_code, points, referred_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, referral_code, welcome_points, referred_by))
            
            # إضافة نقاط الترحيب
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, welcome_points, 'Welcome bonus', 'earned'))
            
            # إذا كان هناك محيل، أضف له نقاط
            if referred_by:
                cursor.execute('''
                    INSERT INTO referrals (referrer_id, referred_id, points_awarded)
                    VALUES (?, ?, ?)
                ''', (referred_by, user_id, 50))
                
                # إضافة نقاط للمحيل
                cursor.execute('''
                    UPDATE users SET points = points + 50 WHERE user_id = ?
                ''', (referred_by,))
                
                cursor.execute('''
                    INSERT INTO points_history (user_id, points, reason, transaction_type)
                    VALUES (?, ?, ?, ?)
                ''', (referred_by, 50, f'Referral bonus for user {user_id}', 'earned'))
            
            conn.commit()
            conn.close()
            return True, "Registration successful"
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)
    
    def get_user_info(self, user_id):
        """الحصول على معلومات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_user_language(self, user_id, language):
        """تحديث لغة المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
        conn.commit()
        conn.close()
    
    def add_points(self, user_id, points, reason):
        """إضافة نقاط للمستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points, user_id))
        cursor.execute('''
            INSERT INTO points_history (user_id, points, reason, transaction_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, points, reason, 'earned'))
        
        conn.commit()
        conn.close()
    
    def spend_points(self, user_id, points, reason):
        """خصم نقاط من المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود نقاط كافية
        cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result or result[0] < points:
            conn.close()
            return False, "Insufficient points"
        
        cursor.execute('UPDATE users SET points = points - ? WHERE user_id = ?', (points, user_id))
        cursor.execute('''
            INSERT INTO points_history (user_id, points, reason, transaction_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, -points, reason, 'spent'))
        
        conn.commit()
        conn.close()
        return True, "Points deducted successfully"
    
    def get_user_by_referral_code(self, referral_code):
        """الحصول على المستخدم بواسطة كود الإحالة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_code,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def insert_sample_lessons(self):
        """إدراج دروس تجريبية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود دروس
        cursor.execute('SELECT COUNT(*) FROM lessons')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        sample_lessons = [
            {
                'title_ar': 'مقدمة في الأمن السيبراني',
                'title_en': 'Introduction to Cybersecurity',
                'content_ar': 'الأمن السيبراني هو ممارسة حماية الأنظمة والشبكات والبرامج من الهجمات الرقمية...',
                'content_en': 'Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks...',
                'level': 'beginner',
                'category': 'basics',
                'points_reward': 15
            },
            {
                'title_ar': 'أنواع البرمجيات الخبيثة',
                'title_en': 'Types of Malware',
                'content_ar': 'البرمجيات الخبيثة هي برامج مصممة لإلحاق الضرر بالحاسوب أو الشبكة...',
                'content_en': 'Malware is software designed to damage or gain unauthorized access to computer systems...',
                'level': 'beginner',
                'category': 'threats',
                'points_reward': 20
            },
            {
                'title_ar': 'كلمات المرور الآمنة',
                'title_en': 'Secure Passwords',
                'content_ar': 'كلمة المرور القوية هي خط الدفاع الأول ضد الهجمات السيبرانية...',
                'content_en': 'A strong password is the first line of defense against cyber attacks...',
                'level': 'beginner',
                'category': 'security',
                'points_reward': 10
            }
        ]
        
        for lesson in sample_lessons:
            cursor.execute('''
                INSERT INTO lessons (title_ar, title_en, content_ar, content_en, level, category, points_reward)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (lesson['title_ar'], lesson['title_en'], lesson['content_ar'], 
                  lesson['content_en'], lesson['level'], lesson['category'], lesson['points_reward']))
        
        conn.commit()
        conn.close()

# إنشاء مثيل من مدير قاعدة البيانات
db = DatabaseManager()

