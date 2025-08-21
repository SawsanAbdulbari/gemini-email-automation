#!/usr/bin/env python3
"""
test_email_format_fix.py - Test script to verify email formatting fixes

This script tests that the automated responses no longer include
"Subject:" lines in the email body.

Run with: python test_email_format_fix.py

Author: HAMK Digital and Social Media Analytics
Date: August 2025
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_processor import EmailProcessor
from gemini_email import GeminiEmailResponder

def test_clean_email_body():
    """Test the _clean_email_body method"""
    processor = EmailProcessor()
    
    print("\n" + "="*60)
    print("Testing Email Body Cleaning")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "input": "Subject: Re: Testing implementation\n\nDear Customer,\n\nThank you for your email.",
            "expected": "Dear Customer,\n\nThank you for your email.",
            "description": "Remove Subject line from body"
        },
        {
            "input": "Re: Testing\n\nHello,\n\nWe received your message.",
            "expected": "Hello,\n\nWe received your message.",
            "description": "Remove Re: prefix from body"
        },
        {
            "input": "From: support@company.com\nTo: customer@example.com\nSubject: Response\n\nDear User,\n\nThank you.",
            "expected": "Dear User,\n\nThank you.",
            "description": "Remove multiple headers from body"
        },
        {
            "input": "Dear Customer,\n\nThank you for your email.\n\nBest regards,\nSupport Team",
            "expected": "Dear Customer,\n\nThank you for your email.\n\nBest regards,\nSupport Team",
            "description": "Leave clean body unchanged"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        result = processor._clean_email_body(test["input"])
        passed = result == test["expected"]
        
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: {repr(test['input'][:50])}...")
        print(f"Expected: {repr(test['expected'][:50])}...")
        print(f"Got: {repr(result[:50])}...")
        
        if passed:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            all_passed = False
    
    return all_passed

def test_clean_response():
    """Test the _clean_response method in GeminiEmailResponder"""
    # Note: This requires mocking the GenerativeModel to avoid API calls
    import unittest.mock as mock
    
    print("\n" + "="*60)
    print("Testing Gemini Response Cleaning")
    print("="*60)
    
    with mock.patch('gemini_email.genai.GenerativeModel'):
        responder = GeminiEmailResponder()
    
    test_cases = [
        {
            "input": "Subject: Re: Your inquiry\n\nDear Customer,\n\nThank you for contacting us.",
            "expected": "Dear Customer,\n\nThank you for contacting us.",
            "description": "Clean Subject from Gemini response"
        },
        {
            "input": "From: support@company.com\n\nHello,\n\nWe appreciate your feedback.",
            "expected": "Hello,\n\nWe appreciate your feedback.",
            "description": "Clean From header from response"
        },
        {
            "input": "Dear valued customer,\n\nWe have received your request.\n\nBest regards,\nSupport Team",
            "expected": "Dear valued customer,\n\nWe have received your request.\n\nBest regards,\nSupport Team",
            "description": "Leave clean response unchanged"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        result = responder._clean_response(test["input"])
        passed = result == test["expected"]
        
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: {repr(test['input'][:50])}...")
        print(f"Expected: {repr(test['expected'][:50])}...")
        print(f"Got: {repr(result[:50])}...")
        
        if passed:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            all_passed = False
    
    return all_passed

def test_prompt_generation():
    """Test that prompts include the instruction to not add headers"""
    import unittest.mock as mock
    
    print("\n" + "="*60)
    print("Testing Prompt Generation Instructions")
    print("="*60)
    
    with mock.patch('gemini_email.genai.GenerativeModel'):
        responder = GeminiEmailResponder()
    
    email_content = {
        'from': 'test@example.com',
        'subject': 'Test Subject',
        'body': 'This is a test email.',
        'sender_name': 'Test User'
    }
    
    email_types = ['complaint', 'product_support', 'feature_request', 
                   'billing_question', 'general_feedback', 'urgent_request',
                   'customer_inquiry', 'spam']
    
    all_passed = True
    
    for email_type in email_types:
        prompt = responder._create_prompt(email_content, email_type)
        
        # Check if prompt contains the instruction
        has_instruction = "Generate ONLY the email body" in prompt or "NO subject lines or headers" in prompt
        
        print(f"\n{email_type}: ", end="")
        if has_instruction:
            print("✅ Contains no-header instruction")
        else:
            print("❌ Missing no-header instruction")
            all_passed = False
    
    return all_passed

def test_end_to_end_format():
    """Test end-to-end email format (requires config)"""
    print("\n" + "="*60)
    print("Testing End-to-End Email Format")
    print("="*60)
    
    try:
        processor = EmailProcessor()
        
        # Test email with problematic content
        test_body_with_header = "Subject: Re: Test\n\nDear Customer,\n\nThis is the actual content."
        
        # Clean the body
        cleaned = processor._clean_email_body(test_body_with_header)
        
        print(f"Original body:\n{test_body_with_header}")
        print(f"\nCleaned body:\n{cleaned}")
        
        # Verify Subject is not in cleaned body
        if "Subject:" not in cleaned:
            print("\n✅ Subject line successfully removed from body")
            return True
        else:
            print("\n❌ Subject line still present in body")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not run end-to-end test: {e}")
        return None

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Email Format Fix Test Suite")
    print("="*60)
    print("Testing fixes for the 'Subject in body' issue")
    
    results = []
    
    # Run tests
    print("\n1. Testing EmailProcessor cleaning...")
    results.append(("EmailProcessor._clean_email_body", test_clean_email_body()))
    
    print("\n2. Testing GeminiEmailResponder cleaning...")
    results.append(("GeminiEmailResponder._clean_response", test_clean_response()))
    
    print("\n3. Testing prompt instructions...")
    results.append(("Prompt Generation", test_prompt_generation()))
    
    print("\n4. Testing end-to-end format...")
    e2e_result = test_end_to_end_format()
    if e2e_result is not None:
        results.append(("End-to-End", e2e_result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result and result is not None)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All email format fixes are working correctly!")
        print("The 'Subject in body' issue should now be resolved.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the fixes.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
