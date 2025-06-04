import random
import time

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

OPENING_MOVES = [(2, 3), (3, 2), (4, 5), (5, 4)]

POSITION_WEIGHTS = [
    [ 4, -3,  2,  2,  2,  2, -3,  4],
    [-3, -4, -1, -1, -1, -1, -4, -3],
    [ 2, -1,  1,  0,  0,  1, -1,  2],
    [ 2, -1,  0,  1,  1,  0, -1,  2],
    [ 2, -1,  0,  1,  1,  0, -1,  2],
    [ 2, -1,  1,  0,  0,  1, -1,  2],
    [-3, -4, -1, -1, -1, -1, -4, -3],
    [ 4, -3,  2,  2,  2,  2, -3,  4]
]

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]

def decide_move2(board, my_symbol):
    start = time.time()

    count = sum(cell != 0 for row in board for cell in row)
    depth = 3
    if count >= 54:
        depth = 5
    elif count >= 36:
        depth = 4

    if is_initial_board(board):
        valid_opening = [move for move in OPENING_MOVES if is_valid_move(board, move[0], move[1], my_symbol)]
        if valid_opening:
            return random.choice(valid_opening)

    _, best_move = minimax(board, depth, True, my_symbol, float('-inf'), float('inf'))

    if best_move is None:
        valid_moves = get_valid_moves(board, my_symbol)
        if valid_moves:
            return valid_moves[0]
        else:
            return None

    elapsed = time.time() - start
    print(f"⏱️ Tiempo de decisión: {elapsed:.3f} segundos")
    return best_move

def minimax(board, depth, maximizing_player, my_symbol, alpha, beta):
    opponent = -my_symbol

    if depth == 0 or game_over(board):
        return evaluate_board(board, my_symbol), None

    current_player = my_symbol if maximizing_player else opponent
    valid_moves = get_valid_moves(board, current_player)
    if not valid_moves:
        return evaluate_board(board, my_symbol), None

    valid_moves.sort(key=lambda m: POSITION_WEIGHTS[m[0]][m[1]], reverse=maximizing_player)

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = apply_move(board, move, current_player)
            eval, _ = minimax(new_board, depth - 1, False, my_symbol, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = apply_move(board, move, current_player)
            eval, _ = minimax(new_board, depth - 1, True, my_symbol, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def evaluate_board(board, my_symbol):
    opponent = -my_symbol
    position_score = 0
    corner_score = 0
    mobility_score = 0

    for r in range(8):
        for c in range(8):
            if board[r][c] == my_symbol:
                position_score += POSITION_WEIGHTS[r][c]
            elif board[r][c] == opponent:
                position_score -= POSITION_WEIGHTS[r][c]

    for r, c in CORNERS:
        if board[r][c] == my_symbol:
            corner_score += 25
        elif board[r][c] == opponent:
            corner_score -= 25

    my_moves = get_valid_moves(board, my_symbol)
    opp_moves = get_valid_moves(board, opponent)
    mobility_score = len(my_moves) - len(opp_moves)

    return position_score + (3 * corner_score) + (2 * mobility_score)

def get_valid_moves(board, symbol):
    return [(r, c) for r in range(8) for c in range(8) if is_valid_move(board, r, c, symbol)]

def is_valid_move(board, row, col, symbol):
    if board[row][col] != 0:
        return False
    opponent = -symbol
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        found_opponent = False
        while 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] == opponent:
                found_opponent = True
            elif board[r][c] == symbol:
                if found_opponent:
                    return True
                break
            else:
                break
            r += dr
            c += dc
    return False

def apply_move(board, move, symbol):
    # Copia superficial rápida
    new_board = [row[:] for row in board]
    r, c = move
    new_board[r][c] = symbol
    opponent = -symbol

    for dr, dc in DIRECTIONS:
        to_flip = []
        rr, cc = r + dr, c + dc
        while 0 <= rr < 8 and 0 <= cc < 8:
            if new_board[rr][cc] == opponent:
                to_flip.append((rr, cc))
            elif new_board[rr][cc] == symbol:
                for fr, fc in to_flip:
                    new_board[fr][fc] = symbol
                break
            else:
                break
            rr += dr
            cc += dc
    return new_board

def is_initial_board(board):
    return sum(cell != 0 for row in board for cell in row) <= 4

def game_over(board):
    return not (get_valid_moves(board, 1) or get_valid_moves(board, -1))