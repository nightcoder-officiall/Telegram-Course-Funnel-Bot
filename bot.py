# bot.py - Main bot entry point

import telebot
import logging
import threading
import time
import uuid
import random
from datetime import datetime, timedelta
from telebot import types
from config import *
from database import DatabaseManager
from admin import AdminPanel
from messages import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.db = DatabaseManager()
        self.admin = AdminPanel(self.bot, self.db)
        
        # Timer management
        self.timers = {}
        self.final_photo_timers = {}
        
        # Load pending timers from DB
        self.timers = self.db.get_pending_timers()
        self.final_photo_timers = self.db.get_pending_final_photo_timers()

        self.setup_handlers()
        
        # Start background threads
        threading.Thread(target=self.reminder_worker, daemon=True).start()
        threading.Thread(target=self.final_photo_worker, daemon=True).start()
    
    def setup_handlers(self):
        """Initialize all bot message handlers."""
        
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.handle_start_command(message)
        
        @self.bot.message_handler(content_types=['text', 'photo', 'video', 'animation'])
        def handle_text_message(message):
            self.handle_text_message(message)
        
        @self.bot.message_handler(content_types=['contact'])
        def handle_contact(message):
            self.handle_contact_message(message)
        
        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            if self.admin.is_admin(message.from_user.id):
                self.admin.handle_admin_message(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            self.handle_callback_query(call)
    
    def handle_start_command(self, message):
        """Handle /start command."""
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            
            if self.admin.is_admin(user_id):
                self.admin.show_admin_menu(message.chat.id)
                return
            
            if self.db.user_exists(user_id):
                user_data = self.db.get_user_data(user_id)
                if user_data and user_data.get('is_completed'):
                    self.bot.send_message(message.chat.id, "شما قبلاً فرآیند ثبت‌نام را تکمیل کرده‌اید! ✅")
                    return
                else:
                    state = self.db.get_user_state(user_id)
                    self.resume_user_flow(message, state)
                    return
            
            self.db.add_user(user_id, username, first_name, last_name)
            self.send_welcome_messages(message)
            
        except Exception as e:
            logging.error(f"Error in start command: {e}")
            self.bot.send_message(message.chat.id, error_general)
    
    def resume_user_flow(self, message, state):
        """Resume user interaction based on last state."""
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            if state == UserState.WAITING_NAME:
                self.bot.send_message(chat_id, name_request)
            elif state == UserState.WAITING_FIRST_CHECK:
                self.send_first_follow_up(chat_id, user_id)
            elif state == UserState.WAITING_SECOND_CHECK:
                self.send_second_follow_up(chat_id, user_id)
            elif state == UserState.WAITING_RATING:
                self.bot.send_message(chat_id, rating_request)
            elif state == UserState.WAITING_PHONE:
                self.request_phone_number_keyboard(chat_id)
            elif state == UserState.WAITING_CONTACT_TIME:
                self.send_contact_time_question(chat_id)
            else:
                user_data = self.db.get_user_data(user_id)
                if user_data and user_data.get('name'):
                    self.send_new_intro_messages(message, user_data['name'])
                else:
                    self.bot.send_message(chat_id, name_request)
                    self.db.update_user_state(user_id, UserState.WAITING_NAME)
                    
        except Exception as e:
            logging.error(f"Error resuming user flow: {e}")
    
    def send_welcome_messages(self, message):
        """Send initial welcome messages."""
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            self.bot.send_message(chat_id, msg_1)
            time.sleep(1)
            
            self.bot.send_message(chat_id, name_request)
            self.db.update_user_state(user_id, UserState.WAITING_NAME)
            
        except Exception as e:
            logging.error(f"Error sending welcome messages: {e}")
    
    def send_new_intro_messages(self, message, name):
        """Send intro sequence after name is received."""
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            self.bot.send_message(chat_id, msg_three_steps)
            time.sleep(2)
            
            self.bot.send_message(chat_id, msg_voice_instruction)
            time.sleep(2)
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📱 دنبال کردن اینستاگرام", url=f"https://{instagram_link}"))
            
            self.bot.send_message(chat_id, msg_instagram, reply_markup=markup)
            time.sleep(2)
            
            self.send_expert_content(chat_id, user_id, name)
            
        except Exception as e:
            logging.error(f"Error sending new intro messages: {e}")
    
    def send_expert_content(self, chat_id, user_id, name):
        """Select expert and send their content."""
        try:
            expert = self.select_random_expert()
            self.db.save_selected_expert(user_id, expert)
            
            if expert == "forough":
                if FOROUGH_PHOTO_FILE_ID:
                    self.bot.send_photo(chat_id, FOROUGH_PHOTO_FILE_ID)
                if FOROUGH_VOICE_1_FILE_ID:
                    self.bot.send_voice(chat_id, FOROUGH_VOICE_1_FILE_ID)
            else:
                if SADEGH_PHOTO_FILE_ID:
                    self.bot.send_photo(chat_id, SADEGH_PHOTO_FILE_ID)
                if SADEGH_VOICE_1_FILE_ID:
                    self.bot.send_voice(chat_id, SADEGH_VOICE_1_FILE_ID)
            
            time.sleep(2)
            self.start_questions(chat_id, user_id, name)
            
        except Exception as e:
            logging.error(f"Error sending expert content: {e}")
    
    def select_random_expert(self):
        """Select random expert (60% Forough, 40% Sadegh)."""
        return "forough" if random.random() < 0.6 else "sadegh"
    
    def handle_text_message(self, message):
        """Handle standard text messages."""
        try:
            user_id = message.from_user.id
            
            if self.admin.is_admin(user_id):
                self.admin.handle_admin_message(message)
                return
            
            state = self.db.get_user_state(user_id)
            
            if state == UserState.WAITING_NAME:
                self.handle_name_input(message)
            elif state == UserState.WAITING_RATING:
                self.handle_rating_input(message)
                
        except Exception as e:
            logging.error(f"Error handling text message: {e}")
    
    def handle_name_input(self, message):
        """Process user name input."""
        try:
            user_id = message.from_user.id
            name = message.text.strip()
            
            if len(name) < 2:
                self.bot.send_message(message.chat.id, "لطفاً نام معتبری وارد کنید.")
                return
            
            self.db.update_user_name(user_id, name)
            self.send_new_intro_messages(message, name)
            
        except Exception as e:
            logging.error(f"Error handling name input: {e}")
    
    def start_questions(self, chat_id, user_id, name):
        """Begin the questionnaire."""
        try:
            question_text = question_1.format(name=name)
            markup = self.create_question_markup(question_1_options, "q1_")
            
            sent_message = self.bot.send_message(chat_id, question_text, reply_markup=markup)
            
            self.db.save_message_id(user_id, sent_message.message_id, "question")
            self.db.update_user_state(user_id, UserState.QUESTION_1)
            
        except Exception as e:
            logging.error(f"Error starting questions: {e}")
    
    def create_question_markup(self, options, prefix):
        """Generate inline keyboard for questions."""
        markup = types.InlineKeyboardMarkup()
        for i, option in enumerate(options):
            markup.add(types.InlineKeyboardButton(option, callback_data=f"{prefix}{i}"))
        return markup
    
    def handle_callback_query(self, call):
        """Handle inline button clicks."""
        try:
            user_id = call.from_user.id
            data = call.data
            
            if self.admin.is_admin(user_id) and data.startswith('bulk_'):
                self.admin.handle_bulk_callback(call)
                return
            
            if data.startswith('q1_'):
                self.handle_question_1_answer(call)
            elif data.startswith('q2_'):
                self.handle_question_2_answer(call)
            elif data.startswith('q3_'):
                self.handle_question_3_answer(call)
            elif data.startswith('q4_'):
                self.handle_question_4_answer(call)
            elif data.startswith('follow1_'):
                self.handle_follow_up_1(call)
            elif data.startswith('follow2_'):
                self.handle_follow_up_2(call)
            elif data.startswith('contact_'):
                self.handle_contact_time(call)
            elif data == 'get_consultation':
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
                self.send_important_voice(call.message.chat.id, user_id)
                
        except Exception as e:
            logging.error(f"Error handling callback: {e}")
    
    def handle_question_1_answer(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            answer = question_1_options[option_index]
            
            self.db.update_question_answer(user_id, 1, answer)
            markup = self.create_question_markup(question_2_options, "q2_")
            
            self.bot.edit_message_text(question_2, call.message.chat.id, call.message.message_id, reply_markup=markup)
            self.db.update_user_state(user_id, UserState.QUESTION_2)
            
        except Exception as e:
            logging.error(f"Error handling question 1 answer: {e}")
    
    def handle_question_2_answer(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            answer = question_2_options[option_index]
            
            self.db.update_question_answer(user_id, 2, answer)
            markup = self.create_question_markup(question_3_options, "q3_")
            
            self.bot.edit_message_text(question_3, call.message.chat.id, call.message.message_id, reply_markup=markup)
            self.db.update_user_state(user_id, UserState.QUESTION_3)
            
        except Exception as e:
            logging.error(f"Error handling question 2 answer: {e}")
    
    def handle_question_3_answer(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            answer = question_3_options[option_index]
            
            self.db.update_question_answer(user_id, 3, answer)
            markup = self.create_question_markup(question_4_options, "q4_")
            
            self.bot.edit_message_text(question_4, call.message.chat.id, call.message.message_id, reply_markup=markup)
            self.db.update_user_state(user_id, UserState.QUESTION_4)
            
        except Exception as e:
            logging.error(f"Error handling question 3 answer: {e}")
    
    def handle_question_4_answer(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            answer = question_4_options[option_index]
            
            self.db.update_question_answer(user_id, 4, answer)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.complete_registration(call.message.chat.id, user_id)
            
        except Exception as e:
            logging.error(f"Error handling question 4 answer: {e}")
    
    def complete_registration(self, chat_id, user_id):
        """Finalize registration and provide course link."""
        try:
            user_data = self.db.get_user_data(user_id)
            name = user_data.get('name', 'کاربر')
            
            invite_link = self.generate_invite_link()
            channel_link = channel_link_template.format(invite_link=invite_link)
            
            self.db.update_channel_link(user_id, channel_link)
            
            success_msg = registration_success.format(name=name)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎥 مشاهده مینی دوره", url=channel_link))
            
            self.bot.send_message(chat_id, success_msg, reply_markup=markup)
            time.sleep(2)
            
            self.bot.send_message(chat_id, watch_reminder)
            self.schedule_reminders(user_id, chat_id)
            
            self.db.update_user_state(user_id, UserState.WAITING_FIRST_CHECK)
            
        except Exception as e:
            logging.error(f"Error completing registration: {e}")
    
    def generate_invite_link(self):
        """Generate single-use invite link."""
        try:
            invite_link = self.bot.create_chat_invite_link(
                chat_id=MINI_COURSE_CHANNEL_ID,
                member_limit=1
            )
            return invite_link.invite_link
        except Exception as e:
            logging.error(f"Error generating invite link: {e}")
            return "https://t.me/your_default_link"
    
    def schedule_reminders(self, user_id, chat_id):
        """Set up follow-up timers."""
        now = datetime.now()
        first_reminder = now + timedelta(seconds=FIRST_REMINDER_DELAY)
        second_reminder = first_reminder + timedelta(seconds=SECOND_REMINDER_DELAY)
        
        self.db.add_timer(user_id, first_reminder, second_reminder)
        self.timers[user_id] = {
            'first_reminder': first_reminder,
            'second_reminder': second_reminder,
            'chat_id': chat_id
        }
    
    def reminder_worker(self):
        """Background thread for checking timers."""
        while True:
            try:
                now = datetime.now()
                completed_timers = []
                
                for user_id, timer_data in self.timers.items():
                    if (timer_data.get('first_reminder') and 
                        now >= timer_data['first_reminder'] and 
                        not timer_data.get('first_sent')):
                        
                        self.send_first_follow_up(timer_data['chat_id'], user_id)
                        self.timers[user_id]['first_sent'] = True
                    
                    if (timer_data.get('second_reminder') and 
                        now >= timer_data['second_reminder'] and 
                        not timer_data.get('second_sent')):
                        
                        self.send_second_follow_up(timer_data['chat_id'], user_id)
                        self.timers[user_id]['second_sent'] = True
                        completed_timers.append(user_id)
                
                for user_id in completed_timers:
                    del self.timers[user_id]
                
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"Error in reminder worker: {e}")
                time.sleep(60)
    
    def final_photo_worker(self):
        """Background thread for final photo timer."""
        while True:
            try:
                now = datetime.now()
                completed_timers = []
                
                for user_id, timer_data in self.final_photo_timers.items():
                    if now >= timer_data['send_time'] and not timer_data.get('sent'):
                        self.send_final_photo(timer_data['chat_id'], user_id)
                        self.final_photo_timers[user_id]['sent'] = True
                        completed_timers.append(user_id)
                
                for user_id in completed_timers:
                    del self.final_photo_timers[user_id]
                
                time.sleep(300)
                
            except Exception as e:
                logging.error(f"Error in final photo worker: {e}")
                time.sleep(300)
    
    def send_first_follow_up(self, chat_id, user_id):
        try:
            markup = self.create_question_markup(follow_up_1_options, "follow1_")
            self.bot.send_message(chat_id, follow_up_1, reply_markup=markup)
            self.db.update_user_state(user_id, UserState.WAITING_FIRST_CHECK)
        except Exception as e:
            logging.error(f"Error sending first follow up: {e}")
    
    def send_second_follow_up(self, chat_id, user_id):
        try:
            markup = self.create_question_markup(follow_up_2_options, "follow2_")
            self.bot.send_message(chat_id, follow_up_2, reply_markup=markup)
            self.db.update_user_state(user_id, UserState.WAITING_SECOND_CHECK)
        except Exception as e:
            logging.error(f"Error sending second follow up: {e}")
    
    def handle_follow_up_1(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            
            if user_id in self.timers:
                del self.timers[user_id]
            
            if option_index == 0:
                self.proceed_to_rating(call)
            else:
                user_data = self.db.get_user_data(user_id)
                channel_link = user_data.get('channel_link', '')
                
                markup = types.InlineKeyboardMarkup()
                if channel_link:
                    markup.add(types.InlineKeyboardButton("🎥 مشاهده مینی دوره", url=channel_link))
                
                self.bot.edit_message_text(no_time_response, call.message.chat.id, call.message.message_id, reply_markup=markup)
                
                now = datetime.now()
                second_reminder = now + timedelta(seconds=SECOND_REMINDER_DELAY)
                
                self.timers[user_id] = {
                    'second_reminder': second_reminder,
                    'chat_id': call.message.chat.id
                }
            
        except Exception as e:
            logging.error(f"Error handling follow up 1: {e}")
    
    def handle_follow_up_2(self, call):
        try:
            self.proceed_to_rating(call)
        except Exception as e:
            logging.error(f"Error handling follow up 2: {e}")
    
    def proceed_to_rating(self, call):
        try:
            user_id = call.from_user.id
            self.bot.edit_message_text(rating_request, call.message.chat.id, call.message.message_id)
            self.db.update_user_state(user_id, UserState.WAITING_RATING)
        except Exception as e:
            logging.error(f"Error proceeding to rating: {e}")
    
    def handle_rating_input(self, message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            self.send_course_introduction(chat_id, user_id)
            self.db.update_user_state(user_id, UserState.WAITING_PHONE)
            self.schedule_final_photo(user_id, chat_id)
        except Exception as e:
            logging.error(f"Error handling rating input: {e}")
    
    def send_course_introduction(self, chat_id, user_id):
            try:
                self.bot.send_message(chat_id, course_intro)
                time.sleep(2)
                
                self.bot.send_message(chat_id, testimonial_intro)
                if TESTIMONIAL_VIDEO_FILE_ID:
                    self.bot.send_video(chat_id, TESTIMONIAL_VIDEO_FILE_ID)
                else:
                    self.bot.send_message(chat_id, "ویدیو نظرات اینجا ارسال می‌شود")
                
                time.sleep(2)
                
                self.bot.send_message(chat_id, success_stories)
                if SUCCESS_STORIES_VIDEO_FILE_ID:
                    self.bot.send_video(chat_id, SUCCESS_STORIES_VIDEO_FILE_ID)
                else:
                    self.bot.send_message(chat_id, "ویدیو")
                
                time.sleep(2)
                self.send_important_voice(chat_id, user_id)
                
            except Exception as e:
                logging.error(f"Error sending course introduction: {e}")
        
    def send_important_voice(self, chat_id, user_id):
        try:
            self.bot.send_message(chat_id, important_voice_msg)
            time.sleep(1)
            
            expert = self.db.get_selected_expert(user_id)
            
            if expert == "forough" and FOROUGH_VOICE_2_FILE_ID:
                self.bot.send_voice(chat_id, FOROUGH_VOICE_2_FILE_ID)
            elif expert == "sadegh" and SADEGH_VOICE_2_FILE_ID:
                self.bot.send_voice(chat_id, SADEGH_VOICE_2_FILE_ID)
            
            time.sleep(2)
            self.request_phone_number_keyboard(chat_id)
            
        except Exception as e:
            logging.error(f"Error sending important voice: {e}")
    
    def request_phone_number_keyboard(self, chat_id):
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button = types.KeyboardButton("ارسال شماره", request_contact=True)
            markup.add(button)
            self.bot.send_message(chat_id, phone_request_urgent, reply_markup=markup)
        except Exception as e:
            logging.error(f"Error requesting phone number: {e}")
    
    def handle_contact_message(self, message):
        try:
            user_id = message.from_user.id
            phone_number = message.contact.phone_number
            
            self.db.update_user_phone(user_id, phone_number)
            self.db.set_hot_lead(user_id, True)
            
            markup = types.ReplyKeyboardRemove()
            self.bot.send_message(message.chat.id, "شماره شما با موفقیت ثبت شد ✅", reply_markup=markup)
            
            self.send_contact_time_question(message.chat.id)
            
        except Exception as e:
            logging.error(f"Error handling contact message: {e}")
    
    def send_contact_time_question(self, chat_id):
        try:
            markup = self.create_question_markup(contact_time_options, "contact_")
            self.bot.send_message(chat_id, contact_time_question, reply_markup=markup)
        except Exception as e:
            logging.error(f"Error sending contact time question: {e}")
    
    def handle_contact_time(self, call):
        try:
            user_id = call.from_user.id
            option_index = int(call.data.split('_')[1])
            contact_time = contact_time_options[option_index]
            
            self.db.update_contact_time(user_id, contact_time)
            
            self.bot.edit_message_text(final_message, call.message.chat.id, call.message.message_id)
            self.db.update_user_state(user_id, UserState.COMPLETED)
            
        except Exception as e:
            logging.error(f"Error handling contact time: {e}")
    
    def schedule_final_photo(self, user_id, chat_id):
        try:
            send_time = datetime.now() + timedelta(seconds=FINAL_PHOTO_DELAY)
            
            self.final_photo_timers[user_id] = {
                'send_time': send_time,
                'chat_id': chat_id
            }
            self.db.add_final_photo_timer(user_id, send_time)
            
        except Exception as e:
            logging.error(f"Error scheduling final photo: {e}")
    
    def send_final_photo(self, chat_id, user_id):
        try:
            user_data = self.db.get_user_data(user_id)
            if user_data and user_data.get('phone'):
                return
            
            if FINAL_PHOTO_FILE_ID:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button = types.KeyboardButton("ارسال شماره", request_contact=True)
                markup.add(button)
                
                self.bot.send_photo(chat_id, FINAL_PHOTO_FILE_ID, caption=final_photo_caption, reply_markup=markup)
                self.db.update_user_state(user_id, UserState.WAITING_PHONE)
            
        except Exception as e:
            logging.error(f"Error sending final photo: {e}")
    
    def start_bot(self):
        try:
            logging.info("Bot started successfully")
            self.bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            time.sleep(15)
            self.start_bot()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.start_bot()