from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import requests
import time  

app = Flask(__name__)
CORS(app)

PEPPER_API_URL = "http://127.0.0.1:5001"  

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
                return [move, available_moves]
            board[move] = ""
        for move in available_moves:
            board[move] = "X"
            if check_winner() == "X":
                board[move] = ""
                return [move, available_moves]
            board[move] = ""
    return [random.choice(available_moves), available_moves]

def get_optimal_human_moves():
    available_moves = [i for i, v in enumerate(board) if v == ""]
    if not available_moves:
        return set()

    optimal_moves = set()

    # First: check all moves that let the human win immediately
    for move in available_moves:
        board[move] = "X"
        if check_winner() == "X":
            optimal_moves.add(move)
        board[move] = ""

    if optimal_moves:
        return optimal_moves

    # Second: check all moves that block the robot from winning
    for move in available_moves:
        board[move] = "O"
        if check_winner() == "O":
            optimal_moves.add(move)
        board[move] = ""

    # If nothing urgent, all remaining are equally fine
    return optimal_moves if optimal_moves else set(available_moves)

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
    index = data.get("indice")

    if index is None or not (0 <= index < 9):
        return jsonify({"message": "Invalid move: Out of range"}), 400

    if board[index] != "":
        return jsonify({"message": "Invalid move: Spot taken"}), 400

    # Get optimal human moves based on current board
    optimal_moves = get_optimal_human_moves()
    is_optimal = index in optimal_moves

    # Apply the move
    board[index] = "X"
    winner = check_winner()
    if winner:
        return jsonify({
            "message": "Game over",
            "winner": winner,
            "board": board
        })

    current_player = "O"

    return jsonify({"message": "Move registered", "board": board, "optimal": is_optimal})

@app.route("/get_optimality_comment", methods=["POST"])
def get_optimality_comment():
    data = request.get_json()
    is_optimal = data.get("optimal")

    # Speak based on optimality
    if is_optimal:
        comment = random.choice([
            "Nice move!",
            "That was the best you could do.",
            "Good call.",
            "You're making sharp choices!"
        ])
    else:
        comment = random.choice([
            "Interesting choice... not optimal though.",
            "I would have gone somewhere else.",
            "You left an opening there.",
            "Hmm, not the best move."
        ])

    requests.post(f"{PEPPER_API_URL}/speak", json={"text": comment})

    return jsonify({"message": "Optimality comment made", "comment": comment})

@app.route("/get_robot_move", methods=["GET"])
def get_robot_move():
    global current_player
    if current_player == "O":

        if len(get_best_move()[1]) > 1:
            times = [0.2, 1, 2]
            time.sleep(random.choice(times))  # Simulate thinking time

        move = get_best_move()[0]
        if move is not None:
            board[move] = "O"
            winner = check_winner()
            if winner:
                return jsonify({"message": "Game over", "winner": winner, "board": board})

            current_player = "X"

            return jsonify({"message": "Robot moved", "move": move, "board": board})
    
    return jsonify({"message": "Not robot's turn"})

# Social interaction routes 
@app.route("/get_yes_no", methods=["GET"])
def get_yes_no():
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Do you want to play a game? Press yes or no."})  
    return jsonify({"answer": "Robot has asked to play."})  

@app.route("/greet_user", methods=["GET"])
def greet_user():
    try:
        print("aooo")
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Hello! I am Pepper, your friendly robot. I'm here to play Tic-Tac-Toe with you."})
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "What's your name? Type it in my tablet."})
    except:
        print("Error communicating with Pepper API")
        
    
    return jsonify({"message": "Robot has greeted the user."})

'''
@app.route("/play_again", methods=["GET"])
def play_again():
    requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Do you want to play again? If yes press rematch, if no press quit."})
    return jsonify({"answer": "Robot has asked to play again."})
'''

@app.route("/get_username", methods=["POST"])
def get_username():
    data = request.get_json()
    username = data.get("name", "").strip()

    # Validation: non-empty, reasonable length, only letters
    if not username:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": f"You must enter a name."})
        return jsonify({"error": "Name cannot be empty."}), 400
    if not username.isalpha():
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": f"Your name must contain only letters."})
        return jsonify({"error": "Name must contain only letters."}), 400
    if len(username) > 20:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": f"Your name must be less than 20 characters."})
        return jsonify({"error": "Name is too long (max 20 characters)."}), 400

    # Check UTF-8 compatibility
    try:
        username.encode("utf-8")
    except UnicodeEncodeError:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": f"Your name contains invalid characters."})
        return jsonify({"error": "Invalid characters in name."}), 400 

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
    elif input == "pause":
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Ok! I'll be here if you want to play again soon. If not just press quit"})
    else:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Alright! See you next time"})
    return jsonify({"message": "Game restarted"})

@app.route("/announce_turn", methods=["POST"])
def announce_turn():
    data = request.get_json()
    player = data.get("player")
    if player == "X":
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "It's your turn!"}) #change to make random
    else:
        requests.post(f"{PEPPER_API_URL}/speak", json={"text": "Let me think..."}) #change to make random
    return jsonify({"message": "Turn announced", "player": player})

@app.route("/announce_winner", methods=["POST"])
def announce_winner():
    data = request.get_json()
    winner = data.get("winner")

    requests.post(f"{PEPPER_API_URL}/announce_winner", json={"winner": winner})
    requests.post(f"{PEPPER_API_URL}/resting_position", json={"winner": winner})

    return jsonify({"message": "Winner announced", "winner": winner})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
