import socket
import threading
import sys

HOST = input("Enter server IP (e.g. 127.0.0.1): ")
PORT = 12345

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                print("\nDisconnected from server.")
                break
            print(f"\n{message}\nYou: ", end="", flush=True)
        except:
            print("\nError receiving data.")
            break
    sock.close()
    sys.exit()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Receive prompt for username
    prompt = client.recv(1024).decode()
    username = input(prompt)
    client.send(username.encode())

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            print("Exiting chat...")
            client.close()
            break
        client.send(msg.encode())

if __name__ == "__main__":
    main()
