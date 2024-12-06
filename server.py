import socket
import threading
import json
import argparse

clients = []
players = {}
moves = {}
game_state = {"players": {}, "moves": {}, "status": "waiting for players"}

# Helper function to send messages with newline termination
def send_message(client, message):
    try:
        client.send((message + "\n").encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Could not send message: {e}")
        client.close()
        if client in clients:
            clients.remove(client)

# Broadcast the updated game state to all clients
def broadcast_game_state():
    game_state_message = json.dumps({"type": "game_state", "state": game_state})
    for client in clients:
        send_message(client, game_state_message)

# Broadcast a message to all clients except the sender
def broadcast(message, sender_socket=None):
    formatted_message = json.dumps({"type": "info", "message": message})
    for client in clients:
        if client != sender_socket:
            send_message(client, formatted_message)

# Handle each client connection
def safe_receive(client_socket):
    try:
        return client_socket.recv(1024).decode("utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to receive data: {e}")
        return None

def safe_send(client_socket, message):
    try:
        client_socket.send(message.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")
        if client_socket in clients:
            clients.remove(client_socket)


def handle_client(client_socket, address):
    global players, game_state
    player_name = None
    print(f"[NEW CONNECTION] {address} connected.")
    clients.append(client_socket)

    # Send current game state and players' information to the newly connected client
    try:
        if players:
            for existing_player in players.keys():
                send_message(client_socket, json.dumps({"type": "info", "message": f"Player {existing_player} has joined the game."}))
        if len(players) < 2:
            send_message(client_socket, json.dumps({"type": "info", "message": "Waiting for Player 2 to join..."}))
        elif len(players) == 2:
            send_message(client_socket, json.dumps({"type": "info", "message": "Both players have joined. The game can now start!"}))
        broadcast_game_state()
    except Exception as e:
        print(f"[ERROR] Failed to initialize connection for {address}: {e}")
        client_socket.close()
        clients.remove(client_socket)
        return

    while True:
        try:
            message = safe_receive(client_socket)
            if not message:
                print(f"[DISCONNECT] {address} connection closed.")
                break

            message = json.loads(message)

            if message["type"] == "join":
                player_name = message["player_name"]
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

            elif message["type"] == "move":
                move = message["move"]
                if move not in ["rock", "paper", "scissors"]:
                    safe_send(client_socket, json.dumps({"type": "error", "message": "Invalid move. Choose rock, paper, or scissors."}))
                    continue

                moves[player_name] = move
                game_state["moves"][player_name] = move
                print(f"Received move from {player_name}: {move}")

                if len(moves) == 2 and all(moves.values()):
                    player1, player2 = list(moves.keys())
                    move1, move2 = moves[player1], moves[player2]

                    # Determine winner
                    rules = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
                    if move1 == move2:
                        result = "Draw!"
                    elif rules[move1] == move2:
                        result = f"{player1} wins!"
                    else:
                        result = f"{player2} wins!"

                    broadcast(f"{player1} chose {move1}. {player2} chose {move2}. Result: {result}")
                    print(f"{player1} chose {move1}. {player2} chose {move2}. Result: {result}")

                    # Update game state
                    game_state["result"] = result
                    game_state["status"] = "Game Over"
                    moves[player1], moves[player2] = None, None
                    game_state["moves"] = {}

                broadcast_game_state()

            elif message["type"] == "chat":
                chat_message = f"Player {player_name}: {message['message']}"
                broadcast(chat_message, client_socket)

            elif message["type"] == "quit":
                if player_name in players:
                    players.pop(player_name, None)
                    moves.pop(player_name, None)
                    game_state["players"].pop(player_name, None)
                    broadcast(f"Player {player_name} has left the game.", client_socket)
                    game_state["status"] = "waiting for players"
                broadcast_game_state()
                break

            safe_send(client_socket, json.dumps({"type": "ack", "message": "Message received"}))
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON message from {address}.")
            safe_send(client_socket, json.dumps({"type": "error", "message": "Invalid message format."}))
        except Exception as e:
            print(f"[ERROR] Unexpected error with {address}: {e}")
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


# Start the server
def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {ip}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rock Paper Scissors Server")
    parser.add_argument("-p", "--port", required=True, type=int, help="Server Port")
    args = parser.parse_args()

    start_server("0.0.0.0", args.port)
