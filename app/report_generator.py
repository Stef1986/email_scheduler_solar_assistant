"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

from datetime import datetime, timedelta
import sqlite3
import csv
import io
from app.emailer import send_email
from config.config import Config
from app.utils import get_selected_metrics

DB_FILE = Config.DATABASE_PATH

def get_daily_data(cursor, date):
    """
    Get energy data for a specific day.
    Returns the first and last readings of the day for each energy metric.
    """
    # Define the metrics you want to track
    energy_metrics = [
        'battery_energy_in',
        'battery_energy_out',
        'grid_energy_in',
        'grid_energy_out',
        'load_energy',
        'pv_energy'
    ]
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    results = {}
    
    for metric in energy_metrics:
        # Get the first reading of the day
        cursor.execute('''
            SELECT value, timestamp FROM readings
            WHERE topic = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT 1
        ''', (f"solar_assistant/total/{metric}/state", start.isoformat(), end.isoformat()))
        first_row = cursor.fetchone()
        
        # Get the last reading of the day
        cursor.execute('''
            SELECT value, timestamp FROM readings
            WHERE topic = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (f"solar_assistant/total/{metric}/state", start.isoformat(), end.isoformat()))
        last_row = cursor.fetchone()
        
        if first_row and last_row:
            first_value, first_timestamp = first_row
            last_value, last_timestamp = last_row
            
            # Calculate the energy used during this day
            daily_value = last_value - first_value
            
            # Store the result
            results[metric] = {
                'first': first_value,
                'last': last_value,
                'daily': daily_value,
                'first_timestamp': first_timestamp,
                'last_timestamp': last_timestamp
            }
        else:
            # No data for this metric on this day
            results[metric] = {
                'first': 0.0,
                'last': 0.0,
                'daily': 0.0,
                'first_timestamp': None,
                'last_timestamp': None
            }
    
    return results

def generate_daily_report(cursor, date):
    """
    Generate a daily report with total energy values for the specified date.
    """
    print(f"Generating daily report for {date.strftime('%Y-%m-%d')}...")
    
    # Define the metrics you want to track
    energy_metrics = [
        'battery_energy_in',
        'battery_energy_out',
        'grid_energy_in',
        'grid_energy_out',
        'load_energy',
        'pv_energy'
    ]
    
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Fetch all relevant data for the day in a single batch per metric
    day_data = {}
    for metric in energy_metrics:
        print(f"Fetching data for {metric}...")
        cursor.execute('''
            SELECT value, timestamp FROM readings
            WHERE topic = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (f"solar_assistant/total/{metric}/state", day_start.isoformat(), day_end.isoformat()))
        readings = cursor.fetchall()
        print(f"Found {len(readings)} readings for {metric}")
        
        if readings:
            first_value = readings[0][0]
            last_value = readings[-1][0]
            daily_value = last_value - first_value
            day_data[metric] = daily_value
        else:
            day_data[metric] = 0.0
    
    # Create a row for the  with just the daily totals
    row = {
        'Date': date.strftime('%Y-%m-%d'),
        'Load (kWh)': round(day_data.get('load_energy', 0.0), 2),
        'Solar PV (kWh)': round(day_data.get('pv_energy', 0.0), 2),
        'Battery Charged (kWh)': round(day_data.get('battery_energy_in', 0.0), 2),
        'Battery Discharged (kWh)': round(day_data.get('battery_energy_out', 0.0), 2),
        'Grid Import (kWh)': round(day_data.get('grid_energy_in', 0.0), 2),
        'Grid Export (kWh)': round(day_data.get('grid_energy_out', 0.0), 2)
    }
    
    print("Daily report generation complete!")
    return row

