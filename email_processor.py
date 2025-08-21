# email_processor.py
"""
Email processor for Gemini API email response automation

- Date filtering to fetch only recent emails
- Threading support for email replies
- HTML/Markdown support
- Message-ID extraction for proper threading

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import json
import smtplib
import imaplib
import email
import re
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from config import EMAIL_CONFIG

class EmailProcessor:
    """
    Email processor with date filtering and threading support.
    """
    
    def __init__(self, config=EMAIL_CONFIG):
        """
        Initialize with email configuration.
        """
        self.config = config
        
    def fetch_emails(self, limit=2, unread_only=True, folder='inbox', days_back=7):
        """
        Fetch emails from the specified folder with date filtering.
        
        Filters emails by date to avoid processing old emails.
        Extracts Message-ID for threading support.
        
        Args:
            limit (int): Maximum number of emails to fetch
            unread_only (bool): Whether to fetch only unread emails
            folder (str): Mailbox folder to fetch from
            days_back (int): Number of days to look back for emails
            
        Returns:
            list: List of email dictionaries with threading information
        """
        try:
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['email_address'], self.config['email_password'])
            mail.select(folder)
            
            # Calculate date for filtering - only get recent emails
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Build search criteria with date filtering
            search_parts = []
            if unread_only:
                search_parts.append('UNSEEN')
            search_parts.append(f'SINCE {since_date}')
            
            # Join search criteria
            search_criteria = f'({" ".join(search_parts)})'
            
            # Search for emails with date filter
            print(f"Searching for emails: {search_criteria}")
            status, data = mail.search(None, search_criteria)
            
            if status != 'OK':
                print(f"Error searching for emails: {status}")
                return []
            
            # Get email IDs and reverse to get newest first
            email_ids = data[0].split()
            email_ids = list(reversed(email_ids))  # Newest first
            
            # Limit the number of emails to process
            if limit > 0:
                email_ids = email_ids[:limit]
            
            if not email_ids:
                print(f"No emails found in the last {days_back} days")
                return []
            
            emails = []
            
            # Process each email
            for email_id in email_ids:
                # Fetch the email using its ID
                status, data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    print(f"Error fetching email ID {email_id}: {status}")
                    continue
                
                # Parse the raw email data
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract email headers including Message-ID for threading
                subject = self._decode_header(msg['subject'])
                from_address = self._decode_header(msg['from'])
                to_address = self._decode_header(msg['to'])
                date = msg['date']
                message_id = msg.get('Message-ID', '')  # Extract Message-ID
                references = msg.get('References', '')   # Extract References
                in_reply_to = msg.get('In-Reply-To', '') # Extract In-Reply-To
                
                # Parse date to check if it's recent
                try:
                    from email.utils import parsedate_to_datetime
                    email_date = parsedate_to_datetime(date)
                    age_days = (datetime.now(email_date.tzinfo) - email_date).days
                    
                    # Skip emails older than days_back
                    if age_days > days_back:
                        print(f"Skipping old email from {age_days} days ago: {subject}")
                        continue
                except Exception as e:
                    print(f"Could not parse date for email: {e}")
                
                # Extract the email body
                body = self._get_email_body(msg)
                
                # Create email dictionary with threading information
                email_data = {
                    'id': email_id.decode(),
                    'message_id': message_id,      # Include Message-ID
                    'references': references,       # Include References
                    'in_reply_to': in_reply_to,   # Include In-Reply-To
                    'from': from_address,
                    'to': to_address,
                    'subject': subject,
                    'date': date,
                    'body': body
                }
                
                emails.append(email_data)
                
                # For debugging purposes
                print(f"Fetched email: {subject} from {from_address} (Date: {date})")
            
            # Close the connection properly
            mail.close()
            mail.logout()
            
            print(f"Successfully fetched {len(emails)} recent email(s)")
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []
    
    def _decode_header(self, header_value):
        """
        Decode email header values properly.
        """
        if header_value is None:
            return ""
            
        try:
            decoded_parts = []
            for part, encoding in decode_header(header_value):
                if isinstance(part, bytes):
                    if encoding:
                        decoded_parts.append(part.decode(encoding or 'utf-8', errors='replace'))
                    else:
                        decoded_parts.append(part.decode('utf-8', errors='replace'))
                else:
                    decoded_parts.append(part)
            return ''.join(decoded_parts)
        except Exception as e:
            print(f"Error decoding header: {str(e)}")
            return header_value
    
    def _get_email_body(self, msg):
        """
        Extract the body content from an email message.
        """
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(charset, errors="replace")
                        break
                    except Exception as e:
                        print(f"Error decoding email body: {str(e)}")
                        continue
                        
                elif content_type == "text/html" and not body:
                    try:
                        charset = part.get_content_charset() or "utf-8"
                        html_body = part.get_payload(decode=True).decode(charset, errors="replace")
                        # Convert HTML to plain text (basic conversion)
                        import re
                        body = re.sub('<[^<]+?>', '', html_body)
                    except Exception as e:
                        print(f"Error decoding HTML body: {str(e)}")
                        continue
        else:
            try:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="replace")
            except Exception as e:
                print(f"Error decoding simple email body: {str(e)}")
        
        return body
    
    def send_email(self, to_address, subject, body, from_address=None, 
                   cc_address=None, message_id=None, references=None, use_html=False):
        """
        Send an email response with threading support.
        
        Properly threads emails using In-Reply-To and References headers.
        Supports HTML formatting for better presentation.
        
        Args:
            to_address (str): Recipient email address
            subject (str): Email subject (properly placed in header)
            body (str): Email body content
            from_address (str, optional): Sender email address
            cc_address (str, optional): CC recipient(s)
            message_id (str, optional): Original Message-ID for threading
            references (str, optional): References header for threading
            use_html (bool): Whether to send HTML formatted email
            
        Returns:
            bool: Success status
        """
        try:
            # Create a multipart message with proper structure
            if use_html:
                msg = MIMEMultipart('alternative')
            else:
                msg = MIMEMultipart()
            
            # Set message headers
            msg['From'] = from_address or self.config['email_address']
            msg['To'] = to_address
            msg['Subject'] = subject  # Subject in header, not body
            
            # Add threading headers for proper email chain
            if message_id:
                msg['In-Reply-To'] = message_id
                # Build References header (original message + any previous references)
                if references:
                    msg['References'] = f"{references} {message_id}"
                else:
                    msg['References'] = message_id
            
            # Add CC if provided
            if cc_address:
                msg['Cc'] = cc_address
            
            # IMPORTANT: Clean the body - remove any "Subject:" lines that shouldn't be there
            cleaned_body = self._clean_email_body(body)
            
            # Add plain text version
            text_part = MIMEText(cleaned_body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML version for better formatting
            if use_html:
                # Convert markdown-style formatting to HTML
                html_body = self._convert_to_html(cleaned_body)
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Connect to the SMTP server
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_address'], self.config['email_password'])
            
            # Determine all recipients
            recipients = [to_address]
            if cc_address:
                recipients.extend([cc for cc in cc_address.split(',') if cc.strip()])
            
            # Send the message
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {to_address} (threaded: {bool(message_id)})")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _clean_email_body(self, body):
        """
        Remove any subject lines or email headers that might have been included in the body.
        
        This prevents the common issue of having "Subject: Re: ..." appearing in the email body.
        """
        if not body:
            return body
            
        # Split into lines for processing
        lines = body.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            # Check if this line looks like an email header
            if (line.strip().startswith('Subject:') or 
                line.strip().startswith('From:') or 
                line.strip().startswith('To:') or 
                line.strip().startswith('Date:') or 
                line.strip().startswith('Re:')):
                # Skip this line and potentially the next empty line
                skip_next_empty = True
                continue
            
            # Skip empty line immediately after a removed header
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        # Join back and clean up any leading/trailing whitespace
        cleaned_body = '\n'.join(cleaned_lines).strip()
        
        # If the body starts with "Dear" or "Hello" after cleaning, it's probably correct
        # Otherwise, if it seems to start mid-sentence, preserve original
        if not cleaned_body and body:
            return body  # Fallback to original if cleaning removed everything
        
        return cleaned_body
    
    def _convert_to_html(self, text):
        """
        Convert plain text with markdown-style formatting to HTML.
        
        Converts markdown formatting to HTML for better email presentation.
        """
        # Basic HTML template
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                p {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
        """
        
        # Convert markdown-style formatting
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Convert line breaks to paragraphs
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                html += f"<p>{para.strip()}</p>\n"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def parse_email_for_response(self, email_data):
        """
        Parse email data to extract information needed for response generation.
        With threading information.
        """
        # Extract relevant fields including threading info
        parsed = {
            'from': email_data.get('from', ''),
            'to': email_data.get('to', ''),
            'subject': email_data.get('subject', ''),
            'body': email_data.get('body', ''),
            'date': email_data.get('date', ''),
            'message_id': email_data.get('message_id', ''),  # Include for threading
            'references': email_data.get('references', ''),   # Include for threading
        }
        
        # Extract sender name from email address if possible
        sender_name = self._extract_sender_name(parsed['from'])
        if sender_name:
            parsed['sender_name'] = sender_name
        
        # Determine email category based on subject and body
        category, keywords = self._categorize_email(parsed)
        parsed['category'] = category
        parsed['matched_keywords'] = keywords
        
        # Determine email sentiment
        sentiment = self._analyze_sentiment(parsed)
        parsed['sentiment'] = sentiment
        
        # Determine priority based on content and sentiment
        priority = self._determine_priority(parsed, category, sentiment)
        parsed['priority'] = priority
        
        print(f"Email categorized as: {category} (Priority: {priority}, Sentiment: {sentiment})")
        print(f"Matched keywords: {', '.join(keywords) if keywords else 'None'}")
        
        return parsed
    
    def _extract_sender_name(self, from_address):
        """Extract the sender's name from an email address."""
        if '<' in from_address and '>' in from_address:
            match = re.search(r'^"?([^"<]+)"?\s*<[^>]+>$', from_address)
            if match:
                return match.group(1).strip()
        return None
    
    def _categorize_email(self, email_data):
        """Categorize email based on content analysis."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        text = f"{subject} {body}"
        
        categories = {
            'complaint': [
                'complaint', 'disappointed', 'unhappy', 'terrible', 'awful', 'poor', 
                'unsatisfied', 'frustrated', 'upset', 'angry', 'annoyed', 'dissatisfied',
                'problem with', 'not working', 'does not work', 'failed', 'failing',
                'issue with', 'bad experience', 'bad service', 'poor quality'
            ],
            'product_support': [
                'login', 'password', 'error', 'not working', 'help', 'how to', 'does not work',
                'broken', 'bug', 'technical', 'support', 'assistance', 'problem',
                'troubleshoot', 'issue', 'fix', 'solution'
            ],
            'feature_request': [
                'feature', 'suggestion', 'improve', 'enhancement', 'add', 'missing', 
                'should have', 'would be nice', 'could you add', 'please include',
                'consider adding', 'new feature', 'functionality', 'capability'
            ],
            'billing_question': [
                'bill', 'charge', 'payment', 'refund', 'subscription', 'price', 'cost',
                'discount', 'invoice', 'credit card', 'transaction', 'receipt',
                'cancellation', 'renewal', 'billing', 'charged', 'fee', 'pricing'
            ],
            'general_feedback': [
                'thank', 'great', 'love', 'awesome', 'excellent', 'amazing', 'good',
                'appreciate', 'feedback', 'enjoyed', 'wonderful', 'fantastic',
                'satisfied', 'helpful', 'impressive'
            ],
            'urgent_request': [
                'urgent', 'emergency', 'asap', 'immediate', 'critical', 'important',
                'time sensitive', 'deadline', 'quickly', 'rush', 'priority', 'immediately',
                'as soon as possible', 'promptly', 'fast', 'today'
            ],
            'spam': [
                'lottery', 'million dollars', 'bitcoin', 'investment opportunity',
                'inheritance', 'claim your', 'free money',
                'winner', 'jackpot', 'casino', 'earn money fast', 'get rich'
            ]
        }
        
        matched_category = None
        matched_keywords = []
        category_matches = {}
        
        for category, keywords in categories.items():
            category_matches[category] = []
            for keyword in keywords:
                if keyword in text:
                    category_matches[category].append(keyword)
                    matched_keywords.append(keyword)
        
        priority_order = ['urgent_request', 'complaint', 'billing_question', 'product_support', 
                        'feature_request', 'spam', 'general_feedback', 'customer_inquiry']
        
        for category in priority_order:
            if category in category_matches and category_matches[category]:
                matched_category = category
                break
        
        if not matched_category:
            return 'customer_inquiry', []
            
        return matched_category, matched_keywords
    
    def _analyze_sentiment(self, email_data):
        """Perform basic sentiment analysis on email content."""
        text = f"{email_data.get('subject', '')} {email_data.get('body', '')}".lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'like',
            'happy', 'pleased', 'satisfied', 'thank', 'thanks', 'helpful', 'appreciate',
            'awesome', 'fantastic', 'perfect', 'best', 'impressed'
        ]
        
        negative_words = [
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointed', 'upset',
            'angry', 'unhappy', 'not working', 'problem', 'issue', 'broken', 'error',
            'failed', 'wrong', 'worst', 'hate', 'dislike', 'annoyed', 'frustrating'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _determine_priority(self, email_data, category, sentiment):
        """Determine the priority level of the email."""
        if category in ['complaint', 'urgent_request']:
            return 'high'
        
        if category in ['product_support', 'billing_question'] or sentiment == 'negative':
            return 'medium'
        
        return 'low'