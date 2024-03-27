import requests

sensor_data_url = "http://localhost:5000/api/v3_0/sensors/data"
auth_url = "http://localhost:5000/api/requestAuthToken"
email = "projects.gepee@gmail.com"
password = "1234"
data_auth ={"email":email,"password":password}
auth_token = requests.post(auth_url, json=data_auth).json().get("auth_token")
sensor_id_com = "ea1.2024-04.localhost:fm1.3"
print("                   ggg                ")

sensor_data = {
    "sensor": sensor_id_com,
    "start": "2024-03-25T00:00:00+05:30",
    "duration": "PT24H",
    "resolution": "PT5M",
    "unit": "MW"
    }

headers = {
        "Authorization": auth_token
    }

response = requests.get(sensor_data_url,params=sensor_data, headers=headers)

if response.status_code == 200:
    print("Sensor data inserted successfully.",response.json()['values'])
else:
    print("Failed to insert sensor data:", response.json())