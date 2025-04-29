import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading
import subprocess
import ctypes
import os

# Server configuration
HOST = "192.168.115.49"  # Change to server IP
PORT = 65432

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Hardcoded credentials (replace with your students)
USER_CREDENTIALS = {
    "student1": "password1",
    "student2": "password2",
    "student3": "password3"
}

# Authorized Wi-Fi BSSID
AUTHORIZED_BSSID = "ee:ee:6d:9d:6f:ba"

def send_data(action, username=None, status=None):
    try:
        data = {"action": action, "username": username, "status": status}
        client_socket.send(json.dumps(data).encode("utf-8"))
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to send data: {str(e)}")

def check_wifi_connection():
    try:
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], 
                              capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "BSSID" in line:
                bssid = ":".join(line.split(":")[1:]).strip().lower()
                return bssid == AUTHORIZED_BSSID.lower()
    except Exception as e:
        messagebox.showerror("Error", f"Wi-Fi check failed: {str(e)}")
    return False

def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Error", "Please enter both username and password")
        return

    if USER_CREDENTIALS.get(username) == password:
        messagebox.showinfo("Success", "Login successful!")
        root.destroy()
        send_data("login", username, "student")
        start_attendance_timer(username)
    else:
        messagebox.showerror("Error", "Invalid credentials")

def start_attendance_timer(username):
    timer_window = tk.Tk()
    timer_window.title("Attendance Timer")
    timer_window.geometry("400x250")
    
    timer_label = tk.Label(timer_window, text="", font=("Arial", 14))
    timer_label.pack(pady=20)
    
    def update_timer(seconds=10):
        if seconds > 0:
            if check_wifi_connection():
                timer_label.config(text=f"Time remaining: {seconds} seconds", fg="black")
                timer_window.after(1000, update_timer, seconds-1)
            else:
                timer_label.config(text="Connect to authorized Wi-Fi!", fg="red")
                timer_window.after(1000, update_timer, seconds)
        else:
            send_data("mark_present", username)
            timer_label.config(text="Attendance marked!", fg="green")
            tk.Button(timer_window, text="Close", command=timer_window.destroy).pack()
    
    tk.Label(timer_window, text="Click Start to begin attendance").pack()
    tk.Button(timer_window, text="Start", command=lambda: update_timer()).pack()
    timer_window.mainloop()

# GUI Setup
root = tk.Tk()
root.title("Student Login")
root.geometry("300x200")

tk.Label(root, text="Username:").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password:").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=login).pack(pady=10)

# Hide console (Windows only)
if os.name == 'nt':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def on_closing():
    client_socket.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
