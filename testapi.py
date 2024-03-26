import tkinter as tk
from tkinter import filedialog, simpledialog
import csv
import requests
import paho.mqtt.client as mqtt
import csv
import json
import threading

broker_address = "broker.hivemq.com"
broker_port = 1883
mqtt_loop_active =False
client = None
temp_sensor_id=None
global sensor_data_url
sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"


def recieve_data():
    global temp_sensor_id, mqtt_loop_active, client
    mqtt_loop_active = not mqtt_loop_active  # Toggle the MQTT loop status
    broker_address = "broker.hivemq.com"
    broker_port = 1883

    if mqtt_loop_active:
        temp_sensor_id = simpledialog.askinteger("temp sensor id ", "enter temp sensor id")
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker_address, broker_port, 60)
        
        # Start MQTT communication loop in a separate thread
        mqtt_thread = threading.Thread(target=client.loop_start)
        mqtt_thread.daemon = True  # Daemonize the thread to stop it when the main thread exits
        mqtt_thread.start()
        
        display_message("started receiving")
    else:
        client.loop_stop()
        display_message("stopped receiving")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("sensor/data")

def on_message(client, userdata, msg):
    # Decode the message payload from JSON
    sensor_data = json.loads(msg.payload)
    print("Received sensor data:", sensor_data)
    display_message(sensor_data)
    # Write the sensor data to a CSV file
    # with open('sensor_data.csv', mode='a', newline='') as file:
    #     writer = csv.DictWriter(file, fieldnames=sensor_data.keys())
    #     if file.tell() == 0:
    #         writer.writeheader()
    #     writer.writerow(sensor_data)
    value = sensor_data["value"]
    timestamp = sensor_data["timestamp"]

    # Create payload for posting to temp sensor API
    print("1           ")
    sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data_auth ={"email":email,"password":password}
    auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
    sensor_id_com = "ea1.2024-04.localhost:fm1."+str(temp_sensor_id)
    print("2               ")

    sensor_data = {
        "type": "PostSensorDataRequest",
        "sensor": sensor_id_com,
        "values": value,
        "start": timestamp,
        "duration": "PT1M",
        "unit": "C"
    }

    headers = {
        "Authorization": auth_token
    }

    response = requests.post(sensor_data_url, json=sensor_data, headers=headers)

    if response.status_code == 200:
        print("Sensor data inserted successfully.")
        display_message("Sensor data inserted successfully.")
    else:
        print("Failed to insert sensor data:", response.json())
        display_message("Failed to insert sensor data")

def display_message(message):
    display.insert(tk.END, message + "\n")
def select_sensor_id():
    sensor_id = simpledialog.askstring("Sensor ID", "Enter Sensor ID:")
    return sensor_id

def select_data_type():
    data_type = simpledialog.askstring("Data Type", "Enter Data Type (single/list/csv):")
    return data_type.lower()

def select_data(data_type):
    if data_type == "single":
        data = simpledialog.askstring("Data", "Enter Single Value:")
        return [data]
    elif data_type == "list":
        data = simpledialog.askstring("Data", "Enter Values (comma-separated):")
        return data.split(",")
    elif data_type == "csv":
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)
        return row

def add_sensor():
    name = simpledialog.askstring("Sensor Details", "Enter Sensor Name:")
    if not name:
        return
    
    # entity_address = simpledialog.askstring("Sensor Details", "Enter Entity Address:")
    # if not entity_address:
    #     return
    unit = simpledialog.askstring("Sensor Details", "Enter Unit:")
    if not unit:
        return
    
    asset_id = simpledialog.askinteger("Sensor Details", "Enter Asset ID:")
    if not asset_id:
        return
    event_resolution = simpledialog.askstring("senor resolution", "enter event resolutions")
    if not event_resolution:
        return
    # Define the URL for adding a sensor
    add_sensor_url = "http://localhost:5000/api/v3_0/sensors"

    # Define the authentication token
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data = {"email": email, "password": password}

    # Request authentication token
    auth_token = requests.post(auth_url, json=data).json().get("auth_token")

    # Define the sensor data to be added
    sensor_data = {
        "name": name,
        "unit": unit,
        "generic_asset_id": asset_id,
        "event_resolution":event_resolution
    }

    # Set the authentication token in the request headers
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }

    # Send a POST request to add the sensor
    response = requests.post(add_sensor_url, json=sensor_data, headers=headers)

    # Check if the request was successful (status code 201)
    if response.status_code == 201:
        print("Sensor added successfully.")
        display_message("Sensor added successfully.")
    else:
        # If the request was unsuccessful, print the error message
        print("Failed to add sensor:", response.json())
        display_message("Failed to add sensor")

