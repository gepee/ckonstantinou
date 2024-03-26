import tkinter as tk
from tkinter import filedialog, simpledialog
import csv
import requests

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
    
    sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data_auth ={"email":email,"password":password}
    auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
    sensor_id_com = "ea1.2024-04.localhost:fm1."+str(sensor_id)

    sensor_data = {
        "type": "PostSensorDataRequest",
        "sensor": sensor_id_com,
        "values": data,
        "start": start_time+"T00:00:00+05:30",
        "duration": "PT24H",
        "unit": "MW"
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
    display.insert(tk.END, message + "\n")

window = tk.Tk()
window.title("FlexMeasures Data Interface")
add_sensor_button = tk.Button(window, text="Add Sensor", command=add_sensor, height=2)
add_sensor_button.pack(pady=5)
post_button = tk.Button(window, text="Add Data", command=post_sensor_data, height=2)
# post_button_asset = tk.Button(window,text="ADD asset",command=post_asset_data,height=2)
# post_button_asset.pack(pady=5)
post_button.pack(pady=5)


display = tk.Text(window, height=10, width=50)
display.pack(pady=5)

window.mainloop()
