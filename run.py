#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from bot import TelegramBot
from config import BOT_TOKEN, ADMIN_IDS

def check_requirements():
    """Check and install required packages"""
    required_packages = [
        'telebot',
        'pandas', 
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 'telebot':
                missing_packages.append('pyTelegramBotAPI')
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print("❌ The following libraries are missing:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print("\n💡 Please install the requirements using:")
        print("pip install -r requirements.txt")
        
        response = input("\nWould you like to install them now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            try:
                print("⏳ Installing libraries, please wait...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("✅ Libraries installed successfully!")
            except Exception as e:
                print(f"❌ Error installing libraries: {e}")
                sys.exit(1)
        else:
            print("👋 Exiting setup.")
            sys.exit(1)

def check_config():
    """Validate configuration settings"""
    issues = []
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        issues.append("BOT_TOKEN is not set in config.py")
    
    # Simple check for default IDs (adjust if your default is different)
    if not ADMIN_IDS or ADMIN_IDS == [123456789, 987654321]:
        issues.append("ADMIN_IDS are not properly configured in config.py")
    
    if issues:
        print("❌ Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Please edit config.py and provide your real bot details")
        sys.exit(1)

def create_directories():
    """Create necessary project folders"""
    directories = ['exports', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Folder '{directory}' created")

def main():
    """Main execution entry point"""
    print("\n" + "=" * 50)
    print("🤖 STARTING TELEGRAM BOT SYSTEM...")
    print("=" * 50)
    
    # Step 1: Check Dependencies
    print("🔍 Checking dependencies...")
    check_requirements()
    print("✅ All libraries are present")
    
    # Step 2: Validate Config
    print("🔍 Validating configuration...")
    check_config()
    print("✅ Configuration looks good")
    
    # Step 3: Setup Folders
    print("📁 Setting up directories...")
    create_directories()
    
    # Step 4: Run Bot
    print("🚀 Initializing bot engine...")
    print("=" * 50)
    
    try:
        bot = TelegramBot()
        print("✅ Bot is online and running!")
        print("📱 Ready to receive messages...")
        print("🛑 Press Ctrl+C to stop the bot")
        print("=" * 50 + "\n")
        
        bot.start_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (KeyboardInterrupt)")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()