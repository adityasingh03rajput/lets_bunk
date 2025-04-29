import socket
import threading
import json
import os

# Server configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65432

# File to store data
DATA_FILE = "data.json"

# Load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                if "attendance" not in data:
                    data["attendance"] = {}
                if "students_online" not in data:
                    data["students_online"] = {}
                if "teachers_online" not in data:
                    data["teachers_online"] = {}
                return data
        except json.JSONDecodeError:
            return {"attendance": {}, "students_online": {}, "teachers_online": {}}
    return {"attendance": {}, "students_online": {}, "teachers_online": {}}

# Save data to file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Broadcast attendance data to all clients
def broadcast_attendance():
    data = load_data()
    attendance_data = json.dumps({"action": "update_attendance", "data": data["attendance"]}).encode("utf-8")
    for conn in data["students_online"].values():
        try:
            conn.send(attendance_data)
        except:
            pass
    for conn in data["teachers_online"].values():
        try:
            conn.send(attendance_data)
        except:
            pass

# Handle client connections
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    data = load_data()
    while True:
        try:
            message = conn.recv(1024).decode("utf-8")
            if not message:
                break

            message = json.loads(message)
            action = message.get("action")
            username = message.get("username")
            status = message.get("status")

            if action == "login":
                role = "students_online" if status == "student" else "teachers_online"
                data[role][username] = conn
                save_data(data)
                broadcast_attendance()

            elif action == "start_timer":
                data["attendance"][username] = "present"
                save_data(data)
                broadcast_attendance()
                print(f"{username} is present")  # Log to console

        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove disconnected clients
    for role in ["students_online", "teachers_online"]:
        for user, client_conn in list(data[role].items()):
            if client_conn == conn:
                del data[role][user]
                save_data(data)
                broadcast_attendance()
                break

    conn.close()

# Start the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
