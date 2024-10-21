import socket
import threading
import json

clients = []
players = {}

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(json.dumps({"type": "info", "message": message}).encode("utf-8"))
            except Exception as e:
                print(f"[ERROR Could not send message to Client: {e}")
                client.close()
                clients.remove(client)
            
        

# Function to handle client connections
def handle_client(client_socket, address):
    global players
    player_name = None
    print(f"[NEW CONNECTION] {address} connected.")
    
    connected = True
    
    clients.append(client_socket)
    
    while connected:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            message = json.loads(message)
            if message["type"] == "join":
                player_name = message['player_name']
                players[player_name] = None
                print(f"{message['player_name']} has joined the game.")
                broadcast(f"Player {player_name} has joined the game.", client_socket)
            elif message["type"] == 'move':
                move = message['move']
                players[player_name] = move  
                print(f"Received move from {address}: {message['move']}")
            elif message["type"] == 'chat':
                chat_message = f"Player {player_name}: {message['message']}"
                broadcast(chat_message, client_socket)
            elif message["type"] == 'quit':
                players.pop(player_name, None)
                print(f"Player {player_name} has quit.")
                connected = False  
                
            client_socket.send(json.dumps({"type": "ack", "message": "Message received"}).encode("utf-8"))
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


