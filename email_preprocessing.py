"""
Email Data Preprocessing and Feature Engineering Utilities
This module provides utilities for preprocessing email data and extracting features
for spam detection and classification.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

class EmailPreprocessor:
    """
    A comprehensive email preprocessing and feature extraction class
    """
    
    def __init__(self):
        """Initialize the email preprocessor"""
        self.suspicious_keywords = [
            'click here', 'verify account', 'confirm identity', 'urgent action',
            'limited time', 'act now', 'congratulations', 'winner', 'claim prize',
            'free money', 'work from home', 'make money fast', 'nigerian prince',
            'refund', 'tax return', 'update payment', 'suspended account'
        ]
        
        self.phishing_indicators = [
            'paypal', 'amazon', 'apple', 'microsoft', 'google', 'bank',
            'verify', 'confirm', 'update', 'validate', 'authenticate'
        ]
    
    def extract_subject_features(self, subject):
        """
        Extract features from email subject line
        """
        features = {}
        
        if pd.isna(subject):
            subject = ""
        
        subject = str(subject).lower()
        
        # Subject length
        features['subject_length'] = len(subject)
        
        # Uppercase ratio
        uppercase_count = sum(1 for c in subject if c.isupper())
        features['subject_uppercase_ratio'] = uppercase_count / max(len(subject), 1)
        
        # Digit ratio
        digit_count = sum(1 for c in subject if c.isdigit())
        features['subject_digit_ratio'] = digit_count / max(len(subject), 1)
        
        # Special character ratio
        special_count = sum(1 for c in subject if not c.isalnum() and c != ' ')
        features['subject_special_char_ratio'] = special_count / max(len(subject), 1)
        
        # Presence of suspicious keywords
        features['subject_has_suspicious_keywords'] = int(any(
            keyword in subject for keyword in self.suspicious_keywords
        ))
        
        # Presence of urgency words
        urgency_words = ['urgent', 'immediate', 'asap', 'now', 'today', 'quickly']
        features['subject_has_urgency'] = int(any(
            word in subject for word in urgency_words
        ))
        
        return features
    
    def extract_body_features(self, body):
        """
        Extract features from email body
        """
        features = {}
        
        if pd.isna(body):
            body = ""
        
        body = str(body).lower()
        
        # Body length
        features['body_length'] = len(body)
        
        # Word count
        words = body.split()
        features['word_count'] = len(words)
        
        # Average word length
        features['avg_word_length'] = np.mean([len(w) for w in words]) if words else 0
        
        # URL count
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        features['url_count'] = len(re.findall(url_pattern, body))
        
        # Email count
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        features['email_count'] = len(re.findall(email_pattern, body))
        
        # Suspicious word frequency
        features['suspicious_word_frequency'] = sum(
            body.count(keyword) for keyword in self.suspicious_keywords
        ) / max(len(words), 1)
        
        # Phishing indicator frequency
        features['phishing_indicator_frequency'] = sum(
            body.count(indicator) for indicator in self.phishing_indicators
        ) / max(len(words), 1)
        
        # Presence of HTML tags
        features['has_html_tags'] = int(bool(re.search(r'<[^>]+>', body)))
        
        # Presence of scripts
        features['has_scripts'] = int(bool(re.search(r'<script|javascript:', body)))
        
        return features
    
    def extract_sender_features(self, sender_email, sender_domain_age=None):
        """
        Extract features from sender information
        """
        features = {}
        
        if pd.isna(sender_email):
            sender_email = ""
        
        sender_email = str(sender_email).lower()
        
        # Extract domain
        if '@' in sender_email:
            domain = sender_email.split('@')[1]
        else:
            domain = ""
        
        features['sender_domain'] = domain
        
        # Domain length
        features['domain_length'] = len(domain)
        
        # Presence of numbers in domain
        features['domain_has_numbers'] = int(any(c.isdigit() for c in domain))
        
        # Presence of hyphens in domain
        features['domain_has_hyphens'] = int('-' in domain)
        
        # Domain age (simulated)
        if sender_domain_age is not None:
            features['domain_age_days'] = sender_domain_age
        else:
            features['domain_age_days'] = np.random.uniform(1, 5000)
        
        # Suspicious domain indicators
        suspicious_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'temp-mail', 'guerrillamail']
        features['has_suspicious_domain'] = int(any(
            sus_domain in domain for sus_domain in suspicious_domains
        ))
        
        return features
    
    def extract_attachment_features(self, attachments):
        """
        Extract features from email attachments
        """
        features = {}
        
        if attachments is None or (isinstance(attachments, list) and len(attachments) == 0):
            attachment_list = []
        elif isinstance(attachments, list):
            attachment_list = attachments
        else:
            attachment_list = [attachments]
        
        # Attachment count
        features['attachment_count'] = len(attachment_list)
        
        # Presence of executable files
        executable_extensions = ['.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js']
        features['has_executable'] = int(any(
            any(ext in str(att).lower() for ext in executable_extensions)
            for att in attachment_list
        ))
        
        # Presence of archive files
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
        features['has_archive'] = int(any(
            any(ext in str(att).lower() for ext in archive_extensions)
            for att in attachment_list
        ))
        
        # Presence of document files
        doc_extensions = ['.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx']
        features['has_document'] = int(any(
            any(ext in str(att).lower() for ext in doc_extensions)
            for att in attachment_list
        ))
        
        return features
    
    def extract_header_features(self, headers_dict):
        """
        Extract features from email headers
        """
        features = {}
        
        if headers_dict is None:
            headers_dict = {}
        
        # SPF validation
        features['spf_valid'] = int(headers_dict.get('spf_valid', False))
        
        # DKIM validation
        features['dkim_valid'] = int(headers_dict.get('dkim_valid', False))
        
        # DMARC validation
        features['dmarc_valid'] = int(headers_dict.get('dmarc_valid', False))
        
        # Presence of Reply-To header
        features['has_reply_to'] = int('reply_to' in headers_dict)
        
        # Presence of X-Originating-IP
        features['has_originating_ip'] = int('x_originating_ip' in headers_dict)
        
        # Presence of X-Mailer
        features['has_x_mailer'] = int('x_mailer' in headers_dict)
        
        return features
    
    def preprocess_email(self, email_dict):
        """
        Comprehensive email preprocessing and feature extraction
        """
        features = {}
        
        # Extract subject features
        subject_features = self.extract_subject_features(email_dict.get('subject', ''))
        features.update({f'subject_{k}': v for k, v in subject_features.items()})
        
        # Extract body features
        body_features = self.extract_body_features(email_dict.get('body', ''))
        features.update({f'body_{k}': v for k, v in body_features.items()})
        
        # Extract sender features
        sender_features = self.extract_sender_features(
            email_dict.get('sender', ''),
            email_dict.get('sender_domain_age', None)
        )
        features.update({f'sender_{k}': v for k, v in sender_features.items()})
        
        # Extract attachment features
        attachment_features = self.extract_attachment_features(
            email_dict.get('attachments', [])
        )
        features.update({f'attachment_{k}': v for k, v in attachment_features.items()})
        
        # Extract header features
        header_features = self.extract_header_features(
            email_dict.get('headers', {})
        )
        features.update({f'header_{k}': v for k, v in header_features.items()})
        
        return features


def generate_sample_emails(n_emails=100, spam_ratio=0.3):
    """
    Generate sample email dataset for demonstration
    """
    preprocessor = EmailPreprocessor()
    emails = []
    
    legitimate_subjects = [
        'Meeting Tomorrow at 2 PM',
        'Project Update - Q3 Results',
        'Team Lunch This Friday',
        'Conference Registration Confirmation',
        'Invoice #12345',
        'Password Reset Request',
        'Delivery Notification',
        'Appointment Reminder',
        'Course Enrollment Confirmation',
        'Weekly Newsletter'
    ]
    
    spam_subjects = [
        'URGENT: Verify Your Account NOW!!!',
        'Congratulations! You Won $1,000,000',
        'Click Here to Claim Your Prize',
        'Nigerian Prince Wants to Send You Money',
        'Limited Time Offer - 90% OFF',
        'Confirm Your Identity Immediately',
        'Your Account Has Been Suspended',
        'Act Now - Only 24 Hours Left',
        'Free Money - No Strings Attached',
        'Update Your Payment Information'
    ]
    
    legitimate_bodies = [
        'Hi, I wanted to touch base about our upcoming meeting. Please confirm your attendance.',
        'Here are the Q3 results. Overall performance exceeded expectations.',
        'The team lunch is scheduled for Friday at noon. Please RSVP.',
        'Thank you for registering for the conference. Your confirmation code is ABC123.',
        'Please find attached the invoice for your recent purchase.',
        'You requested a password reset. Click the link below to proceed.',
        'Your package has been delivered. Thank you for your order.',
        'This is a reminder of your appointment on Friday at 3 PM.',
        'Welcome to the course. Your enrollment is confirmed.',
        'This week\'s newsletter contains important updates and announcements.'
    ]
    
    spam_bodies = [
        'Your account has been compromised. Click here immediately to verify your identity.',
        'You have won a prize! Click here to claim your reward now.',
        'Limited time offer! Get 90% off on all products. Act now!',
        'A Nigerian prince has selected you to receive a large sum of money.',
        'This offer expires in 24 hours. Don\'t miss out on this opportunity.',
        'We need to confirm your identity for security purposes. Click here.',
        'Your account will be suspended unless you update your payment information.',
        'Hurry! Only a few spots left. Register now to secure your place.',
        'Earn money from home with our proven system. Start today!',
        'Update your payment method to avoid service interruption.'
    ]
    
    for i in range(n_emails):
        is_spam = np.random.random() < spam_ratio
        
        if is_spam:
            subject = np.random.choice(spam_subjects)
            body = np.random.choice(spam_bodies)
            sender = f'spammer{i}@suspicious-domain-{i}.com'
            domain_age = np.random.uniform(1, 100)  # New domains
        else:
            subject = np.random.choice(legitimate_subjects)
            body = np.random.choice(legitimate_bodies)
            sender = f'colleague{i}@company.com'
            domain_age = np.random.uniform(1000, 5000)  # Old domains
        
        email_dict = {
            'email_id': i + 1,
            'subject': subject,
            'body': body,
            'sender': sender,
            'sender_domain_age': domain_age,
            'attachments': [] if np.random.random() > 0.3 else ['document.pdf'],
            'headers': {
                'spf_valid': not is_spam,
                'dkim_valid': not is_spam,
                'dmarc_valid': not is_spam,
                'reply_to': True,
                'x_originating_ip': True
            },
            'is_spam': int(is_spam)
        }
        
        # Extract features
        features = preprocessor.preprocess_email(email_dict)
        email_dict.update(features)
        
        emails.append(email_dict)
    
    return pd.DataFrame(emails)


def save_sample_dataset(filename='sample_emails.csv', n_emails=100):
    """
    Generate and save sample email dataset
    """
    df = generate_sample_emails(n_emails=n_emails, spam_ratio=0.3)
    df.to_csv(filename, index=False)
    print(f"✓ Sample email dataset saved to {filename}")
    print(f"  Total emails: {len(df)}")
    print(f"  Legitimate: {(df['is_spam'] == 0).sum()}")
    print(f"  Spam: {(df['is_spam'] == 1).sum()}")
    return df


if __name__ == '__main__':
    # Generate and save sample dataset
    print("Generating sample email dataset...")
    df = save_sample_dataset('/home/ubuntu/sample_emails.csv', n_emails=500)
    
    print("\nDataset Preview:")
    print(df.head())
    
    print("\nDataset Statistics:")
    print(df.describe())
