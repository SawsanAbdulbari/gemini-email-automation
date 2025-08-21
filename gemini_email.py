# gemini_email.py
"""
Gemini API Email Response Generator - Core Module

This module provides the core functionality for generating email responses
using the Gemini API. It handles API interaction, prompt engineering, and 
response formatting based on email categories.

This is part of the HAMK Digital and Social Media Analytics module project
to demonstrate AI-powered email automation using Google's Gemini API.

Author: Linda Marin and Sawsan Abdulbari for HAMK Digital and Social Media Analytics
Date: August 2025
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_CONFIG
import time

# Configure the Gemini API with our API key
genai.configure(api_key=GEMINI_API_KEY)

class GeminiEmailResponder:
    """
    Class for generating email responses using Gemini API.
    
    This class encapsulates the logic for creating prompts based on email categories
    and communicating with the Gemini API to generate appropriate responses.
    """
    
    def __init__(self, model_name=GEMINI_CONFIG["model"], config=GEMINI_CONFIG):
        """
        Initialize the responder with the specified model and configuration.
        
        Args:
            model_name (str): The Gemini model to use
                (Default: model specified in GEMINI_CONFIG)
            config (dict): Configuration for the Gemini API
                (Default: GEMINI_CONFIG from config.py)
        """
        # Initialize the Gemini model with the specified name
        self.model = genai.GenerativeModel(model_name)
        self.config = config
        
        # Initialize counters for rate limiting
        self.requests_count = 0
        self.last_request_time = time.time()
    
    def generate_response(self, email_content, email_type=None):
        """
        Generate a response to an email using Gemini API.
        
        This method creates an appropriate prompt based on the email type,
        sends it to the Gemini API, and returns the generated response.
        
        Args:
            email_content (dict): Email content with from, subject, and body fields
            email_type (str, optional): Type of email for context
                (e.g., 'complaint', 'inquiry', 'product_support')
            
        Returns:
            str: Generated email response
        """
        # Check if we need to handle rate limiting
        self._handle_rate_limiting()
        
        # Create a prompt with instructions based on email type
        prompt = self._create_prompt(email_content, email_type)
        
        # For educational purposes, show the prompt being used
        print(f"\nUsing prompt for {email_type}:")
        print(f"{prompt[:200]}... (truncated)")
        
        try:
            # Configure generation parameters
            generation_config = {
                "temperature": self._get_temperature_for_type(email_type),
                "top_p": self.config["top_p"],
                "top_k": self.config["top_k"],
                "max_output_tokens": self.config["max_output_tokens"],
            }
            
            # Generate content using the Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Update request counter
            self.requests_count += 1
            self.last_request_time = time.time()
            
            # Extract the text from the response
            generated_text = response.text
            
            # IMPORTANT: Clean the response to remove any subject lines or headers
            generated_text = self._clean_response(generated_text)
            
            # For educational purposes, show a preview of the response
            preview = generated_text[:100] + "..." if len(generated_text) > 100 else generated_text
            print(f"\nGenerated response preview: {preview}")
            
            return generated_text
            
        except Exception as e:
            # Handle API errors gracefully
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            
            # Provide a fallback response for real-world scenarios
            fallback_response = self._get_fallback_response(email_content, email_type)
            print(f"Using fallback response instead.")
            
            return fallback_response
    
    def _handle_rate_limiting(self, max_requests_per_minute=60):
        """
        Handle API rate limiting to avoid exceeding quotas.
        
        Implements a simple rate limiting mechanism to ensure we don't
        exceed the API's rate limits.
        
        Args:
            max_requests_per_minute (int): Maximum requests allowed per minute
        """
        # Calculate time since last request
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # If it's been more than a minute, reset counter
        if elapsed > 60:
            self.requests_count = 0
            return
        
        # If we're approaching the limit, wait
        if self.requests_count >= max_requests_per_minute:
            wait_time = 60 - elapsed + 1  # Add 1 second buffer
            print(f"Rate limit approaching, waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            self.requests_count = 0
    
    def _get_temperature_for_type(self, email_type):
        """
        Get an appropriate temperature setting based on email type.
        
        Different email types benefit from different levels of creativity:
        - Technical responses should be more deterministic (lower temperature)
        - General inquiries can be more varied (higher temperature)
        
        Args:
            email_type (str): The type of email
            
        Returns:
            float: The temperature value to use (0.0-1.0)
        """
        # Use different temperatures based on email type
        if email_type in ['product_support', 'billing_question', 'urgent_request']:
            # More precise, less creative for technical/important matters
            return max(0.1, self.config["temperature"] - 0.3)
        elif email_type in ['complaint']:
            # Balanced approach for complaints
            return max(0.3, self.config["temperature"] - 0.1)
        elif email_type in ['feature_request', 'general_feedback']:
            # More creative for positive or idea-based emails
            return min(0.9, self.config["temperature"] + 0.1)
        else:
            # Default to configured temperature
            return self.config["temperature"]
    
    def _clean_response(self, response_text):
        """
        Clean the generated response to remove any unintended headers.
        
        This ensures no "Subject:", "From:", "To:" or similar headers
        appear in the email body.
        """
        if not response_text:
            return response_text
            
        # Remove any lines that look like email headers
        lines = response_text.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for line in lines:
            # Skip lines that look like headers
            if (line.startswith('Subject:') or 
                line.startswith('From:') or 
                line.startswith('To:') or 
                line.startswith('Date:') or
                line.startswith('Re:')):
                skip_next_empty = True
                continue
            
            # Skip empty line after a header
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _create_prompt(self, email_content, email_type=None):
        """
        Create a prompt for the Gemini API based on email content and type.
        
        This method constructs an appropriate prompt with instructions
        tailored to the specific email category.
        
        Args:
            email_content (dict): Email content with from, subject, and body fields
            email_type (str, optional): Type of email for context
            
        Returns:
            str: Formatted prompt for Gemini API
        """
        # Extract sender name if available
        sender_name = email_content.get('sender_name', 'the customer')
        
        # Base instructions for all email types
        instructions = f"""
        You are a helpful customer support assistant. Generate a professional and empathetic response to the following email.
        Address the sender by name if available. Be concise but thorough in your response.
        Sign the email as 'Customer Support Team'.
        
        IMPORTANT: Generate ONLY the email body content. Do NOT include:
        - Subject line or "Subject:" prefix
        - "Re:" prefix
        - Email headers (From:, To:, Date:)
        - Any metadata
        Just provide the body text starting with the greeting (e.g., "Dear [Name]," or "Hello,").
        """
        
        # Add specific instructions based on email type
        if email_type == "complaint":
            instructions = f"""
            You are a professional customer support assistant handling a complaint. 
            Generate a professional, apologetic, and solution-oriented response to the following complaint email.
            
            Guidelines:
            1. Start by acknowledging the issue and apologizing sincerely
            2. Show empathy for {sender_name}'s frustration
            3. Explain what might have happened (if clear from the email)
            4. Provide a specific solution or next steps
            5. Offer some form of goodwill or compensation if appropriate
            6. Thank them for bringing this to your attention
            7. Sign off as 'Customer Support Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "product_support":
            instructions = f"""
            You are a technical support specialist. Generate a professional, clear, and step-by-step response to 
            the following support email.
            
            Guidelines:
            1. Acknowledge {sender_name}'s issue
            2. Provide clear, step-by-step instructions to solve the problem
            3. Use simple, non-technical language when possible
            4. Explain why your solution works (if relevant)
            5. Offer alternative solutions if available
            6. Invite them to reach out again if the issue persists
            7. Sign off as 'Technical Support Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "feature_request":
            instructions = f"""
            You are a product manager. Generate a thoughtful response to the following feature request email.
            
            Guidelines:
            1. Thank {sender_name} for their suggestion
            2. Show appreciation for their engagement with the product
            3. Give your impression of the idea (positively framed)
            4. Explain if similar features are planned or already available
            5. If appropriate, ask for more details about their use case
            6. Set realistic expectations about implementation possibilities
            7. Sign off as 'Product Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "billing_question":
            instructions = f"""
            You are a billing specialist. Generate a professional, clear, and helpful response to 
            the following billing question.
            
            Guidelines:
            1. Address {sender_name}'s billing concern directly
            2. Provide clear information about the billing process
            3. If relevant, explain why charges appear as they do
            4. Offer specific next steps if action is needed
            5. Reassure them about data security
            6. Provide contact information for further billing questions
            7. Sign off as 'Billing Support Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "general_feedback":
            instructions = f"""
            You are a customer experience manager. Generate a warm and appreciative response to 
            the following feedback email.
            
            Guidelines:
            1. Thank {sender_name} enthusiastically for their feedback
            2. Acknowledge specific positive points they mentioned
            3. Explain how this feedback helps your team
            4. Mention any relevant upcoming improvements
            5. Invite them to continue providing feedback
            6. Sign off warmly as 'Customer Experience Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "urgent_request":
            instructions = f"""
            You are an urgent response specialist. Generate a prompt, clear, and action-oriented response to 
            the following time-sensitive email.
            
            Guidelines:
            1. Acknowledge the urgency of {sender_name}'s request
            2. Provide immediate next steps or solutions
            3. Be direct and concise
            4. If you can't resolve immediately, explain exactly when they can expect resolution
            5. Provide alternative contact methods for faster response
            6. Sign off as 'Urgent Response Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "customer_inquiry" or email_type is None:
            instructions = f"""
            You are a customer support specialist. Generate a professional, informative response to 
            the following inquiry email.
            
            Guidelines:
            1. Greet {sender_name} warmly
            2. Answer their questions directly and completely
            3. Provide relevant additional information they might find helpful
            4. Include links or references to resources if relevant
            5. Invite further questions
            6. Sign off as 'Customer Support Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        elif email_type == "spam":
            instructions = f"""
            You are a security specialist. Generate a brief, professional response to what appears to be a 
            spam or phishing email. Do not engage with specific claims in the email.
            
            Guidelines:
            1. Be extremely brief and generic
            2. Do not reference or acknowledge specific claims from the email
            3. Provide general security advice
            4. Do not include links or contact information
            5. Sign off as 'Security Team'
            
            Remember: Generate ONLY the email body. NO subject lines or headers.
            """
        
        # Format the email content for the prompt
        email_text = f"From: {email_content.get('from', 'customer@example.com')}\n"
        email_text += f"To: {email_content.get('to', 'support@company.com')}\n"
        email_text += f"Subject: {email_content.get('subject', 'No Subject')}\n"
        email_text += f"Body: {email_content.get('body', '')}"
        
        # Add sentiment information if available
        if 'sentiment' in email_content:
            email_text += f"\n\nEmail sentiment: {email_content['sentiment']}"
        
        # Add priority information if available
        if 'priority' in email_content:
            email_text += f"\nPriority: {email_content['priority']}"
        
        # Combine instructions and email content
        prompt = f"{instructions}\n\n{email_text}"
        
        return prompt
    
    def _get_fallback_response(self, email_content, email_type=None):
        """
        Get a fallback response when API generation fails.
        
        This provides a basic response to send when the API fails to generate one.
        
        Args:
            email_content (dict): Email content
            email_type (str, optional): Type of email
        
        Returns:
            str: A generic fallback response
        """
        # Extract sender name if available, otherwise use a generic greeting
        sender_name = email_content.get('sender_name', '')
        greeting = f"Dear {sender_name}," if sender_name else "Hello,"
        
        # Create different fallbacks based on email type
        if email_type == "urgent_request":
            return f"""
            {greeting}

            Thank you for your urgent message. We've received your request and are working on it with highest priority.

            Due to technical limitations, we're unable to provide a detailed response at this moment. A member of our team will contact you directly within the next hour.

            For immediate assistance, please call our urgent support line at (555) 123-4567.

            Best regards,
            Urgent Response Team
            """
        elif email_type == "complaint":
            return f"""
            {greeting}

            Thank you for bringing this matter to our attention. We sincerely apologize for any inconvenience you've experienced.

            We take all feedback seriously and are currently reviewing your concerns. A customer relations specialist will contact you within the next 24 hours to address this matter personally.

            We appreciate your patience.

            Sincerely,
            Customer Support Team
            """
        else:
            # Default generic response for all other types
            return f"""
            {greeting}

            Thank you for your message. We've received your email and appreciate you reaching out to us.

            A member of our team will get back to you within 1-2 business days.

            We appreciate your understanding.

            Best regards,
            Customer Support Team
            """