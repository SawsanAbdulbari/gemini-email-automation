"""
test_email_automation.py - Unit Tests for Email Automation System

This file contains unit tests to verify the email automation system works correctly.
Students can run these tests to ensure their implementation is working.

Run with: python -m pytest test_email_automation.py
Or simply: python test_email_automation.py

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_processor import EmailProcessor
from gemini_email import GeminiEmailResponder

class TestEmailCategorization(unittest.TestCase):
    """Test email categorization functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_processor = EmailProcessor()
    
    def test_complaint_categorization(self):
        """Test if complaints are correctly identified"""
        email_data = {
            'from': 'angry@customer.com',
            'subject': 'Terrible service',
            'body': 'I am extremely disappointed with your product. It does not work at all!'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'complaint')
        self.assertEqual(result['sentiment'], 'negative')
    
    def test_support_categorization(self):
        """Test if support requests are correctly identified"""
        email_data = {
            'from': 'user@example.com',
            'subject': 'Login help needed',
            'body': 'I cannot log in to my account. Getting an error message. Please help!'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'product_support')
    
    def test_feature_request_categorization(self):
        """Test if feature requests are correctly identified"""
        email_data = {
            'from': 'user@example.com',
            'subject': 'Feature suggestion',
            'body': 'It would be great if you could add dark mode to the application.'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'feature_request')
    
    def test_positive_feedback_categorization(self):
        """Test if positive feedback is correctly identified"""
        email_data = {
            'from': 'happy@customer.com',
            'subject': 'Love your product!',
            'body': 'Thank you for creating such an amazing product. It works perfectly!'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'general_feedback')
        self.assertEqual(result['sentiment'], 'positive')
    
    def test_billing_categorization(self):
        """Test if billing questions are correctly identified"""
        email_data = {
            'from': 'customer@example.com',
            'subject': 'Question about my bill',
            'body': 'I see a charge of $99 on my credit card but I thought it was $79?'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'billing_question')
    
    def test_urgent_categorization(self):
        """Test if urgent requests are correctly identified"""
        email_data = {
            'from': 'urgent@customer.com',
            'subject': 'URGENT - Need help immediately',
            'body': 'This is critical! Our system is down and we need help ASAP!'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'urgent_request')
        self.assertEqual(result['priority'], 'high')
    
    def test_spam_categorization(self):
        """Test if spam is correctly identified"""
        email_data = {
            'from': 'spammer@fake.com',
            'subject': 'You won million dollars!',
            'body': 'Click here to claim your lottery winnings! Get rich quick!'
        }
        result = self.email_processor.parse_email_for_response(email_data)
        self.assertEqual(result['category'], 'spam')

