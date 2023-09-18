import os
import platform
import random
import subprocess
import uuid
from datetime import datetime
import PySimpleGUI as sg

# Check if the script is running with root privileges (sudo)
if os.geteuid() != 0:
    print("This script must be run with root privileges (sudo).")
    exit(1)

# Determine the OS platform
current_os = platform.system()


# Function to get the current MAC address
def get_current_mac(interface):
    try:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    except Exception as e:
        return str(e)


# Initialize MAC address change logs
mac_change_logs = []

# Initialize a list to store liked MAC addresses
liked_mac_addresses = []

# Get the current MAC address
current_mac = get_current_mac("eth0")


# Function to change the MAC address
def change_mac(interface, new_mac):
    try:
        subprocess.call(["sudo", "ifconfig", interface, "down"])
        subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
        subprocess.call(["sudo", "ifconfig", interface, "up"])
        return True, None
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

# Set initial theme
sg.theme(themes[0])

# Help/Documentation window layout
help_layout = [
    [sg.Multiline("Welcome to MACHA - MAC Address Changer!\n\n"
                  "This application allows you to change the MAC address of your network interface. "
                  "MAC address changes can be useful for various reasons, such as enhancing privacy or "
                  "solving network connectivity issues. Here's how to use the application:\n\n"
                  "Step 1: Enter the New MAC Address\n"
                  "In the 'New MAC Address' field, you can enter the desired MAC address that you want to assign "
                  "to your network interface. The MAC address should be in the following format:\n\n"
                  "01:23:45:67:89:ab\n\n"
                  "Make sure to use colons (:) to separate each pair of hexadecimal digits. The new MAC address "
                  "should be unique and not currently in use on your network.\n\n"
                  "Step 2: Change MAC Address\n"
                  "After entering the new MAC address, click the 'Change MAC Address' button. The application will "
                  "attempt to change your network interface's MAC address to the one you provided. If successful, "
                  "you will see a confirmation message.\n\n"
                  "For More Information and Support\n"
                  "For more detailed information about the application's features and advanced settings, please "
                  "refer to the user manual or contact our support team. We are here to assist you with any questions "
                  "or issues you may encounter while using MACHA.",
                  size=(60, 20), disabled=True, key="-HELP-", text_color="black")],
    [sg.Button("Close")]
]


# Function to show the help/documentation window
def show_help_window():
    help_window = sg.Window("Help & Documentation", help_layout, finalize=True, size=(400, 300))
    while True:
        event, _ = help_window.read()
        if event == sg.WIN_CLOSED or event == "Close":
            break
    help_window.close()


# Create the GUI layout
layout = [
    [sg.Text(
        '''
        ___  ___           _           
        |  \/  |          | |          
        | .  . | __ _  ___| |__   __ _ 
        | |\/| |/ _` |/ __| '_ \ / _` |
        | |  | | (_| | (__| | | | (_| |
        \_|  |_/\__,_|\___|_| |_|\__,_|

        ~by inxdict
        ''',
        size=(50, 8), justification='center')],
    [sg.Text("By inxdict", font=("Helvetica", 10))],
    [sg.Text("Current MAC Address:", size=(20, 1)), sg.Text(current_mac, size=(17, 1), key="-CURRENT_MAC-")],
    [sg.Text("New MAC Address:", size=(20, 1)), sg.InputText("", size=(17, 1), key="-NEW_MAC-")],
    [sg.Button("Change MAC Address")],
    [sg.Button("Generate Random MAC")],
    [sg.Button("Like It")],  # Add "Like It" button next to "Generate MAC" button
    [sg.Text("", size=(40, 1), key="-STATUS-")],
    [sg.Multiline("", size=(40, 4), key="-ERROR-", text_color="red")],
    [sg.Button("View Logs"), sg.Button("Clear Logs"), sg.Button("Help")],  # Add a "Help" button

    # Section for storing liked MAC addresses
    [sg.Text("Liked MAC Addresses:", size=(20, 1))],
    [sg.Listbox(values=liked_mac_addresses, size=(30, 6), key="-LIKED_MACS-", enable_events=True)],
    [sg.Button("Use"), sg.Button("Remove")],  # Add "Use" and "Remove" buttons
]

# Create the GUI window
window = sg.Window("MACHA - MAC Address Changer", layout, resizable=True, finalize=True, size=(400, 500))

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
                # Display the error message in the GUI
                window["-STATUS-"].update("Failed to change MAC Address.")
                window["-ERROR-"].update(result)  # Display the error message
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

    if event == "Help":
        show_help_window()

    # Add functionality to "Like It" button
    if event == "Like It":
        liked_mac = values["-NEW_MAC-"]
        if liked_mac:
            liked_mac_addresses.append(liked_mac)
            window["-LIKED_MACS-"].update(values=liked_mac_addresses)

    # Add functionality to "Use" button
    if event == "Use":
        selected_mac_text = values["-LIKED_MACS-"]
        if selected_mac_text:
            selected_mac = selected_mac_text[0]
            window["-NEW_MAC-"].update(selected_mac)  # Set the selected MAC as the New MAC Address

    # Add functionality to "Remove" button
    if event == "Remove":
        selected_mac_indices = values["-LIKED_MACS-"]
        if selected_mac_indices:
            # Remove the selected MAC address from the liked_mac_addresses list
            selected_mac = selected_mac_text[0]
            liked_mac_addresses.remove(selected_mac)
            window["-LIKED_MACS-"].update(values=liked_mac_addresses)

window.close()
