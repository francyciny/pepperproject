from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import requests
import time  

app = Flask(__name__)
CORS(app)

PEPPER_API_URL = "http://127.0.0.1:5001"  # To change when using real robot!!

# Tic-Tac-Toe Board
board = ["" for _ in range(9)]
current_player = "X"

def check_winner():
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]
    if "" not in board:
        return "draw"
    return None

def get_best_move():
    available_moves = [i for i, v in enumerate(board) if v == ""]
    if not available_moves:
        return None
    if random.random() < 0.8:
        for move in available_moves:
            board[move] = "O"
            if check_winner() == "O":
                board[move] = ""
                return move
            board[move] = ""
        for move in available_moves:
            board[move] = "X"
            if check_winner() == "X":
                board[move] = ""
                return move
            board[move] = ""
    return random.choice(available_moves)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Tic-Tac-Toe API is running!"})

@app.route("/start_game", methods=["POST"])
def start_game():
    global board, current_player
    board = ["" for _ in range(9)]
    current_player = random.choice(["X", "O"])

    # Tell Pepper to announce the first player
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "The first player is {}".format(current_player)})

    # Announce the turn for the first player
    requests.post(f"{PEPPER_API_URL}/announce_turn", json={"player": current_player})

    return jsonify({"message": "Game started", "first_player": current_player})

@app.route("/update_board", methods=["POST"])
def update_board():
    global current_player
    data = request.get_json()
    index = data.get("index")
    
    if index is None or not (0 <= index < 9):
        return jsonify({"message": "Invalid move: Out of range"}), 400

    if board[index] != "":
        return jsonify({"message": "Invalid move: Spot taken"}), 400

    board[index] = "X"  # Human moves
    winner = check_winner()
    if winner:
        requests.post(f"{PEPPER_API_URL}/announce_winner", json={"winner": winner})
        time.sleep(3)
        requests.post(f"{PEPPER_API_URL}/resting_position", json={"winner": winner})
        return jsonify({"message": "Game over", "winner": winner, "board": board})

    current_player = "O"
    
    # Announce Pepper's turn before it plays
    requests.post(f"{PEPPER_API_URL}/announce_turn", json={"player": current_player})

    return jsonify({"message": "Move registered", "board": board})

@app.route("/get_robot_move", methods=["GET"])
def get_robot_move():
    global current_player
    if current_player == "O":
        # Introduce a delay before pepper moves to make it more natural
        time.sleep(2)

        move = get_best_move()
        if move is not None:
            board[move] = "O"
            winner = check_winner()
            if winner:
                requests.post(f"{PEPPER_API_URL}/announce_winner", json={"winner": winner})
                time.sleep(3)
                requests.post(f"{PEPPER_API_URL}/resting_position", json={"winner": winner})
                return jsonify({"message": "Game over", "winner": winner, "board": board})
            
            current_player = "X"

            # Make Pepper say a random comment, i have to maybe change this later
            comments = ["Nice move!", "You're a tough opponent!", "That was smart!", "Hmm... tricky!"]
            requests.post(f"{PEPPER_API_URL}/speak", json={"text": random.choice(comments)})

            # Announce the human's turn after Pepper moves
            requests.post(f"{PEPPER_API_URL}/announce_turn", json={"player": current_player})

            return jsonify({"message": "Robot moved", "move": move, "board": board})
    
    return jsonify({"message": "Not robot's turn"})

# Social interaction routes 
@app.route("/get_yes_no", methods=["GET"])
def get_yes_no():
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Do you want to play a game? Press yes or no."})  
    return jsonify({"answer": "Robot has asked to play."})  

@app.route("/greet_user", methods=["GET"])
def greet_user():
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Hello! I am Pepper, your friendly robot. I'm here to play Tic-Tac-Toe with you."})
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "What's your name? Type it in my tablet."})
    return jsonify({"message": "Robot has greeted the user."})

@app.route("/play_again", methods=["GET"])
def play_again():
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Do you want to play again? If yes press rematch, if no press quit."})
    return jsonify({"answer": "Robot has asked to play again."})

@app.route("/get_username", methods=["POST"])
def get_username():
    data = request.get_json()
    username = data.get("name")
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": f"Nice to meet you, {username}!"})
    return jsonify({"message": "Username received", "username": username})

@app.route("/game_response", methods=["POST"])
def game_response():
    data = request.get_json()
    response = data.get("response")
    if response == "yes":
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Great! Let's play!"})
    else:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Alright! Press the button when you want to play!"})
    return jsonify({"message": "Response received"})

@app.route("/restart_game", methods=["POST"])
def restart_game():
    data = request.get_json()
    input = data.get("input")
    if input == "rematch":
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Great! It's a rematch"})
    else:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Alright! See you next time"})
    return jsonify({"message": "Game restarted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