def generate_weekly_report(cursor, end_date):
    """
    Generate a weekly report with daily rows and a total row at the bottom.
    """
    print("Starting weekly report generation...")
    rows = []
    totals = {
        'Load (kWh)': 0.0,
        'Solar PV (kWh)': 0.0,
        'Battery Charged (kWh)': 0.0,
        'Battery Discharged (kWh)': 0.0,
        'Grid Import (kWh)': 0.0,
        'Grid Export (kWh)': 0.0
    }
    
    # Calculate the start date (7 days ago)
    start_date = end_date - timedelta(days=6)
    print(f"Generating weekly report from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Define the metrics we want to track
    energy_metrics = [
        'battery_energy_in',
        'battery_energy_out',
        'grid_energy_in',
        'grid_energy_out',
        'load_energy',
        'pv_energy'
    ]
    
    # Pre-fetch all energy metrics for the week to reduce database queries
    week_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Fetch all relevant data for the entire week
    all_readings = {}
    for metric in energy_metrics:
        print(f"Fetching data for {metric}...")
        cursor.execute('''
            SELECT value, timestamp FROM readings
            WHERE topic = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (f"solar_assistant/total/{metric}/state", week_start.isoformat(), week_end.isoformat()))
        all_readings[metric] = cursor.fetchall()
        print(f"Found {len(all_readings[metric])} readings for {metric}")
    
    # Process each day of the week
    current_date = start_date
    days_processed = 0
    
    while current_date <= end_date:
        print(f"Processing day {current_date.strftime('%Y-%m-%d')} ({days_processed+1}/7)...")
        
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get data for this day from pre-fetched readings
        day_data = {}
        for metric in energy_metrics:
            # Filter readings for this day
            day_readings = [r for r in all_readings[metric] 
                           if day_start.isoformat() <= r[1] <= day_end.isoformat()]
            
            if day_readings:
                first_value = day_readings[0][0]
                last_value = day_readings[-1][0]
                daily_value = last_value - first_value
                day_data[metric] = daily_value
            else:
                day_data[metric] = 0.0
        
        # Create a row for this day
        daily_row = {
            'Date': current_date.strftime('%Y-%m-%d'),
            'Load (kWh)': round(day_data.get('load_energy', 0.0), 2),
            'Solar PV (kWh)': round(day_data.get('pv_energy', 0.0), 2),
            'Battery Charged (kWh)': round(day_data.get('battery_energy_in', 0.0), 2),
            'Battery Discharged (kWh)': round(day_data.get('battery_energy_out', 0.0), 2),
            'Grid Import (kWh)': round(day_data.get('grid_energy_in', 0.0), 2),
            'Grid Export (kWh)': round(day_data.get('grid_energy_out', 0.0), 2)
        }
        
        rows.append(daily_row)
        
        # Add to totals
        for key in totals.keys():
            totals[key] += daily_row[key]
        
        current_date += timedelta(days=1)
        days_processed += 1
    
    print("Finished processing all days, adding total row...")
    
    # Add a total row
    total_row = {'Date': 'Total'}
    for key, value in totals.items():
        total_row[key] = round(value, 2)
    
    rows.append(total_row)
    print("Weekly report generation complete!")
    return rows

def generate_monthly_report(cursor, end_date):
    """
    Generate a monthly report with daily rows and a total row at the bottom.
    """
    print("Starting monthly report generation...")
    rows = []
    totals = {
        'Load (kWh)': 0.0,
        'Solar PV (kWh)': 0.0,
        'Battery Charged (kWh)': 0.0,
        'Battery Discharged (kWh)': 0.0,
        'Grid Import (kWh)': 0.0,
        'Grid Export (kWh)': 0.0
    }
    
    # Calculate the start date (30 days ago)
    start_date = end_date - timedelta(days=30)
    print(f"Generating monthly report from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Generate daily reports for each day of the month
    current_date = start_date
    days_processed = 0
    
    # Pre-fetch all energy metrics for the month to reduce database queries
    month_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    month_end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Define the metrics you want to track
    energy_metrics = [
        'battery_energy_in',
        'battery_energy_out',
        'grid_energy_in',
        'grid_energy_out',
        'load_energy',
        'pv_energy'
    ]
    
    # Fetch all relevant data for the entire month
    all_readings = {}
    for metric in energy_metrics:
        print(f"Fetching data for {metric}...")
        cursor.execute('''
            SELECT value, timestamp FROM readings
            WHERE topic = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (f"solar_assistant/total/{metric}/state", month_start.isoformat(), month_end.isoformat()))
        all_readings[metric] = cursor.fetchall()
        print(f"Found {len(all_readings[metric])} readings for {metric}")
    
    while current_date <= end_date:
        print(f"Processing day {current_date.strftime('%Y-%m-%d')} ({days_processed+1}/31)...")
        
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get data for this day from pre-fetched readings
        day_data = {}
        for metric in energy_metrics:
            # Filter readings for this day
            day_readings = [r for r in all_readings[metric] 
                           if day_start.isoformat() <= r[1] <= day_end.isoformat()]
            
            if day_readings:
                first_value = day_readings[0][0]
                last_value = day_readings[-1][0]
                daily_value = last_value - first_value
                day_data[metric] = daily_value
            else:
                day_data[metric] = 0.0
        
        # Create a row for this day
        daily_row = {
            'Date': current_date.strftime('%Y-%m-%d'),
            'Load (kWh)': round(day_data.get('load_energy', 0.0), 2),
            'Solar PV (kWh)': round(day_data.get('pv_energy', 0.0), 2),
            'Battery Charged (kWh)': round(day_data.get('battery_energy_in', 0.0), 2),
            'Battery Discharged (kWh)': round(day_data.get('battery_energy_out', 0.0), 2),
            'Grid Import (kWh)': round(day_data.get('grid_energy_in', 0.0), 2),
            'Grid Export (kWh)': round(day_data.get('grid_energy_out', 0.0), 2)
        }
        
        rows.append(daily_row)
        
        # Add to totals
        for key in totals.keys():
            totals[key] += daily_row[key]
        
        current_date += timedelta(days=1)
        days_processed += 1
    
    print("Finished processing all days, adding total row...")
    
    # Add a total row
    total_row = {'Date': 'Total'}
    for key, value in totals.items():
        total_row[key] = round(value, 2)
    
    rows.append(total_row)
    print("Monthly report generation complete!")
    return rows

def create__content(rows):
    """
    Create  content from the rows data.
    """
    if not rows:
        return ""
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    
    _content = output.getvalue()
    output.close()
    
    return _content

def create_html_table(rows):
    """
    Create an HTML table from the rows data.
    """
    if not rows:
        return "<p>No data available for this period.</p>"
    
    html = """
    <table style="width: 100%; border-collapse: collapse;">
      <tr style="background-color: #f2f2f2;">
    """
    
    # Create headers
    for header in rows[0].keys():
        html += f'<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">{header}</th>'
    
    html += "</tr>"
    
    # Create data rows
    for i, row in enumerate(rows):
        # Style differently for the total row
        if row['Date'] == 'Total':
            html += '<tr style="background-color: #e0f0ff; font-weight: bold;">'
        elif i % 2 == 0:
            html += '<tr style="background-color: #f9f9f9;">'
        else:
            html += '<tr>'
        
        for value in row.values():
            html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{value}</td>'
        
        html += "</tr>"
    
    html += "</table>"
    
    return html

def generate_and_send_report(period="daily"):
    """
    Generates and sends an HTML report (with a  attachment) for the specified period.
    'period' can be "daily", "weekly", or "monthly".
    
    The HTML report shows a summary table using only the metrics the user has configured (via METRIC_* in the .env),
    and the  provides energy totals for the reporting period.
    """
    print(f"📋 Starting {period} report generation...")
    try:
        # For the HTML report: only the user-selected metrics will be summarized as before
        selected_metrics = get_selected_metrics()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.now()

        # Determine date range based on the report period (for both reports)
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            date_range_str = f"{now.strftime('%Y-%m-%d')}"
            report_title = f"Daily Solar Report - {date_range_str}"
            email_subject = f"Solar Report - {date_range_str} (Daily Report)"
            html_title = f"Solar Report for {date_range_str} (Daily Report)"
        elif period == "weekly":
            start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            date_range_str = f"{start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
            report_title = f"Weekly Solar Report - {date_range_str}"
            email_subject = f"Solar Report - {date_range_str} (Weekly Report)"
            html_title = f"Solar Report for Week of {date_range_str} (Weekly Report)"
        elif period == "monthly":
            start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            date_range_str = f"{start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
            report_title = f"Monthly Solar Report - {date_range_str}"
            email_subject = f"Solar Report - {date_range_str} (Monthly Report)"
            html_title = f"Solar Report for Month of {date_range_str} (Monthly Report)"
        else:
            # Default to daily
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            date_range_str = f"{now.strftime('%Y-%m-%d')}"
            report_title = f"Daily Solar Report - {date_range_str}"
            email_subject = f"Solar Report - {date_range_str} (Daily Report)"
            html_title = f"Solar Report for {date_range_str} (Daily Report)"
        
        print(f"📅 Looking for data from {start.strftime('%Y-%m-%d %H:%M:%S')} to {end.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all the readings for the original email format
        cursor.execute('''
            SELECT topic, value, timestamp FROM readings
            WHERE timestamp BETWEEN ? AND ?
        ''', (start.isoformat(), end.isoformat()))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"⚠️ No data for the {period} period, skipping report.")
            return
        
        print(f"✅ Found {len(rows)} rows of data.")
        
        # Generate energy report data for  attachment
        if period == "daily":
            report_rows = [generate_daily_report(cursor, now)]
        elif period == "weekly":
            report_rows = generate_weekly_report(cursor, now)
        elif period == "monthly":
            report_rows = generate_monthly_report(cursor, now)
        else:
            # Default to daily
            report_rows = [generate_daily_report(cursor, now)]
        
        conn.close()
        
        # Build summary statistics for the HTML email body (original format)
        stats_email = {}
        for topic, value, ts in rows:
            # For example, topic: "solar_assistant/total/battery_state_of_charge/state"
            short_topic = topic.split("/")[-2]  # 'battery_state_of_charge'
            if short_topic not in selected_metrics:
                continue
            stats_email.setdefault(short_topic, []).append(value)
        
        # Define friendly names (with units) for display (original format)
        metric_names = {
            "battery_power": "Battery Power (W)",
            "battery_state_of_charge": "Battery SOC (%)",
            "battery_temperature": "Battery Temperature (°C)",
            "bus_voltage": "Bus Voltage (V)",
            "grid_frequency": "Grid Frequency (Hz)",
            "grid_power": "Grid Power (W)",
            "grid_voltage": "Grid Voltage (V)",
            "load_percentage": "Load Percentage (%)",
            "load_power": "Load Power (W)",
            "pv_power": "PV Power (W)",
            "pv_voltage": "PV Voltage (V)",
            "pv_current": "PV Current (A)",
            "battery_voltage": "Battery Voltage (V)",
            "battery_current": "Battery Current (A)",
            "battery_charge_power_from_ac": "Battery Charge Power from AC (W)",
            # If you have cumulative energy counters, you could include them too:
            "battery_energy_in": "Battery Energy In (kWh)",
            "battery_energy_out": "Battery Energy Out (kWh)",
            "grid_energy_in": "Grid Energy In (kWh)",
            "grid_energy_out": "Grid Energy Out (kWh)",
            "load_energy": "Load Energy (kWh)",
            "pv_energy": "PV Energy (kWh)"
        }
        
        # Build the HTML email body with the original summary table format
        html = f"""
<html>
  <head>
    <style>
      table {{
        width: 80%;
        border-collapse: collapse;
      }}
      th, td {{
        border: 1px solid #dddddd;
        text-align: center;
        padding: 8px;
      }}
      th {{
        background-color: #f2f2f2;
      }}
    </style>
  </head>
  <body>
    <h2>🌞 {html_title} 🌞</h2>
    <table>
      <tr>
        <th>Metric</th>
        <th>Max</th>
        <th>Min</th>
        <th>Avg</th>
      </tr>
"""
        for short_topic, values in stats_email.items():
            if values:  # Only include metrics that have values
                max_val = max(values)
                min_val = min(values)
                avg_val = sum(values) / len(values)
                friendly = metric_names.get(short_topic, short_topic.replace("_", " ").title())
                html += f"""
      <tr>
        <td>{friendly}</td>
        <td>{round(max_val, 2)}</td>
        <td>{round(min_val, 2)}</td>
        <td>{round(avg_val, 2)}</td>
      </tr>
"""
        html += """
    </table>
    <br>
    <h4>Legend / Explanation:</h4>
    <ul style="font-size:12px;">
      <li><strong>Battery Power (W):</strong> Positive means charging; negative means discharging.</li>
      <li><strong>Battery SOC (%):</strong> Indicates how full the battery is.</li>
      <li><strong>Battery Temperature (°C):</strong> The operating temperature of the battery.</li>
      <li><strong>Bus Voltage (V):</strong> The DC voltage on the main system bus.</li>
      <li><strong>Grid Frequency (Hz):</strong> The frequency of the AC grid (typically around 50 Hz).</li>
      <li><strong>Grid Power (W):</strong> Positive means power drawn from the grid; negative means power fed back.</li>
      <li><strong>Grid Voltage (V):</strong> The voltage at the grid connection.</li>
      <li><strong>Load Percentage (%):</strong> The percentage of the system's capacity being used.</li>
      <li><strong>Load Power (W):</strong> The power consumed by your home.</li>
      <li><strong>PV Power (W):</strong> The power output from the solar panels.</li>
      <li><strong>PV Voltage (V):</strong> The voltage output from the solar panels.</li>
      <li><strong>PV Current (A):</strong> The current from the solar panels.</li>
      <li><strong>Battery Voltage (V):</strong> The voltage of the battery bank.</li>
      <li><strong>Battery Current (A):</strong> The current entering or leaving the battery.</li>
      <li><strong>Battery Charge Power from AC (W):</strong> Power drawn from AC to charge the battery.</li>
    </ul>
    <p style="font-size:12px;">The CSV attachment contains detailed energy totals for the {period.capitalize()} period.</p>
    <p style="font-size:12px;color:gray;">Generated automatically by Email scheduler for Solar Assistant 🌞</p>
  </body>
</html>
"""
        
        # Create CSV attachment with energy totals
        csv_content = create_csv_content(report_rows)
        filename = f"solar_report_{period}_{now.strftime('%Y-%m-%d')}.csv"
        attachments = [(filename, csv_content, "text/csv")]
        
        print("📤 Sending email...")
        send_email(subject=email_subject,
                   body=html,
                   attachments=attachments)
        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
