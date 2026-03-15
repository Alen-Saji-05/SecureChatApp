import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

clients = []

def broadcast(data, sender):
    for c in clients:
        if c != sender:
            try:
                c.send(data)
            except:
                pass

def handle_client(conn):
    clients.append(conn)

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            broadcast(data, conn)
        except:
            break

    clients.remove(conn)
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server running...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()