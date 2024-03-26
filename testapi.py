import tkinter as tk
from tkinter import filedialog

def select_file():
    file_path = filedialog.askopenfilename()
    file_label.config(text=file_path)

def clear_display():
    display.delete('1.0', tk.END)

def add_solar():
    # Your code to add solar data to FlexMeasures
    display_message("Solar data added")

def add_wind():
    # Your code to add wind data to FlexMeasures
    display_message("Wind data added")

def add_residential_consumer():
    # Your code to add residential consumer data to FlexMeasures
    display_message("Residential consumer data added")

def add_rtp():
    # Your code to add RTP data to FlexMeasures
    display_message("RTP data added")

def add_dg():
    # Your code to add DG data to FlexMeasures
    display_message("DG data added")

def display_message(message):
    display.insert(tk.END, message + "\n")

window = tk.Tk()
window.title("FlexMeasures Data Interface")

file_button = tk.Button(window, text="Select File", command=select_file, height=2)
file_button.pack(pady=5)

file_label = tk.Label(window, text="", wraplength=300)
file_label.pack(pady=5)

buttons = [
    ("Add Solar", add_solar),
    ("Add Wind", add_wind),
    ("Add Residential Consumer", add_residential_consumer),
    ("Add RTP", add_rtp),
    ("Add DG", add_dg),
    ("Clear Display", clear_display)
]

for btn_text, btn_command in buttons:
    btn = tk.Button(window, text=btn_text, command=btn_command, height=2, width=len(btn_text))
    btn.pack(pady=5, ipadx=5, ipady=5)

display = tk.Text(window, height=10, width=50)
display.pack(pady=5)

window.mainloop()
