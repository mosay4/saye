
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_app = Flask(__name__)
CORS(admin_app)

# إعدادات التطبيق
admin_app.config["SECRET_KEY"] = "cyberbot_admin_secret_key_2024"
admin_app.config["JWT_SECRET_KEY"] = "cyberbot_jwt_secret_key_2024"

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'telegram_bot', 'cyberbot.db')

def get_db_connection():
    """الحصول على اتصال قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """التحقق من كلمة المرور"""
    return hash_password(password) == hashed

def generate_token(admin_id):
    """إنشاء JWT token"""
    payload = {
        'admin_id': admin_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, admin_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def token_required(f):
    """decorator للتحقق من صحة التوكن"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, admin_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            current_admin = data['admin_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_admin, *args, **kwargs)
    
    return decorated

def init_admin_table():
    """إنشاء جدول المشرفين"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # إنشاء مشرف افتراضي
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@cyberbot.ai', 'super_admin'))
    
    conn.commit()
    conn.close()

# API Routes

@admin_app.route("/api/admin/login", methods=["POST"])
def admin_login():
    """تسجيل دخول المشرف"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password_hash, role FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        
        if admin and verify_password(password, admin['password_hash']):
            # تحديث آخر تسجيل دخول
            cursor.execute('UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (admin['id'],))
            conn.commit()
            
            token = generate_token(admin['id'])
            
            conn.close()
            
            return jsonify({
                'success': True,
                'token': token,
                'admin': {
                    'id': admin['id'],
                    'username': admin['username'],
                    'role': admin['role']
                }
            })
        else:
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route("/api/admin/dashboard", methods=["GET"])
@token_required
def get_dashboard_stats(current_admin):
    """الحصول على إحصائيات لوحة التحكم"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # إحصائيات المستخدمين
        cursor.execute('SELECT COUNT(*) as total_users FROM users')
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute('SELECT COUNT(*) as new_users FROM users WHERE DATE(registration_date) = DATE("now")')
        new_users_today = cursor.fetchone()['new_users']
        
        cursor.execute('SELECT COUNT(*) as vip_users FROM users WHERE is_vip = TRUE')
        vip_users = cursor.fetchone()['vip_users']
        
        # إحصائيات الدروس
        cursor.execute('SELECT COUNT(*) as total_lessons FROM lessons')
        total_lessons = cursor.fetchone()['total_lessons']
        
        cursor.execute('SELECT COUNT(*) as completed_lessons FROM user_progress WHERE completed = TRUE')
        completed_lessons = cursor.fetchone()['completed_lessons']
        
        # إحصائيات النقاط
        cursor.execute('SELECT SUM(points) as total_points FROM users')
        total_points = cursor.fetchone()['total_points'] or 0
        
        cursor.execute('SELECT COUNT(*) as total_transactions FROM points_history')
        total_transactions = cursor.fetchone()['total_transactions']
        
        # إحصائيات الأخبار
        cursor.execute('SELECT COUNT(*) as total_news FROM news')
        total_news = cursor.fetchone()['total_news']
        
        cursor.execute('SELECT COUNT(*) as news_today FROM news WHERE DATE(published_date) = DATE("now")')
        news_today = cursor.fetchone()['news_today']
        
        # إحصائيات المتجر
        cursor.execute('SELECT COUNT(*) as total_purchases FROM purchases')
        total_purchases = cursor.fetchone()['total_purchases']
        
        cursor.execute('SELECT SUM(amount_usd) as total_revenue FROM purchases WHERE status = "completed"')
        total_revenue = cursor.fetchone()['total_revenue'] or 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'new_today': new_users_today,
                    'vip': vip_users
                },
                'lessons': {
                    'total': total_lessons,
                    'completed': completed_lessons
                },
                'points': {
                    'total': total_points,
                    'transactions': total_transactions
                },
                'news': {
                    'total': total_news,
                    'today': news_today
                },
                'shop': {
                    'purchases': total_purchases,
                    'revenue': total_revenue
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route("/api/admin/users", methods=["GET"])
@token_required
def get_users(current_admin):
    """الحصول على قائمة المستخدمين"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بناء الاستعلام
        query = '''
            SELECT user_id, username, first_name, last_name, language, points, 
                   level, registration_date, is_vip, total_lessons_completed
            FROM users
        '''
        params = []
        
        if search:
            query += ' WHERE username LIKE ? OR first_name LIKE ? OR last_name LIKE ?'
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        query += ' ORDER BY registration_date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        users = [dict(row) for row in cursor.fetchall()]
        
        # عدد المستخدمين الإجمالي
        count_query = 'SELECT COUNT(*) as total FROM users'
        if search:
            count_query += ' WHERE username LIKE ? OR first_name LIKE ? OR last_name LIKE ?'
            cursor.execute(count_query, [search_param, search_param, search_param])
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route("/api/admin/users/<int:user_id>", methods=["GET"])
@token_required
def get_user_details(current_admin, user_id):
    """الحصول على تفاصيل مستخدم"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # معلومات المستخدم
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # تاريخ النقاط
        cursor.execute('''
            SELECT points, reason, transaction_type, date 
            FROM points_history 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT 10
        ''', (user_id,))
        points_history = [dict(row) for row in cursor.fetchall()]
        
        # تقدم الدروس
        cursor.execute('''
            SELECT l.title_ar, l.title_en, up.completed, up.completion_date, up.quiz_score
            FROM user_progress up
            JOIN lessons l ON up.lesson_id = l.id
            WHERE up.user_id = ?
            ORDER BY up.completion_date DESC
        ''', (user_id,))
        lessons_progress = [dict(row) for row in cursor.fetchall()]
        
        # المشتريات
        cursor.execute('''
            SELECT s.name_ar, s.name_en, p.payment_method, p.amount_points, 
                   p.amount_usd, p.purchase_date, p.status
            FROM purchases p
            JOIN shop_items s ON p.item_id = s.id
            WHERE p.user_id = ?
            ORDER BY p.purchase_date DESC
        ''', (user_id,))
        purchases = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user': dict(user),
            'points_history': points_history,
            'lessons_progress': lessons_progress,
            'purchases': purchases
        })
        
    except Exception as e:
        logger.error(f"Get user details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route("/api/admin/users/<int:user_id>/points", methods=["POST"])
@token_required
def update_user_points(current_admin, user_id):
    """تحديث نقاط المستخدم"""
    try:
        data = request.get_json()
        points = data.get('points')
        reason = data.get('reason', 'Admin adjustment')
        action = data.get('action', 'add')  # add or subtract
        
        if not isinstance(points, int) or points <= 0:
            return jsonify({'error': 'Invalid points value'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود المستخدم
        cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if action == 'add':
            cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points, user_id))
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, points, reason, 'earned'))
        else:  # subtract
            if user['points'] < points:
                return jsonify({'error': 'Insufficient points'}), 400
            
            cursor.execute('UPDATE users SET points = points - ? WHERE user_id = ?', (points, user_id))
            cursor.execute('''
                INSERT INTO points_history (user_id, points, reason, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, -points, reason, 'spent'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Points updated successfully'})
        
    except Exception as e:
        logger.error(f"Update user points error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route('/api/admin/lessons', methods=['GET'])
@token_required
def get_lessons(current_admin):
    """الحصول على قائمة الدروس"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT l.*, 
                   COUNT(up.user_id) as enrolled_users,
                   COUNT(CASE WHEN up.completed = TRUE THEN 1 END) as completed_users
            FROM lessons l
            LEFT JOIN user_progress up ON l.id = up.lesson_id
            GROUP BY l.id
            ORDER BY l.id
        ''')
        lessons = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'lessons': lessons
        })
        
    except Exception as e:
        logger.error(f"Get lessons error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_app.route('/api/admin/news', methods=['GET'])
@token_required
def get_news(current_admin):
    """الحصول على قائمة الأخبار"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title_ar, title_en, category, severity, published_date, is_featured
            FROM news
            ORDER BY published_date DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        news = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT COUNT(*) as total FROM news')
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'news': news,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logger.error(f"Get news error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_admin_table()
    admin_app.run(host='0.0.0.0', port=5001, debug=True)


