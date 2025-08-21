# email_filter.py
"""
Email filtering module for security and spam prevention.

This module provides filtering capabilities to prevent the system from
responding to potentially dangerous or spam emails.

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import re
from typing import List, Tuple, Dict

class EmailFilter:
    """
    Filter emails to prevent responding to spam, phishing, and dangerous senders.
    """
    
    # Known no-reply patterns
    NO_REPLY_PATTERNS = [
        r'noreply@.*',
        r'no-reply@.*',
        r'donotreply@.*',
        r'do-not-reply@.*',
        r'notifications@.*',
        r'alerts@.*',
        r'automated@.*',
        r'system@.*',
        r'mailer-daemon@.*',
        r'postmaster@.*'
    ]
    
    # Suspicious sender patterns (potential phishing)
    SUSPICIOUS_SENDERS = [
        r'.*@.*paypal\..*',  # PayPal phishing (unless from paypal.com)
        r'.*@.*banking\..*',
        r'.*@.*amazon\..*',  # Amazon phishing (unless from amazon.com)
        r'.*@.*ebay\..*',    # eBay phishing (unless from ebay.com)
        r'.*@.*lottery\..*',
        r'.*@.*winner\..*',
        r'.*@.*prize\..*',
        r'.*@.*kilpailu\..*',  # Finnish contest/lottery
        r'.*@.*arvonta\..*',   # Finnish lottery
        r'.*voita@.*',         # Finnish "win" emails
    ]
    
    # Whitelisted domains (legitimate companies)
    WHITELIST_DOMAINS = [
        'paypal.com',
        'amazon.com',
        'amazon.co.uk',
        'ebay.com',
        'google.com',
        'microsoft.com',
        'apple.com',
        'facebook.com',
        'linkedin.com'
    ]
    
    # Spam keywords in subject or body
    SPAM_KEYWORDS = [
        # Financial scams
        'lottery', 'winner', 'million dollars', 'inheritance', 'bitcoin',
        'investment opportunity', 'claim your', 'free money', 'jackpot',
        'casino', 'get rich', 'earn money fast', 'prize winner',
        
        # Finnish spam
        'voita', 'arvonta', 'kilpailu', 'ilmainen', 'voittaja',
        
        # Urgency scams
        'act now', 'limited time', 'expires today', 'urgent action required',
        
        # Phishing attempts
        'verify your account', 'suspended account', 'click here immediately',
        'confirm your identity', 'update payment information',
        
        # Adult content
        'xxx', 'adult', 'singles', 'dating',
        
        # Pharmaceuticals
        'viagra', 'cialis', 'pharmacy', 'pills', 'medication'
    ]
    
    @classmethod
    def is_no_reply_address(cls, email_address: str) -> bool:
        """
        Check if an email address is a no-reply address.
        
        Args:
            email_address: The sender's email address
            
        Returns:
            bool: True if it's a no-reply address
        """
        email_lower = email_address.lower()
        
        # Check against no-reply patterns
        for pattern in cls.NO_REPLY_PATTERNS:
            if re.match(pattern, email_lower):
                return True
        
        return False
    
    @classmethod
    def is_suspicious_sender(cls, email_address: str) -> bool:
        """
        Check if an email address appears to be suspicious or phishing.
        
        Args:
            email_address: The sender's email address
            
        Returns:
            bool: True if the sender appears suspicious
        """
        # Extract just the email part if it includes a name
        if '<' in email_address and '>' in email_address:
            match = re.search(r'<([^>]+)>', email_address)
            if match:
                email_address = match.group(1)
        
        email_lower = email_address.lower()
        
        # Check if it's from a whitelisted domain
        for domain in cls.WHITELIST_DOMAINS:
            if email_lower.endswith(f'@{domain}'):
                return False  # Legitimate sender
        
        # Check against suspicious patterns
        for pattern in cls.SUSPICIOUS_SENDERS:
            if re.match(pattern, email_lower):
                return True
        
        return False
    
    @classmethod
    def calculate_spam_score(cls, email_data: Dict) -> Tuple[float, List[str]]:
        """
        Calculate a spam score for an email based on various factors.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Tuple of (spam_score, reasons)
            spam_score: 0.0 (not spam) to 1.0 (definitely spam)
            reasons: List of reasons for the score
        """
        score = 0.0
        reasons = []
        
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        from_address = email_data.get('from', '').lower()
        
        # Check sender
        if cls.is_no_reply_address(from_address):
            score += 0.3
            reasons.append("No-reply address")
        
        if cls.is_suspicious_sender(from_address):
            score += 0.5
            reasons.append("Suspicious sender pattern")
        
        # Check for spam keywords
        spam_keyword_count = 0
        found_keywords = []
        for keyword in cls.SPAM_KEYWORDS:
            if keyword in subject or keyword in body:
                spam_keyword_count += 1
                found_keywords.append(keyword)
        
        if spam_keyword_count > 0:
            # Add score based on number of spam keywords
            keyword_score = min(0.5, spam_keyword_count * 0.1)
            score += keyword_score
            reasons.append(f"Spam keywords found: {', '.join(found_keywords[:5])}")
        
        # Check for excessive capitalization in subject
        if subject:
            caps_ratio = sum(1 for c in subject if c.isupper()) / len(subject)
            if caps_ratio > 0.5:
                score += 0.2
                reasons.append("Excessive capitalization")
        
        # Check for suspicious attachments mentioned
        suspicious_extensions = ['.exe', '.zip', '.rar', '.bat', '.cmd', '.scr']
        for ext in suspicious_extensions:
            if ext in body:
                score += 0.3
                reasons.append(f"Suspicious attachment type: {ext}")
        
        # Check for URL shorteners (often used in phishing)
        url_shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co']
        for shortener in url_shorteners:
            if shortener in body:
                score += 0.2
                reasons.append(f"URL shortener detected: {shortener}")
        
        # Cap the score at 1.0
        score = min(1.0, score)
        
        return score, reasons
    
    @classmethod
    def should_skip_email(cls, email_data: Dict, spam_threshold: float = 0.5) -> Tuple[bool, str]:
        """
        Determine if an email should be skipped (not responded to).
        
        Args:
            email_data: Dictionary containing email information
            spam_threshold: Threshold above which email is considered spam (0.0-1.0)
            
        Returns:
            Tuple of (should_skip, reason)
        """
        from_address = email_data.get('from', '')
        
        # Check if it's a no-reply address
        if cls.is_no_reply_address(from_address):
            return True, "No-reply address"
        
        # Calculate spam score
        spam_score, reasons = cls.calculate_spam_score(email_data)
        
        # Skip if spam score exceeds threshold
        if spam_score >= spam_threshold:
            reason = f"High spam score ({spam_score:.2f}): {'; '.join(reasons)}"
            return True, reason
        
        # Check for specific dangerous patterns
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        
        # Never respond to emails about payments/receipts from payment processors
        payment_keywords = ['receipt', 'payment', 'invoice', 'transaction']
        payment_domains = ['paypal', 'stripe', 'square', 'venmo']
        
        for keyword in payment_keywords:
            if keyword in subject:
                for domain in payment_domains:
                    if domain in from_address.lower():
                        return True, f"Payment processor email ({domain})"
        
        return False, ""
    
    @classmethod
    def sanitize_email_for_response(cls, email_data: Dict) -> Dict:
        """
        Sanitize email data before generating a response.
        Removes potentially dangerous content.
        
        Args:
            email_data: Original email data
            
        Returns:
            Sanitized email data
        """
        import copy
        sanitized = copy.deepcopy(email_data)
        
        # Remove any URLs from the body to prevent clicking on malicious links
        body = sanitized.get('body', '')
        # Simple URL removal (not perfect but helps)
        url_pattern = r'https?://[^\s]+'
        body = re.sub(url_pattern, '[URL REMOVED]', body)
        sanitized['body'] = body
        
        # Truncate very long bodies (potential attack vector)
        max_body_length = 5000
        if len(body) > max_body_length:
            sanitized['body'] = body[:max_body_length] + '... [TRUNCATED]'
        
        return sanitized