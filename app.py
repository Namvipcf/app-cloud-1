from flask import Flask, render_template, request, session, jsonify
from google.cloud import datastore
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key_here'
Session(app)

client = datastore.Client()

def check_for_win(player, board):
    # Kiểm tra các hàng
    for i in range(0, 3):
        if board[1 + i * 3] == board[2 + i * 3] == board[3 + i * 3] == player:
            return True

    # Kiểm tra các cột
    for i in range(0, 3):
        if board[1 + i] == board[4 + i] == board[7 + i] == player:
            return True

    # Kiểm tra đường chéo
    if board[1] == board[5] == board[9] == player:
        return True
    if board[3] == board[5] == board[7] == player:
        return True

    return False

def check_for_draw(board):
    for i in board.keys():
        if board[i] == " ":
            return False
    return True

def play_computer(board):
    best_score = -10
    best_move = 0

    for key in board.keys():
        if board[key] == " ":
            board[key] = "O"
            score = minimax(board, False)  # Sử dụng thuật toán minimax
            board[key] = " "
            if score > best_score:
                best_score = score
                best_move = key

    board[best_move] = "O"

def minimax(board, is_maximizing):
    if check_for_win("O", board):
        return 1

    if check_for_win("X", board):
        return -1

    if check_for_draw(board):
        return 0

    if is_maximizing:
        best_score = -1
        for key in board.keys():
            if board[key] == " ":
                board[key] = "O"
                score = minimax(board, False)
                board[key] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = 1
        for key in board.keys():
            if board[key] == " ":
                board[key] = "X"
                score = minimax(board, True)
                board[key] = " "
                best_score = min(score, best_score)
        return best_score

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play():
    cell = int(request.form["cell"])
    board = session.get('board', {1: " ", 2: " ", 3: " ", 4: " ", 5: " ", 6: " ", 7: " ", 8: " ", 9: " "})
    turn = session.get('turn', 'X')
    mode = session.get('mode', 'multiPlayer')
    game_end = session.get('game_end', False)

    if board[cell] == " " and not game_end:
        board[cell] = turn

        if check_for_win(turn, board):
            result = f"{turn} wins the game!"
            game_end = True
        elif check_for_draw(board):
            result = "Game Draw!"
            game_end = True
        else:
            result = None

        if mode == "multiPlayer":
            turn = "O" if turn == "X" else "X"
        else:
            play_computer(board)
            if check_for_win("O", board):
                result = "Computer wins the game!"
                game_end = True
            elif check_for_draw(board):
                result = "Game Draw!"
                game_end = True

            turn = "X"

        session['board'] = board
        session['turn'] = turn
        session['game_end'] = game_end

        return jsonify({"result": result, "board": board, "game_end": game_end})

@app.route("/restart", methods=["POST"])
def restart():
    session['board'] = {1: " ", 2: " ", 3: " ", 4: " ", 5: " ", 6: " ", 7: " ", 8: " ", 9: " "}
    session['turn'] = 'X'
    session['game_end'] = False
    return jsonify({"board": session['board'], "turn": session['turn'], "game_end": session['game_end']})

@app.route("/mode", methods=["POST"])
def change_mode():
    session['mode'] = request.form["mode"]
    return jsonify({"mode": session['mode']})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
