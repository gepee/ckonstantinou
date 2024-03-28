import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# MQTT broker parameters
broker_address = "broker.hivemq.com"
broker_port = 1883

# Define the range for the random sensor value
min_value = 20.0
max_value = 30.0

# Callback function to handle connection established
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Create MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect

# Connect to MQTT broker
client.connect(broker_address, broker_port, 60)

# Loop to publish sensor data
while True:
    # Generate a random sensor value within the specified range
    sensor_value = round(random.uniform(min_value, max_value), 2)

    # Get the current timestamp in the required format
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:30')

    # Define the sensor data as a dictionary
    sensor_data = {
        "value": sensor_value,
        "timestamp": timestamp
    }

    # Convert sensor data to JSON format
    sensor_data_json = json.dumps(sensor_data)

    # Publish sensor data
    client.publish("sensor/data", sensor_data_json)
    print("Published sensor data:", sensor_data_json)

    # Wait for some time before publishing again
    time.sleep(60)
