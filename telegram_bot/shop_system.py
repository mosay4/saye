import stripe
import os
from database import db
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class ShopSystem:
    def __init__(self):
        self.db = db
        # إعداد Stripe (يحتاج مفاتيح حقيقية في الإنتاج)
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
        
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'shop_menu': '🛒 المتجر',
                'browse_items': '🛍️ تصفح المنتجات',
                'my_purchases': '📦 مشترياتي',
                'vip_subscription': '👑 اشتراك VIP',
                'points_packages': '💎 حزم النقاط',
                'premium_courses': '📚 الدورات المميزة',
                'certificates': '🏆 الشهادات',
                'current_points': 'نقاطك الحالية: {} نقطة',
                'insufficient_points': '❌ نقاطك غير كافية',
                'purchase_successful': '✅ تم الشراء بنجاح!',
                'purchase_failed': '❌ فشل في الشراء',
                'confirm_purchase': 'تأكيد الشراء',
                'cancel': 'إلغاء',
                'price_points': 'السعر: {} نقطة',
                'price_usd': 'السعر: ${} دولار',
                'buy_with_points': '💰 شراء بالنقاط',
                'buy_with_card': '💳 شراء بالبطاقة',
                'item_description': 'الوصف:',
                'back_to_shop': '🔙 العودة للمتجر',
                'main_menu': '🏠 القائمة الرئيسية',
                'vip_benefits': 'مميزات VIP:\n• استخدام الذكاء الاصطناعي بلا حدود\n• دروس حصرية\n• أولوية في الدعم\n• شارات خاصة',
                'already_vip': '👑 أنت عضو VIP بالفعل!',
                'vip_expires': 'ينتهي اشتراك VIP في: {}',
                'processing_payment': '⏳ جاري معالجة الدفع...',
                'payment_link': '🔗 رابط الدفع',
                'no_purchases': 'لا توجد مشتريات حتى الآن'
            },
            'en': {
                'shop_menu': '🛒 Shop',
                'browse_items': '🛍️ Browse Items',
                'my_purchases': '📦 My Purchases',
                'vip_subscription': '👑 VIP Subscription',
                'points_packages': '💎 Points Packages',
                'premium_courses': '📚 Premium Courses',
                'certificates': '🏆 Certificates',
                'current_points': 'Your current points: {} points',
                'insufficient_points': '❌ Insufficient points',
                'purchase_successful': '✅ Purchase successful!',
                'purchase_failed': '❌ Purchase failed',
                'confirm_purchase': 'Confirm Purchase',
                'cancel': 'Cancel',
                'price_points': 'Price: {} points',
                'price_usd': 'Price: ${} USD',
                'buy_with_points': '💰 Buy with Points',
                'buy_with_card': '💳 Buy with Card',
                'item_description': 'Description:',
                'back_to_shop': '🔙 Back to Shop',
                'main_menu': '🏠 Main Menu',
                'vip_benefits': 'VIP Benefits:\n• Unlimited AI usage\n• Exclusive lessons\n• Priority support\n• Special badges',
                'already_vip': '👑 You are already a VIP member!',
                'vip_expires': 'VIP subscription expires: {}',
                'processing_payment': '⏳ Processing payment...',
                'payment_link': '🔗 Payment Link',
                'no_purchases': 'No purchases yet'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def init_shop_items(self):
        """إنشاء منتجات المتجر الافتراضية"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود منتجات
        cursor.execute('SELECT COUNT(*) FROM shop_items')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        default_items = [
            {
                'name_ar': 'حزمة 100 نقطة',
                'name_en': '100 Points Package',
                'description_ar': 'احصل على 100 نقطة إضافية لاستخدامها في البوت',
                'description_en': 'Get 100 additional points to use in the bot',
                'price_points': 0,
                'price_usd': 2.99,
                'category': 'points'
            },
            {
                'name_ar': 'حزمة 500 نقطة',
                'name_en': '500 Points Package',
                'description_ar': 'احصل على 500 نقطة إضافية مع خصم 20%',
                'description_en': 'Get 500 additional points with 20% discount',
                'price_points': 0,
                'price_usd': 9.99,
                'category': 'points'
            },
            {
                'name_ar': 'اشتراك VIP شهري',
                'name_en': 'Monthly VIP Subscription',
                'description_ar': 'اشتراك VIP لمدة شهر واحد مع جميع المميزات',
                'description_en': 'One month VIP subscription with all benefits',
                'price_points': 500,
                'price_usd': 9.99,
                'category': 'vip'
            },
            {
                'name_ar': 'اشتراك VIP سنوي',
                'name_en': 'Yearly VIP Subscription',
                'description_ar': 'اشتراك VIP لمدة سنة كاملة مع خصم 50%',
                'description_en': 'One year VIP subscription with 50% discount',
                'price_points': 2000,
                'price_usd': 59.99,
                'category': 'vip'
            },
            {
                'name_ar': 'دورة الاختراق الأخلاقي',
                'name_en': 'Ethical Hacking Course',
                'description_ar': 'دورة شاملة في الاختراق الأخلاقي مع شهادة',
                'description_en': 'Comprehensive ethical hacking course with certificate',
                'price_points': 1000,
                'price_usd': 49.99,
                'category': 'course'
            },
            {
                'name_ar': 'شهادة إتمام الأمن السيبراني',
                'name_en': 'Cybersecurity Completion Certificate',
                'description_ar': 'شهادة رسمية بإتمام دورة الأمن السيبراني',
                'description_en': 'Official certificate for completing cybersecurity course',
                'price_points': 200,
                'price_usd': 19.99,
                'category': 'certificate'
            }
        ]
        
        for item in default_items:
            cursor.execute('''
                INSERT INTO shop_items (name_ar, name_en, description_ar, description_en,
                                      price_points, price_usd, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item['name_ar'], item['name_en'], item['description_ar'], 
                  item['description_en'], item['price_points'], item['price_usd'], item['category']))
        
        conn.commit()
        conn.close()
    
    def create_shop_menu(self, user_id):
        """إنشاء قائمة المتجر الرئيسية"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_info = self.db.get_user_info(user_id)
        points = user_info[5] if user_info else 0
        
        text = f"{self.get_text(user_id, 'shop_menu')}\n\n"
        text += f"{self.get_text(user_id, 'current_points').format(points)}"
        
        keyboard = [
            [
                InlineKeyboardButton(self.get_text(user_id, 'points_packages'), 
                                   callback_data='shop_category_points'),
                InlineKeyboardButton(self.get_text(user_id, 'vip_subscription'), 
                                   callback_data='shop_category_vip')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'premium_courses'), 
                                   callback_data='shop_category_course'),
                InlineKeyboardButton(self.get_text(user_id, 'certificates'), 
                                   callback_data='shop_category_certificate')
            ],
            [
                InlineKeyboardButton(self.get_text(user_id, 'my_purchases'), 
                                   callback_data='shop_purchases'),
                InlineKeyboardButton(self.get_text(user_id, 'main_menu'), 
                                   callback_data='main_menu')
            ]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_items_by_category(self, category):
        """الحصول على المنتجات حسب الفئة"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name_ar, name_en, description_ar, description_en,
                   price_points, price_usd, category
            FROM shop_items 
            WHERE category = ? AND is_available = TRUE
            ORDER BY price_usd ASC
        ''', (category,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    def create_category_menu(self, user_id, category):
        """إنشاء قائمة منتجات الفئة"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        items = self.get_items_by_category(category)
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        text = f"{self.get_text(user_id, 'browse_items')} - {category.title()}\n\n"
        
        keyboard = []
        
        for item in items:
            name = item[1] if lang == 'ar' else item[2]
            price_display = ""
            
            if item[5] > 0:  # price_points
                price_display += f"💰 {item[5]} نقطة"
            if item[6] > 0:  # price_usd
                if price_display:
                    price_display += " | "
                price_display += f"💳 ${item[6]}"
            
            button_text = f"{name}\n{price_display}"
            keyboard.append([InlineKeyboardButton(button_text, 
                                                callback_data=f"shop_item_{item[0]}")])
        
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_shop'), 
                                            callback_data='shop')])
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_item_details(self, item_id):
        """الحصول على تفاصيل منتج"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name_ar, name_en, description_ar, description_en,
                   price_points, price_usd, category
            FROM shop_items WHERE id = ?
        ''', (item_id,))
        item = cursor.fetchone()
        conn.close()
        return item
    
    def create_item_details_menu(self, user_id, item_id):
        """إنشاء قائمة تفاصيل المنتج"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        item = self.get_item_details(item_id)
        if not item:
            return None, None
        
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        name = item[1] if lang == 'ar' else item[2]
        description = item[3] if lang == 'ar' else item[4]
        
        text = f"🛍️ {name}\n\n"
        text += f"{self.get_text(user_id, 'item_description')}\n{description}\n\n"
        
        keyboard = []
        
        # أزرار الشراء
        if item[5] > 0:  # price_points
            text += f"{self.get_text(user_id, 'price_points').format(item[5])}\n"
            keyboard.append([InlineKeyboardButton(
                f"{self.get_text(user_id, 'buy_with_points')} ({item[5]} نقطة)",
                callback_data=f"shop_buy_points_{item_id}"
            )])
        
        if item[6] > 0:  # price_usd
            text += f"{self.get_text(user_id, 'price_usd').format(item[6])}\n"
            keyboard.append([InlineKeyboardButton(
                f"{self.get_text(user_id, 'buy_with_card')} (${item[6]})",
                callback_data=f"shop_buy_card_{item_id}"
            )])
        
        # التحقق من اشتراك VIP للمنتجات ذات الصلة
        if item[7] == 'vip':
            is_vip = user_info[11] if len(user_info) > 11 else False
            if is_vip:
                text += f"\n{self.get_text(user_id, 'already_vip')}"
                keyboard = []  # إزالة أزرار الشراء
        
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_shop'), 
                                            callback_data=f"shop_category_{item[7]}")])
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def create_purchase_confirmation(self, user_id, item_id, payment_method):
        """إنشاء تأكيد الشراء"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        item = self.get_item_details(item_id)
        if not item:
            return None, None
        
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        name = item[1] if lang == 'ar' else item[2]
        
        if payment_method == 'points':
            price = item[5]
            currency = 'نقطة'
            user_points = user_info[5]
            
            text = f"💰 {self.get_text(user_id, 'confirm_purchase')}\n\n"
            text += f"📦 {name}\n"
            text += f"💰 {price} {currency}\n\n"
            text += f"رصيدك الحالي: {user_points} نقطة\n"
            
            if user_points < price:
                text += f"\n❌ {self.get_text(user_id, 'insufficient_points')}"
                keyboard = [[InlineKeyboardButton(self.get_text(user_id, 'back_to_shop'), 
                                                callback_data='shop')]]
            else:
                text += f"الرصيد بعد الشراء: {user_points - price} نقطة"
                keyboard = [
                    [
                        InlineKeyboardButton("✅ تأكيد", 
                                           callback_data=f"shop_confirm_points_{item_id}"),
                        InlineKeyboardButton(self.get_text(user_id, 'cancel'), 
                                           callback_data=f"shop_item_{item_id}")
                    ]
                ]
        else:  # card payment
            price = item[6]
            text = f"💳 {self.get_text(user_id, 'confirm_purchase')}\n\n"
            text += f"📦 {name}\n"
            text += f"💳 ${price} USD\n\n"
            text += "سيتم توجيهك لصفحة الدفع الآمنة"
            
            keyboard = [
                [
                    InlineKeyboardButton("💳 متابعة للدفع", 
                                       callback_data=f"shop_confirm_card_{item_id}"),
                    InlineKeyboardButton(self.get_text(user_id, 'cancel'), 
                                       callback_data=f"shop_item_{item_id}")
                ]
            ]
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def process_points_purchase(self, user_id, item_id):
        """معالجة الشراء بالنقاط"""
        item = self.get_item_details(item_id)
        if not item:
            return False, "المنتج غير موجود"
        
        price = item[5]
        if price <= 0:
            return False, "هذا المنتج غير متاح للشراء بالنقاط"
        
        # خصم النقاط
        success, message = self.db.spend_points(user_id, price, f"Purchase: {item[1]}")
        
        if success:
            # إنشاء سجل الشراء
            purchase_id = self.create_purchase_record(user_id, item_id, 'points', price, 0)
            
            # تطبيق المنتج (VIP، نقاط، إلخ)
            self.apply_purchase(user_id, item, purchase_id)
            
            return True, "تم الشراء بنجاح!"
        
        return False, message
    
    def create_stripe_payment_link(self, user_id, item_id):
        """إنشاء رابط دفع Stripe"""
        try:
            item = self.get_item_details(item_id)
            if not item:
                return None
            
            user_info = self.db.get_user_info(user_id)
            lang = user_info[4] if user_info else 'ar'
            
            name = item[1] if lang == 'ar' else item[2]
            price = int(item[6] * 100)  # تحويل لسنت
            
            # إنشاء جلسة دفع
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://t.me/your_bot?start=payment_success_{user_id}_{item_id}',
                cancel_url=f'https://t.me/your_bot?start=payment_cancel_{user_id}_{item_id}',
                metadata={
                    'user_id': str(user_id),
                    'item_id': str(item_id),
                    'bot_purchase': 'true'
                }
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Error creating Stripe payment link: {e}")
            return None
    
    def create_purchase_record(self, user_id, item_id, payment_method, amount_points=0, amount_usd=0):
        """إنشاء سجل الشراء"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        purchase_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO purchases (id, user_id, item_id, payment_method, 
                                 amount_points, amount_usd, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (purchase_id, user_id, item_id, payment_method, amount_points, amount_usd, 'completed'))
        
        conn.commit()
        conn.close()
        
        return purchase_id
    
    def apply_purchase(self, user_id, item, purchase_id):
        """تطبيق المنتج المشترى"""
        category = item[7]
        
        if category == 'points':
            # إضافة نقاط
            if '100' in item[1] or '100' in item[2]:
                self.db.add_points(user_id, 100, "Points package purchase")
            elif '500' in item[1] or '500' in item[2]:
                self.db.add_points(user_id, 500, "Points package purchase")
        
        elif category == 'vip':
            # تفعيل VIP
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # تحديد مدة الاشتراك
            if 'شهري' in item[1] or 'Monthly' in item[2]:
                vip_duration = 30
            elif 'سنوي' in item[1] or 'Yearly' in item[2]:
                vip_duration = 365
            else:
                vip_duration = 30
            
            vip_expires = datetime.now() + timedelta(days=vip_duration)
            
            cursor.execute('''
                UPDATE users 
                SET is_vip = TRUE, vip_expires = ?
                WHERE user_id = ?
            ''', (vip_expires, user_id))
            
            conn.commit()
            conn.close()
    
    def get_user_purchases(self, user_id):
        """الحصول على مشتريات المستخدم"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, s.name_ar, s.name_en, p.payment_method,
                   p.amount_points, p.amount_usd, p.purchase_date, p.status
            FROM purchases p
            JOIN shop_items s ON p.item_id = s.id
            WHERE p.user_id = ?
            ORDER BY p.purchase_date DESC
        ''', (user_id,))
        purchases = cursor.fetchall()
        conn.close()
        return purchases
    
    def create_purchases_menu(self, user_id):
        """إنشاء قائمة المشتريات"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        purchases = self.get_user_purchases(user_id)
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        if not purchases:
            text = self.get_text(user_id, 'no_purchases')
        else:
            text = f"{self.get_text(user_id, 'my_purchases')}\n\n"
            
            for purchase in purchases:
                name = purchase[1] if lang == 'ar' else purchase[2]
                date = datetime.strptime(purchase[6], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                
                if purchase[3] == 'points':
                    price_info = f"{purchase[4]} نقطة"
                else:
                    price_info = f"${purchase[5]}"
                
                status_emoji = "✅" if purchase[7] == 'completed' else "⏳"
                
                text += f"{status_emoji} {name}\n"
                text += f"💰 {price_info} | 📅 {date}\n\n"
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'back_to_shop'), callback_data='shop')]
        ]
        
        return text, InlineKeyboardMarkup(keyboard)

# إنشاء مثيل من نظام المتجر
shop_system = ShopSystem()

