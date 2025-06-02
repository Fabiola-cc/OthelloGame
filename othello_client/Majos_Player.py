import copy
import random


DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

OPENING_MOVES = [(2, 3), (3, 2), (4, 5), (5, 4)]

# Pesos estáticos mejorados para posiciones del tablero
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

# Esquinas del tablero
CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]

def decide_move_enhanced(board, my_symbol):
    """
    Función principal mejorada para decidir el siguiente movimiento
    """
    if is_initial_board(board):
        valid_opening = [move for move in OPENING_MOVES if is_valid_move(board, move[0], move[1], my_symbol)]
        if valid_opening:
            return random.choice(valid_opening)
    
    # Usar profundidad adaptativa basada en la fase del juego
    filled_squares = sum(1 for row in board for cell in row if cell != 0)
    if filled_squares > 50:  # Endgame
        depth = 6
    elif filled_squares > 30:  # Midgame
        depth = 4
    else:  # Early game
        depth = 3
    
    _, best_move = minimax_enhanced(board, depth=depth, maximizing_player=True, 
                                  my_symbol=my_symbol, alpha=float('-inf'), beta=float('inf'))
    
    if best_move is None:
        valid_moves = get_valid_moves(board, my_symbol)
        if valid_moves:
            return valid_moves[0]  
        else:
            return None 
    
    return best_move

