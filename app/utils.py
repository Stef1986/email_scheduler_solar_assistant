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

def get_selected_metrics():
    """Return a list of active metrics (value == 1) from the .env file."""
    selected_metrics = []
    for key, value in os.environ.items():
        if key.startswith("METRIC_") and value.strip() == "1":
            metric_name = key.replace("METRIC_", "").lower()
            selected_metrics.append(metric_name)
    return selected_metrics
