import socket
import json
import threading

def receive_messages(client_socket):
    buffer = ""
    while True:
        try:
            response = client_socket.recv(1024).decode("utf-8")
            if not response:
                print("[SERVER] Connection closed.")
                break
            
            buffer += response
            # Process each complete message in buffer
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                response_data = json.loads(message)
                
                if response_data["type"] == "info":
                    print(f"[SERVER] {response_data['message']}")
                elif response_data["type"] == "game_state":
                    game_state = response_data["state"]
                    print(f"[GAME STATE] {json.dumps(game_state, indent=2)}")
        except json.JSONDecodeError:
            print("[ERROR] Could not decode message from server.")
        except Exception as e:
            print(f"[ERROR] Failed to receive message from the server: {e}")
            break

def start_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("[CONNECTED] Connected to the server.")
        
        player_name = input("Enter your player name: ")
        join_message = json.dumps({"type": "join", "player_name": player_name})
        client_socket.send(join_message.encode("utf-8"))
        
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            action = input("Enter 'move', 'chat', or 'quit': ").strip().lower()
            
            if action == "move":
                move = input("Enter move (rock, paper, or scissors): ").strip().lower()
                message = json.dumps({"type": "move", "move": move})
            elif action == "chat":
                chat_message = input("Enter chat message: ")
                message = json.dumps({"type": "chat", "message": chat_message})
            elif action == "quit":
                message = json.dumps({"type": "quit"})
                client_socket.send(message.encode("utf-8"))
                break
            else:
                print("[ERROR] Invalid action. Please enter 'move, 'chat', or 'quit'.")
                continue
            
            client_socket.send(message.encode("utf-8"))

    except ConnectionRefusedError:
        print("[ERROR] Connection failed. Is the server running?")
    finally:
        client_socket.close()
        print("[DISCONNECTED] Disconnected from server.")

if __name__ == "__main__":
    server_ip = input("Enter the server IP address (default is 127.0.0.1): ") or "127.0.0.1"
    port = int(input("Enter the port number to connect to: "))
    start_client(server_ip, port)
