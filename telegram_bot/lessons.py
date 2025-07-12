from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db
import random

class LessonsManager:
    def __init__(self):
        self.db = db
    
    def get_text(self, user_id, key):
        """الحصول على النص حسب لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        lang = user_info[4] if user_info else 'ar'
        
        texts = {
            'ar': {
                'lessons_menu': '📚 الدروس التعليمية',
                'choose_level': 'اختر مستواك:',
                'beginner': '🟢 مبتدئ',
                'intermediate': '🟡 متوسط', 
                'advanced': '🔴 متقدم',
                'lesson_completed': '✅ مكتمل',
                'lesson_locked': '🔒 مقفل',
                'start_lesson': '▶️ بدء الدرس',
                'take_quiz': '📝 اختبار',
                'lesson_progress': 'التقدم: {}/{}',
                'points_earned': 'حصلت على {} نقطة!',
                'quiz_question': 'السؤال {}/{}',
                'correct_answer': '✅ إجابة صحيحة!',
                'wrong_answer': '❌ إجابة خاطئة',
                'quiz_completed': 'انتهى الاختبار!\nالنتيجة: {}/{}\nالنقاط المكتسبة: {}',
                'back_to_lessons': '🔙 العودة للدروس',
                'next_lesson': '➡️ الدرس التالي',
                'main_menu': '🏠 القائمة الرئيسية'
            },
            'en': {
                'lessons_menu': '📚 Educational Lessons',
                'choose_level': 'Choose your level:',
                'beginner': '🟢 Beginner',
                'intermediate': '🟡 Intermediate',
                'advanced': '🔴 Advanced',
                'lesson_completed': '✅ Completed',
                'lesson_locked': '🔒 Locked',
                'start_lesson': '▶️ Start Lesson',
                'take_quiz': '📝 Quiz',
                'lesson_progress': 'Progress: {}/{}',
                'points_earned': 'You earned {} points!',
                'quiz_question': 'Question {}/{}',
                'correct_answer': '✅ Correct answer!',
                'wrong_answer': '❌ Wrong answer',
                'quiz_completed': 'Quiz completed!\nScore: {}/{}\nPoints earned: {}',
                'back_to_lessons': '🔙 Back to Lessons',
                'next_lesson': '➡️ Next Lesson',
                'main_menu': '🏠 Main Menu'
            }
        }
        
        return texts.get(lang, texts['ar']).get(key, key)
    
    def create_levels_menu(self, user_id):
        """إنشاء قائمة المستويات"""
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'beginner'), callback_data='level_beginner')],
            [InlineKeyboardButton(self.get_text(user_id, 'intermediate'), callback_data='level_intermediate')],
            [InlineKeyboardButton(self.get_text(user_id, 'advanced'), callback_data='level_advanced')],
            [InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_lessons_by_level(self, level):
        """الحصول على الدروس حسب المستوى"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE level = ? ORDER BY id', (level,))
        lessons = cursor.fetchall()
        conn.close()
        return lessons
    
    def get_user_progress(self, user_id, level):
        """الحصول على تقدم المستخدم في مستوى معين"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.id, up.completed 
            FROM lessons l 
            LEFT JOIN user_progress up ON l.id = up.lesson_id AND up.user_id = ?
            WHERE l.level = ?
            ORDER BY l.id
        ''', (user_id, level))
        progress = cursor.fetchall()
        conn.close()
        return progress
    
    def create_lessons_menu(self, user_id, level):
        """إنشاء قائمة الدروس لمستوى معين"""
        lessons = self.get_lessons_by_level(level)
        progress = self.get_user_progress(user_id, level)
        
        # تحويل التقدم إلى قاموس للوصول السريع
        progress_dict = {lesson_id: completed for lesson_id, completed in progress}
        
        keyboard = []
        for lesson in lessons:
            lesson_id = lesson[0]
            title = lesson[1] if self.get_user_language(user_id) == 'ar' else lesson[2]
            
            # تحديد حالة الدرس
            is_completed = progress_dict.get(lesson_id, False)
            
            if is_completed:
                status = self.get_text(user_id, 'lesson_completed')
            else:
                status = ""
            
            button_text = f"{title} {status}"
            callback_data = f"lesson_{lesson_id}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        # إضافة أزرار التنقل
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_lessons'), callback_data='lessons')])
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'main_menu'), callback_data='main_menu')])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_user_language(self, user_id):
        """الحصول على لغة المستخدم"""
        user_info = self.db.get_user_info(user_id)
        return user_info[4] if user_info else 'ar'
    
    def get_lesson_content(self, user_id, lesson_id):
        """الحصول على محتوى الدرس"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        lesson = cursor.fetchone()
        conn.close()
        
        if not lesson:
            return None
        
        lang = self.get_user_language(user_id)
        title = lesson[1] if lang == 'ar' else lesson[2]
        content = lesson[3] if lang == 'ar' else lesson[4]
        
        # التحقق من إكمال الدرس
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT completed FROM user_progress WHERE user_id = ? AND lesson_id = ?', 
                      (user_id, lesson_id))
        progress = cursor.fetchone()
        conn.close()
        
        is_completed = progress and progress[0]
        
        # إنشاء الأزرار
        keyboard = []
        if not is_completed:
            keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'take_quiz'), 
                                                callback_data=f"quiz_{lesson_id}")])
        
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_lessons'), 
                                            callback_data=f"level_{lesson[5]}")])
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'main_menu'), 
                                            callback_data='main_menu')])
        
        return {
            'title': title,
            'content': content,
            'keyboard': InlineKeyboardMarkup(keyboard),
            'is_completed': is_completed
        }
    
    def create_sample_quizzes(self):
        """إنشاء اختبارات تجريبية"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # التحقق من وجود اختبارات
        cursor.execute('SELECT COUNT(*) FROM quizzes')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        sample_quizzes = [
            {
                'lesson_id': 1,
                'question_ar': 'ما هو الهدف الرئيسي من الأمن السيبراني؟',
                'question_en': 'What is the main goal of cybersecurity?',
                'option_a_ar': 'حماية البيانات والأنظمة',
                'option_a_en': 'Protect data and systems',
                'option_b_ar': 'زيادة سرعة الإنترنت',
                'option_b_en': 'Increase internet speed',
                'option_c_ar': 'تطوير البرمجيات',
                'option_c_en': 'Develop software',
                'option_d_ar': 'بيع المنتجات',
                'option_d_en': 'Sell products',
                'correct_answer': 'A',
                'explanation_ar': 'الهدف الرئيسي من الأمن السيبراني هو حماية البيانات والأنظمة من التهديدات.',
                'explanation_en': 'The main goal of cybersecurity is to protect data and systems from threats.'
            },
            {
                'lesson_id': 2,
                'question_ar': 'أي من التالي يعتبر نوعاً من البرمجيات الخبيثة؟',
                'question_en': 'Which of the following is a type of malware?',
                'option_a_ar': 'متصفح الويب',
                'option_a_en': 'Web browser',
                'option_b_ar': 'فيروس الحاسوب',
                'option_b_en': 'Computer virus',
                'option_c_ar': 'نظام التشغيل',
                'option_c_en': 'Operating system',
                'option_d_ar': 'برنامج الرسم',
                'option_d_en': 'Drawing software',
                'correct_answer': 'B',
                'explanation_ar': 'فيروس الحاسوب هو نوع من البرمجيات الخبيثة المصممة لإلحاق الضرر بالنظام.',
                'explanation_en': 'Computer virus is a type of malware designed to damage the system.'
            }
        ]
        
        for quiz in sample_quizzes:
            cursor.execute('''
                INSERT INTO quizzes (lesson_id, question_ar, question_en, option_a_ar, option_a_en,
                                   option_b_ar, option_b_en, option_c_ar, option_c_en, 
                                   option_d_ar, option_d_en, correct_answer, explanation_ar, explanation_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (quiz['lesson_id'], quiz['question_ar'], quiz['question_en'],
                  quiz['option_a_ar'], quiz['option_a_en'], quiz['option_b_ar'], quiz['option_b_en'],
                  quiz['option_c_ar'], quiz['option_c_en'], quiz['option_d_ar'], quiz['option_d_en'],
                  quiz['correct_answer'], quiz['explanation_ar'], quiz['explanation_en']))
        
        conn.commit()
        conn.close()
    
    def get_quiz_questions(self, lesson_id):
        """الحصول على أسئلة الاختبار للدرس"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quizzes WHERE lesson_id = ?', (lesson_id,))
        questions = cursor.fetchall()
        conn.close()
        return questions
    
    def create_quiz_question(self, user_id, lesson_id, question_index=0):
        """إنشاء سؤال الاختبار"""
        questions = self.get_quiz_questions(lesson_id)
        
        if not questions or question_index >= len(questions):
            return None
        
        question = questions[question_index]
        lang = self.get_user_language(user_id)
        
        question_text = question[2] if lang == 'ar' else question[3]
        options = [
            (question[4] if lang == 'ar' else question[5], 'A'),  # Option A
            (question[6] if lang == 'ar' else question[7], 'B'),  # Option B
            (question[8] if lang == 'ar' else question[9], 'C'),  # Option C
            (question[10] if lang == 'ar' else question[11], 'D') # Option D
        ]
        
        # خلط الخيارات
        random.shuffle(options)
        
        keyboard = []
        for option_text, option_letter in options:
            callback_data = f"answer_{lesson_id}_{question_index}_{option_letter}"
            keyboard.append([InlineKeyboardButton(option_text, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton(self.get_text(user_id, 'back_to_lessons'), 
                                            callback_data=f"lesson_{lesson_id}")])
        
        header = self.get_text(user_id, 'quiz_question').format(question_index + 1, len(questions))
        full_text = f"{header}\n\n{question_text}"
        
        return {
            'text': full_text,
            'keyboard': InlineKeyboardMarkup(keyboard),
            'correct_answer': question[12],
            'explanation': question[13] if lang == 'ar' else question[14],
            'total_questions': len(questions)
        }
    
    def complete_lesson(self, user_id, lesson_id, quiz_score=0):
        """إكمال الدرس ومنح النقاط"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # التحقق من إكمال الدرس مسبقاً
        cursor.execute('SELECT completed FROM user_progress WHERE user_id = ? AND lesson_id = ?', 
                      (user_id, lesson_id))
        existing = cursor.fetchone()
        
        if existing and existing[0]:
            conn.close()
            return False, 0  # الدرس مكتمل مسبقاً
        
        # الحصول على نقاط الدرس
        cursor.execute('SELECT points_reward FROM lessons WHERE id = ?', (lesson_id,))
        lesson_points = cursor.fetchone()[0]
        
        # حساب النقاط الإضافية حسب نتيجة الاختبار
        bonus_points = quiz_score * 2  # نقطتان إضافيتان لكل إجابة صحيحة
        total_points = lesson_points + bonus_points
        
        # تحديث أو إدراج التقدم
        if existing:
            cursor.execute('''
                UPDATE user_progress 
                SET completed = TRUE, quiz_score = ?, completion_date = CURRENT_TIMESTAMP
                WHERE user_id = ? AND lesson_id = ?
            ''', (quiz_score, user_id, lesson_id))
        else:
            cursor.execute('''
                INSERT INTO user_progress (user_id, lesson_id, completed, quiz_score, completion_date)
                VALUES (?, ?, TRUE, ?, CURRENT_TIMESTAMP)
            ''', (user_id, lesson_id, quiz_score))
        
        # إضافة النقاط للمستخدم
        cursor.execute('UPDATE users SET points = points + ?, total_lessons_completed = total_lessons_completed + 1 WHERE user_id = ?', 
                      (total_points, user_id))
        
        # تسجيل تاريخ النقاط
        cursor.execute('''
            INSERT INTO points_history (user_id, points, reason, transaction_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, total_points, f'Completed lesson {lesson_id}', 'earned'))
        
        conn.commit()
        conn.close()
        
        return True, total_points

# إنشاء مثيل من مدير الدروس
lessons_manager = LessonsManager()

