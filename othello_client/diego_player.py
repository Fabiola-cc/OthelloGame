import copy
import random


DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

OPENING_MOVES = [(2, 3), (3, 2), (4, 5), (5, 4)]

def decide_move2(board, my_symbol):
    if is_initial_board(board):
        valid_opening = [move for move in OPENING_MOVES if is_valid_move(board, move[0], move[1], my_symbol)]
        if valid_opening:
            return random.choice(valid_opening)
    
    _, best_move = minimax(board, depth=3, maximizing_player=True, my_symbol=my_symbol, alpha=float('-inf'), beta=float('inf'))
    
    if best_move is None:
        valid_moves = get_valid_moves(board, my_symbol)
        if valid_moves:
            return valid_moves[0]  
        else:
            return None 
    
    return best_move

def minimax(board, depth, maximizing_player, my_symbol, alpha, beta):
    opponent = -my_symbol

    if depth == 0 or game_over(board):
        return evaluate_board(board, my_symbol), None

    valid_moves = get_valid_moves(board, my_symbol if maximizing_player else opponent)
    if not valid_moves:
        return evaluate_board(board, my_symbol), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = apply_move(board, move, my_symbol)
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
            new_board = apply_move(board, move, opponent)
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
    my_score = 0
    opp_score = 0

    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    corner_score = 0
    for r, c in corners:
        if board[r][c] == my_symbol:
            corner_score += 25
        elif board[r][c] == opponent:
            corner_score -= 25

    my_moves = get_valid_moves(board, my_symbol)
    opp_moves = get_valid_moves(board, opponent)
    mobility_score = len(my_moves) - len(opp_moves)

    for row in board:
        for cell in row:
            if cell == my_symbol:
                my_score += 1
            elif cell == opponent:
                opp_score += 1

    total_score = (my_score - opp_score) + corner_score + (2 * mobility_score)
    return total_score

def get_valid_moves(board, symbol):
    valid_moves = []
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, r, c, symbol):
                valid_moves.append((r, c))
    return valid_moves

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
                else:
                    break
            else:
                break
            r += dr
            c += dc
    return False

def apply_move(board, move, symbol):
    new_board = copy.deepcopy(board)
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
    count = sum(cell != 0 for row in board for cell in row)
    return count <= 4  


def game_over(board):
    return not (get_valid_moves(board, 1) or get_valid_moves(board, -1))
