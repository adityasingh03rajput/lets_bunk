import tkinter as tk
from tkinter import ttk
import socket
import json
import threading

HOST = "192.168.115.49"  # Same as server IP
PORT = 65432

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_data(action, username=None, status=None):
    data = {"action": action, "username": username, "status": status}
    client_socket.send(json.dumps(data).encode("utf-8"))

def update_table(data):
    for row in tree.get_children():
        tree.delete(row)
    for student, status in data.items():
        tree.insert("", "end", values=(student, "Present" if status == "present" else "Absent"))

def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            message = json.loads(data)
            if message.get("action") == "update_attendance":
                root.after(0, update_table, message.get("data", {}))
        except:
            break

# Start receive thread
threading.Thread(target=receive_messages, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("Teacher Dashboard")
root.geometry("600x400")

# Attendance Table
tree = ttk.Treeview(root, columns=("Student", "Status"), show="headings")
tree.heading("Student", text="Student")
tree.heading("Status", text="Status")
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Login as teacher
send_data("login", "teacher", "teacher")

def on_closing():
    client_socket.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
