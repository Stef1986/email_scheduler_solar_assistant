"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

import sqlite3
from datetime import datetime
from config.config import Config
import os

DB_FILE = Config.DATABASE_PATH

def init_db():
    if not os.path.exists(os.path.dirname(DB_FILE)):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            topic TEXT NOT NULL,
            value REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("📦 Database initialized!")

def save_reading(topic, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute('''
        INSERT INTO readings (timestamp, topic, value)
        VALUES (?, ?, ?)
    ''', (timestamp, topic, value))

    conn.commit()
    conn.close()
