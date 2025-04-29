import tkinter as tk
from tkinter import ttk
import socket
import json
import threading

# Server configuration
HOST = "192.168.115.174"  # Change to server IP
PORT = 65432

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Function to send login data
def send_login():
    username = "teacher"  # Hardcoded for simplicity (can be input)
    send_data("login", username, "teacher")

# Function to send data to the server
def send_data(action, username=None, status=None):
    data = {"action": action, "username": username, "status": status}
    try:
        client_socket.send(json.dumps(data).encode("utf-8"))
    except (ConnectionError, OSError) as e:
        print(f"Error sending data: {e}")

# Function to update the attendance table
def update_table(data):
    for row in tree.get_children():
        tree.delete(row)
    for username, status in data.items():
        tree.insert("", "end", values=(username, "Present" if status == "present" else "Absent"))
        if status == "present":
            status_label.config(text=f"{username} is present!", fg="green")
            teacher_root.after(3000, lambda: status_label.config(text=""))

# Function to handle incoming messages
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            message = json.loads(data)
            if message.get("action") == "update_attendance":
                teacher_root.after(0, update_table, message.get("data", {}))
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except ConnectionError:
            print("Connection lost")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Start the receive thread
threading.Thread(target=receive_messages, daemon=True).start()

# Create the teacher window
teacher_root = tk.Tk()
teacher_root.title("Teacher Panel")
teacher_root.geometry("800x600")

# Status label
status_label = tk.Label(teacher_root, text="", font=("Arial", 14))
status_label.pack(pady=10)

# Treeview for attendance
tree = ttk.Treeview(teacher_root, columns=("Username", "Status"), show="headings")
tree.heading("Username", text="Username")
tree.heading("Status", text="Status")
tree.column("Username", width=400)
tree.column("Status", width=400)
tree.pack(fill="both", expand=True, padx=20, pady=20)

# Send login info
send_login()

# Close socket on exit
def on_closing():
    client_socket.close()
    teacher_root.destroy()

teacher_root.protocol("WM_DELETE_WINDOW", on_closing)
teacher_root.mainloop()
