import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import openai
import os
from datetime import datetime, timedelta
from database import db
import schedule
import time
import threading
import logging

logger = logging.getLogger(__name__)

class NewsSystem:
    def __init__(self):
        self.db = db
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # مصادر الأخبار
        self.news_sources = {
            'bleeping_computer': 'https://www.bleepingcomputer.com/feed/',
            'krebs_security': 'https://krebsonsecurity.com/feed/',
            'threatpost': 'https://threatpost.com/feed/',
            'security_week': 'https://www.securityweek.com/feed',
            'dark_reading': 'https://www.darkreading.com/rss.xml',
            'cisa_alerts': 'https://www.cisa.gov/cybersecurity-advisories/all.xml'
        }
    
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'daily_news': '📰 النشرة الإخبارية اليومية',
                'latest_news': 'آخر الأخبار',
                'news_categories': 'تصنيفات الأخبار',
                'critical_alerts': '🚨 تنبيهات حرجة',
                'security_updates': '🔒 تحديثات أمنية',
                'threat_intelligence': '🎯 معلومات التهديدات',
                'vulnerabilities': '🔓 الثغرات الأمنية',
                'malware_analysis': '🦠 تحليل البرمجيات الخبيثة',
                'no_news': 'لا توجد أخبار متاحة حالياً',
                'loading_news': 'جاري تحميل الأخبار...',
                'news_summary': 'ملخص الخبر',
                'read_full': 'قراءة كاملة',
                'back_to_news': '🔙 العودة للأخبار',
                'main_menu': '🏠 القائمة الرئيسية',
                'published': 'نُشر في:',
                'source': 'المصدر:'
            },
            'en': {
                'daily_news': '📰 Daily Newsletter',
                'latest_news': 'Latest News',
                'news_categories': 'News Categories',
                'critical_alerts': '🚨 Critical Alerts',
                'security_updates': '🔒 Security Updates',
                'threat_intelligence': '🎯 Threat Intelligence',
                'vulnerabilities': '🔓 Vulnerabilities',
                'malware_analysis': '🦠 Malware Analysis',
                'no_news': 'No news available at the moment',
                'loading_news': 'Loading news...',
                'news_summary': 'News Summary',
                'read_full': 'Read Full',
                'back_to_news': '🔙 Back to News',
                'main_menu': '🏠 Main Menu',
                'published': 'Published:',
                'source': 'Source:'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def fetch_rss_news(self, source_name, rss_url, limit=5):
        """جلب الأخبار من RSS"""
        try:
            feed = feedparser.parse(rss_url)
            news_items = []
            
            for entry in feed.entries[:limit]:
                try:
                    # استخراج المحتوى
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # تنظيف المحتوى من HTML
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text().strip()
                    
                    # تاريخ النشر
                    published_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    
                    news_item = {
                        'title': entry.title,
                        'content': content,
                        'url': entry.link,
                        'source': source_name,
                        'published_date': published_date,
                        'category': self.categorize_news(entry.title + " " + content)
                    }
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching RSS from {rss_url}: {e}")
            return []
    
    def categorize_news(self, text):
        """تصنيف الأخبار حسب المحتوى"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'urgent', 'emergency', 'zero-day', 'exploit']):
            return 'critical'
        elif any(word in text_lower for word in ['vulnerability', 'cve', 'patch', 'security update']):
            return 'vulnerability'
        elif any(word in text_lower for word in ['malware', 'ransomware', 'trojan', 'virus', 'botnet']):
            return 'malware'
        elif any(word in text_lower for word in ['threat', 'attack', 'breach', 'incident']):
            return 'threat'
        else:
            return 'general'
    
    def get_severity_level(self, category, content):
        """تحديد مستوى الخطورة"""
        content_lower = content.lower()
        
        if category == 'critical':
            return 'critical'
        elif any(word in content_lower for word in ['widespread', 'global', 'massive', 'major']):
            return 'high'
        elif any(word in content_lower for word in ['limited', 'minor', 'small']):
            return 'low'
        else:
            return 'medium'
    
    def summarize_with_ai(self, title, content, target_language='ar'):
        """تلخيص الخبر باستخدام الذكاء الاصطناعي"""
        try:
            prompt = f"""
            قم بتلخيص هذا الخبر الأمني باللغة {target_language}:
            
            العنوان: {title}
            المحتوى: {content}
            
            المطلوب:
            1. ملخص مختصر في 2-3 جمل
            2. النقاط الرئيسية
            3. التأثير المحتمل
            4. التوصيات (إن وجدت)
            
            اجعل الملخص مفهوماً للمبتدئين في الأمن السيبراني.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "أنت خبير في الأمن السيبراني متخصص في تلخيص الأخبار الأمنية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing with AI: {e}")
            return content[:200] + "..." if len(content) > 200 else content
    
    def translate_content(self, content, target_language):
        """ترجمة المحتوى"""
        try:
            if target_language == 'ar':
                prompt = f"ترجم هذا النص إلى العربية مع الحفاظ على المصطلحات التقنية:\n\n{content}"
            else:
                prompt = f"Translate this text to English while preserving technical terms:\n\n{content}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "أنت مترجم متخصص في المصطلحات التقنية والأمن السيبراني."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error translating content: {e}")
            return content
    
    def collect_daily_news(self):
        """جمع الأخبار اليومية من جميع المصادر"""
        all_news = []
        
        for source_name, rss_url in self.news_sources.items():
            logger.info(f"Fetching news from {source_name}")
            news_items = self.fetch_rss_news(source_name, rss_url)
            all_news.extend(news_items)
        
        # ترتيب الأخبار حسب الأهمية والتاريخ
        all_news.sort(key=lambda x: (
            0 if x['category'] == 'critical' else 1 if x['category'] == 'vulnerability' else 2,
            -x['published_date'].timestamp()
        ))
        
        return all_news[:10]  # أهم 10 أخبار
    
    def save_news_to_db(self, news_items):
        """حفظ الأخبار في قاعدة البيانات"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for news in news_items:
            try:
                # التحقق من وجود الخبر
                cursor.execute('SELECT id FROM news WHERE source_url = ?', (news['url'],))
                if cursor.fetchone():
                    continue
                
                # تلخيص وترجمة المحتوى
                summary_ar = self.summarize_with_ai(news['title'], news['content'], 'ar')
                summary_en = self.summarize_with_ai(news['title'], news['content'], 'en')
                
                # ترجمة العنوان
                title_ar = self.translate_content(news['title'], 'ar')
                title_en = news['title']  # العنوان الأصلي عادة بالإنجليزية
                
                severity = self.get_severity_level(news['category'], news['content'])
                
                cursor.execute('''
                    INSERT INTO news (title_ar, title_en, content_ar, content_en, 
                                    source_url, category, severity, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title_ar, title_en, summary_ar, summary_en, 
                      news['url'], news['category'], severity, news['published_date']))
                
            except Exception as e:
                logger.error(f"Error saving news to DB: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def get_latest_news(self, user_id, limit=5, category=None):
        """الحصول على آخر الأخبار"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title_ar, title_en, content_ar, content_en, 
                   source_url, category, severity, published_date
            FROM news 
        '''
        params = []
        
        if category:
            query += ' WHERE category = ?'
            params.append(category)
        
        query += ' ORDER BY published_date DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        news_items = cursor.fetchall()
        conn.close()
        
        return news_items
    
    def create_news_menu(self, user_id):
        """إنشاء قائمة الأخبار"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton(self.get_text(user_id, 'latest_news'), callback_data='news_latest'),
                InlineKeyboardButton(self.get_text(user_id, 'critical_alerts'), callback_data='news_critical')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'vulnerabilities'), callback_data='news_vulnerability'),
                InlineKeyboardButton(self.get_text(user_id, 'malware_analysis'), callback_data='news_malware')
            ],
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_news_list(self, user_id, news_items):
        """إنشاء قائمة الأخبار للعرض"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        if not news_items:
            text = self.get_text(user_id, 'no_news')
            keyboard = [[InlineKeyboardButton(self.get_text(user_id, 'back_to_news'), callback_data='news')]]
            return text, InlineKeyboardMarkup(keyboard)
        
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        text = f"{self.get_text(user_id, 'latest_news')}\n\n"
        keyboard = []
        
        for i, news in enumerate(news_items):
            title = news[1] if lang == 'ar' else news[2]
            severity_emoji = {
                'critical': '🚨',
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(news[7], '📰')
            
            # تقصير العنوان للعرض
            display_title = title[:50] + "..." if len(title) > 50 else title
            text += f"{severity_emoji} {display_title}\n"
            
            # إضافة زر للخبر
            keyboard.append([InlineKeyboardButton(f"📖 {i+1}", callback_data=f"news_read_{news[0]}")])
        
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_news'), callback_data='news')])
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_news_detail(self, user_id, news_id):
        """الحصول على تفاصيل خبر معين"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title_ar, title_en, content_ar, content_en, 
                   source_url, category, severity, published_date
            FROM news WHERE id = ?
        ''', (news_id,))
        news = cursor.fetchone()
        conn.close()
        
        if not news:
            return None, None
        
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        title = news[0] if lang == 'ar' else news[1]
        content = news[2] if lang == 'ar' else news[3]
        
        severity_emoji = {
            'critical': '🚨',
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(news[6], '📰')
        
        # تنسيق التاريخ
        published_date = datetime.strptime(news[7], '%Y-%m-%d %H:%M:%S')
        formatted_date = published_date.strftime('%Y-%m-%d %H:%M')
        
        text = f"{severity_emoji} {title}\n\n"
        text += f"{content}\n\n"
        text += f"📅 {self.get_text(user_id, 'published')} {formatted_date}\n"
        text += f"🔗 {self.get_text(user_id, 'source')}: {news[4]}"
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back_to_news'), callback_data='news_latest')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def generate_daily_newsletter(self):
        """إنشاء النشرة الإخبارية اليومية"""
        logger.info("Generating daily newsletter...")
        
        # جمع الأخبار
        news_items = self.collect_daily_news()
        
        if news_items:
            # حفظ في قاعدة البيانات
            self.save_news_to_db(news_items)
            logger.info(f"Saved {len(news_items)} news items to database")
        
        return len(news_items)
    
    def start_news_scheduler(self):
        """بدء جدولة جمع الأخبار"""
        # جدولة جمع الأخبار كل 6 ساعات
        schedule.every(6).hours.do(self.generate_daily_newsletter)
        
        # جدولة النشرة اليومية في الساعة 8 مساءً
        schedule.every().day.at("20:00").do(self.generate_daily_newsletter)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # فحص كل دقيقة
        
        # تشغيل الجدولة في خيط منفصل
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("News scheduler started")

# إنشاء مثيل من نظام الأخبار
news_system = NewsSystem()

