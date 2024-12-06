import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox
import argparse

def receive_messages(client_socket):
    buffer = ""
    while True:
        try:
            response = client_socket.recv(1024).decode("utf-8")
            if not response:
                log_message("[SERVER] Connection closed.")
                break

            buffer += response
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                try:
                    response_data = json.loads(message)
                    if response_data["type"] == "info":
                        log_message(f"[SERVER] {response_data['message']}")
                    elif response_data["type"] == "game_state":
                        update_game_state(response_data["state"])
                except json.JSONDecodeError:
                    log_message(f"[ERROR] Could not decode message: {message}")
        except Exception as e:
            log_message(f"[ERROR] Failed to receive message: {e}")
            break

def log_message(message):
    if 'log_area' in globals() and log_area:
        log_area.insert(tk.END, f"{message}\n")
        log_area.see(tk.END)
    else:
        print(message)

def update_game_state(state):
    if "moves" in state and len(state["moves"]) == 2:
        player1, player2 = list(state["moves"].keys())
        move1, move2 = state["moves"][player1], state["moves"][player2]
        result = determine_winner(move1, move2)
        game_state_label.config(
            text=f"{player1} chose {move1}. {player2} chose {move2}. Result: {result}"
        )
        log_message(f"{player1} chose {move1}. {player2} chose {move2}. Result: {result}")
    else:
        log_message("Waiting for both players to make their moves.")

def determine_winner(move1, move2):
    rules = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock",
    }
    if move1 == move2:
        return "Draw!"
    elif rules[move1] == move2:
        return "You win!"
    else:
        return "You lose!"
    
def safe_send(client_socket, message):
    try:
        client_socket.send(message.encode("utf-8"))
    except Exception as e:
        log_message(f"[ERROR] Failed to send message: {e}")

def send_move():
    move = move_entry.get().strip().lower()
    if move not in ["rock", "paper", "scissors"]:
        messagebox.showerror("Invalid Move", "Move must be 'rock', 'paper', or 'scissors'.")
        return
    try:
        message = json.dumps({"type": "move", "move": move})
        safe_send(client_socket, message)
        move_entry.delete(0, tk.END)
        log_message(f"You chose: {move}. Waiting for the other player...")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send move: {e}")
        log_message(f"[ERROR] Failed to send move: {e}")

def send_chat_message():
    chat_message = chat_entry.get().strip()
    if not chat_message:
        messagebox.showerror("Invalid Message", "Chat message cannot be empty.")
        return
    try:
        message = json.dumps({"type": "chat", "message": chat_message})
        safe_send(client_socket, message)
        chat_entry.delete(0, tk.END)
        log_message(f"You: {chat_message}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send chat message: {e}")
        log_message(f"[ERROR] Failed to send chat message: {e}")

def start_client_ui(server_ip, server_port):
    global log_area, move_entry, game_state_label, client_socket, chat_entry

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))

        player_name = input("Enter your player name: ")
        join_message = json.dumps({"type": "join", "player_name": player_name})
        client_socket.send(join_message.encode("utf-8"))

        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        root = tk.Tk()
        root.title("Rock Paper Scissors Game")

        game_state_label = tk.Label(root, text="Game State: Waiting for other player...")
        game_state_label.pack()

        tk.Label(root, text="Enter your move (rock, paper, or scissors):").pack()
        move_entry = tk.Entry(root)
        move_entry.pack()

        tk.Button(root, text="Submit Move", command=send_move).pack()

        tk.Label(root, text="Game Log:").pack()
        log_area = tk.Text(root, height=15, state="normal")
        log_area.pack(fill=tk.BOTH, padx=10, pady=10)

        tk.Label(root, text="Chat:").pack()
        chat_entry = tk.Entry(root)
        chat_entry.pack()

        tk.Button(root, text="Send Chat", command=send_chat_message).pack()

        log_message("[CONNECTED] Connected to the server.")

        root.mainloop()

    except ConnectionRefusedError:
        print("[ERROR] Connection failed. Is the server running?")
    finally:
        client_socket.close()
        print("[DISCONNECTED] Disconnected from server.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rock Paper Scissors Client")
    parser.add_argument("-i", "--ip", required=True, help="Server IP or DNS")
    parser.add_argument("-p", "--port", required=True, type=int, help="Server Port")
    args = parser.parse_args()

    start_client_ui(args.ip, args.port)