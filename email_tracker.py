# email_tracker.py
"""
Email tracking module to prevent duplicate processing and track email history.

This module maintains a history of processed emails to prevent
responding to the same email multiple times.

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Set

class EmailTracker:
    """
    Track processed emails to prevent duplicate responses.
    """
    
    def __init__(self, history_file: str = "processed_emails.json", max_history_days: int = 7):
        """
        Initialize the email tracker.
        
        Args:
            history_file: Path to file storing processed email history
            max_history_days: Number of days to keep email history
        """
        self.history_file = history_file
        self.max_history_days = max_history_days
        self.processed_emails = self._load_history()
        
    def _load_history(self) -> Dict:
        """
        Load email processing history from file.
        
        Returns:
            Dictionary containing email history
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                return {"emails": {}, "last_cleanup": datetime.now().isoformat()}
        else:
            return {"emails": {}, "last_cleanup": datetime.now().isoformat()}
    
    def _save_history(self):
        """Save email processing history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.processed_emails, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save email history: {e}")
    
    def _cleanup_old_entries(self):
        """Remove email entries older than max_history_days."""
        cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
        emails_to_remove = []
        
        for email_id, data in self.processed_emails.get("emails", {}).items():
            processed_date = datetime.fromisoformat(data.get("processed_at", datetime.now().isoformat()))
            if processed_date < cutoff_date:
                emails_to_remove.append(email_id)
        
        for email_id in emails_to_remove:
            del self.processed_emails["emails"][email_id]
        
        if emails_to_remove:
            print(f"Cleaned up {len(emails_to_remove)} old email entries")
            self.processed_emails["last_cleanup"] = datetime.now().isoformat()
            self._save_history()
    
    def is_processed(self, email_id: str) -> bool:
        """
        Check if an email has already been processed.
        
        Args:
            email_id: Unique identifier for the email
            
        Returns:
            True if email has been processed before
        """
        return email_id in self.processed_emails.get("emails", {})
    
    def mark_as_processed(self, email_id: str, email_data: Dict, response_sent: bool = True):
        """
        Mark an email as processed.
        
        Args:
            email_id: Unique identifier for the email
            email_data: Email information
            response_sent: Whether a response was sent
        """
        if "emails" not in self.processed_emails:
            self.processed_emails["emails"] = {}
        
        self.processed_emails["emails"][email_id] = {
            "processed_at": datetime.now().isoformat(),
            "subject": email_data.get("subject", "")[:100],  # Store first 100 chars
            "from": email_data.get("from", ""),
            "category": email_data.get("category", "unknown"),
            "response_sent": response_sent
        }
        
        self._save_history()
        
        # Periodic cleanup
        last_cleanup = datetime.fromisoformat(
            self.processed_emails.get("last_cleanup", datetime.now().isoformat())
        )
        if (datetime.now() - last_cleanup).days >= 1:
            self._cleanup_old_entries()
    
    def get_processing_stats(self) -> Dict:
        """
        Get statistics about processed emails.
        
        Returns:
            Dictionary containing processing statistics
        """
        emails = self.processed_emails.get("emails", {})
        
        if not emails:
            return {
                "total_processed": 0,
                "responses_sent": 0,
                "categories": {}
            }
        
        stats = {
            "total_processed": len(emails),
            "responses_sent": sum(1 for e in emails.values() if e.get("response_sent")),
            "categories": {}
        }
        
        # Count by category
        for email_data in emails.values():
            category = email_data.get("category", "unknown")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        return stats
    
    def get_recent_senders(self, hours: int = 24) -> Set[str]:
        """
        Get list of senders who have sent emails in the last N hours.
        Used to detect potential spam/flooding.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Set of sender email addresses
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_senders = set()
        
        for email_data in self.processed_emails.get("emails", {}).values():
            processed_time = datetime.fromisoformat(email_data.get("processed_at"))
            if processed_time >= cutoff_time:
                recent_senders.add(email_data.get("from", "").lower())
        
        return recent_senders
    
    def count_sender_emails(self, sender: str, hours: int = 24) -> int:
        """
        Count how many emails a sender has sent in the last N hours.
        
        Args:
            sender: Sender email address
            hours: Number of hours to look back
            
        Returns:
            Number of emails from this sender
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        sender_lower = sender.lower()
        count = 0
        
        for email_data in self.processed_emails.get("emails", {}).values():
            processed_time = datetime.fromisoformat(email_data.get("processed_at"))
            if processed_time >= cutoff_time:
                if email_data.get("from", "").lower() == sender_lower:
                    count += 1
        
        return count