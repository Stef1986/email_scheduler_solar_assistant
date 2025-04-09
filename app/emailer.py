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
    try:
        # Create a multipart message.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = Config.EMAIL_USERNAME
        msg['To'] = Config.EMAIL_TO

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

        with smtplib.SMTP(Config.EMAIL_SMTP, Config.EMAIL_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_USERNAME, Config.EMAIL_TO, msg.as_string())

    except Exception as e:
        print(f"❌ Error sending email: {e}")
