from machine import Pin, I2C
import ssd1306
import time
import random
import math

# =========================
# OLED SETUP
# =========================
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

W = 128
H = 64

# =========================
# GAME SETTINGS
# =========================
GRID_SIZE = 60
OFFSET_X = 34
OFFSET_Y = 2
CELL = GRID_SIZE // 3  # 20

board = [["", "", ""], ["", "", ""], ["", "", ""]]
current = "X"

mode = "PVP"        # PVP or ROBOT
difficulty = "EASY" # EASY, MEDIUM, HARD
player1 = "P1"
player2 = "P2"
human_name = "HUMAN"

# =========================
# BASIC DISPLAY HELPERS
# =========================
def clear():
    oled.fill(0)

def show():
    oled.show()

def center_x(text):
    return max(0, (W - len(text) * 8) // 2)

def draw_text_line(text, y):
    oled.text(text, center_x(text), y)

def show_message(lines, pause=0.0):
    clear()
    y = 0
    for line in lines:
        if line is None:
            y += 10
        else:
            draw_text_line(line, y)
            y += 10
    show()
    if pause > 0:
        time.sleep(pause)

def splash():
    show_message([
        "TIC TAC TOE",
        "",
        "Starting..."
    ], pause=1.2)

def ask_serial(prompt_text, display_lines):
    show_message(display_lines)
    return input(prompt_text).strip()

# =========================
# MENU
# =========================
def choose_mode():
    global mode
    while True:
        choice = ask_serial(
            "Choose mode (1=PvP, 2=Robot): ",
            ["TIC TAC TOE", "", "1  PVP", "2  ROBOT"]
        )
        if choice == "1":
            mode = "PVP"
            return
        if choice == "2":
            mode = "ROBOT"
            return

def choose_names():
    global player1, player2, human_name

    if mode == "PVP":
        p1 = ask_serial("Player 1 name: ", ["PVP MODE", "", "Enter P1 name"])
        p2 = ask_serial("Player 2 name: ", ["PVP MODE", "", "Enter P2 name"])
        player1 = p1[:10] if p1 else "P1"
        player2 = p2[:10] if p2 else "P2"
    else:
        hn = ask_serial("Human name: ", ["ROBOT MODE", "", "Enter human name"])
        human_name = hn[:10] if hn else "HUMAN"

def choose_difficulty():
    global difficulty
    if mode != "ROBOT":
        return

    while True:
        choice = ask_serial(
            "Choose difficulty (1=Easy, 2=Medium, 3=Hard): ",
            ["ROBOT LEVEL", "1 EASY", "2 MED", "3 HARD"]
        )
        if choice == "1":
            difficulty = "EASY"
            return
        if choice == "2":
            difficulty = "MEDIUM"
            return
        if choice == "3":
            difficulty = "HARD"
            return

# =========================
# BOARD / DRAWING
# =========================
def draw_grid():
    clear()
    oled.rect(OFFSET_X, OFFSET_Y, GRID_SIZE, GRID_SIZE, 1)

    for i in range(1, 3):
        x = OFFSET_X + i * CELL
        oled.line(x, OFFSET_Y, x, OFFSET_Y + GRID_SIZE, 1)

    for i in range(1, 3):
        y = OFFSET_Y + i * CELL
        oled.line(OFFSET_X, y, OFFSET_X + GRID_SIZE, y, 1)

    show()

def cell_origin(r, c):
    return OFFSET_X + c * CELL, OFFSET_Y + r * CELL

# =========================
# X DRAWING
# =========================
def draw_x(r, c):
    x, y = cell_origin(r, c)

    for i in range(0, CELL - 6, 2):
        oled.line(x + 3, y + 3, x + 3 + i, y + 3 + i, 1)
        show()
        time.sleep(0.01)

    for i in range(0, CELL - 6, 2):
        oled.line(x + CELL - 3, y + 3, x + CELL - 3 - i, y + 3 + i, 1)
        show()
        time.sleep(0.01)

# =========================
# O DRAWING
# =========================
def plot_circle_points(cx, cy, x, y):
    pts = [
        (cx + x, cy + y),
        (cx - x, cy + y),
        (cx + x, cy - y),
        (cx - x, cy - y),
        (cx + y, cy + x),
        (cx - y, cy + x),
        (cx + y, cy - x),
        (cx - y, cy - x),
    ]
    for px, py in pts:
        if 0 <= px < W and 0 <= py < H:
            oled.pixel(px, py, 1)

def draw_circle(cx, cy, radius):
    x = radius
    y = 0
    err = 0

    while x >= y:
        plot_circle_points(cx, cy, x, y)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1

def draw_o(r, c):
    x, y = cell_origin(r, c)
    cx = x + CELL // 2
    cy = y + CELL // 2

    for radius in range(1, 8):
        draw_circle(cx, cy, radius)
        show()
        time.sleep(0.01)

# =========================
# GAME LOGIC
# =========================
def check_winner(b):
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != "":
            return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] != "":
            return b[0][i]

    if b[0][0] == b[1][1] == b[2][2] != "":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != "":
        return b[0][2]

    return None

