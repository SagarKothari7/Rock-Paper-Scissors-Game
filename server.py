import socket
import threading

# Function to handle client connections
def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    connected = True
    
    while connected:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            print(f"[{address}] {message}")
            client_socket.send("Message received".encode("utf-8"))
        except ConnectionResetError:
            print(f"[ERROR] Connection lost with {address}")
            break
    
    print(f"[DISCONNECT] {address} disconnected.")
    client_socket.close()

# Server setup
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

        # Show active connections
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    port = int(input("Enter the port number for the server: "))
    start_server(port)
