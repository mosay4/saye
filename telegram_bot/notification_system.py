import sqlite3
from datetime import datetime, timedelta
import asyncio
import logging
from database import db

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self, bot_application=None):
        self.db = db
        self.bot_application = bot_application
    
    def create_notification(self, user_id, title, message, notification_type='general', priority='normal', scheduled_time=None):
        """إنشاء إشعار جديد"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, notification_type, 
                                         priority, scheduled_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, message, notification_type, priority, 
                  scheduled_time or datetime.now(), datetime.now()))
            
            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # إرسال فوري إذا لم يكن مجدولاً
            if not scheduled_time:
                asyncio.create_task(self.send_notification(notification_id))
            
            return notification_id
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    def create_broadcast_notification(self, title, message, target_criteria=None, scheduled_time=None):
        """إنشاء إشعار جماعي"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # تحديد المستخدمين المستهدفين
            if target_criteria:
                query = "SELECT user_id FROM users WHERE "
                conditions = []
                params = []
                
                if target_criteria.get('level'):
                    conditions.append("level = ?")
                    params.append(target_criteria['level'])
                
                if target_criteria.get('is_vip') is not None:
                    conditions.append("is_vip = ?")
                    params.append(target_criteria['is_vip'])
                
                if target_criteria.get('min_points'):
                    conditions.append("points >= ?")
                    params.append(target_criteria['min_points'])
                
                if target_criteria.get('language'):
                    conditions.append("language = ?")
                    params.append(target_criteria['language'])
                
                if conditions:
                    query += " AND ".join(conditions)
                    cursor.execute(query, params)
                else:
                    cursor.execute("SELECT user_id FROM users")
            else:
                cursor.execute("SELECT user_id FROM users")
            
            target_users = [row[0] for row in cursor.fetchall()]
            
            # إنشاء إشعار لكل مستخدم
            notification_ids = []
            for user_id in target_users:
                cursor.execute('''
                    INSERT INTO notifications (user_id, title, message, notification_type, 
                                             priority, scheduled_time, created_at, is_broadcast)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, title, message, 'broadcast', 'normal', 
                      scheduled_time or datetime.now(), datetime.now(), True))
                
                notification_ids.append(cursor.lastrowid)
            
            conn.commit()
            conn.close()
            
            # إرسال فوري إذا لم يكن مجدولاً
            if not scheduled_time:
                for notification_id in notification_ids:
                    asyncio.create_task(self.send_notification(notification_id))
            
            return notification_ids
            
        except Exception as e:
            logger.error(f"Error creating broadcast notification: {e}")
            return []
    
    async def send_notification(self, notification_id):
        """إرسال إشعار محدد"""
        try:
            if not self.bot_application:
                logger.warning("Bot application not set, cannot send notification")
                return False
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, title, message, notification_type, priority
                FROM notifications 
                WHERE id = ? AND sent = FALSE
            ''', (notification_id,))
            
            notification = cursor.fetchone()
            if not notification:
                conn.close()
                return False
            
            user_id, title, message, notification_type, priority = notification
            
            # تنسيق الرسالة
            formatted_message = self.format_notification_message(title, message, notification_type, priority)
            
            # إرسال الإشعار
            try:
                await self.bot_application.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    parse_mode='Markdown'
                )
                
                # تحديث حالة الإرسال
                cursor.execute('''
                    UPDATE notifications 
                    SET sent = TRUE, sent_at = ?
                    WHERE id = ?
                ''', (datetime.now(), notification_id))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Notification {notification_id} sent to user {user_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send notification {notification_id} to user {user_id}: {e}")
                
                # تسجيل فشل الإرسال
                cursor.execute('''
                    UPDATE notifications 
                    SET failed = TRUE, error_message = ?
                    WHERE id = ?
                ''', (str(e), notification_id))
                
                conn.commit()
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {e}")
            return False
    
    def format_notification_message(self, title, message, notification_type, priority):
        """تنسيق رسالة الإشعار"""
        # رموز حسب نوع الإشعار
        type_icons = {
            'general': '📢',
            'security': '🔒',
            'lesson': '📚',
            'news': '📰',
            'shop': '🛒',
            'achievement': '🏆',
            'reminder': '⏰',
            'broadcast': '📡'
        }
        
        # رموز حسب الأولوية
        priority_icons = {
            'low': '🔵',
            'normal': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        icon = type_icons.get(notification_type, '📢')
        priority_icon = priority_icons.get(priority, '🟡')
        
        formatted = f"{icon} **{title}**\n\n"
        formatted += f"{message}\n\n"
        
        if priority in ['high', 'critical']:
            formatted += f"{priority_icon} *أولوية {'عالية' if priority == 'high' else 'حرجة'}*"
        
        return formatted
    
    def schedule_reminder(self, user_id, title, message, reminder_time):
        """جدولة تذكير"""
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='reminder',
            scheduled_time=reminder_time
        )
    
    def notify_lesson_completion(self, user_id, lesson_title, points_earned):
        """إشعار إكمال درس"""
        title = "🎉 تهانينا! درس مكتمل"
        message = f"لقد أكملت درس **{lesson_title}** بنجاح!\n\n⭐ النقاط المكتسبة: {points_earned}"
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='achievement'
        )
    
    def notify_level_up(self, user_id, new_level):
        """إشعار ترقية المستوى"""
        level_names = {
            'intermediate': 'متوسط',
            'advanced': 'متقدم'
        }
        
        title = "🚀 ترقية المستوى!"
        message = f"تهانينا! لقد وصلت إلى مستوى **{level_names.get(new_level, new_level)}**\n\nاستمر في التعلم لفتح المزيد من المحتوى المتقدم!"
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='achievement',
            priority='high'
        )
    
    def notify_vip_expiry(self, user_id, days_remaining):
        """إشعار انتهاء اشتراك VIP"""
        if days_remaining <= 0:
            title = "⚠️ انتهى اشتراك VIP"
            message = "لقد انتهى اشتراكك المميز. قم بتجديد الاشتراك للاستمرار في الاستفادة من المميزات الحصرية!"
            priority = 'high'
        elif days_remaining <= 3:
            title = "⏰ تذكير: اشتراك VIP ينتهي قريباً"
            message = f"سينتهي اشتراكك المميز خلال {days_remaining} أيام. جدد الآن لتجنب انقطاع الخدمة!"
            priority = 'normal'
        else:
            return None
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='reminder',
            priority=priority
        )
    
    def notify_security_alert(self, title, description, severity='medium'):
        """إشعار تنبيه أمني جماعي"""
        severity_icons = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        icon = severity_icons.get(severity, '🟡')
        notification_title = f"{icon} تنبيه أمني"
        message = f"**{title}**\n\n{description}\n\nتابع الأخبار الأمنية للمزيد من التفاصيل."
        
        priority = 'high' if severity in ['high', 'critical'] else 'normal'
        
        return self.create_broadcast_notification(
            title=notification_title,
            message=message,
            scheduled_time=None
        )
    
    def get_pending_notifications(self):
        """الحصول على الإشعارات المعلقة"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, title, message, notification_type, priority, scheduled_time
                FROM notifications 
                WHERE sent = FALSE AND failed = FALSE 
                AND scheduled_time <= ?
                ORDER BY priority DESC, scheduled_time ASC
            ''', (datetime.now(),))
            
            notifications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []
    
    async def process_pending_notifications(self):
        """معالجة الإشعارات المعلقة"""
        pending = self.get_pending_notifications()
        
        for notification in pending:
            await self.send_notification(notification['id'])
            # تأخير قصير لتجنب حدود التيليجرام
            await asyncio.sleep(0.1)
    
    def get_user_notification_preferences(self, user_id):
        """الحصول على تفضيلات الإشعارات للمستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT notification_types, quiet_hours_start, quiet_hours_end
                FROM user_notification_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'notification_types': result[0].split(',') if result[0] else [],
                    'quiet_hours_start': result[1],
                    'quiet_hours_end': result[2]
                }
            else:
                # إعدادات افتراضية
                return {
                    'notification_types': ['general', 'security', 'achievement', 'reminder'],
                    'quiet_hours_start': None,
                    'quiet_hours_end': None
                }
                
        except Exception as e:
            logger.error(f"Error getting notification preferences: {e}")
            return {
                'notification_types': ['general', 'security', 'achievement', 'reminder'],
                'quiet_hours_start': None,
                'quiet_hours_end': None
            }
    
    def update_user_notification_preferences(self, user_id, notification_types, quiet_hours_start=None, quiet_hours_end=None):
        """تحديث تفضيلات الإشعارات للمستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_notification_preferences 
                (user_id, notification_types, quiet_hours_start, quiet_hours_end)
                VALUES (?, ?, ?, ?)
            ''', (user_id, ','.join(notification_types), quiet_hours_start, quiet_hours_end))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")
            return False
    
    def get_notification_stats(self, days=30):
        """إحصائيات الإشعارات"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # إجمالي الإشعارات
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN sent = TRUE THEN 1 END) as sent,
                    COUNT(CASE WHEN failed = TRUE THEN 1 END) as failed
                FROM notifications 
                WHERE created_at >= ?
            ''', (start_date,))
            
            stats = dict(cursor.fetchone())
            
            # الإشعارات حسب النوع
            cursor.execute('''
                SELECT notification_type, COUNT(*) as count
                FROM notifications 
                WHERE created_at >= ?
                GROUP BY notification_type
                ORDER BY count DESC
            ''', (start_date,))
            
            stats['by_type'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return None

# إنشاء مثيل من نظام الإشعارات
notification_system = NotificationSystem()

