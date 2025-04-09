# Email Scheduler for Solar Assistant

**Author: Stefan Verster**

*Copyright © 2025 Stefan Verster. This code is available for personal and non-commercial use.*

If you find this software useful, please consider supporting the author by making a donation:

[![Donate with PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C)

Thank you for your support!

## Overview

This application generates and emails customizable reports about your solar energy system based on data collected from a Solar Assistant instance. It creates daily, weekly, and monthly reports that track your energy production, consumption, grid usage, and battery status.

## Features

- **Daily Reports**: Summarizes energy totals for the current day
- **Weekly Reports**: Shows daily energy totals for each day of the week with a weekly sum
- **Monthly Reports**: Shows daily energy totals for each day of the month with a monthly sum
- **Automated Email Delivery**: Reports are sent via email at configurable times
- **Customizable Metrics**: Choose which metrics to include in your email reports
- **CSV Attachments**: Detailed energy data in CSV format for further analysis

## Report Contents

### Email Reports
The email includes a summary table with **Min, Max, and Average values** for the metrics you've selected in your configuration. This summary metrics in the body of the email are the realtime stats at the time of running the report. The email also provides explanations of what each metric means and information about the reporting period.

### CSV Reports
The CSV attachment provides standardized energy totals in these columns:
```
Date,Load (kWh),Solar PV (kWh),Battery Charged (kWh),Battery Discharged (kWh),Grid Import (kWh),Grid Export (kWh)
```

These represent cumulative energy values for each component of your solar system, allowing you to track energy production, consumption, and grid interaction over time.

## Installation with Docker

### Prerequisites

- Docker and Docker Compose installed on your system
- A running Solar Assistant instance
- SMTP server details for sending emails

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Stef1986/email_scheduler_solar_assistant.git
   cd email_scheduler_solar_assistant
   ```

2. Copy the example environment file and customize it with your settings:
   ```bash
   cp .env.example .env
   nano .env
   ```

3. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

4. Check the container logs to ensure everything is running correctly:
   ```bash
   docker-compose logs -f
   ```

## Configuration

All configuration is done through the `.env` file. Here are the available settings:

### MQTT Settings
```
MQTT_BROKER=192.168.0.1
MQTT_PORT=1883
MQTT_USERNAME=solarassistant
MQTT_PASSWORD=password
```

### Email Settings
```
EMAIL_SMTP=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=from_email_address
EMAIL_PASSWORD=password
EMAIL_TO=to_email_address
```

### Database Location
```
DATABASE_PATH=data/solar_assistant.db
```

### Report Schedules (24h format)
```
# Set REPORT_DAILY to 1 to enable daily reports
REPORT_DAILY=1
REPORT_DAILY_TIME=13:43

# Set REPORT_WEEKLY to 1 to enable weekly reports (runs on Monday)
REPORT_WEEKLY=0
REPORT_WEEKLY_TIME=12:00

# Set REPORT_MONTHLY to 1 to enable monthly reports (runs on 1st day of month)
REPORT_MONTHLY=0
REPORT_MONTHLY_TIME=12:30
```

### Timezone Setting
```
# Set this to your local timezone using the IANA time zone identifier
TZ=Africa/Johannesburg
```

### Metrics to Include in Email Reports
```
# 1 = include in email report, 0 = omit from email report
# These settings only affect the metrics shown in the email body
# The CSV attachment will always include the standard energy metrics
METRIC_battery_power=1                 # Battery power in watts
METRIC_battery_state_of_charge=1       # Battery charge percentage
METRIC_battery_temperature=1           # Battery temperature in °C
METRIC_bus_voltage=1                   # DC bus voltage
METRIC_grid_frequency=1                # Grid frequency in Hz
METRIC_grid_power=1                    # Grid power in watts
METRIC_grid_voltage=1                  # Grid voltage
METRIC_load_percentage=1               # Load percentage of capacity
METRIC_load_power=1                    # Load power in watts
METRIC_pv_power=1                      # Solar panel power output in watts
METRIC_pv_voltage=1                    # Solar panel voltage
METRIC_pv_current=1                    # Solar panel current in amps
METRIC_battery_voltage=1               # Battery voltage
METRIC_battery_current=1               # Battery current in amps
METRIC_battery_charge_power_from_ac=1  # AC charging power to battery in watts
```

### CSV Attachment Option
```
# 1 = include CSV report, 0 = don't include
CSV_REPORT=1
```

## Manual Report Generation

You can trigger reports manually without waiting for the scheduled time:

```bash
# Generate a daily report
docker exec -it solarassistant-reports python -c "from app.report_generator import generate_and_send_report; generate_and_send_report('daily')"

# Generate a weekly report
docker exec -it solarassistant-reports python -c "from app.report_generator import generate_and_send_report; generate_and_send_report('weekly')"

# Generate a monthly report
docker exec -it solarassistant-reports python -c "from app.report_generator import generate_and_send_report; generate_and_send_report('monthly')"
```

## Report Formats

### Daily Reports
- **Email**: Summary statistics for selected metrics
- **CSV**: A single row with energy totals for the day

### Weekly Reports
- **Email**: Summary statistics for selected metrics over the week
- **CSV**: Daily rows for each day of the week plus a total row at the bottom

### Monthly Reports
- **Email**: Summary statistics for selected metrics over the month
- **CSV**: Daily rows for each day of the month plus a total row at the bottom

## Troubleshooting

### No Data in Reports

- Check that your Solar Assistant instance is correctly configured and collecting data
- Verify that the MQTT connection details are correct
- Look in the logs for any connection errors

### Email Not Sending

- Check your SMTP server settings
- Verify that your email account allows sending via SMTP
- For Gmail, you may need to set up an app password

### Reports Not Running on Schedule

- Check that the correct timezone is set in the .env file
- Verify that the report is enabled (REPORT_DAILY=1, etc.)
- Check the logs for any errors in the scheduler

## Docker Management Commands

### Viewing Logs
```bash
docker-compose logs -f
```

### Stopping the Container
```bash
docker-compose down
```

### Restarting the Container
```bash
docker-compose restart
```

### Updating the Application
```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Support

For questions, issues, or feature requests, please contact the author, Stefan Verster.

## License

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C
