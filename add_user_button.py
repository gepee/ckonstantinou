import tkinter as tk
import requests

def add_user():
    # Get the username and email from the entry fields
    username = username_entry.get()
    email = email_entry.get()

    # Send a POST request to the API endpoint to add the user
    url = "http://localhost:5000/api/v3_0/users"
    data = {"username": username, "email": email}
    response = requests.post(url, json=data)

    # Check the response status and show a message accordingly
    if response.status_code == 201:
        result_label.config(text="User added successfully.", fg="green")
    else:
        result_label.config(text="Failed to add user. Error: " + response.text, fg="red")

# Create the Tkinter window
window = tk.Tk()
window.title("Add User")

# Add labels and entry fields for username and email
username_label = tk.Label(window, text="Username:")
username_label.pack()
username_entry = tk.Entry(window)
username_entry.pack()

email_label = tk.Label(window, text="Email:")
email_label.pack()
email_entry = tk.Entry(window)
email_entry.pack()

# Add a button to add a user
add_user_button = tk.Button(window, text="Add User", command=add_user)
add_user_button.pack()

# Add a label to display the result of adding the user
result_label = tk.Label(window, text="", fg="black")
result_label.pack()

# Run the Tkinter event loop
window.mainloop()

