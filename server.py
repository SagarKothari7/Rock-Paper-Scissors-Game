import socket
import threading
import json

clients = []
players = {}
moves = {}
game_state = {"players": {}, "moves": {}, "status": "waiting for players"}

def broadcast_game_state():
    """Broadcast the updated game state to all connected clients."""
    game_state_message = json.dumps({"type": "game_state", "state": game_state}) + "\n"
    for client in clients:
        try:
            client.send(game_state_message.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Could not send game state to client: {e}")
            client.close()
            clients.remove(client)

def broadcast(message, sender_socket=None):
    """Broadcast a message to all clients except the sender."""
    for client in clients:
            try:
                client.send((json.dumps({"type": "info", "message": message}) + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[ERROR] Could not send message to client: {e}")
                client.close()
                clients.remove(client)


# Function to handle client connections
def handle_client(client_socket, address):
    global players, game_state
    player_name = None
    print(f"[NEW CONNECTION] {address} connected.")
    
    clients.append(client_socket)
    
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            
            message = json.loads(message)
            
            if message["type"] == "join":
                player_name = message['player_name']
                if player_name in players:
                    player_name = f"{player_name}_{address[1]}"
                    
                players[player_name] = client_socket
                game_state["players"][player_name] = "connected"
                moves[player_name] = None

                broadcast(f"Player {player_name} has joined the game.", client_socket)
                
                if len(players) == 2:
                    game_state["status"] = "ready"
                    broadcast("Both players have joined. The game can now start!", None)
                else:
                    game_state["status"] = "waiting for players"
                    broadcast("Waiting for Player 2 to join...", None)
                
                broadcast_game_state()

            elif message["type"] == 'move':
                move = message['move']
                moves[player_name] = move  
                game_state["moves"][player_name] = move
                print(f"Received move from {player_name}: {move}")
                
                if len(moves) == 2 and all(moves.values()):
                    player1, player2 = list(moves.keys())
                    move1, move2 = moves[player1], moves[player2]

                    broadcast(f"{player1} chose {move1}. {player2} chose {move2}.")
                    
                    # Reset moves in game state
                    moves[player1], moves[player2] = None, None
                    game_state["moves"] = {}
                
                broadcast_game_state()

            elif message["type"] == 'chat':
                chat_message = f"Player {player_name}: {message['message']}"
                broadcast(chat_message, client_socket)
                
            elif message["type"] == 'quit':
                if player_name in players:
                    players.pop(player_name, None)
                    moves.pop(player_name, None)
                    game_state["players"].pop(player_name, None)
                    broadcast(f"Player {player_name} has left the game.", client_socket)
                    game_state["status"] = "waiting for players"
                broadcast_game_state()
                break

            client_socket.send(json.dumps({"type": "ack", "message": "Message received"}).encode("utf-8"))
        except ConnectionResetError:
            print(f"[ERROR] Connection lost with {address}")
            break

    clients.remove(client_socket)
    client_socket.close()
    print(f"[DISCONNECT] {address} disconnected.")
    if player_name in players:
        players.pop(player_name, None)
        moves.pop(player_name, None)
        game_state["players"].pop(player_name, None)
        broadcast(f"Player {player_name} has disconnected.")
        game_state["status"] = "waiting for players"
    broadcast_game_state()

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

        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    port = int(input("Enter the port number for the server: "))
    start_server(port)
