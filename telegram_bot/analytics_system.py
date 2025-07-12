import sqlite3
from datetime import datetime, timedelta
import json
import logging
from database import db

logger = logging.getLogger(__name__)

class AnalyticsSystem:
    def __init__(self):
        self.db = db
    
    def track_user_activity(self, user_id, activity_type, details=None):
        """تتبع نشاط المستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activities (user_id, activity_type, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, json.dumps(details) if details else None, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error tracking user activity: {e}")
    
    def get_user_engagement_stats(self, days=30):
        """إحصائيات تفاعل المستخدمين"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # المستخدمين النشطين
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) as active_users
                FROM user_activities 
                WHERE timestamp >= ?
            ''', (start_date,))
            active_users = cursor.fetchone()[0]
            
            # المستخدمين الجدد
            cursor.execute('''
                SELECT COUNT(*) as new_users
                FROM users 
                WHERE registration_date >= ?
            ''', (start_date,))
            new_users = cursor.fetchone()[0]
            
            # الأنشطة الأكثر شعبية
            cursor.execute('''
                SELECT activity_type, COUNT(*) as count
                FROM user_activities 
                WHERE timestamp >= ?
                GROUP BY activity_type
                ORDER BY count DESC
                LIMIT 10
            ''', (start_date,))
            popular_activities = cursor.fetchall()
            
            # معدل الاحتفاظ
            cursor.execute('''
                SELECT 
                    COUNT(CASE WHEN last_activity >= ? THEN 1 END) * 100.0 / COUNT(*) as retention_rate
                FROM (
                    SELECT user_id, MAX(timestamp) as last_activity
                    FROM user_activities
                    GROUP BY user_id
                )
            ''', (datetime.now() - timedelta(days=7),))
            retention_rate = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'active_users': active_users,
                'new_users': new_users,
                'popular_activities': [dict(row) for row in popular_activities],
                'retention_rate': round(retention_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement stats: {e}")
            return None
    
    def get_learning_analytics(self):
        """تحليلات التعلم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # معدل إكمال الدروس
            cursor.execute('''
                SELECT 
                    l.level,
                    COUNT(up.user_id) as enrolled,
                    COUNT(CASE WHEN up.completed = TRUE THEN 1 END) as completed,
                    COUNT(CASE WHEN up.completed = TRUE THEN 1 END) * 100.0 / COUNT(up.user_id) as completion_rate
                FROM lessons l
                LEFT JOIN user_progress up ON l.id = up.lesson_id
                GROUP BY l.level
            ''')
            completion_by_level = [dict(row) for row in cursor.fetchall()]
            
            # الدروس الأكثر صعوبة
            cursor.execute('''
                SELECT 
                    l.title_ar,
                    l.level,
                    AVG(up.quiz_score) as avg_score,
                    COUNT(up.user_id) as attempts
                FROM lessons l
                JOIN user_progress up ON l.id = up.lesson_id
                WHERE up.completed = TRUE
                GROUP BY l.id
                ORDER BY avg_score ASC
                LIMIT 5
            ''')
            difficult_lessons = [dict(row) for row in cursor.fetchall()]
            
            # توزيع النقاط
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN points < 100 THEN '0-99'
                        WHEN points < 500 THEN '100-499'
                        WHEN points < 1000 THEN '500-999'
                        WHEN points < 2000 THEN '1000-1999'
                        ELSE '2000+'
                    END as points_range,
                    COUNT(*) as user_count
                FROM users
                GROUP BY points_range
                ORDER BY MIN(points)
            ''')
            points_distribution = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'completion_by_level': completion_by_level,
                'difficult_lessons': difficult_lessons,
                'points_distribution': points_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting learning analytics: {e}")
            return None
    
    def get_revenue_analytics(self, days=30):
        """تحليلات الإيرادات"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # إجمالي الإيرادات
            cursor.execute('''
                SELECT 
                    SUM(amount_usd) as total_revenue,
                    COUNT(*) as total_purchases
                FROM purchases 
                WHERE purchase_date >= ? AND status = 'completed'
            ''', (start_date,))
            revenue_data = cursor.fetchone()
            
            # الإيرادات حسب المنتج
            cursor.execute('''
                SELECT 
                    s.name_ar,
                    s.category,
                    SUM(p.amount_usd) as revenue,
                    COUNT(p.id) as sales_count
                FROM purchases p
                JOIN shop_items s ON p.item_id = s.id
                WHERE p.purchase_date >= ? AND p.status = 'completed'
                GROUP BY s.id
                ORDER BY revenue DESC
            ''', (start_date,))
            revenue_by_product = [dict(row) for row in cursor.fetchall()]
            
            # الإيرادات اليومية
            cursor.execute('''
                SELECT 
                    DATE(purchase_date) as date,
                    SUM(amount_usd) as daily_revenue,
                    COUNT(*) as daily_sales
                FROM purchases 
                WHERE purchase_date >= ? AND status = 'completed'
                GROUP BY DATE(purchase_date)
                ORDER BY date DESC
                LIMIT 30
            ''', (start_date,))
            daily_revenue = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_revenue': revenue_data[0] or 0,
                'total_purchases': revenue_data[1] or 0,
                'revenue_by_product': revenue_by_product,
                'daily_revenue': daily_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return None
    
    def get_ai_usage_analytics(self, days=30):
        """تحليلات استخدام الذكاء الاصطناعي"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # إجمالي الاستخدام
            cursor.execute('''
                SELECT COUNT(*) as total_queries
                FROM user_activities 
                WHERE activity_type = 'ai_chat' AND timestamp >= ?
            ''', (start_date,))
            total_queries = cursor.fetchone()[0]
            
            # المستخدمين النشطين في الذكاء الاصطناعي
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) as active_ai_users
                FROM user_activities 
                WHERE activity_type = 'ai_chat' AND timestamp >= ?
            ''', (start_date,))
            active_ai_users = cursor.fetchone()[0]
            
            # الاستخدام حسب المستوى
            cursor.execute('''
                SELECT 
                    u.level,
                    COUNT(ua.id) as queries_count
                FROM user_activities ua
                JOIN users u ON ua.user_id = u.user_id
                WHERE ua.activity_type = 'ai_chat' AND ua.timestamp >= ?
                GROUP BY u.level
            ''', (start_date,))
            usage_by_level = [dict(row) for row in cursor.fetchall()]
            
            # الاستخدام اليومي
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as daily_queries
                FROM user_activities 
                WHERE activity_type = 'ai_chat' AND timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''', (start_date,))
            daily_usage = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_queries': total_queries,
                'active_ai_users': active_ai_users,
                'usage_by_level': usage_by_level,
                'daily_usage': daily_usage
            }
            
        except Exception as e:
            logger.error(f"Error getting AI usage analytics: {e}")
            return None
    
    def generate_weekly_report(self):
        """إنشاء تقرير أسبوعي"""
        try:
            engagement = self.get_user_engagement_stats(7)
            learning = self.get_learning_analytics()
            revenue = self.get_revenue_analytics(7)
            ai_usage = self.get_ai_usage_analytics(7)
            
            report = {
                'period': 'weekly',
                'generated_at': datetime.now().isoformat(),
                'engagement': engagement,
                'learning': learning,
                'revenue': revenue,
                'ai_usage': ai_usage
            }
            
            # حفظ التقرير
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analytics_reports (report_type, period, data, generated_at)
                VALUES (?, ?, ?, ?)
            ''', ('weekly', 'last_7_days', json.dumps(report), datetime.now()))
            
            conn.commit()
            conn.close()
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return None
    
    def get_user_behavior_insights(self, user_id):
        """تحليل سلوك مستخدم محدد"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # نشاط المستخدم
            cursor.execute('''
                SELECT activity_type, COUNT(*) as count
                FROM user_activities 
                WHERE user_id = ?
                GROUP BY activity_type
                ORDER BY count DESC
            ''', (user_id,))
            activity_breakdown = [dict(row) for row in cursor.fetchall()]
            
            # تقدم التعلم
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_lessons,
                    COUNT(CASE WHEN completed = TRUE THEN 1 END) as completed_lessons,
                    AVG(quiz_score) as avg_score
                FROM user_progress 
                WHERE user_id = ?
            ''', (user_id,))
            learning_progress = dict(cursor.fetchone())
            
            # تاريخ النقاط
            cursor.execute('''
                SELECT 
                    transaction_type,
                    SUM(points) as total_points
                FROM points_history 
                WHERE user_id = ?
                GROUP BY transaction_type
            ''', (user_id,))
            points_breakdown = [dict(row) for row in cursor.fetchall()]
            
            # آخر نشاط
            cursor.execute('''
                SELECT MAX(timestamp) as last_activity
                FROM user_activities 
                WHERE user_id = ?
            ''', (user_id,))
            last_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'activity_breakdown': activity_breakdown,
                'learning_progress': learning_progress,
                'points_breakdown': points_breakdown,
                'last_activity': last_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior insights: {e}")
            return None

# إنشاء مثيل من نظام التحليلات
analytics_system = AnalyticsSystem()

