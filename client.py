import socket
import json

def start_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("[CONNECTED] Connected to the server.")

        while True:
            move = input("Enter move (rock, paper, or scissors): ")
            message = json.dumps({"type": "move", "move": move})
            client_socket.send(message.encode("utf-8"))
            
            response = client_socket.recv(1024).decode("utf-8")
            response_data = json.loads(response)
            print(f"[SERVER] {response}")
    except ConnectionRefusedError:
        print("[ERROR] Connection failed. Is the server running?")
    finally:
        client_socket.close()
        print("[DISCONNECTED] Disconnected from server.")

if __name__ == "__main__":
    server_ip = input("Enter the server IP address (default is 127.0.0.1): ") or "127.0.0.1"
    port = int(input("Enter the port number to connect to: "))
    start_client(server_ip, port)
