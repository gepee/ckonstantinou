import tkinter as tk
import requests
from tkinter import simpledialog

def add_assets():
    # Authentication
    email = "projects.gepee@gmail.com"
    password = "1234"
    auth_token = authenticate(email, password)
    if not auth_token:
        return

    # Get asset details
    name = simpledialog.askstring("Asset Details", "Enter asset name:")
    asset_type_id = simpledialog.askinteger("Asset Details", "Enter asset type ID:")
    latitude = simpledialog.askfloat("Asset Details", "Enter latitude:")
    longitude = simpledialog.askfloat("Asset Details", "Enter longitude:")
    account_id = 1

    # Add assets
    add_assets_request(auth_token, name, asset_type_id, latitude, longitude, account_id)

def authenticate(email, password):
    auth_url = "http://localhost:5000/api/requestAuthToken"
    data = {"email": email, "password": password}
    response = requests.post(auth_url, json=data)
    if response.status_code == 200:
        return response.json().get("auth_token")
    else:
        print("Failed to authenticate:", response.text)
        return None

def add_assets_request(auth_token, name, asset_type_id, latitude, longitude, account_id):
    assets_url = "http://localhost:5000/api/addAssets"
    headers = {"Authorization": auth_token}
    data = {
        "name": name,
        "asset_type_id": asset_type_id,
        "latitude": latitude,
        "longitude": longitude,
        "account_id": account_id
    }
    response = requests.post(assets_url, json=data, headers=headers)
    if response.status_code == 200:
        print("Assets added successfully.")
    else:
        print("Failed to add assets:", response.text)

# Create GUI window
window = tk.Tk()
window.title("Add Assets")

# Add button to add assets
add_assets_button = tk.Button(window, text="Add Assets", command=add_assets)
add_assets_button.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()
