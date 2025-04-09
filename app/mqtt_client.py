"""
Email Scheduler for Solar Assistant

Author: Stefan Verster
Copyright © 2025 Stefan Verster

This code is available for personal and non-commercial use.
If you find this software useful, please consider supporting the author by making a donation:
https://www.paypal.com/donate/?hosted_button_id=2YZ4F42REQX4C

Thank you for your support!
"""

import paho.mqtt.client as mqtt
import json
from app.db import save_reading
from config.config import Config

client = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        # Subscribe to solar_assistant total topics
        client.subscribe("solar_assistant/total/#")
        print("📡 Subscribed to solar_assistant/total/#")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')

    try:
        # First, try to parse as JSON
        data = json.loads(payload)
        if isinstance(data, dict) and 'state' in data:
            state = data['state']
        else:
            # If no 'state' key, just store raw payload
            state = float(payload)
    except json.JSONDecodeError:
        # If not JSON, assume raw value
        state = float(payload)

    topic = msg.topic
    save_reading(topic, state)
    print(f"📝 Saved reading: {topic} = {state}")


def start_mqtt():
    global client
    client = mqtt.Client()
    client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)

    # Run network loop in the background
    client.loop_start()
