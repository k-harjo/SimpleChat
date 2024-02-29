import socket
import threading

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

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '127.0.0.1'
    port = 8088
    server_socket.bind((host, port))
    server_socket.listen(100)
    clients = []

    print("Chat server started on port " + str(port))

    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        print(f"{addr} connected.")
        threading.Thread(target=client_thread, args=(conn, addr, clients)).start()

if __name__ == "__main__":
    main()
