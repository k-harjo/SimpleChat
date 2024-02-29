import socket
import threading
import os

def client_thread(conn, addr, clients):
    conn.send("Welcome to the chatroom!".encode('utf-8'))
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"{addr} says: {message}")
                broadcast(message, conn, clients)
            else:
                remove(conn, clients)
        except:
            continue

def broadcast(message, connection, clients):
    for client in clients:
        if client != connection:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove(client, clients)

def remove(connection, clients):
    if connection in clients:
        clients.remove(connection)

def get_host_and_port():
    try:
        # Create a temporary socket to determine the host's IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Use Google's Public DNS server to find the host IP
            s.connect(("127.0.0.1", 80))
            host_ip = s.getsockname()[0]
    except Exception as e:
        print(input("Error loading default host. Enter the host IP address: "))
        host_ip = '127.0.0.1'  # Fallback to localhost

    port = int(os.environ.get("PORT", 8088))
    if port != 8088:
        print("Using default port 8080.")
        port = 8080
    return host_ip, port

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = get_host_and_port()[0]
    port = get_host_and_port()[1]
    server_socket.bind((host, port))
    server_socket.listen(100)
    clients = []

    print("Chat server started on host: " + host + " & port: " + str(port))

    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        print(f"{addr} connected.")
        threading.Thread(target=client_thread, args=(conn, addr, clients)).start()

if __name__ == "__main__":
    main()