def is_full(b):
    for r in range(3):
        for c in range(3):
            if b[r][c] == "":
                return False
    return True

def reset_game():
    global board, current
    board = [["", "", ""], ["", "", ""], ["", "", ""]]
    current = "X"
    draw_grid()

def winner_name(symbol):
    if mode == "PVP":
        return player1 if symbol == "X" else player2
    return human_name if symbol == "X" else "ROBOT"

# =========================
# ROBOT AI
# =========================
def available_moves(b):
    moves = []
    for r in range(3):
        for c in range(3):
            if b[r][c] == "":
                moves.append((r, c))
    return moves

def robot_easy():
    moves = available_moves(board)
    return random.choice(moves) if moves else None

def robot_medium():
    for r, c in available_moves(board):
        board[r][c] = "O"
        if check_winner(board) == "O":
            board[r][c] = ""
            return (r, c)
        board[r][c] = ""

    for r, c in available_moves(board):
        board[r][c] = "X"
        if check_winner(board) == "X":
            board[r][c] = ""
            return (r, c)
        board[r][c] = ""

    return robot_easy()

def minimax(b, depth, maximizing):
    win = check_winner(b)

    if win == "O":
        return 10 - depth
    if win == "X":
        return depth - 10
    if is_full(b):
        return 0

    if maximizing:
        best = -999
        for r, c in available_moves(b):
            b[r][c] = "O"
            score = minimax(b, depth + 1, False)
            b[r][c] = ""
            if score > best:
                best = score
        return best
    else:
        best = 999
        for r, c in available_moves(b):
            b[r][c] = "X"
            score = minimax(b, depth + 1, True)
            b[r][c] = ""
            if score < best:
                best = score
        return best

def robot_hard():
    best_score = -999
    best_move = None

    for r, c in available_moves(board):
        board[r][c] = "O"
        score = minimax(board, 0, False)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            best_move = (r, c)

    return best_move

def robot_move():
    if difficulty == "EASY":
        return robot_easy()
    if difficulty == "MEDIUM":
        return robot_medium()
    return robot_hard()

# =========================
# ANIMATIONS
# =========================
def win_animation(name):
    for _ in range(3):
        show_message([name, "WINS!"], pause=0.3)
        clear()
        show()
        time.sleep(0.15)
    show_message([name, "WINS!"], pause=0.9)

def draw_animation():
    for _ in range(2):
        show_message(["DRAW!", "", "Nice game"], pause=0.6)
        clear()
        show()
        time.sleep(0.15)
    show_message(["DRAW!", "", "Nice game"], pause=1.0)

# =========================
# MOVE INPUT
# =========================
def ask_move():
    while True:
        try:
            r = int(input("Row (0-2): ").strip())
            c = int(input("Col (0-2): ").strip())
        except:
            print("Invalid input. Enter numbers 0 to 2.")
            continue

        if 0 <= r <= 2 and 0 <= c <= 2:
            return r, c

        print("Out of range. Enter 0 to 2.")

# =========================
# MAIN ROUND
# =========================
def play_round():
    global current

    reset_game()

    while True:
        if mode == "PVP":
            who = player1 if current == "X" else player2
            print(f"\n{who}'s turn ({current})")
            r, c = ask_move()
        else:
            if current == "X":
                print(f"\n{human_name}'s turn (X)")
                r, c = ask_move()
            else:
                print("\nRobot is thinking...")
                move = robot_move()
                if move is None:
                    draw_animation()
                    reset_game()
                    return
                r, c = move
                print(f"Robot chose: row={r}, col={c}")

        if board[r][c] != "":
            print("Cell already filled. Try again.")
            continue

        board[r][c] = current

        if current == "X":
            draw_x(r, c)
        else:
            draw_o(r, c)

        win = check_winner(board)
        if win:
            win_animation(winner_name(win))
            reset_game()
            return

        if is_full(board):
            draw_animation()
            reset_game()
            return

        current = "O" if current == "X" else "X"

        if mode == "ROBOT" and current == "O":
            print("\nRobot is thinking...")
            move = robot_move()
            if move is None:
                draw_animation()
                reset_game()
                return

            rr, cc = move
            print(f"Robot chose: row={rr}, col={cc}")
            board[rr][cc] = "O"
            draw_o(rr, cc)

            win = check_winner(board)
            if win:
                win_animation("ROBOT")
                reset_game()
                return

            if is_full(board):
                draw_animation()
                reset_game()
                return

            current = "X"

# =========================
# STARTUP
# =========================
splash()
choose_mode()
choose_names()
choose_difficulty()
draw_grid()
play_round()