class TestGeminiResponder(unittest.TestCase):
    """Test Gemini API response generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Gemini API to avoid actual API calls during testing
        with patch('gemini_email.genai.GenerativeModel'):
            self.responder = GeminiEmailResponder()
    
    def test_temperature_selection(self):
        """Test if correct temperature is selected for different email types"""
        # Technical support should have lower temperature
        temp = self.responder._get_temperature_for_type('product_support')
        self.assertLess(temp, 0.5)
        
        # Feature requests can have higher temperature
        temp = self.responder._get_temperature_for_type('feature_request')
        self.assertGreater(temp, 0.7)
        
        # Complaints should be balanced
        temp = self.responder._get_temperature_for_type('complaint')
        self.assertGreaterEqual(temp, 0.3)
        self.assertLessEqual(temp, 0.7)
    
    def test_prompt_creation_complaint(self):
        """Test prompt creation for complaint emails"""
        email_content = {
            'from': 'john.doe@example.com',
            'subject': 'Product issue',
            'body': 'Your product is not working',
            'sender_name': 'John'
        }
        prompt = self.responder._create_prompt(email_content, 'complaint')
        
        # Check if prompt contains necessary elements
        self.assertIn('apologetic', prompt.lower())
        self.assertIn('John', prompt)
        self.assertIn('Customer Support Team', prompt)
    
    def test_prompt_creation_support(self):
        """Test prompt creation for support emails"""
        email_content = {
            'from': 'user@example.com',
            'subject': 'Help needed',
            'body': 'Cannot log in',
            'sender_name': 'User'
        }
        prompt = self.responder._create_prompt(email_content, 'product_support')
        
        # Check if prompt contains necessary elements
        self.assertIn('step-by-step', prompt.lower())
        self.assertIn('Technical Support Team', prompt)
    
    def test_fallback_response(self):
        """Test fallback response generation"""
        email_content = {
            'from': 'test@example.com',
            'subject': 'Test',
            'body': 'Test email'
        }
        
        # Test urgent fallback
        response = self.responder._get_fallback_response(email_content, 'urgent_request')
        self.assertIn('urgent', response.lower())
        
        # Test complaint fallback
        response = self.responder._get_fallback_response(email_content, 'complaint')
        self.assertIn('apologize', response.lower())
        
        # Test generic fallback
        response = self.responder._get_fallback_response(email_content, 'general')
        self.assertIn('Thank you', response)

class TestEmailSenderName(unittest.TestCase):
    """Test sender name extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_processor = EmailProcessor()
    
    def test_extract_sender_name_with_quotes(self):
        """Test extracting name from quoted format"""
        from_address = '"John Doe" <john.doe@example.com>'
        name = self.email_processor._extract_sender_name(from_address)
        self.assertEqual(name, 'John Doe')
    
    def test_extract_sender_name_without_quotes(self):
        """Test extracting name without quotes"""
        from_address = 'Jane Smith <jane@example.com>'
        name = self.email_processor._extract_sender_name(from_address)
        self.assertEqual(name, 'Jane Smith')
    
    def test_extract_sender_name_email_only(self):
        """Test when only email is provided"""
        from_address = 'user@example.com'
        name = self.email_processor._extract_sender_name(from_address)
        self.assertIsNone(name)

class TestPriorityDetermination(unittest.TestCase):
    """Test email priority determination"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_processor = EmailProcessor()
    
    def test_high_priority(self):
        """Test high priority assignment"""
        email_data = {'subject': 'test', 'body': 'test'}
        
        # Complaints should be high priority
        priority = self.email_processor._determine_priority(email_data, 'complaint', 'negative')
        self.assertEqual(priority, 'high')
        
        # Urgent requests should be high priority
        priority = self.email_processor._determine_priority(email_data, 'urgent_request', 'neutral')
        self.assertEqual(priority, 'high')
    
    def test_medium_priority(self):
        """Test medium priority assignment"""
        email_data = {'subject': 'test', 'body': 'test'}
        
        # Support requests should be medium priority
        priority = self.email_processor._determine_priority(email_data, 'product_support', 'neutral')
        self.assertEqual(priority, 'medium')
        
        # Negative sentiment should raise priority
        priority = self.email_processor._determine_priority(email_data, 'general_feedback', 'negative')
        self.assertEqual(priority, 'medium')
    
    def test_low_priority(self):
        """Test low priority assignment"""
        email_data = {'subject': 'test', 'body': 'test'}
        
        # Positive feedback should be low priority
        priority = self.email_processor._determine_priority(email_data, 'general_feedback', 'positive')
        self.assertEqual(priority, 'low')
        
        # Feature requests with positive sentiment should be low priority
        priority = self.email_processor._determine_priority(email_data, 'feature_request', 'positive')
        self.assertEqual(priority, 'low')

def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmailCategorization))
    suite.addTests(loader.loadTestsFromTestCase(TestGeminiResponder))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailSenderName))
    suite.addTests(loader.loadTestsFromTestCase(TestPriorityDetermination))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Your email automation system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Run the tests
    success = run_tests()
    sys.exit(0 if success else 1)