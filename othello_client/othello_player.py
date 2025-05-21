import requests
import random
import sys
import time
import copy

### Public IP Server
### Testing Server
host_name = 'http://localhost:8000'

class OthelloPlayer():

    def __init__(self, username):
        ### Player username
        self.username = username
        ### Player symbol in a match
        self.current_symbol = 0


    def connect(self, session_name) -> bool:
        """
        :param session_name:
        :return:
        """
        new_player = requests.post(host_name + '/player/new_player?session_name=' + session_name + '&player_name=' +self.username)
        new_player = new_player.json()
        self.session_name = session_name
        print(new_player['message'])
        return new_player['status'] == 200

    def play(self) -> bool:
        """
        :return:
        """
        session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
        session_info = session_info.json()

        while session_info['session_status'] == 'active':
            try:
                if (session_info['round_status'] == 'ready'):

                    match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                    match_info = match_info.json()

                    while match_info['match_status'] == 'bench':
                        print('You are benched this round. Take a rest while you wait.')
                        time.sleep(15)
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()

                    if (match_info['match_status'] == 'active'):
                        self.current_symbol = match_info['symbol']
                        if self.current_symbol == 1:
                            print('Lets play! You are the white pieces.')
                        if self.current_symbol == -1:
                            print('Lets play! You are the black pieces.')


                    while (match_info['match_status'] == 'active'):
                        turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                        turn_info = turn_info.json()
                        while not turn_info['game_over']:
                            if turn_info['turn']:
                                print('SCORE ', turn_info['score'])
                                row, col = self.AI_MOVE(turn_info['board'])
                                move = requests.post(
                                    host_name + '/player/move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +
                                    match_info['match'] + '&row=' + str(row) + '&col=' + str(col))
                                move = move.json()
                                print(move['message'])
                            time.sleep(2)
                            turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                            turn_info = turn_info.json()

                        print('Game Over. Winner : ' + turn_info['winner'])
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()


                else:
                    print('Waiting for match lottery...')
                    time.sleep(5)

            except requests.exceptions.ConnectionError:
                continue

            session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
            session_info = session_info.json()

    def get_valid_moves(self, board, player):
        """
        Retorna una lista de tuplas (fila, columna) que representan movimientos válidos
        para el jugador en el tablero actual.
        """
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(board, row, col, player):
                    valid_moves.append((row, col))
        return valid_moves
    
    def is_valid_move(self, board, row, col, player):
        """
        Verifica si un movimiento es válido para el jugador dado.
        """
        # Si la casilla no está vacía, el movimiento no es válido
        if board[row][col] != 0:
            return False

        # Direcciones (arriba, abajo, izquierda, derecha, diagonales)
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # Verificamos en todas las direcciones si hay un movimiento válido
        for dr, dc in directions:
            r, c = row + dr, col + dc
            # Primero debe haber una ficha del oponente adyacente
            if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == -player:
                r += dr
                c += dc
                # Seguimos en esa dirección
                while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == -player:
                    r += dr
                    c += dc
                # Si llegamos a una ficha del jugador actual, el movimiento es válido
                if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
                    return True
        
        return False

    def make_move(self, board, row, col, player):
        """
        Realiza un movimiento en el tablero y retorna el nuevo estado del tablero.
        """
        if not self.is_valid_move(board, row, col, player):
            return board  # El movimiento no es válido
        
        # Hacemos una copia profunda del tablero para no modificar el original
        new_board = copy.deepcopy(board)
        new_board[row][col] = player  # Colocamos la ficha del jugador
        
        # Direcciones (arriba, abajo, izquierda, derecha, diagonales)
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        # Verificamos en todas las direcciones y volteamos las fichas necesarias
        for dr, dc in directions:
            pieces_to_flip = []
            r, c = row + dr, col + dc
            
            # Seguimos en esa dirección recogiendo fichas del oponente
            while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == -player:
                pieces_to_flip.append((r, c))
                r += dr
                c += dc
            
            # Si la dirección termina con una ficha del jugador actual, volteamos las fichas
            if 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == player:
                for flip_r, flip_c in pieces_to_flip:
                    new_board[flip_r][flip_c] = player
        
        return new_board

    def evaluate_board(self, board, player):
        """
        Evalúa la posición del tablero para el jugador.
        Retorna un valor positivo si es favorable para el jugador.
        """
        # Matriz de pesos para cada posición del tablero
        # Las esquinas son las más valiosas, seguidas por los bordes
        weights = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100]
        ]
        
        # Calculamos la puntuación ponderada para el jugador y el oponente
        player_score = 0
        opponent_score = 0
        
        for row in range(8):
            for col in range(8):
                if board[row][col] == player:
                    player_score += weights[row][col]
                elif board[row][col] == -player:
                    opponent_score += weights[row][col]
        
        # Diferencia de fichas considerando la matriz de pesos
        weighted_score = player_score - opponent_score
        
        # También consideramos la cantidad de movimientos disponibles
        # Más movimientos disponibles generalmente es mejor (movilidad)
        player_moves = len(self.get_valid_moves(board, player))
        opponent_moves = len(self.get_valid_moves(board, -player))
        mobility = player_moves - opponent_moves
        
        # Combinamos las puntuaciones
        return weighted_score + 2 * mobility

    def minimax(self, board, depth, alpha, beta, maximizing_player, player):
        """
        Implementación del algoritmo Minimax con poda Alpha-Beta.
        """
        # Caso base: si alcanzamos la profundidad máxima o el juego termina
        if depth == 0:
            return self.evaluate_board(board, player), None
        
        # Obtenemos los movimientos válidos para el jugador actual
        valid_moves = self.get_valid_moves(board, player if maximizing_player else -player)
        
        # Si no hay movimientos válidos, pasamos el turno
        if not valid_moves:
            # Si tampoco hay movimientos para el oponente, el juego terminó
            if not self.get_valid_moves(board, -player if maximizing_player else player):
                # Contamos las fichas para determinar el ganador
                player_count = sum(row.count(player) for row in board)
                opponent_count = sum(row.count(-player) for row in board)
                return (player_count - opponent_count) * 1000, None
            
            # Pasamos el turno y continuamos con el oponente
            return self.minimax(board, depth - 1, alpha, beta, not maximizing_player, player)
        
        best_move = None
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                row, col = move
                new_board = self.make_move(board, row, col, player)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False, player)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Poda beta
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                row, col = move
                new_board = self.make_move(board, row, col, -player)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True, player)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Poda alpha
            return min_eval, best_move

    def AI_MOVE(self, board):
        """
        Utiliza el algoritmo Minimax con Alpha-Beta pruning para determinar
        el mejor movimiento en el estado actual del tablero.
        """
        # Verificamos si hay movimientos válidos
        valid_moves = self.get_valid_moves(board, self.current_symbol)
        
        if not valid_moves:
            # Si no hay movimientos válidos, devolvemos una jugada inválida
            # (el servidor deberá manejar esto como un paso de turno)
            return (0, 0)
        
        # Profundidad de búsqueda (ajustar según sea necesario)
        depth = 4  # Prueba con diferentes valores según la potencia de cálculo
        
        # Llamamos a minimax
        _, best_move = self.minimax(
            board, 
            depth, 
            float('-inf'), 
            float('inf'), 
            True, 
            self.current_symbol
        )
        
        if best_move:
            return best_move
        else:
            # Fallback a un movimiento aleatorio si algo falla
            return random.choice(valid_moves)

if __name__ == '__main__':
    script_name = sys.argv[0]
    # The rest of the arguments start from sys.argv[1]
    ### The first argument is the session id you want to join
    session_id = sys.argv[1]
    ### The second argument is the username you want to have
    player_id = sys.argv[2]

    print('Bienvenido ' + player_id + '!')
    othello_player = OthelloPlayer(player_id)
    if othello_player.connect(session_id):
        othello_player.play()
    print('Hasta pronto!')