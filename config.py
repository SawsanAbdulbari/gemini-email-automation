# config.py
"""
Secure Configuration file for Gemini API Email Response Automation project.

This version uses environment variables to keep sensitive information secure.
Students should:
1. Copy .env.example to .env
2. Fill in their actual credentials in .env
3. Never commit .env to version control

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
Version: 4.0
"""

import os
import sys
from pathlib import Path

# Try to import python-dotenv
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")
    print("Install with: pip install python-dotenv")

# Security check function
def check_configuration():
    """Check if configuration is properly set up"""
    issues = []
    
    # Check API key
    if os.getenv("GEMINI_API_KEY", "").startswith("your_"):
        issues.append("❌ GEMINI_API_KEY not configured in .env file")
    
    # Check email configuration
    if os.getenv("EMAIL_ADDRESS", "").endswith("@gmail.com"):
        if os.getenv("EMAIL_ADDRESS") == "your.email@gmail.com":
            issues.append("❌ EMAIL_ADDRESS not configured in .env file")
    
    if len(os.getenv("EMAIL_PASSWORD", "")) != 16:
        issues.append("❌ EMAIL_PASSWORD should be a 16-character App Password")
    
    if issues:
        print("\n⚠️  Configuration Issues Detected:")
        for issue in issues:
            print(f"   {issue}")
        print("\n📝 How to fix:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your actual credentials")
        print("   3. Never commit .env to version control")
        print("\n📚 See README.md for detailed setup instructions\n")
        return False
    return True

# Your Gemini API key from Google AI Studio
# To obtain a key:
# 1. Visit https://aistudio.google.com/
# 2. Sign in with your Google account
# 3. Navigate to API access and create a new key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")

# Email configuration
# For Gmail:
# - You'll need to set up an "App Password" in your Google account security settings
# - Do not use your regular Gmail password
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
    "imap_port": int(os.getenv("IMAP_PORT", "993")),
    "email_address": os.getenv("EMAIL_ADDRESS", "your.email@gmail.com"),
    "email_password": os.getenv("EMAIL_PASSWORD", "your_app_password_here")
}

# Gemini API configuration
# These settings control how the AI generates responses
GEMINI_CONFIG = {
    "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    "max_output_tokens": int(os.getenv("MAX_OUTPUT_TOKENS", "1024")),
    "top_p": float(os.getenv("TOP_P", "0.95")),
    "top_k": int(os.getenv("TOP_K", "40"))
}

# Email categories for response customization
EMAIL_CATEGORIES = [
    "complaint",          # Customer expressing dissatisfaction
    "product_support",    # Technical questions or issues
    "feature_request",    # Suggestions for new features
    "billing_question",   # Questions about payments, subscriptions
    "general_feedback",   # Positive or neutral feedback
    "urgent_request",     # Time-sensitive matters
    "spam",               # Potential spam or irrelevant messages
    "customer_inquiry"    # General product or service questions
]

# Application settings
APP_CONFIG = {
    "check_interval": int(os.getenv("EMAIL_CHECK_INTERVAL", "10")),  # seconds
    "fetch_limit": int(os.getenv("EMAIL_FETCH_LIMIT", "5")),
    "debug_mode": os.getenv("DEBUG_MODE", "False").lower() == "true",
    "log_file": os.getenv("LOG_FILE", "email_automation.log")
}

# Display configuration status (only in debug mode)
if APP_CONFIG["debug_mode"]:
    print("\n🔧 Debug Mode: Configuration Status")
    print("=" * 50)
    print(f"API Key Configured: {'✅' if not GEMINI_API_KEY.startswith('your_') else '❌'}")
    print(f"Email Configured: {'✅' if not EMAIL_CONFIG['email_address'].startswith('your.') else '❌'}")
    print(f"Model: {GEMINI_CONFIG['model']}")
    print(f"Temperature: {GEMINI_CONFIG['temperature']}")
    print("=" * 50)

# Run configuration check when module is imported
if __name__ == "__main__":
    if check_configuration():
        print("✅ Configuration looks good!")
        print(f"   Email: {EMAIL_CONFIG['email_address']}")
        print(f"   Model: {GEMINI_CONFIG['model']}")
    else:
        sys.exit(1)
