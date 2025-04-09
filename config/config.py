"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MQTT_BROKER = os.getenv('MQTT_BROKER')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    EMAIL_SMTP = os.getenv('EMAIL_SMTP')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/solar_assistant.db')
    
    # Report scheduling settings
    REPORT_DAILY = os.getenv('REPORT_DAILY', "0")
    REPORT_DAILY_TIME = os.getenv('REPORT_DAILY_TIME', "11:40")
    REPORT_WEEKLY = os.getenv('REPORT_WEEKLY', "0")
    REPORT_WEEKLY_TIME = os.getenv('REPORT_WEEKLY_TIME', "12:00")
    REPORT_MONTHLY = os.getenv('REPORT_MONTHLY', "0")
    REPORT_MONTHLY_TIME = os.getenv('REPORT_MONTHLY_TIME', "12:30")
    
    # CSV Attachment Option: set to "1" to include a CSV report, "0" otherwise.
    CSV_REPORT = os.getenv('CSV_REPORT', "0")
    
    # Timezone setting: used for container time display
    TZ = os.getenv('TZ', 'UTC')
