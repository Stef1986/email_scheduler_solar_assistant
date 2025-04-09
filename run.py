"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

from app.mqtt_client import start_mqtt
from app.scheduler import start_scheduler
from app.db import init_db  # 🛠️ ADD this import!
import time

def main():
    # 🛠️ Initialize the database first
    init_db()

    # Start the MQTT listener
    start_mqtt()

    # Start the Scheduler
    start_scheduler()

    # Keep the app running forever
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()