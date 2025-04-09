"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.report_generator import generate_and_send_report
from config.config import Config

scheduler = BackgroundScheduler()

def schedule_reports():
    # Schedule Daily Report
    if Config.REPORT_DAILY == "1":
        daily_time = Config.REPORT_DAILY_TIME  # expected in HH:MM format
        hour, minute = map(int, daily_time.split(":"))
        scheduler.add_job(
            lambda: generate_and_send_report(period="daily"),
            trigger="cron",
            hour=hour,
            minute=minute,
            id="daily_report",
            replace_existing=True
        )
        print(f"⏰ Daily report scheduled for {daily_time}")

    # Schedule Weekly Report (runs on Monday)
    if Config.REPORT_WEEKLY == "1":
        weekly_time = Config.REPORT_WEEKLY_TIME  # expected in HH:MM format
        hour, minute = map(int, weekly_time.split(":"))
        scheduler.add_job(
            lambda: generate_and_send_report(period="weekly"),
            trigger="cron",
            day_of_week="mon",  
            hour=hour,
            minute=minute,
            id="weekly_report",
            replace_existing=True
        )
        print(f"⏰ Weekly report scheduled for {weekly_time} on Monday")

    # Schedule Monthly Report (runs on the 1st day of each month)
    if Config.REPORT_MONTHLY == "1":
        monthly_time = Config.REPORT_MONTHLY_TIME  # expected in HH:MM format
        hour, minute = map(int, monthly_time.split(":"))
        scheduler.add_job(
            lambda: generate_and_send_report(period="monthly"),
            trigger="cron",
            day=1,
            hour=hour,
            minute=minute,
            id="monthly_report",
            replace_existing=True
        )
        print(f"⏰ Monthly report scheduled for {monthly_time} on the 1st day of the month")

    scheduler.start()
    print("⏰ Scheduler started with configured report jobs.")

def start_scheduler():
    schedule_reports()
