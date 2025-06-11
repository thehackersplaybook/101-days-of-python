import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = []  # List of (socket, username)

def broadcast(message, sender_socket):
    print(message)  # Print all messages on server terminal
    for client_socket, _ in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                remove_client(client_socket)

def remove_client(client_socket):
    for i, (sock, username) in enumerate(clients):
        if sock == client_socket:
            print(f"{username} disconnected.")
            clients.pop(i)
            break
    client_socket.close()

def handle_client(client_socket):
    try:
        client_socket.send("Enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()
        if not username:
            client_socket.close()
            return

        clients.append((client_socket, username))
        print(f"{username} connected.")
        broadcast(f"*** {username} has joined the chat ***", client_socket)

        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            broadcast(f"{username}: {message}", client_socket)

    except Exception as e:
        pass
    finally:
        remove_client(client_socket)
        broadcast(f"*** {username} has left the chat ***", None)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on port {PORT}...")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

if __name__ == "__main__":
    main()
