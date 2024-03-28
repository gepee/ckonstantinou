import tkinter as tk
from tkinter import filedialog, simpledialog
import csv
import requests
import paho.mqtt.client as mqtt
import csv
import json
import threading
import pulp
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


broker_address = "broker.hivemq.com"
broker_port = 1883
mqtt_loop_active =False
client = None
temp_sensor_id=None
global sensor_data_url
sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"

def read_csv(filename):
    with open(filename,'r') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            print(row)
        for element in row:
            data.append(float(element))
    print(data)
    return data

def downsampled_list(sereies):
    downsampled_length = 24

    segment_length = len(sereies) // downsampled_length
    # Downsample the original list by calculating the average of each segment
    downsampled_list = []
    for i in range(downsampled_length):
        start_index = i * segment_length
        end_index = start_index + segment_length
        segment = sereies[start_index:end_index]
        average = sum(segment) / len(segment)
        downsampled_list.append(average)
    return downsampled_list


    if type(data) is not 'str':
        data = str(data)
    return data

def get_data(thing):
    # makeitstr(sensorno)
    # makeitstr(units)
    # makeitstr(date)
    # makeitstr(utc)
    sensor_no = simpledialog.askstring("sensor_no","Enter the sensor no. for "+thing)
    sensor_units = simpledialog.askstring("sensor_units","Enter the sensor units for "+thing)
    date = simpledialog.askstring("date","Enter the date")
    utc = simpledialog.askstring("utc","enter the utc")
   

    sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data_auth ={"email":email,"password":password}
    auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
    sensor_id_com = "ea1.2024-04.localhost:fm1."+sensor_no
    
    print("                   ggg                ")

    sensor_data = {
        "sensor": sensor_id_com,
        "start": date+"T00:00:00+"+utc,
        "duration": "PT24H",
        "resolution": "PT5M",
        "unit": sensor_units
        }

    headers = {
            "Authorization": auth_token
        }

    response = requests.get(sensor_data_url,params=sensor_data, headers=headers)

    if response.status_code == 200:
        print("Sensor data inserted successfully.",response.json()['values'])
        display_message("upadted successfully for "+thing)
    else:
        print("Failed to insert sensor data: "+thing, response.json())
        display_message(response.json)
    return response.json()['values']
def schedule():
    Zmax = simpledialog.askfloat("battery cap", "enter the battery cap in MW")
    Qmax = simpledialog.askinteger("battery charging rate", "enter the battery charging discharging rate")
    is_solar = simpledialog.askstring("is_solar", "Is solar data avaialable yes or no")
    T =24
    if is_solar=='yes':
        S = downsampled_list(get_data("solar"))
    elif is_solar=='no':
        S=[0 for i in range(0,T)]
    is_wind = simpledialog.askstring("is_solar", "Is wind data avaialable yes or no")
    if is_wind=='yes':
        W = downsampled_list(get_data("wind"))
    elif is_wind=='no':
        W=[0 for i in range(0,T)]

    P = downsampled_list(get_data("price"))
    
    L = downsampled_list(get_data("load"))
    
    Zmax =Zmax
    Zmin = Zmax*0.05
    Qmax = Qmax
    Qmin = -Qmax
    times = range(T)
    model = pulp.LpProblem("Battery Scheduling", pulp.LpMinimize)
    Q = pulp.LpVariable.dicts("Q", times, lowBound=Qmin, upBound=Qmax)
    Z = pulp.LpVariable.dicts("Z", times, lowBound=Zmin, upBound=Zmax)

    cost = pulp.lpSum(P[t]*(L[t] +S[t] + Q[t]+W[t]) for t in times)
    model += cost

    for t in times:
        model += Z[t] >= Zmin
        model += Z[t] <= Zmax
        model += L[t] + S[t] + Q[t] +W[t] >= 0


    for t in range(T-1):  # We iterate till T-1 because there's no t+1 for the last time step
        model += Z[t+1] == Z[t] + Q[t]

    
    model.solve()
    display_message("Total cost ="+str(pulp.value(model.objective)))

    sensor_update = simpledialog.askstring("update_sensor","Which sensor you want to be updated")
    date = simpledialog.askstring("uploading date","date on which the data to be uploaded")
    sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
    auth_url = "http://localhost:5000/api/requestAuthToken"
    email = "projects.gepee@gmail.com"
    password = "1234"
    data_auth ={"email":email,"password":password}
    auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
    sensor_id_com = "ea1.2024-04.localhost:fm1."+sensor_update
    # print("                   ggg                ")
    # print(data)
    sensor_data = {
        "type": "PostSensorDataRequest",
        "sensor": sensor_id_com,
        "values": [pulp.value(Z[t]) for t in times],
        "start": date+"T00:00:00+05:30",
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
    start_time = simpledialog.askstring("Start Time", "Enter Start date yyyy-mm-dd:")
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
window.title("Gepee-FlexMeasures Data Interface")
add_scheduler_button = tk.Button(window, text="Schedule", command=schedule, height=2)
add_scheduler_button.pack(pady=5)
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
