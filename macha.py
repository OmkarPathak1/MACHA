import os
import platform
import threading
import subprocess
import PySimpleGUI as sg
import random
from datetime import datetime
import uuid
import time

# Check if the script is running with root privileges (sudo)
if os.geteuid() != 0:
    print("This script must be run with root privileges (sudo).")
    exit(1)

# Define the ASCII art banner
ascii_art = """
___  ___           _           
|  \/  |          | |          
| .  . | __ _  ___| |__   __ _ 
| |\/| |/ _` |/ __| '_ \ / _` |
| |  | | (_| | (__| | | | (_| |
\_|  |_/\__,_|\___|_| |_|\__,_|
                               
~by inxdict
"""

# Determine the OS platform
current_os = platform.system()

# Function to get the current MAC address
def get_current_mac(interface):
    try:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e+2] for e in range(0, 11, 2)])
    except Exception as e:
        return str(e)

# Initialize MAC address change logs
mac_change_logs = []

# Get the current MAC address
current_mac = get_current_mac("eth0")

# Function to change the MAC address
def change_mac(interface, new_mac):
    try:
        subprocess.call(["sudo", "ifconfig", interface, "down"])
        subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
        subprocess.call(["sudo", "ifconfig", interface, "up"])
        return True, None  # Success
    except Exception as e:
        return False, str(e)

# Function to generate a random MAC address
def generate_random_mac():
    first_byte = random.randint(0x00, 0xFE) 
    random_mac = [first_byte] + [random.randint(0x00, 0xFF) for _ in range(5)]
    return ':'.join([format(x, '02x') for x in random_mac])

# Available themes
themes = [
    'DarkGrey5'
]

# Randomly select the initial theme
current_theme_index = random.randint(0, len(themes) - 1)

# Function to automatically change the theme
def auto_change_theme():
    global current_theme_index
    while True:
        current_theme_index = (current_theme_index + 1) % len(themes)
        sg.change_look_and_feel(themes[current_theme_index])
        time.sleep(5)

# Start the theme rotation thread
theme_thread = threading.Thread(target=auto_change_theme)
theme_thread.daemon = True
theme_thread.start()

# Set initial theme
sg.change_look_and_feel(themes[current_theme_index])

# Create the GUI layout
layout = [
    [sg.Text(ascii_art, size=(40, 8))], 
    [sg.Text("By inxdict", font=("Helvetica", 10))],
    [sg.Text("Current MAC Address:", size=(20, 1)), sg.Text(current_mac, size=(17, 1), key="-CURRENT_MAC-")],
    [sg.Text("New MAC Address:", size=(20, 1)), sg.InputText("", size=(17, 1), key="-NEW_MAC-")],
    [sg.Button("Change MAC Address")],
    [sg.Button("Generate Random MAC")],
    [sg.Text("", size=(40, 1), key="-STATUS-")],
    [sg.Multiline("", size=(40, 4), key="-ERROR-", text_color="red")],
    [sg.Button("View Logs")],
    [sg.Button("Clear Logs")],
]

# Create the GUI window
window = sg.Window("MACHA - MAC Address Changer", layout, resizable=True)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "Change MAC Address":
        new_mac = values["-NEW_MAC-"]
        if len(new_mac) == 17 and new_mac.count(":") == 5:
            success, result = change_mac("eth0", new_mac) if current_os == "Linux" else ("Unsupported OS", None)
            if success:
                window["-STATUS-"].update("MAC Address changed successfully.")
                window["-ERROR-"].update("")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mac_change_logs.append(f"Changed MAC address from {current_mac} to {new_mac} at {current_time}")
                current_mac = new_mac 
                window["-CURRENT_MAC-"].update(current_mac) 
            else:
                window["-STATUS-"].update("Failed to change MAC Address.")
                window["-ERROR-"].update(result)
        else:
            window["-STATUS-"].update("Invalid MAC Address format.")
            window["-ERROR-"].update("A valid MAC address format is like 01:23:45:67:89:ab")

    if event == "Generate Random MAC":
        random_mac = generate_random_mac()
        window["-NEW_MAC-"].update(random_mac)

    if event == "View Logs":
        logs = "\n".join(mac_change_logs)
        sg.popup_scrolled("MAC Address Change Logs", logs, size=(80, 20))

    if event == "Clear Logs":
        mac_change_logs.clear()

window.close()
