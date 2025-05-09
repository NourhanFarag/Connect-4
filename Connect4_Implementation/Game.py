import math
import time
from copy import deepcopy
from enum import Enum

class Algorithm(Enum):
    MINIMAX = 1
    ALPHA_BETA = 2
    ITERATIVE_DEEPENING = 3

class Node:
    def __init__(self, parent, board, depth, player, current_player, move=None):
        self.move_count = parent.move_count +1 if parent else 0 
        self.parent = parent
        self.board = board
        self.depth = depth
        self.player = player  # The player who will make the next move
        self.current_player = current_player  # The player who made the last move
        self.move = move  # The column that was played (0-6)
        self.turn = current_player  # Alias for compatibility
        
    def is_terminal(self):
        """Check if the node represents a terminal state"""
        return (self.check_win(self.board, 1) or 
                self.check_win(self.board, 2) or 
                all(cell != 0 for row in self.board for cell in row))
    
    def check_win(self, board, piece):
        """Check if the specified player has won"""
        # Horizontal
        for r in range(6):
            for c in range(4):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
        # Vertical
        for c in range(7):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
        # Diagonals
        for r in range(3):
            for c in range(4):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True
        for r in range(3, 6):
            for c in range(4):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
        return False

class Connect4Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.board = [[0]*7 for _ in range(6)]
        self.current_player = 1
        self.game_over = False
        self.winner = None

    def is_valid_move(self, board, col):
        return 0 <= col < 7 and board[0][col] == 0

    def get_valid_moves(self, board):
        valid_moves = [col for col in range(7) if self.is_valid_move(board, col)]
        # Prefer columns that block opponent wins or complete wins
        for move in valid_moves:
           temp_board = self.drop_disc(board, move, 3 - self.current_player)
        if self.check_win(temp_board, 3 - self.current_player):
            return [move]  # Must block here
        return sorted(valid_moves, key=lambda x: abs(x - 3))  # Default: center first

    def drop_disc(self, board, col, piece):
        new_board = deepcopy(board)
        for row in reversed(range(6)):
            if new_board[row][col] == 0:
                new_board[row][col] = piece
                return new_board
        return new_board

    def check_win(self, board, piece):
        # Horizontal
        for r in range(6):
            for c in range(4):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
        # Vertical
        for c in range(7):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
        # Diagonals
        for r in range(3):
            for c in range(4):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True
        for r in range(3, 6):
            for c in range(4):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
        return False

    def is_terminal(self, board):
        return self.check_win(board, 1) or self.check_win(board, 2) or not self.get_valid_moves(board)

    def evaluate_position(self, board, piece):
        score = 0
        opponent_piece = 3 - piece
        
        # Center control
        center_col = [board[r][3] for r in range(6)]
        score += center_col.count(piece) * 3
        
        # Horizontal
        for r in range(6):
            for c in range(4):
                window = board[r][c:c+4]
                score += self.evaluate_window(window, piece, opponent_piece)
        
        # Vertical
        for c in range(7):
            col = [board[r][c] for r in range(6)]
            for r in range(3):
                window = col[r:r+4]
                score += self.evaluate_window(window, piece, opponent_piece)
        
        # Diagonals
        for r in range(3):
            for c in range(4):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opponent_piece)
        
        for r in range(3, 6):
            for c in range(4):
                window = [board[r-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opponent_piece)
        
        return score

    def evaluate_window(self, window, piece, opponent_piece):
       score = 0
    # Prioritize blocking opponent wins
       if window.count(opponent_piece) == 3 and window.count(0) == 1:
         return -100  # Urgent block (was -4)
    # Reward potential wins
       if window.count(piece) == 3 and window.count(0) == 1:
         score += 50   # Immediate win chance (was 5)
       elif window.count(piece) == 2 and window.count(0) == 2:
         score += 10   # Potential future win (was 2)
       return score

    def minimax(self, node, depth, maximizing_player, player_piece):
        valid_moves = self.get_valid_moves(node.board)
        terminal = node.is_terminal()
        
        if depth == 0 or terminal:
            if terminal:
                if node.check_win(node.board, player_piece):
                    return None, math.inf
                elif node.check_win(node.board, 3 - player_piece):
                    return None, -math.inf
                else:
                    return None, 0
            return None, self.evaluate_position(node.board, player_piece)
        
        if maximizing_player:
            value = -math.inf
            best_move = valid_moves[0]
            for move in valid_moves:
                new_board = self.drop_disc(node.board, move, player_piece)
                child = Node(node, new_board, depth-1, 3 - player_piece, player_piece, move)
                _, new_score = self.minimax(child, depth-1, False, player_piece)
                if new_score > value:
                    value = new_score
                    best_move = move
            return best_move, value
        else:
            value = math.inf
            best_move = valid_moves[0]
            opponent_piece = 3 - player_piece
            for move in valid_moves:
                new_board = self.drop_disc(node.board, move, opponent_piece)
                child = Node(node, new_board, depth-1, 3 - opponent_piece, opponent_piece, move)
                _, new_score = self.minimax(child, depth-1, True, player_piece)
                if new_score < value:
                    value = new_score
                    best_move = move
            return best_move, value

    def alphabeta(self, node, depth, alpha, beta, maximizing_player, player_piece):
        valid_moves = self.get_valid_moves(node.board)
        terminal = node.is_terminal()
        
        if depth == 0 or terminal:
            if terminal:
                if node.check_win(node.board, player_piece):
                    return None, math.inf
                elif node.check_win(node.board, 3 - player_piece):
                    return None, -math.inf
                else:
                    return None, 0
            return None, self.evaluate_position(node.board, player_piece)
        
        if maximizing_player:
            value = -math.inf
            best_move = valid_moves[0]
            for move in valid_moves:
                new_board = self.drop_disc(node.board, move, player_piece)
                child = Node(node, new_board, depth-1, 3 - player_piece, player_piece, move)
                _, new_score = self.alphabeta(child, depth-1, alpha, beta, False, player_piece)
                if new_score > value:
                    value = new_score
                    best_move = move
                    alpha = max(alpha, value)
                if value >= beta:
                    break
            return best_move, value
        else:
            value = math.inf
            best_move = valid_moves[0]
            opponent_piece = 3 - player_piece
            for move in valid_moves:
                new_board = self.drop_disc(node.board, move, opponent_piece)
                child = Node(node, new_board, depth-1, 3 - opponent_piece, opponent_piece, move)
                _, new_score = self.alphabeta(child, depth-1, alpha, beta, True, player_piece)
                if new_score < value:
                    value = new_score
                    best_move = move
                    beta = min(beta, value)
                if value <= alpha:
                    break
            return best_move, value

    def iterative_deepening_alphabeta(self, root, max_depth=10, time_limit=None):
        start_time = time.time()
        best_move = self.get_valid_moves(root.board)[0]
        best_value = -math.inf

        for depth in range(1, max_depth + 1):
          # Skip time check if time_limit is None
          if time_limit is not None and time.time() - start_time > time_limit * 0.8:
            break

          current_move, current_value = self.alphabeta(root, depth, -math.inf, math.inf, True, root.current_player)
        
        if current_move is not None and current_value > best_value:
            best_move = current_move
            best_value = current_value
            if best_value == math.inf:  # Early win
                return best_move

        return best_move
# Standalone functions for GUI
def get_valid_moves(board):
    game = Connect4Game()
    return game.get_valid_moves(board)

def minimax(board, depth, maximizing_player, player_piece):
    game = Connect4Game()
    root = Node(None, board, depth, 3 - player_piece if maximizing_player else player_piece, player_piece)
    move, _ = game.minimax(root, depth, maximizing_player, player_piece)
    return move

def alphabeta(board, depth, alpha, beta, maximizing_player, player_piece):
    game = Connect4Game()
    root = Node(None, board, depth, 3 - player_piece if maximizing_player else player_piece, player_piece)
    move, _ = game.alphabeta(root, depth, alpha, beta, maximizing_player, player_piece)
    return move

def iterative_deepening_alphabeta(board, max_depth, time_limit, player_piece):
    game = Connect4Game()
    root = Node(None, board, max_depth, player_piece, player_piece)
    return game.iterative_deepening_alphabeta(root, max_depth, time_limit)