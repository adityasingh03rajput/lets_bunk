import socket
import threading
import json
import os

# Server configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65432

# File to store data
DATA_FILE = "data.json"

# Store active connections in memory (not in JSON)
active_connections = {
    "students_online": {},  # Format: {username: socket_conn}
    "teachers_online": {}   # Format: {username: socket_conn}
}

# Load data from file (only non-socket data)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                if "attendance" not in data:
                    data["attendance"] = {}
                return data
        except json.JSONDecodeError:
            return {"attendance": {}}
    return {"attendance": {}}

# Save data to file (only non-socket data)
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump({"attendance": data["attendance"]}, file, indent=4)

# Broadcast attendance data to all clients
def broadcast_attendance():
    data = load_data()
    attendance_data = json.dumps({"action": "update_attendance", "data": data["attendance"]}).encode("utf-8")
    
    # Send to all students
    for conn in active_connections["students_online"].values():
        try:
            conn.send(attendance_data)
        except:
            pass
    
    # Send to all teachers
    for conn in active_connections["teachers_online"].values():
        try:
            conn.send(attendance_data)
        except:
            pass

# Handle client connections
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    data = load_data()
    username = None
    
    try:
        while True:
            message = conn.recv(1024).decode("utf-8")
            if not message:
                break

            message = json.loads(message)
            action = message.get("action")
            username = message.get("username")
            status = message.get("status")

            if action == "login":
                role = "students_online" if status == "student" else "teachers_online"
                active_connections[role][username] = conn  # Store in memory
                save_data(data)  # Update JSON file (without sockets)
                broadcast_attendance()

            elif action == "start_timer":
                data["attendance"][username] = "present"
                save_data(data)
                broadcast_attendance()
                print(f"{username} is present")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Remove disconnected clients
        if username:
            for role in ["students_online", "teachers_online"]:
                if username in active_connections[role]:
                    del active_connections[role][username]
                    broadcast_attendance()
        conn.close()

# Start the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