def select_start_time():
    start_time = simpledialog.askstring("Start Time", "Enter Start Time (YYYY-MM-DD HH:MM:SS):")
    return start_time
def units_():
    units = simpledialog.askstring("units","enter the units")
    return units

def post_sensor_data():
    sensor_id = select_sensor_id()
    if not sensor_id:
        return

    data_type = select_data_type()
    if not data_type:
        return

    data = select_data(data_type)
    if not data:
        return

    start_time = select_start_time()
    if not start_time:
        return
    units = units_()
    if not units:
        return
    sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data_auth ={"email":email,"password":password}
    auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
    sensor_id_com = "ea1.2024-04.localhost:fm1."+str(sensor_id)
    print("                   ggg                ")
    print(data)
    sensor_data = {
        "type": "PostSensorDataRequest",
        "sensor": sensor_id_com,
        "values": data,
        "start": start_time+"T00:00:00+05:30",
        "duration": "PT24H",
        "unit": units
    }

    headers = {
        "Authorization": auth_token
    }

    response = requests.post(sensor_data_url, json=sensor_data, headers=headers)

    if response.status_code == 200:
        print("Sensor data inserted successfully.")
        display_message("Sensor data inserted successfully.")
    else:
        print("Failed to insert sensor data:", response.json())
        display_message("Failed to insert sensor data")

def post_asset_data():
    name = simpledialog.askstring("Asset Name", "Enter Asset Name:")
    if not name:
        return

    asset_type_id = simpledialog.askstring("Asset Type ID", "Enter Asset Type ID:")
    if not asset_type_id:
        return

    latitude = simpledialog.askstring("Latitude", "Enter Latitude:")
    if not latitude:
        return

    longitude = simpledialog.askstring("Longitude", "Enter Longitude:")
    if not longitude:
        return

    account_id = simpledialog.askstring("Account ID", "Enter Account ID:")
    if not account_id:
        return
    
    asset_data_url = "http://localhost:5000/api/v3_0/assets"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "gurpindersinghk786@gmail.com"
    password = "1234"
    data={"email":email,"password":password}
    
    auth_token = requests.post(auth_url, json=data).json().get("auth_token")

    asset_data = {
        "name": name,
        "asset_type_id": asset_type_id,
        "latitude": latitude,
        "longitude": longitude,
        "account_id": account_id
    }

    headers = {
        "Authorization": auth_token
    }

    response = requests.post(asset_data_url, json=asset_data, headers=headers)

    if response.status_code == 200:
        print("Asset data added successfully.")
        display_message("Asset data added successfully.")
    else:
        print("Failed to add asset data:", response.json())
        display_message("Failed to add asset data")

def display_message(message):
    display.insert(tk.END, str(message) + "\n")

window = tk.Tk()
window.title("FlexMeasures Data Interface")
add_sensor_button = tk.Button(window, text="Add Sensor", command=add_sensor, height=2)
add_sensor_button.pack(pady=5)
post_button = tk.Button(window, text="Add Data", command=post_sensor_data, height=2)
# post_button_asset = tk.Button(window,text="ADD asset",command=post_asset_data,height=2)
# post_button_asset.pack(pady=5)
post_button.pack(pady=5)
reiceve_button = tk.Button(window,text="Start/Stop temp sensor data", command=recieve_data, height=2)
reiceve_button.pack(pady=5)

display = tk.Text(window, height=10, width=50)
display.pack(pady=5)

window.mainloop()
