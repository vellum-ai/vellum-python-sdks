#!/usr/bin/env python3
"""
Email Sender Script
Sends emails using SMTP with app password authentication.
This script can work independently or with email addresses from email_getter.py
"""

import smtplib
import ssl
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded email credentials
SENDER_EMAIL = "jashanpratap123@gmail.com"
APP_PASSWORD = "acwk irmv ybje gheo"

def main(
) -> Dict:
    recipients: List[Dict] = []
    subject = ""
    body = ""
    html_body = ""
    attachments = ""
    """
    Send emails to recipients using hardcoded credentials.
    
    Args:
        recipients: List of recipient dictionaries with 'email' and optional 'name'
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        attachments: List of file paths to attach (optional)
        
    Returns:
        Dict with sending results
    """
    
    def connect_to_smtp():
        """Connect to SMTP server."""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls(context=context)
            server.login(SENDER_EMAIL, APP_PASSWORD)
            logger.info("Successfully connected to SMTP server")
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            return None
    
    def send_single_email(server, recipient_email, recipient_name=None):
        """Send a single email."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add plain text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                    else:
                        logger.warning(f"Attachment file not found: {file_path}")
            
            # Send email
            server.send_message(msg)
            
            recipient_display = recipient_name or recipient_email
            logger.info(f"Email sent successfully to {recipient_display}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False
    
    # Initialize results
    results = {
        "success": 0,
        "failed": 0,
        "errors": [],
        "sent_emails": []
    }
    
    # Connect to SMTP server
    server = connect_to_smtp()
    if not server:
        results["failed"] = len(recipients)
        results["errors"].append("Failed to connect to SMTP server")
        return results
    
    try:
        # Send emails to each recipient
        for recipient in recipients:
            email = recipient.get('email')
            name = recipient.get('name', recipient.get('full_name', ''))
            
            if not email:
                results["failed"] += 1
                results["errors"].append(f"Missing email for recipient: {recipient}")
                continue
            
            # Send email
            success = send_single_email(server, email, name)
            
            if success:
                results["success"] += 1
                results["sent_emails"].append({
                    'email': email,
                    'name': name,
                    'subject': subject
                })
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to send to {email}")
    
    finally:
        # Disconnect from server
        server.quit()
        logger.info("Disconnected from SMTP server")
    
    logger.info(f"Email sending complete: {results['success']} successful, {results['failed']} failed")
    return results

def load_emails_from_json(json_file: str) -> List[Dict]:
    """Load email addresses from a JSON file (from email_getter output)."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract email and name information
        recipients = []
        for item in data:
            email = item.get('email')
            name = item.get('full_name') or item.get('name', '')
            
            if email:
                recipients.append({
                    'email': email,
                    'name': name,
                    'company': item.get('company', ''),
                    'job_title': item.get('job_title', '')
                })
        
        logger.info(f"Loaded {len(recipients)} recipients from {json_file}")
        return recipients
        
    except Exception as e:
        logger.error(f"Failed to load emails from {json_file}: {e}")
        return []

def email_sender_from_json(
    json_file: str,
    subject: str,
    body: str,
    html_body: str = None,
    attachments: List[str] = None
) -> Dict:
    """
    Send emails to recipients loaded from JSON file.
    
    Args:
        json_file: JSON file with extracted email data
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        attachments: List of file paths to attach (optional)
        
    Returns:
        Dict with sending results
    """
    # Load recipients from JSON file
    recipients = load_emails_from_json(json_file)
    
    if not recipients:
        return {"success": 0, "failed": 0, "errors": ["No recipients found in JSON file"]}
    
    # Send emails using the main function
    return email_sender(recipients, subject, body, html_body, attachments)