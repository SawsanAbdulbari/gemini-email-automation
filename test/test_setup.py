#!/usr/bin/env python3
"""
test_setup.py - Test Script for Gemini Email Automation Setup

This script helps verify that your environment is properly configured
before running the main email automation system.

Run with: python test_setup.py

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import sys
import os
import importlib.util
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header():
    """Print test header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'Gemini Email Automation - Setup Test'.center(60)}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def test_python_version():
    """Test Python version"""
    print(f"{Colors.BOLD}1. Testing Python Version...{Colors.ENDC}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} - OK{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}❌ Python {version.major}.{version.minor} - Requires 3.8+{Colors.ENDC}")
        return False

def test_required_packages():
    """Test if required packages are installed"""
    print(f"\n{Colors.BOLD}2. Testing Required Packages...{Colors.ENDC}")
    packages = {
        'google.generativeai': 'google-generativeai',
        'dotenv': 'python-dotenv'
    }
    
    all_installed = True
    for module, package in packages.items():
        spec = importlib.util.find_spec(module)
        if spec is not None:
            print(f"{Colors.GREEN}✅ {package} - Installed{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ {package} - Not installed (run: pip install {package}){Colors.ENDC}")
            all_installed = False
    
    return all_installed

def test_env_file():
    """Test if .env file exists and has required variables"""
    print(f"\n{Colors.BOLD}3. Testing Environment Configuration...{Colors.ENDC}")
    
    if not os.path.exists('.env'):
        print(f"{Colors.RED}❌ .env file not found{Colors.ENDC}")
        print(f"{Colors.YELLOW}   → Create .env from .env.example and add your credentials{Colors.ENDC}")
        return False
    
    print(f"{Colors.GREEN}✅ .env file found{Colors.ENDC}")
    
    # Try to load and check environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['GEMINI_API_KEY', 'EMAIL_ADDRESS', 'EMAIL_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith('your_'):
                missing_vars.append(var)
                print(f"{Colors.RED}❌ {var} - Not configured{Colors.ENDC}")
            else:
                # Mask sensitive information
                if var == 'GEMINI_API_KEY':
                    masked = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
                elif var == 'EMAIL_ADDRESS':
                    masked = value.split('@')[0][:3] + '***@' + value.split('@')[1] if '@' in value else '***'
                else:
                    masked = '*' * 16 if len(value) == 16 else f"Length: {len(value)}"
                print(f"{Colors.GREEN}✅ {var} - Configured ({masked}){Colors.ENDC}")
        
        return len(missing_vars) == 0
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  python-dotenv not installed, cannot verify .env{Colors.ENDC}")
        return False

def test_project_files():
    """Test if all required project files exist"""
    print(f"\n{Colors.BOLD}4. Testing Project Files...{Colors.ENDC}")
    
    required_files = [
        'config.py',
        'email_processor.py',
        'gemini_email.py',
        'main.py'
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"{Colors.GREEN}✅ {file} - Found{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ {file} - Missing{Colors.ENDC}")
            all_present = False
    
    return all_present

def test_gemini_connection():
    """Test Gemini API connection"""
    print(f"\n{Colors.BOLD}5. Testing Gemini API Connection...{Colors.ENDC}")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.startswith('your_'):
            print(f"{Colors.YELLOW}⚠️  Skipping - API key not configured{Colors.ENDC}")
            return None
        
        print(f"{Colors.BLUE}   Connecting to Gemini API...{Colors.ENDC}")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Simple test prompt
        response = model.generate_content("Respond with exactly: 'Connection successful'")
        
        if response and response.text:
            print(f"{Colors.GREEN}✅ Gemini API - Connected successfully{Colors.ENDC}")
            print(f"{Colors.BLUE}   Response: {response.text.strip()[:50]}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}❌ Gemini API - No response received{Colors.ENDC}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if 'API_KEY_INVALID' in error_msg:
            print(f"{Colors.RED}❌ Invalid API key{Colors.ENDC}")
        elif 'RATE_LIMIT' in error_msg:
            print(f"{Colors.YELLOW}⚠️  Rate limit reached - try again later{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Connection failed: {error_msg[:100]}{Colors.ENDC}")
        return False

def test_email_config():
    """Test email configuration (without connecting)"""
    print(f"\n{Colors.BOLD}6. Testing Email Configuration...{Colors.ENDC}")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        email = os.getenv('EMAIL_ADDRESS', '')
        password = os.getenv('EMAIL_PASSWORD', '')
        
        # Basic validation
        if '@gmail.com' in email and email != 'your.email@gmail.com':
            print(f"{Colors.GREEN}✅ Gmail address configured{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}⚠️  Email address needs configuration{Colors.ENDC}")
            return False
        
        if len(password) == 16:
            print(f"{Colors.GREEN}✅ App password format correct (16 chars){Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}⚠️  App password should be 16 characters{Colors.ENDC}")
            return False
        
        print(f"{Colors.BLUE}   Note: Actual email connection will be tested when running main.py{Colors.ENDC}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error checking email config: {str(e)}{Colors.ENDC}")
        return False

def generate_report(results):
    """Generate final test report"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r == True)
    failed = sum(1 for r in results.values() if r == False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {failed}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Skipped: {skipped}{Colors.ENDC}")
    
    if failed == 0 and skipped == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your setup is ready.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"1. Run the main application: {Colors.BLUE}python main.py{Colors.ENDC}")
        print(f"2. Send test emails to: {Colors.BLUE}{os.getenv('EMAIL_ADDRESS', 'your configured email')}{Colors.ENDC}")
        print(f"3. Watch the automation in action!")
    elif failed > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please fix the issues above.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Common fixes:{Colors.ENDC}")
        if 'packages' in results and not results['packages']:
            print(f"• Install missing packages: {Colors.BLUE}pip install -r requirements.txt{Colors.ENDC}")
        if 'env_file' in results and not results['env_file']:
            print(f"• Configure credentials: {Colors.BLUE}Copy .env.example to .env and add your keys{Colors.ENDC}")
        if 'project_files' in results and not results['project_files']:
            print(f"• Ensure all project files are in the current directory")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests were skipped. Setup may be incomplete.{Colors.ENDC}")

def main():
    """Run all tests"""
    print_test_header()
    
    results = {}
    
    # Run tests in order
    results['python'] = test_python_version()
    results['packages'] = test_required_packages()
    results['env_file'] = test_env_file()
    results['project_files'] = test_project_files()
    
    # Only test API connection if environment is configured
    if results['env_file']:
        results['gemini_api'] = test_gemini_connection()
        results['email_config'] = test_email_config()
    else:
        results['gemini_api'] = None
        results['email_config'] = None
    
    # Generate report
    generate_report(results)
    
    # Return exit code based on results
    if any(r == False for r in results.values()):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)