# Telegram-Course-Funnel-Bot

A professional Telegram bot designed for automated lead generation, user segmentation, and delivering mini-courses. Built with Python and `pyTelegramBotAPI`, featuring a robust admin panel, SQLite database, and automated follow-up timers.

## 🤖 Live Demo
Check out the live version running for the "Too America" academy:
> **[👉 Click here to Start (@tooamerica_minibot)](https://t.me/tooamerica_minibot)**

*(Note: This is a live production bot. Please interact respectfully!)*

---

## ✨ Key Features

* **Smart User Funnel:** Step-by-step registration flow to qualify leads.
* **Interactive Questionnaire:** Assesses user level and goals before course delivery.
* **Automated Follow-ups:** * Timers for 1-hour and 24-hour reminders.
    * "Final Photo" trigger (e.g., sending a special offer after 6 hours).
* **Media Handling:** Sends photos, voice messages, and videos based on logic.
* **Admin Panel:**
    * 📊 **Live Statistics:** Total users, VIPs (users with phone numbers), and Hot Leads.
    * 📥 **Excel Export:** Download full user database with one click.
    * 📢 **Bulk Messaging:** Send text/media to all users (secured with a math captcha).
* **Database:** Efficient SQLite storage with auto-JSON backups.

## 🛠️ Project Structure

* `bot.py`: Main entry point and message handlers.
* `config.py`: Configuration (Tokens, Channel IDs, File IDs).
* `database.py`: SQLite database manager and timer logic.
* `admin.py`: Admin panel logic and bulk messaging system.
* `messages.py`: Centralized text content (Persian/Farsi).

## 🚀 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nightcoder-officiall/REPO_NAME.git](https://github.com/nightcoder-officiall/REPO_NAME.git)
    cd REPO_NAME
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the bot:**
    * Open `config.py`.
    * Set your `BOT_TOKEN` (get from @BotFather).
    * Add your numeric Telegram ID to `ADMIN_IDS`.
    * Set up your Channel IDs and Media File IDs.

4.  **Run the bot:**
    ```bash
    python bot.py
    ```

## ⚙️ Configuration Example

**Important:** Never commit your real API tokens to GitHub.

```python
# config.py sample
BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
ADMIN_IDS = [123456789]
MINI_COURSE_CHANNEL_ID = "-1001234567890"
```

## 📦 Requirements

The following libraries are required to run the bot. They will be automatically checked and can be installed via `run.py`:

* **Python 3.8+**
* **pyTelegramBotAPI**: High-level interface for the Telegram Bot API.
* **pandas**: Used for data processing and managing user information.
* **openpyxl**: Required for exporting data to Excel format.
* **sqlite3**: Built-in Python library for database management.

## 🤝 Contact & Support

This project was developed by **[NightCoder](https://github.com/nightcoder-officiall)**. 
I specialize in creating smart Telegram bots and automation tools.

* **GitHub:** [nightcoder-officiall](https://github.com/nightcoder-officiall)
* **Telegram Bot Demo:** [@tooamerica_minibot](https://t.me/tooamerica_minibot)

Feel free to reach out for custom bot development, collaborations, or if you have any questions! ✨

---
*This project is for educational and portfolio purposes. All rights reserved.*
