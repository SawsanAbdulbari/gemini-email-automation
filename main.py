# main.py
"""
Main Application Script for Gemini API Email Response Automation
Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
Version: 4.0 
"""

import time
import datetime
import logging
import sys
from typing import Dict
from gemini_email import GeminiEmailResponder
from email_processor import EmailProcessor
from email_filter import EmailFilter
from email_tracker import EmailTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailAutomationSystem:
    """
    Email automation system with threading and date filtering.
    """
    
    def __init__(self):
        """Initialize all system components."""
        self.email_processor = EmailProcessor()
        self.gemini_responder = GeminiEmailResponder()
        self.email_tracker = EmailTracker()
        self.email_filter = EmailFilter()
        
        # Configuration
        self.config = {
            "max_emails_per_cycle": 1,  # Process one email at a time
            "check_interval": 30,  # Seconds between checks
            "max_emails_per_sender": 3,  # Max emails from same sender per day
            "spam_threshold": 0.5,  # Spam score threshold (0.0-1.0)
            "rate_limit_window": 24,  # Hours for rate limiting
            "days_to_check": 7,  # Only check emails from last N days
            "use_html_emails": True,  # Use HTML for better formatting
        }
        
        # Statistics
        self.stats = {
            "total_processed": 0,
            "responses_sent": 0,
            "emails_skipped": 0,
            "errors": 0,
            "categories": {}
        }
    
    def should_process_email(self, email_data: Dict) -> tuple[bool, str]:
        """
        Determine if an email should be processed and responded to.
        """
        email_id = email_data.get('id')
        from_address = email_data.get('from', '')
        
        # Check if already processed
        if self.email_tracker.is_processed(email_id):
            return False, "Already processed"
        
        # Check if it should be filtered out
        should_skip, skip_reason = self.email_filter.should_skip_email(
            email_data, 
            self.config["spam_threshold"]
        )
        if should_skip:
            return False, skip_reason
        
        # Check rate limiting per sender
        sender_count = self.email_tracker.count_sender_emails(
            from_address, 
            hours=self.config["rate_limit_window"]
        )
        if sender_count >= self.config["max_emails_per_sender"]:
            return False, f"Rate limit exceeded for sender (max {self.config['max_emails_per_sender']} per {self.config['rate_limit_window']}h)"
        
        return True, ""
    
    def process_single_email(self, email_data: Dict) -> bool:
        """
        Process a single email and generate/send response if appropriate.
        
        """
        email_id = email_data.get('id')
        
        try:
            # Display email information
            print(f"\n{'='*50}")
            print(f"Processing Email ID: {email_id}")
            print(f"Subject: {email_data['subject'][:80]}...")
            print(f"From: {email_data['from']}")
            print(f"Date: {email_data.get('date', 'Unknown')}") 
            
            # Check if we should process this email
            should_process, reason = self.should_process_email(email_data)
            
            if not should_process:
                print(f"⚠️ Skipping email: {reason}")
                logger.info(f"Skipped email {email_id}: {reason}")
                self.stats["emails_skipped"] += 1
                
                # Mark as processed even though we didn't respond
                self.email_tracker.mark_as_processed(
                    email_id, 
                    email_data, 
                    response_sent=False
                )
                return True
            
            # Parse and categorize the email
            parsed_email = self.email_processor.parse_email_for_response(email_data)
            category = parsed_email.get('category', 'unknown')
            
            # Update statistics
            self.stats["total_processed"] += 1
            if category not in self.stats["categories"]:
                self.stats["categories"][category] = 0
            self.stats["categories"][category] += 1
            
            # Display categorization
            print(f"Category: {category}")
            print(f"Sentiment: {parsed_email.get('sentiment', 'neutral')}")
            print(f"Priority: {parsed_email.get('priority', 'medium')}")
            
            # Additional security check for high-risk categories
            if category == "spam":
                print("⚠️ Email categorized as spam - not responding")
                self.email_tracker.mark_as_processed(
                    email_id, 
                    parsed_email, 
                    response_sent=False
                )
                return True
            
            # Sanitize email content before generating response
            sanitized_email = self.email_filter.sanitize_email_for_response(parsed_email)
            
            # Generate response using Gemini API
            print("\n📝 Generating response using Gemini API...")
            response = self.gemini_responder.generate_response(
                sanitized_email, 
                email_type=category
            )
            
            if not response:
                logger.error(f"Failed to generate response for email {email_id}")
                self.stats["errors"] += 1
                return False
            
            # Preview response
            preview = response[:150] + "..." if len(response) > 150 else response
            print(f"Response preview: {preview}")
            
            # Create proper reply subject
            original_subject = parsed_email.get('subject', '')
            # Check if it already has "Re:" prefix
            if original_subject.lower().startswith('re:'):
                reply_subject = original_subject
            else:
                reply_subject = f"Re: {original_subject}"
            
            # Send the response with threading information
            print(f"\n📧 Sending threaded response to {parsed_email['from']}...")
            
            # Extract threading information
            message_id = parsed_email.get('message_id', '')
            references = parsed_email.get('references', '')
            
            # Send with proper threading
            success = self.email_processor.send_email(
                to_address=parsed_email['from'],
                subject=reply_subject,  # Subject in proper field
                body=response,
                message_id=message_id,  # Include for threading
                references=references,   # Include for threading
                use_html=self.config["use_html_emails"]  # Use HTML formatting
            )
            
            if success:
                print("✅ Response sent successfully (threaded reply)")
                self.stats["responses_sent"] += 1
                logger.info(f"Successfully processed and responded to email {email_id}")
            else:
                print("❌ Failed to send response")
                self.stats["errors"] += 1
                logger.error(f"Failed to send response for email {email_id}")
            
            # Mark as processed
            self.email_tracker.mark_as_processed(
                email_id, 
                parsed_email, 
                response_sent=success
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            
            # Mark as processed to avoid retrying problematic emails
            self.email_tracker.mark_as_processed(
                email_id, 
                email_data, 
                response_sent=False
            )
            return False
    
    def display_statistics(self):
        """Display current processing statistics."""
        print("\n" + "="*50)
        print("📊 Processing Statistics:")
        print(f"  Total processed: {self.stats['total_processed']}")
        print(f"  Responses sent: {self.stats['responses_sent']}")
        print(f"  Emails skipped: {self.stats['emails_skipped']}")
        print(f"  Errors: {self.stats['errors']}")
        
        if self.stats["categories"]:
            print("  Categories:")
            for category, count in self.stats["categories"].items():
                print(f"    - {category}: {count}")
        
        # Get tracker statistics
        tracker_stats = self.email_tracker.get_processing_stats()
        print(f"\n  Historical stats (last {self.email_tracker.max_history_days} days):")
        print(f"    - Total in history: {tracker_stats['total_processed']}")
        print("="*50)
    
    def run(self):
        """
        Main execution loop for the email automation system.
        
        Fetches only recent emails.
        """
        # Display startup banner
        print("\n" + "="*60)
        print("   Gemini API Email Response Automation System v4.0")
        print("   Threading & Date Filtering")
        print("   HAMK Digital and Social Media Analytics")
        print("="*60)
        print(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Configuration:")
        print(f"  - Check interval: {self.config['check_interval']} seconds")
        print(f"  - Max emails per cycle: {self.config['max_emails_per_cycle']}")
        print(f"  - Days to check: {self.config['days_to_check']} days")  # Show date range
        print(f"  - Spam threshold: {self.config['spam_threshold']}")
        print(f"  - Rate limit: {self.config['max_emails_per_sender']} emails per sender per {self.config['rate_limit_window']}h")
        print(f"  - HTML emails: {self.config['use_html_emails']}")  # Show HTML status
        print("\nPress Ctrl+C to stop the system")
        print("-"*60)
        
        logger.info("Email automation system started (v4.0)")
        
        try:
            while True:
                try:
                    current_time = datetime.datetime.now().strftime('%H:%M:%S')
                    print(f"\n🔍 Checking for new emails from last {self.config['days_to_check']} days... ({current_time})")
                    
                    # Fetch unread emails with date filtering
                    emails = self.email_processor.fetch_emails(
                        limit=self.config["max_emails_per_cycle"],
                        unread_only=True,
                        days_back=self.config["days_to_check"]  # Only recent emails
                    )
                    
                    if emails:
                        print(f"📬 Found {len(emails)} new email(s) from the last {self.config['days_to_check']} days")
                        
                        for email_data in emails:
                            self.process_single_email(email_data)
                        
                        # Display statistics after processing
                        self.display_statistics()
                    else:
                        print(f"📭 No new emails in the last {self.config['days_to_check']} days")
                    
                    # Wait before next check
                    print(f"\n⏰ Next check in {self.config['check_interval']} seconds...")
                    time.sleep(self.config['check_interval'])
                    
                except KeyboardInterrupt:
                    raise  # Re-raise to handle in outer try block
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                    print(f"\n❌ Error occurred: {str(e)}")
                    print("Retrying in 60 seconds...")
                    time.sleep(60)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested by user...")
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of the system."""
        print("\n" + "="*60)
        print("System Shutdown")
        print("="*60)
        
        # Display final statistics
        print("Final Statistics:")
        print(f"  Total emails processed: {self.stats['total_processed']}")
        print(f"  Responses sent: {self.stats['responses_sent']}")
        print(f"  Emails skipped: {self.stats['emails_skipped']}")
        print(f"  Errors encountered: {self.stats['errors']}")
        
        if self.stats["categories"]:
            print("\n  Categories breakdown:")
            for category, count in self.stats["categories"].items():
                print(f"    - {category}: {count}")
        
        # Get historical statistics
        tracker_stats = self.email_tracker.get_processing_stats()
        print(f"\n  Historical totals (last {self.email_tracker.max_history_days} days):")
        print(f"    - Total processed: {tracker_stats['total_processed']}")
        print(f"    - Responses sent: {tracker_stats['responses_sent']}")
        
        print("\n✨ Thank you for using the Gemini Email Automation System!")
        print("="*60)
        
        logger.info("Email automation system shut down gracefully")

def main():
    """Entry point for the application."""
    try:
        system = EmailAutomationSystem()
        system.run()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()