# config.py - Bot configuration

import os

# Bot Token - Get from BotFather
# Use environment variables or replace the string below
BOT_TOKEN = os.getenv("BOT_TOKEN", "ENTER_YOUR_BOT_TOKEN_HERE")

# Admin numeric IDs
ADMIN_IDS = [
    # Add admin IDs here, e.g., 123456789
]

# Channel IDs
MINI_COURSE_CHANNEL_ID = "ENTER_CHANNEL_ID"
VIDEO_SOURCE_CHANNEL_ID = "ENTER_CHANNEL_ID"

# File IDs - Expert assets
# Forough
FOROUGH_PHOTO_FILE_ID = "ENTER_FILE_ID"
FOROUGH_VOICE_1_FILE_ID = "ENTER_FILE_ID"
FOROUGH_VOICE_2_FILE_ID = "ENTER_FILE_ID" 

# Sadegh
SADEGH_PHOTO_FILE_ID = "ENTER_FILE_ID"
SADEGH_VOICE_1_FILE_ID = "ENTER_FILE_ID"
SADEGH_VOICE_2_FILE_ID = "ENTER_FILE_ID"

# Other media assets
TESTIMONIAL_VIDEO_FILE_ID = "ENTER_FILE_ID"
SUCCESS_STORIES_VIDEO_FILE_ID = "ENTER_FILE_ID"
FINAL_PHOTO_FILE_ID = "ENTER_FILE_ID"

# Database & Paths
DB_FILE = "users.db"
JSON_BACKUP_FILE = "users_data.json"
LOG_FILE = "bot.log"
EXCEL_EXPORT_DIR = "exports"

# Timing Settings (in seconds)
FIRST_REMINDER_DELAY = 3600   # 1 hour
SECOND_REMINDER_DELAY = 3600  # 1 hour
FINAL_PHOTO_DELAY = 21600     # 6 hours

# Create export directory
os.makedirs(EXCEL_EXPORT_DIR, exist_ok=True)

# User States
class UserState:
    START = "start"
    WAITING_NAME = "waiting_name"
    QUESTION_1 = "question_1"
    QUESTION_2 = "question_2"
    QUESTION_3 = "question_3"
    QUESTION_4 = "question_4"
    WAITING_FIRST_CHECK = "waiting_first_check"
    WAITING_SECOND_CHECK = "waiting_second_check"
    WAITING_RATING = "waiting_rating"
    WAITING_PHONE = "waiting_phone"
    WAITING_CONTACT_TIME = "waiting_contact_time"
    COMPLETED = "completed"

# Admin States
class AdminState:
    MAIN_MENU = "admin_main"
    BULK_QUIZ = "bulk_quiz"
    BULK_FILE = "bulk_file"
    BULK_MESSAGE = "bulk_message"
    BULK_CONFIRM = "bulk_confirm"