"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import mimetypes
from config.config import Config

def send_email(subject, body, attachments=None):
    email_sent = False  # Flag to track if email was sent
    
    try:
        # Create a multipart message.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = Config.EMAIL_USERNAME
        
        # Handle multiple recipients including whitespace handling
        recipients = [email.strip() for email in Config.EMAIL_TO.split(',')]
        msg['To'] = ', '.join(recipients)
        
        # Attach the HTML body.
        msg.attach(MIMEText(body, 'html'))
        
        # Process attachments if provided.
        if attachments:
            for filename, content, mime_type in attachments:
                # If no MIME type is provided, guess it.
                if not mime_type:
                    mime_type, _ = mimetypes.guess_type(filename)
                main_type, sub_type = mime_type.split('/', 1)
                part = MIMEBase(main_type, sub_type)
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)
                
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(Config.EMAIL_SMTP, Config.EMAIL_PORT)
        server.starttls()
        server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        server.sendmail(Config.EMAIL_USERNAME, recipients, msg.as_string())
        server.quit()
        
        # If we get here without exceptions, the email was sent successfully
        email_sent = True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
    
    # Only print success message if email was actually sent
    if email_sent:
        print(f"✅ Email sent successfully to {len(recipients)} recipients!")
