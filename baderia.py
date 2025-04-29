import socket
import threading
import json

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65432

# In-memory storage
attendance = {}
online_students = {}
online_teachers = {}

def broadcast_attendance():
    data = json.dumps({"action": "update_attendance", "data": attendance})
    for teacher_socket in online_teachers.values():
        try:
            teacher_socket.send(data.encode("utf-8"))
        except:
            pass

def handle_client(conn, addr):
    print(f"New connection: {addr}")
    while True:
        try:
            message = json.loads(conn.recv(1024).decode("utf-8"))
            action = message.get("action")
            username = message.get("username")
            
            if action == "login":
                if message.get("status") == "student":
                    online_students[username] = conn
                    attendance[username] = "absent"
                else:  # teacher
                    online_teachers[username] = conn
                broadcast_attendance()
                
            elif action == "mark_present":
                attendance[username] = "present"
                broadcast_attendance()
                
        except:
            break

    # Cleanup disconnected clients
    for username, socket_conn in list(online_students.items()):
        if socket_conn == conn:
            del online_students[username]
            del attendance[username]
    for username, socket_conn in list(online_teachers.items()):
        if socket_conn == conn:
            del online_teachers[username]
    conn.close()
    broadcast_attendance()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server running on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
