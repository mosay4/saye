import openai
import os
from database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIChatSystem:
    def __init__(self):
        self.db = db
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # حفظ تاريخ المحادثات
        self.conversation_history = {}
    
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'ai_chat': '🤖 الذكاء الاصطناعي',
                'ask_question': 'اسأل سؤالك حول الأمن السيبراني:',
                'thinking': '🤔 جاري التفكير...',
                'error_occurred': '❌ حدث خطأ، حاول مرة أخرى',
                'clear_chat': '🗑️ مسح المحادثة',
                'back_to_menu': '🔙 العودة للقائمة',
                'chat_cleared': '✅ تم مسح المحادثة',
                'sample_questions': 'أسئلة مقترحة:',
                'what_is_phishing': 'ما هو التصيد الإلكتروني؟',
                'how_to_secure_password': 'كيف أحمي كلمة المرور؟',
                'latest_threats': 'ما أحدث التهديدات؟',
                'security_tips': 'نصائح أمنية للمبتدئين',
                'main_menu': '🏠 القائمة الرئيسية'
            },
            'en': {
                'ai_chat': '🤖 AI Chat',
                'ask_question': 'Ask your cybersecurity question:',
                'thinking': '🤔 Thinking...',
                'error_occurred': '❌ An error occurred, please try again',
                'clear_chat': '🗑️ Clear Chat',
                'back_to_menu': '🔙 Back to Menu',
                'chat_cleared': '✅ Chat cleared',
                'sample_questions': 'Suggested questions:',
                'what_is_phishing': 'What is phishing?',
                'how_to_secure_password': 'How to secure passwords?',
                'latest_threats': 'What are the latest threats?',
                'security_tips': 'Security tips for beginners',
                'main_menu': '🏠 Main Menu'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def get_system_prompt(self, user_id):
        """الحصول على prompt النظام حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        if lang == 'ar':
            return """أنت CyberBot AI، خبير في الأمن السيبراني ومساعد تعليمي ذكي.

مهامك:
1. الإجابة على أسئلة الأمن السيبراني بطريقة واضحة ومفهومة
2. تقديم نصائح عملية وقابلة للتطبيق
3. شرح المفاهيم المعقدة بطريقة بسيطة
4. تحديث المستخدمين بأحدث التهديدات والحلول
5. تقديم أمثلة عملية عند الحاجة

قواعد مهمة:
- استخدم اللغة العربية في الإجابة
- اجعل إجاباتك مختصرة ومفيدة (200-400 كلمة)
- استخدم الرموز التعبيرية المناسبة
- قدم نصائح عملية قابلة للتطبيق
- إذا كان السؤال خارج نطاق الأمن السيبراني، وجه المستخدم بلطف للموضوع الصحيح
- لا تقدم معلومات قد تُستخدم لأغراض ضارة"""
        else:
            return """You are CyberBot AI, a cybersecurity expert and intelligent educational assistant.

Your tasks:
1. Answer cybersecurity questions clearly and understandably
2. Provide practical and applicable advice
3. Explain complex concepts in simple terms
4. Update users on the latest threats and solutions
5. Provide practical examples when needed

Important rules:
- Use English in your responses
- Keep your answers concise and useful (200-400 words)
- Use appropriate emojis
- Provide practical, actionable advice
- If the question is outside cybersecurity scope, gently redirect the user to the correct topic
- Do not provide information that could be used for malicious purposes"""
    
    def create_ai_chat_menu(self, user_id):
        """إنشاء قائمة الذكاء الاصطناعي"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'what_is_phishing'), 
                                callback_data='ai_ask_phishing')],
            [InlineKeyboardButton(self.get_text(user_id, 'how_to_secure_password'), 
                                callback_data='ai_ask_password')],
            [InlineKeyboardButton(self.get_text(user_id, 'latest_threats'), 
                                callback_data='ai_ask_threats')],
            [InlineKeyboardButton(self.get_text(user_id, 'security_tips'), 
                                callback_data='ai_ask_tips')],
            [
                InlineKeyboardButton(self.get_text(user_id, 'clear_chat'), 
                                   callback_data='ai_clear'),
                InlineKeyboardButton(self.get_text(user_id, 'main_menu'), 
                                   callback_data='main_menu')
            ]
        ]
        
        text = f"{self.get_text(user_id, 'ai_chat')}\n\n"
        text += f"{self.get_text(user_id, 'ask_question')}\n\n"
        text += f"{self.get_text(user_id, 'sample_questions')}"
        
        return text, InlineKeyboardMarkup(keyboard)
    
    def get_conversation_history(self, user_id, limit=5):
        """الحصول على تاريخ المحادثة"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        return self.conversation_history[user_id][-limit*2:]  # آخر 5 أسئلة وإجابات
    
    def add_to_conversation(self, user_id, role, content):
        """إضافة رسالة لتاريخ المحادثة"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # الاحتفاظ بآخر 20 رسالة فقط
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def clear_conversation(self, user_id):
        """مسح تاريخ المحادثة"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
    
    def get_predefined_answer(self, user_id, question_type):
        """الحصول على إجابات محددة مسبقاً للأسئلة الشائعة"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        predefined_questions = {
            'ar': {
                'phishing': 'ما هو التصيد الإلكتروني وكيف أحمي نفسي منه؟',
                'password': 'كيف أنشئ كلمة مرور قوية وآمنة؟',
                'threats': 'ما هي أحدث التهديدات السيبرانية التي يجب أن أعرفها؟',
                'tips': 'ما هي أهم النصائح الأمنية للمبتدئين في الأمن السيبراني؟'
            },
            'en': {
                'phishing': 'What is phishing and how can I protect myself from it?',
                'password': 'How do I create a strong and secure password?',
                'threats': 'What are the latest cyber threats I should know about?',
                'tips': 'What are the most important security tips for cybersecurity beginners?'
            }
        }
        
        question = predefined_questions.get(lang, predefined_questions['ar']).get(question_type, '')
        
        if question:
            return self.ask_ai(user_id, question)
        
        return None
    
    def ask_ai(self, user_id, question):
        """طرح سؤال على الذكاء الاصطناعي"""
        try:
            # إضافة السؤال لتاريخ المحادثة
            self.add_to_conversation(user_id, "user", question)
            
            # بناء رسائل المحادثة
            messages = [
                {"role": "system", "content": self.get_system_prompt(user_id)}
            ]
            
            # إضافة تاريخ المحادثة
            history = self.get_conversation_history(user_id)
            for msg in history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # إضافة السؤال الحالي إذا لم يكن في التاريخ
            if not history or history[-1]["content"] != question:
                messages.append({"role": "user", "content": question})
            
            # استدعاء OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            answer = response.choices[0].message.content.strip()
            
            # إضافة الإجابة لتاريخ المحادثة
            self.add_to_conversation(user_id, "assistant", answer)
            
            # خصم نقاط للاستخدام (إذا لم يكن VIP)
            user_info = self.db.get_user_info(user_id)
            is_vip = user_info[11] if len(user_info) > 11 else False
            
            if not is_vip:
                # خصم نقطة واحدة لكل سؤال
                success, message = self.db.spend_points(user_id, 1, "AI Chat Question")
                if not success:
                    return "⚠️ نقاطك غير كافية لاستخدام الذكاء الاصطناعي. احصل على المزيد من النقاط من خلال إكمال الدروس!"
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return self.get_text(user_id, 'error_occurred')
    
    def create_ai_response_menu(self, user_id):
        """إنشاء قائمة بعد الإجابة"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton(self.get_text(user_id, 'clear_chat'), 
                                   callback_data='ai_clear'),
                InlineKeyboardButton(self.get_text(user_id, 'back_to_menu'), 
                                   callback_data='ai_chat')
            ],
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), 
                                callback_data='main_menu')]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_usage_stats(self, user_id):
        """الحصول على إحصائيات الاستخدام"""
        history = self.get_conversation_history(user_id)
        user_questions = [msg for msg in history if msg["role"] == "user"]
        
        return {
            'total_questions': len(user_questions),
            'today_questions': len([q for q in user_questions 
                                  if q["timestamp"].date() == datetime.now().date()])
        }

# إنشاء مثيل من نظام الذكاء الاصطناعي
ai_chat_system = AIChatSystem()