def minimax_enhanced(board, depth, maximizing_player, my_symbol, alpha, beta):
    """
    Minimax mejorado con mejor función de evaluación
    """
    opponent = -my_symbol

    if depth == 0 or game_over(board):
        return evaluate_board_enhanced(board, my_symbol), None

    valid_moves = get_valid_moves(board, my_symbol if maximizing_player else opponent)
    if not valid_moves:
        return evaluate_board_enhanced(board, my_symbol), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = apply_move(board, move, my_symbol)
            eval, _ = minimax_enhanced(new_board, depth - 1, False, my_symbol, alpha, beta)
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
            eval, _ = minimax_enhanced(new_board, depth - 1, True, my_symbol, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def evaluate_board_enhanced(board, my_symbol):
    """
    Función de evaluación mejorada basada en el paper académico
    Incorpora: Stability, Corner Strategy, Mobility Avanzada, y Coin Parity
    """
    opponent = -my_symbol
    
    # Determinar fase del juego para pesos dinámicos
    filled_squares = sum(1 for row in board for cell in row if cell != 0)
    game_phase = get_game_phase(filled_squares)
    
    # Calcular cada heurística
    coin_parity_score = calculate_coin_parity(board, my_symbol, opponent)
    corner_score = calculate_corner_strategy(board, my_symbol, opponent)
    mobility_score = calculate_mobility_enhanced(board, my_symbol, opponent)
    stability_score = calculate_stability(board, my_symbol, opponent)
    
    # Pesos dinámicos basados en la fase del juego
    weights = get_dynamic_weights(game_phase, filled_squares)
    
    total_score = (
        weights['coin_parity'] * coin_parity_score +
        weights['corner'] * corner_score +
        weights['mobility'] * mobility_score +
        weights['stability'] * stability_score
    )
    
    return total_score

def get_game_phase(filled_squares):
    """Determina la fase del juego"""
    if filled_squares <= 20:
        return 'early'
    elif filled_squares <= 45:
        return 'mid'
    else:
        return 'late'

def get_dynamic_weights(game_phase, filled_squares):
    """
    Pesos dinámicos basados en el paper:
    - Early game: Stability y Mobility altos
    - Mid game: Corner y Stability altos
    - Late game: Coin parity alto (si podemos buscar hasta el final)
    """
    if game_phase == 'early':
        return {
            'coin_parity': 10,
            'corner': 25,
            'mobility': 20,
            'stability': 30
        }
    elif game_phase == 'mid':
        return {
            'coin_parity': 15,
            'corner': 35,
            'mobility': 15,
            'stability': 35
        }
    else:  # late game
        if filled_squares > 55:  # Muy cerca del final
            return {
                'coin_parity': 50,
                'corner': 20,
                'mobility': 10,
                'stability': 20
            }
        else:
            return {
                'coin_parity': 25,
                'corner': 30,
                'mobility': 15,
                'stability': 30
            }

def calculate_coin_parity(board, my_symbol, opponent):
    """Calcula la diferencia de fichas (normalizada)"""
    my_count = sum(row.count(my_symbol) for row in board)
    opp_count = sum(row.count(opponent) for row in board)
    
    total_pieces = my_count + opp_count
    if total_pieces == 0:
        return 0
    
    return 100 * (my_count - opp_count) / total_pieces

def calculate_corner_strategy(board, my_symbol, opponent):
    """
    Estrategia de esquinas mejorada:
    - Esquinas capturadas: +25 puntos
    - Esquinas potenciales: +10 puntos
    - Esquinas del oponente: -25 puntos
    """
    my_corners = 0
    opp_corners = 0
    potential_corners = 0
    
    for r, c in CORNERS:
        if board[r][c] == my_symbol:
            my_corners += 25
        elif board[r][c] == opponent:
            opp_corners += 25
        elif board[r][c] == 0:
            # Verificar si es una esquina potencial (podemos capturarla en el próximo movimiento)
            if is_valid_move(board, r, c, my_symbol):
                potential_corners += 10
            elif is_valid_move(board, r, c, opponent):
                potential_corners -= 5  # El oponente puede capturarla
    
    return my_corners - opp_corners + potential_corners

def calculate_mobility_enhanced(board, my_symbol, opponent):
    """
    Movilidad mejorada: actual + potencial
    """
    # Movilidad actual
    my_moves = len(get_valid_moves(board, my_symbol))
    opp_moves = len(get_valid_moves(board, opponent))
    
    actual_mobility = my_moves - opp_moves
    
    # Movilidad potencial: espacios vacíos adyacentes a fichas del oponente
    my_potential = calculate_potential_mobility(board, my_symbol, opponent)
    opp_potential = calculate_potential_mobility(board, opponent, my_symbol)
    
    potential_mobility = my_potential - opp_potential
    
    # Normalizar y combinar
    if my_moves + opp_moves > 0:
        actual_normalized = 100 * actual_mobility / (my_moves + opp_moves)
    else:
        actual_normalized = 0
    
    return actual_normalized + (potential_mobility * 0.5)

def calculate_potential_mobility(board, player, opponent):
    """Calcula espacios vacíos adyacentes a fichas del oponente"""
    potential_squares = set()
    
    for r in range(8):
        for c in range(8):
            if board[r][c] == opponent:
                # Verificar espacios adyacentes vacíos
                for dr, dc in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 0:
                        potential_squares.add((nr, nc))
    
    return len(potential_squares)

def calculate_stability(board, my_symbol, opponent):
    """
    Calcula la estabilidad de las fichas:
    - Stable: +3 puntos (no pueden ser flanqueadas nunca)
    - Semi-stable: +1 punto (podrían ser flanqueadas en el futuro)
    - Unstable: -1 punto (pueden ser flanqueadas inmediatamente)
    """
    my_stability = 0
    opp_stability = 0
    
    for r in range(8):
        for c in range(8):
            if board[r][c] == my_symbol:
                my_stability += get_piece_stability(board, r, c, my_symbol)
            elif board[r][c] == opponent:
                opp_stability += get_piece_stability(board, r, c, opponent)
    
    return my_stability - opp_stability

def get_piece_stability(board, row, col, player):
    """
    Determina la estabilidad de una ficha específica
    """
    # Las esquinas son siempre estables
    if (row, col) in CORNERS:
        return 3
    
    # Verificar si la ficha puede ser flanqueada
    can_be_flanked = False
    opponent = -player
    
    for dr, dc in DIRECTIONS:
        # Verificar en ambas direcciones
        r1, c1 = row + dr, col + dc
        r2, c2 = row - dr, col - dc
        
        # Si hay espacios vacíos en línea que podrían permitir flanqueo futuro
        line_has_potential_flank = False
        
        # Verificar hacia adelante
        temp_r, temp_c = r1, c1
        found_opponent = False
        found_empty = False
        
        while 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if board[temp_r][temp_c] == 0:
                found_empty = True
                break
            elif board[temp_r][temp_c] == opponent:
                found_opponent = True
            elif board[temp_r][temp_c] == player:
                break
            temp_r += dr
            temp_c += dc
        
        # Verificar hacia atrás
        temp_r, temp_c = r2, c2
        found_opponent_back = False
        found_empty_back = False
        
        while 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if board[temp_r][temp_c] == 0:
                found_empty_back = True
                break
            elif board[temp_r][temp_c] == opponent:
                found_opponent_back = True
            elif board[temp_r][temp_c] == player:
                break
            temp_r -= dr
            temp_c -= dc
        
        # Si hay potencial para flanqueo (espacios vacíos y oponentes en línea)
        if (found_empty and found_opponent) or (found_empty_back and found_opponent_back):
            line_has_potential_flank = True
        
        # Verificar si puede ser flanqueada inmediatamente
        if can_piece_be_flanked_immediately(board, row, col, player, dr, dc):
            can_be_flanked = True
            break
    
    # Clasificar estabilidad
    if can_be_flanked:
        return -1  # Unstable
    elif any(can_piece_be_flanked_in_future(board, row, col, player, dr, dc) for dr, dc in DIRECTIONS):
        return 1   # Semi-stable
    else:
        return 3   # Stable

def can_piece_be_flanked_immediately(board, row, col, player, dr, dc):
    """Verifica si una pieza puede ser flanqueada en el próximo movimiento"""
    opponent = -player
    
    # Buscar en la dirección dada
    r, c = row + dr, col + dc
    found_empty_for_opponent = False
    
    while 0 <= r < 8 and 0 <= c < 8:
        if board[r][c] == 0:
            # Verificar si el oponente puede jugar aquí y flanquear
            if is_valid_move(board, r, c, opponent):
                # Simular el movimiento y ver si flanquea nuestra pieza
                temp_board = copy.deepcopy(board)
                temp_board = apply_move(temp_board, (r, c), opponent)
                if temp_board[row][col] == opponent:
                    return True
            break
        elif board[r][c] == opponent:
            # Continuar buscando
            pass
        else:  # board[r][c] == player
            break
        r += dr
        c += dc
    
    return False

def can_piece_be_flanked_in_future(board, row, col, player, dr, dc):
    """Verifica si una pieza podría ser flanqueada en movimientos futuros"""
    opponent = -player
    
    # Buscar espacios vacíos en la línea que podrían permitir flanqueo futuro
    r, c = row + dr, col + dc
    has_opponent_in_line = False
    
    while 0 <= r < 8 and 0 <= c < 8:
        if board[r][c] == 0:
            return has_opponent_in_line  # Si hay oponentes en la línea y un espacio vacío
        elif board[r][c] == opponent:
            has_opponent_in_line = True
        else:  # board[r][c] == player
            break
        r += dr
        c += dc
    
    return False

# Mantener las funciones originales que funcionan bien
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

# Función alternativa usando la función original para comparación
def decide_move2(board, my_symbol):
    """Función original mantenida para comparación"""
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
    """Función minimax original"""
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
    """Función de evaluación original simple"""
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

def ai_move(board, player_color):
    """
    Función requerida por othello_player.py
    
    Args:
        board: Lista 8x8 representando el tablero
        player_color: 1 o -1 indicando el color del jugador
    
    Returns:
        Tupla (x, y) con la mejor jugada, o None si no hay jugadas válidas
    """
    return decide_move_enhanced(board, player_color)