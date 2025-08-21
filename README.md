# 📧 Gemini API Email Response Automation System

> **⚠️ IMPORTANT SECURITY NOTICE**: Never commit real API keys or passwords to version control! Always use environment variables for sensitive information.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Method 1: Python Implementation](#method-1-python-implementation)
- [Method 2: Postman Implementation](#method-2-postman-implementation)
- [Troubleshooting](#troubleshooting)
- [Testing the System](#testing-the-system)
- [Assignment Guidelines](#assignment-guidelines)
- [Support](#support)

## 🎯 Project Overview

This project demonstrates how to build an AI-powered email response automation system using Google's Gemini API. The system:
- 📨 Fetches emails from Gmail inbox (with date filtering - last 7 days)
- 🤖 Analyzes and categorizes emails (8 categories including complaints, support, inquiries)
- ✨ Generates contextually appropriate responses using Gemini AI
- 📤 Sends professional automated replies with proper email threading
- 🔒 Includes spam filtering and security measures
- 📊 Tracks processed emails to prevent duplicates

**Learning Objectives:**
- Integrate with Google's Gemini API
- Implement email processing with IMAP/SMTP
- Practice prompt engineering
- Handle errors and edge cases
- Understand API rate limiting

## 📦 Prerequisites

### Required Software
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **VS Code** ([Download](https://code.visualstudio.com/))
- **Postman** ([Download](https://www.postman.com/downloads/))
- **Git** (optional but recommended) ([Download](https://git-scm.com/))
- **Gmail Account** with 2-Factor Authentication enabled

### System Requirements
- Windows 10/11, macOS, or Linux
- 4GB RAM minimum
- Internet connection
- ~500MB free disk space

## 🚀 Quick Start Guide

### Step 1: Get Your Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click on **"Get API Key"** in the left sidebar
4. Click **"Create API Key"**
5. Copy your API key and save it securely (you won't be able to see it again!)

⚠️ **IMPORTANT**: Never commit your API key to version control!

### Step 2: Set Up Gmail App Password
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (must be enabled)
3. Click on **App passwords** at the bottom
4. Select **Mail** from the dropdown
5. Click **Generate**
6. Copy the 16-character password (save it securely!)

### Step 3: Download Project Files
```bash
# Option 1: Clone repository (if using Git)
git clone https://github.com/SawsanAbdulbari/gemini-email-automation.git
cd gemini-email-automation

# Option 2: Download ZIP file
# Download and extract the project files to your Desktop
```

### Step 4: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install manually
pip install google-generativeai python-dotenv
```

---

## 🐍 Method 1: Python Implementation

### 1️⃣ Installation Setup

#### A. Install Python Dependencies
Open terminal/command prompt in the project directory:

```bash
# Windows
pip install google-generativeai

# macOS/Linux
pip3 install google-generativeai
```

#### B. Create Environment Variables File
Copy the example file and add your credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your actual credentials:
GEMINI_API_KEY=your_actual_api_key_here
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

⚠️ **Security Note**: The `.env` file is already in `.gitignore` to prevent accidental commits.

#### C. Update config.py
Replace the existing config.py with this secure version:

```python
# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Gemini API key from Google AI Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "email_address": os.getenv("EMAIL_ADDRESS", "your.email@gmail.com"),
    "email_password": os.getenv("EMAIL_PASSWORD", "your_app_password_here")
}

# Gemini API configuration
GEMINI_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "max_output_tokens": 1024,
    "top_p": 0.95,
    "top_k": 40
}

# Email categories
EMAIL_CATEGORIES = [
    "complaint",
    "product_support",
    "feature_request",
    "billing_question",
    "general_feedback",
    "urgent_request",
    "spam",
    "customer_inquiry"
]
```

#### D. Install Additional Dependencies
```bash
pip install python-dotenv
```

### 2️⃣ Project Structure
Complete project structure:
```
gemini-email-automation/
│
├── 📁 Core Files
│   ├── config.py              # Configuration settings
│   ├── email_processor.py     # Email handling with threading support
│   ├── gemini_email.py       # Gemini API integration
│   ├── email_filter.py       # Spam and security filtering
│   ├── email_tracker.py      # Duplicate prevention
│   └── main.py               # Main application (v4.0 with fixes)
│
├── 📁 test/                  # Test suite
│   ├── test_setup.py         # Setup verification
│   └── test_email_automation.py  # Unit tests
│
├── 📁 Postman/              # API testing
│   ├── Gemini_Email_Collection.json
│   └── Gemini_Email_Environment.json
│
├── 📁 docs/                 # Documentation
│   ├── README.md            # Main documentation
│   └── PROJECT_SUMMARY.md  # Project overview
│
├── .env                     # Your credentials 
├── .env.example            # Template for credentials
├── .gitignore              # Git ignore rules
└── requirements.txt        # Python dependencies
```

### 3️⃣ Create .gitignore File
Create a `.gitignore` file to protect sensitive data:
```
# .gitignore
.env
*.pyc
__pycache__/
*.log
config_local.py
test_emails/
```

### 4️⃣ Running the Python Application

#### Test Your Setup First
Create a test script `test_setup.py`:

```python
# test_setup.py
import google.generativeai as genai
from config import GEMINI_API_KEY, EMAIL_CONFIG

def test_gemini_connection():
    """Test if Gemini API is working"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'Hello, World!'")
        print("✅ Gemini API connected successfully!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        return False

def test_email_config():
    """Test if email configuration is set"""
    if EMAIL_CONFIG['email_address'] == "your.email@gmail.com":
        print("❌ Please update your email configuration in .env file")
        return False
    print("✅ Email configuration looks good!")
    return True

if __name__ == "__main__":
    print("Testing your setup...\n")
    gemini_ok = test_gemini_connection()
    email_ok = test_email_config()
    
    if gemini_ok and email_ok:
        print("\n🎉 All tests passed! You're ready to run the main application.")
    else:
        print("\n⚠️ Please fix the issues above before running the main application.")
```

Run the test:
```bash
python test_setup.py
```

#### Run the Main Application
Once tests pass:
```bash
python main.py
```

You should see:
```
============================================================
   Gemini API Email Response Automation System v4.0
   Enhanced with Threading & Date Filtering
   HAMK Digital and Social Media Analytics
============================================================
Started at: 2025-08-20 18:30:00
Configuration:
  - Check interval: 30 seconds
  - Max emails per cycle: 1
  - Days to check: 7 days
  - Spam threshold: 0.5
  - Rate limit: 3 emails per sender per 24h
  - HTML emails: True

Press Ctrl+C to stop the system
------------------------------------------------------------

🔍 Checking for new emails from last 7 days... (18:30:00)
```

### 5️⃣ Testing with Sample Emails

Send test emails to your configured Gmail account with these subjects and bodies:

#### Test Email 1: Customer Complaint
```
Subject: Terrible service experience
Body: I am extremely disappointed with your product. It stopped working after just one day of use. This is unacceptable and I want a full refund immediately.
```

#### Test Email 2: Technical Support
```
Subject: Can't login to my account
Body: Hi, I'm getting an error message when trying to log in. It says "Invalid credentials" but I'm sure my password is correct. Can you help me reset it?
```

#### Test Email 3: Feature Request
```
Subject: Suggestion for new feature
Body: Love your product! It would be great if you could add dark mode support. Many users would appreciate this feature for nighttime use.
```

---

## 📮 Method 2: Postman Implementation

### 1️⃣ Postman Setup

#### A. Create Postman Account
1. Open Postman and sign up/sign in
2. Create a new Workspace: "Gemini Email Automation"

#### B. Set Up Environment Variables
1. Click on **Environments** in the left sidebar
2. Click **Create Environment**
3. Name it: "Gemini API Environment"
4. Add these variables:

| Variable Name | Type | Initial Value | Current Value |
|--------------|------|---------------|---------------|
| gemini_api_key | secret | YOUR_API_KEY | YOUR_API_KEY |
| base_url | default | https://generativelanguage.googleapis.com | (same) |
| model | default | gemini-2.0-flash | (same) |

5. Click **Save**

### 2️⃣ Create API Collection

#### A. Create New Collection
1. Click **Collections** → **Create Collection**
2. Name: "Gemini Email Responses"
3. Description: "Automated email response generation using Gemini API"

#### B. Add Authentication
1. Click on the collection name
2. Go to **Authorization** tab
3. Type: **API Key**
4. Key: `key`
5. Value: `{{gemini_api_key}}`
6. Add to: **Query Params**

### 3️⃣ Create API Requests

#### Request 1: Test Connection
```
Name: Test Gemini Connection
Method: POST
URL: {{base_url}}/v1/models/{{model}}:generateContent?key={{gemini_api_key}}

Headers:
Content-Type: application/json

Body (raw JSON):
{
  "contents": [{
    "parts": [{
      "text": "Say hello!"
    }]
  }]
}
```

#### Request 2: Generate Email Response - Complaint
```
Name: Handle Customer Complaint
Method: POST
URL: {{base_url}}/v1/models/{{model}}:generateContent?key={{gemini_api_key}}

Headers:
Content-Type: application/json

Body (raw JSON):
{
  "contents": [{
    "parts": [{
      "text": "You are a customer support assistant. Generate a professional, apologetic response to this complaint email:\n\nFrom: john.doe@example.com\nSubject: Product not working\nBody: Your product stopped working after 2 days. I'm very disappointed and want a refund.\n\nGuidelines:\n1. Apologize sincerely\n2. Show empathy\n3. Offer a solution\n4. Sign as 'Customer Support Team'"
    }]
  }],
  "generationConfig": {
    "temperature": 0.7,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 1024
  }
}
```

#### Request 3: Generate Email Response - Support
```
Name: Handle Technical Support
Method: POST
URL: {{base_url}}/v1/models/{{model}}:generateContent?key={{gemini_api_key}}

Headers:
Content-Type: application/json

Body (raw JSON):
{
  "contents": [{
    "parts": [{
      "text": "You are a technical support specialist. Generate a helpful response to this support email:\n\nFrom: user@example.com\nSubject: Can't log in\nBody: I forgot my password and can't access my account. Help!\n\nGuidelines:\n1. Acknowledge the issue\n2. Provide step-by-step instructions\n3. Offer alternatives\n4. Sign as 'Technical Support Team'"
    }]
  }],
  "generationConfig": {
    "temperature": 0.5,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 1024
  }
}
```

### 4️⃣ Create Test Scripts

In each request, add this test script in the **Tests** tab:

```javascript
// Test Script for Response Validation
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has candidates", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('candidates');
    pm.expect(jsonData.candidates).to.be.an('array');
    pm.expect(jsonData.candidates.length).to.be.greaterThan(0);
});

pm.test("Generated text exists", function () {
    var jsonData = pm.response.json();
    var text = jsonData.candidates[0].content.parts[0].text;
    pm.expect(text).to.be.a('string');
    pm.expect(text.length).to.be.greaterThan(50);
    
    // Log the response for review
    console.log("Generated Response:", text);
});

pm.test("Response is professional", function () {
    var jsonData = pm.response.json();
    var text = jsonData.candidates[0].content.parts[0].text.toLowerCase();
    
    // Check for professional elements
    pm.expect(text).to.include.oneOf(['dear', 'hello', 'hi']);
    pm.expect(text).to.include.oneOf(['sincerely', 'regards', 'best', 'team']);
});
```

### 5️⃣ Create Collection Runner Tests

1. Click **Runner** button in Postman
2. Select your collection
3. Set iterations: 3
4. Add data file (CSV) with test emails:

Create `test_emails.csv`:
```csv
email_from,email_subject,email_body,category
angry.customer@test.com,Worst product ever,This is terrible. Nothing works!,complaint
confused.user@test.com,How to reset password,I can't remember my password,support
happy.user@test.com,Great product!,Just wanted to say I love your service,feedback
```

### 6️⃣ Monitor API Usage

Create a Pre-request Script for the collection:
```javascript
// Pre-request Script - Rate Limiting Check
const lastRequestTime = pm.globals.get("lastRequestTime");
const currentTime = Date.now();

if (lastRequestTime) {
    const timeDiff = currentTime - lastRequestTime;
    if (timeDiff < 1000) { // Less than 1 second
        console.log("Rate limit protection: Waiting...");
        setTimeout(function(){}, 1000 - timeDiff);
    }
}

pm.globals.set("lastRequestTime", currentTime);
pm.globals.set("requestCount", (pm.globals.get("requestCount") || 0) + 1);

console.log(`Request #${pm.globals.get("requestCount")} at ${new Date().toLocaleTimeString()}`);
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "API Key Invalid"
**Error:** `Error generating response: API key not valid`

**Solutions:**
1. Check if API key is correctly copied (no extra spaces)
2. Verify API key is active in Google AI Studio
3. Ensure you're using the correct environment variable
4. Make sure `.env` file is in the project root directory
5. Try regenerating the API key

#### Issue 2: "Subject in Email Body"
**Error:** Email responses contain "Subject: Re:..." in the body

**Solution:** This has been fixed in v4.0. The system now:
- Cleans email bodies before sending
- Instructs Gemini to not include headers
- Properly threads emails using headers only

#### Issue 2: "Gmail Authentication Failed"
**Error:** `[AUTHENTICATIONFAILED] Invalid credentials`

**Solutions:**
1. Ensure 2-Factor Authentication is enabled on Gmail
2. Use App Password, not your regular Gmail password
3. Check for typos in email address
4. Verify IMAP is enabled in Gmail settings:
   - Gmail → Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP

#### Issue 3: "Module Not Found"
**Error:** `ModuleNotFoundError: No module named 'google.generativeai'`

**Solutions:**
```bash
# Windows
pip install google-generativeai python-dotenv

# macOS/Linux
pip3 install google-generativeai python-dotenv

# If still not working, try:
python -m pip install google-generativeai python-dotenv
```

#### Issue 4: "Connection Timeout"
**Error:** `TimeoutError: Connection timed out`

**Solutions:**
1. Check internet connection
2. Verify firewall settings
3. Try using a VPN if in a restricted network
4. Check if Gmail servers are accessible

#### Issue 5: "Rate Limit Exceeded"
**Error:** `Resource has been exhausted`

**Solutions:**
1. Wait 60 seconds before retrying
2. Reduce request frequency
3. Check your API quota in Google AI Studio
4. Implement exponential backoff in your code

### Debug Mode

Add this to your main.py for detailed debugging:
```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='email_automation.log'
)
```

---

## 🧪 Testing the System

### Unit Tests (Python)

Create `test_email_automation.py`:
```python
import unittest
from unittest.mock import Mock, patch
from email_processor import EmailProcessor
from gemini_email import GeminiEmailResponder

class TestEmailAutomation(unittest.TestCase):
    
    def setUp(self):
        self.email_processor = EmailProcessor()
        self.gemini_responder = GeminiEmailResponder()
    
    def test_email_categorization(self):
        """Test if emails are correctly categorized"""
        test_cases = [
            ("I hate this product", "complaint"),
            ("How do I reset my password?", "product_support"),
            ("Please add dark mode", "feature_request"),
            ("Thank you for great service", "general_feedback")
        ]
        
        for body, expected_category in test_cases:
            email_data = {
                'subject': 'Test',
                'body': body,
                'from': 'test@example.com'
            }
            result = self.email_processor.parse_email_for_response(email_data)
            self.assertEqual(result['category'], expected_category)
    
    def test_response_generation(self):
        """Test if responses are generated"""
        email_content = {
            'from': 'test@example.com',
            'subject': 'Help needed',
            'body': 'I cannot log in to my account'
        }
        
        response = self.gemini_responder.generate_response(
            email_content, 
            email_type='product_support'
        )
        
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 50)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python test_email_automation.py
```

### Integration Tests (Postman)

Create a test collection with these scenarios:
1. **Happy Path:** Valid email → Correct categorization → Appropriate response
2. **Edge Cases:** Empty email, very long email, non-English email
3. **Error Handling:** Invalid API key, network timeout, rate limiting
4. **Response Quality:** Check for professionalism, completeness, tone

---

## 📝 Assignment Guidelines

### Part 1: Postman Implementation (40%)
1. Create a complete Postman collection with at least 5 different email scenarios
2. Implement proper error handling
3. Add comprehensive test scripts
4. Document your API calls

**Deliverables:**
- Exported Postman collection (.json)
- Environment variables file
- Screenshots of successful requests
- 1-page reflection on API behavior

### Part 2: Python Implementation (40%)
1. Implement the complete email automation system
2. Add at least 2 new email categories
3. Improve response quality with better prompts
4. Add logging and error handling

**Deliverables:**
- Complete Python code (all 4 files)
- Test results document
- Sample email responses (at least 10)
- Code documentation

### Part 3: Enhancement (20%)
Choose ONE:
- Add multi-language support
- Implement priority queue for urgent emails
- Create web dashboard for monitoring
- Add sentiment analysis visualization
- Implement email threading support

**Deliverables:**
- Enhanced code
- Documentation of new features
- Demonstration video (3-5 minutes)

### Grading Rubric
- **Functionality (40%):** Does it work as expected?
- **Code Quality (25%):** Clean, commented, follows best practices
- **Error Handling (15%):** Graceful handling of edge cases
- **Documentation (10%):** Clear instructions and comments
- **Innovation (10%):** Creative enhancements or improvements

### Submission Checklist
- [ ] All code files included
- [ ] `.env` file NOT included (only .env.example)
- [ ] README updated with your specific instructions
- [ ] Test results documented
- [ ] Screenshots/video included
- [ ] No hardcoded credentials in code

---

## 🆘 Support

### Resources
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Python Email Tutorial](https://realpython.com/python-email/)
- [Postman Learning Center](https://learning.postman.com/)
- [Gmail IMAP Settings](https://support.google.com/mail/answer/7126229)


### Common Questions

**Q: Can I use a different email provider?**
A: Yes, but you'll need to modify the IMAP/SMTP settings in config.py

**Q: How many API calls can I make?**
A: Free tier allows 60 requests per minute. The system includes rate limiting.

**Q: Why does it only check emails from the last 7 days?**
A: To prevent processing old emails. You can adjust `days_back` parameter.

**Q: How does email threading work?**
A: The system uses Message-ID and References headers to maintain conversation chains.

**Q: Can I work in groups?**
A: Check with your instructor, but typically this is an individual assignment

**Q: What if I exceed my API quota?**
A: Use the fallback responses implemented in the code, or wait for quota reset

**Q: How do I test if the fixes work?**
A: Run `python test/test_email_format_fix.py` to verify all fixes are applied.

---

## 📜 License & Ethics

### Important Ethical Considerations
- **Never** use this system to send spam or unsolicited emails
- **Always** inform recipients that responses are AI-generated
- **Respect** user privacy and data protection regulations
- **Test** thoroughly before deploying to production

### Academic Integrity
- This is educational material - cite appropriately
- Do not share your API keys with others
- Submit your own work

---



You've successfully set up the Gemini Email Automation System! This project demonstrates real-world API integration and practical automation skills that are highly valuable in the industry.

### Next Steps
1. Experiment with different prompt styles
2. Try handling more complex email scenarios
3. Consider building a UI for the system
4. Explore other Gemini API capabilities

**Happy Coding! 🚀**

---

*Last Updated: August 2025*

*Version: 4.0 (with threading and format)*

*Course: Digital and Social Media Analytics - HAMK*

*Contributors: Linda Marin, Sawsan Abdulbari*