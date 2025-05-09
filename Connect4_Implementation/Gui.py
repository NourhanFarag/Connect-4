import pygame
import sys
import math
import time
from Game import (
    Algorithm,
    get_valid_moves,
    minimax,
    alphabeta,
    iterative_deepening_alphabeta
)

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 750
BOARD_WIDTH, BOARD_HEIGHT = 700, 600
PADDING = 40

# Colors
BLUE = (33, 150, 243)
DARK_BLUE = (13, 71, 161)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (244, 67, 54)
YELLOW = (255, 235, 59)
GRAY = (189, 189, 189)
LIGHT_GRAY = (238, 238, 238)
PANEL_COLOR = (250, 250, 250)
ghame2 = (155, 117, 214)

# Fonts
FONT_SMALL = pygame.font.SysFont('Segoe UI', 18)
FONT_MEDIUM = pygame.font.SysFont('Segoe UI', 24, bold=True)
FONT_LARGE = pygame.font.SysFont('Segoe UI', 48, bold=True)
FONT_TITLE = pygame.font.SysFont('Segoe UI', 64, bold=True)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, corner_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        text_surf = FONT_MEDIUM.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class Connect4Board:
    def __init__(self):
        self.reset()
        self.GRID_SIZE = 100
        self.RADIUS = int(self.GRID_SIZE / 2 - 5)
        self.ANIMATION_SPEED = 15
        
    def reset(self):
        self.board = [[0 for _ in range(7)] for _ in range(6)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.animated_piece = None

    def is_valid_move(self, col):
        return 0 <= col < 7 and self.board[0][col] == 0

    def drop_piece(self, col):
        if self.game_over or not self.is_valid_move(col):
            return False

        for row in reversed(range(6)):
            if self.board[row][col] == 0:
                self.animated_piece = {
                    'col': col,
                    'row': row,
                    'player': self.current_player,
                    'y': 50 - self.GRID_SIZE
                }
                self.last_move = (row, col)
                return True
        return False

    def update_animation(self):
        if self.animated_piece:
            target_y = 50 + self.animated_piece['row'] * self.GRID_SIZE + self.GRID_SIZE//2
            if self.animated_piece['y'] < target_y:
                self.animated_piece['y'] += self.ANIMATION_SPEED
            else:
                row = self.animated_piece['row']
                col = self.animated_piece['col']
                self.board[row][col] = self.animated_piece['player']
                self.check_winner()
                self.current_player = 3 - self.current_player
                self.animated_piece = None
                return True
        return False

    def check_winner(self):
        if not self.last_move:
            return
            
        row, col = self.last_move
        piece = self.board[row][col]
        
        directions = [
            [(0,1),(0,-1)],  # Horizontal
            [(1,0),(-1,0)],  # Vertical
            [(1,1),(-1,-1)], # Diagonal /
            [(1,-1),(-1,1)]  # Diagonal \
        ]
        
        for axis in directions:
            count = 1
            for dr, dc in axis:
                r, c = row + dr, col + dc
                while 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == piece:
                    count += 1
                    r += dr
                    c += dc
            
            if count >= 4:
                self.game_over = True
                self.winner = piece
                return

        if all(cell != 0 for row in self.board for cell in row):
            self.game_over = True

    def draw(self, surface):
        # Draw board
        pygame.draw.rect(surface, ghame2, (PADDING, 50, BOARD_WIDTH, BOARD_HEIGHT), border_radius=8)
        
        # Draw slots
        for row in range(6):
            for col in range(7):
                center_x = PADDING + col * self.GRID_SIZE + self.GRID_SIZE//2
                center_y = 50 + row * self.GRID_SIZE + self.GRID_SIZE//2
                
                pygame.draw.circle(surface, BLACK, (center_x, center_y), self.RADIUS)
                pygame.draw.circle(surface, LIGHT_GRAY, (center_x, center_y), self.RADIUS-2)
                
                if self.board[row][col] == 1:
                    pygame.draw.circle(surface, RED, (center_x, center_y), self.RADIUS-5)
                elif self.board[row][col] == 2:
                    pygame.draw.circle(surface, YELLOW, (center_x, center_y), self.RADIUS-5)
                    
                if (row, col) == self.last_move:
                    pygame.draw.circle(surface, WHITE, (center_x, center_y), self.RADIUS - 1, 2)


        # Draw animated piece
        if self.animated_piece:
            col = self.animated_piece['col']
            y_pos = self.animated_piece['y']
            color = RED if self.animated_piece['player'] == 1 else YELLOW
            x_pos = PADDING + col * self.GRID_SIZE + self.GRID_SIZE//2
            
            pygame.draw.circle(surface, BLACK, (x_pos, y_pos), self.RADIUS)
            pygame.draw.circle(surface, color, (x_pos, y_pos), self.RADIUS-5)

class MenuScreen:
    def __init__(self):
        button_width, button_height = 300, 70
        start_y = 250
        PANEL_COLOR=(12, 12, 60)
        LIGHT_BLUE = (135, 206, 235)
        MINT_GREEN = (62, 180, 137)
        Burghandy=(140,21,21)
        self.buttons = [
            Button(SCREEN_WIDTH//2 - button_width//2, start_y, 
                  button_width, button_height, "Human vs AI", Burghandy, (255,235,59),BLACK),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + button_height + 25,
                  button_width, button_height, "AI vs AI", Burghandy, (255,235,59),BLACK),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 2*(button_height + 25),
                  button_width, button_height, "Quit", Burghandy, (255,235,59),BLACK)
        ]
        
        # Load or create icon
        try:
            self.icon = pygame.image.load(r"D:\College\3rd year\Second Term\AI\AiProjectG9\Project1\Connect4Game\Icons\connect4-64px.png").convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (80, 80))
        except:
            # Create fallback icon
            self.icon = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(self.icon, BLACK, (40, 40), 40)
            pygame.draw.circle(self.icon, RED, (40, 40), 30)
        
    def draw(self, surface):
        #PANEL_COLOR=(145, 145, 145)
        NEW= (26,10,70)
        PANEL_COLOR=(12, 12, 60)

        surface.fill(NEW)
        
        # Create title text
        title = FONT_TITLE.render("CONNECT 4", True, (198,207,50))
        title_rect = title.get_rect()
        
        # Calculate total width of icon + text + spacing
        total_width = self.icon.get_width() + title_rect.width + 20
        
        # Starting x position for centered group
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Draw icon (left element)
        icon_rect = self.icon.get_rect(center=(start_x + self.icon.get_width()//2, 150))
        surface.blit(self.icon, icon_rect)
        
        # Draw title (right element)
        title_rect.center = (start_x + self.icon.get_width() + 20 + title_rect.width//2, 150)
        surface.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        
    def handle_event(self, event):
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                return i
        return None

class AlgorithmSelectScreen:
    def __init__(self):
        button_width, button_height = 300, 70
        start_y = 180
        Burghandy = (140, 21, 21)
        
        self.algorithms = [
            {
                "type": Algorithm.MINIMAX,
                "name": "MINIMAX",
                "desc": "Perfect play but slower,Uses full depth search.",
                "color": Burghandy,
                "hover_color": (255, 235, 59),
                "text_color": BLACK
            },
            {
                "type": Algorithm.ALPHA_BETA,
                "name": "ALPHA-BETA", 
                "desc": "Optimal moves, faster, Prunes unnecessary branches.",
                "color": Burghandy,
                "hover_color": (255, 235, 59),
                "text_color": BLACK
            },
            {
                "type": Algorithm.ITERATIVE_DEEPENING,
                "name": "I-D ALPHA BETA",
                "desc": "Iterative deeping alpha-Beta is Balanced, time-limited,Gradually increases depth.",
                "color": Burghandy,
                "hover_color": (255, 235, 59),
                "text_color": BLACK
            }
        ]
        
        self.buttons = [
            Button(
                SCREEN_WIDTH//2 - button_width//2,
                start_y + i*(button_height + 20),
                button_width,
                button_height,
                algo['name'],
                algo["color"],
                algo["hover_color"],
                algo["text_color"],
                12
            )
            for i, algo in enumerate(self.algorithms)
        ]
        
        self.back_button = Button(
            SCREEN_WIDTH - 130,
            SCREEN_HEIGHT - 70,
            100, 40,
            "Back",
            Burghandy,
            (255, 235, 59),
            BLACK,
            8
        )
        
    def draw(self, surface):
        NEW= (26,10,70)
        surface.fill(NEW)
        
        title = FONT_LARGE.render("SELECT AI ALGORITHM", True, (198, 207, 50))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 120))
        surface.blit(title, title_rect)
        
        for button in self.buttons:
            button.draw(surface)
        
        self.back_button.draw(surface)
        
    def handle_event(self, event):
        if self.back_button.handle_event(event):
            return ("back", None)
            
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                return ("algorithm", self.algorithms[i])
        return (None, None)

class AlgorithmDescriptionScreen:
    def __init__(self, algorithm_info):
        self.algorithm_info = algorithm_info
        
        # Calculate box dimensions based on text content
        self.box_width, self.box_height = self.calculate_box_size()
        
        # Box position (centered)
        self.box_x = (SCREEN_WIDTH - self.box_width) // 2
        self.box_y = (SCREEN_HEIGHT - self.box_height) // 2
        
        # Create buttons inside the box
        button_y = self.box_y + self.box_height - 70  # Position at bottom of box
        self.back_button = Button(
            self.box_x + 50,  # Positioned inside box
            button_y,
            120, 40,
            "Back",
            (140, 21, 21),  # Burgundy
            (255, 235, 59),  # Yellow hover
            BLACK,
            8
        )
        
        self.continue_button = Button(
            self.box_x + self.box_width - 170,  # Positioned inside box
            button_y,
            120, 40,
            "Continue",
            (140, 21, 21),  # Burgundy
            (255, 235, 59),  # Yellow hover
            BLACK,
            8
        )
        
    def calculate_box_size(self):
        # Calculate required width based on algorithm name
        name_width = FONT_LARGE.size(self.algorithm_info["name"])[0]
        
        # Calculate required height based on description
        words = self.algorithm_info["desc"].split(' ')
        lines = []
        current_line = ""
        max_line_width = 0
        
        for word in words:
            test_line = current_line + word + " "
            test_width = FONT_MEDIUM.size(test_line)[0]
            if test_width < 500:  # Reasonable max line width
                current_line = test_line
                max_line_width = max(max_line_width, test_width)
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Calculate dimensions with padding
        box_width = min(650, max(400, max_line_width + 80))  # Between 400-650 width
        box_height = 150 + len(lines) * 30  # Base height + line height
        
        return box_width, box_height
        
    def draw(self, surface):
        NEW = (26, 10, 70)
        ghame2 = (155, 117, 214)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Description box with dynamic size
        pygame.draw.rect(surface, ghame2, 
                        (self.box_x, self.box_y, self.box_width, self.box_height), 
                        border_radius=15)
        
        # Draw algorithm name (centered)
        name_surf = FONT_LARGE.render(self.algorithm_info["name"], True, NEW)
        name_rect = name_surf.get_rect(center=(SCREEN_WIDTH//2, self.box_y + 50))
        surface.blit(name_surf, name_rect)
        
        # Draw description with word wrapping
        words = self.algorithm_info["desc"].split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if FONT_MEDIUM.size(test_line)[0] < self.box_width - 60:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Calculate starting y position for text
        text_start_y = self.box_y + 100
        
        # Draw each line centered
        for i, line in enumerate(lines):
            text_surf = FONT_MEDIUM.render(line, True, NEW)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, text_start_y + i * 30))
            surface.blit(text_surf, text_rect)
        
        # Draw buttons inside the box
        self.back_button.draw(surface)
        self.continue_button.draw(surface)
        
    def handle_event(self, event):
        if self.back_button.handle_event(event):
            return "back"
        if self.continue_button.handle_event(event):
            return "continue"
        return None
def get_ai_move(board, algorithm, player_piece, depth=4, time_limit=2.5):
    """Calculate AI move using specified algorithm"""
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return None
        
    try:
        if algorithm == Algorithm.MINIMAX:
            move = minimax(board, depth, True, player_piece)
        elif algorithm == Algorithm.ALPHA_BETA:
            move = alphabeta(board, depth, -math.inf, math.inf, True, player_piece)
        else:  # Iterative Deepening
            move = iterative_deepening_alphabeta(board, depth, time_limit, player_piece)
            
        return move if move in valid_moves else valid_moves[0]
    except Exception as e:
        print(f"AI Error: {e}")
        return valid_moves[0]

class GameScreen:
    NEW= (26,10,70)
    def __init__(self, player1_ai=None, player2_ai=None):
        NEW= (26,10,70)
        self.board = Connect4Board()
        self.player1_ai = player1_ai
        self.player2_ai = player2_ai
        
        # Calculate position for button in bottom of right panel
        panel_x = BOARD_WIDTH + PADDING + 20
        panel_bottom = 50 + BOARD_HEIGHT
        button_y = panel_bottom - 60  # 60px from bottom of panel
        
        # Create menu button with specified colors
        self.back_button = Button(
            x=panel_x + 20,          # 20px from left edge of panel
            y=button_y,              # 60px from bottom
            width=210,               # Width to span most of panel
            height=50,               # Height
            text="Menu",
            color=(128, 0, 32),     # Burgundy color
            hover_color=(255, 235, 59),  # Yellow hover
            text_color=NEW,  # ghame2 text color
            corner_radius=8
        )
        
        # Game timer and stats
        self.game_start_time = time.time()
        self.final_time = None
        self.total_moves = 0
        
    def draw(self, surface):
        NEW= (26,10,70)
        surface.fill(NEW)
        self.board.draw(surface)
        self.draw_side_panel(surface)
        self.back_button.draw(surface)  # Draw the menu button
        
        if self.board.game_over:
            self.draw_game_over_message(surface)
    
    def draw_side_panel(self, surface):
        panel_x = BOARD_WIDTH + PADDING + 20
        panel_width = 250
        
        # Panel background
        pygame.draw.rect(surface, WHITE, (panel_x, 50, panel_width, BOARD_HEIGHT), border_radius=8)
        
        # Current player info
        player_text = FONT_MEDIUM.render("CURRENT PLAYER", True, DARK_BLUE)
        surface.blit(player_text, (panel_x + 20, 70))
        
        player_color = RED if self.board.current_player == 1 else YELLOW
        player_name = "RED" if self.board.current_player == 1 else "YELLOW"
        
        name_text = FONT_MEDIUM.render(player_name, True, player_color)
        surface.blit(name_text, (panel_x + 90, 110))
        
        # Game stats
        self.draw_stats_box(surface, panel_x, 140)
        
        # AI info (only if AI is playing)
        if self.player1_ai or self.player2_ai:
            ai_text = FONT_MEDIUM.render("AI STATUS", True, DARK_BLUE)
            surface.blit(ai_text, (panel_x + 20, 220))
            
            current_ai = self.player1_ai if self.board.current_player == 1 else self.player2_ai
            if current_ai:
                algo_name = "Minimax" if current_ai == Algorithm.MINIMAX else \
                           "Alpha-Beta" if current_ai == Algorithm.ALPHA_BETA else \
                           "Iterative Deepening"
                
                status = FONT_SMALL.render("Thinking..." if not self.board.game_over else "Finished", True, DARK_BLUE)
                surface.blit(status, (panel_x + 30, 260))
                
                algo = FONT_SMALL.render(f"Algorithm: {algo_name}", True, BLACK)
                surface.blit(algo, (panel_x + 30, 290))
    
    def draw_stats_box(self, surface, x, y):
        # Box background
        pygame.draw.rect(surface, LIGHT_GRAY, (x + 20, y, 210, 70), border_radius=8)
        
        # Moves count
        moves_text = FONT_SMALL.render(f"Moves: {self.total_moves}", True, BLACK)
        surface.blit(moves_text, (x + 30, y + 15))
        
        # Game time
        current_time = self.final_time if self.final_time is not None else time.time() - self.game_start_time
        time_text = FONT_SMALL.render(f"Time: {current_time:.1f}s", True, BLACK)
        surface.blit(time_text, (x + 30, y + 40))
    
    def draw_game_over_message(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        if self.board.winner:
            text = f"Player {'RED' if self.board.winner == 1 else 'YELLOW'} Wins!"
            color = RED if self.board.winner == 1 else YELLOW
        else:
            text = "It's a Draw!"
            color = WHITE
            
        text_surf = FONT_LARGE.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
        
        # Final stats
        if self.final_time is None:
            self.final_time = time.time() - self.game_start_time
        
        stats_text = FONT_MEDIUM.render(
            f"Moves: {self.total_moves} | Time: {self.final_time:.1f}s", 
            True, WHITE
        )
        surface.blit(stats_text, stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
        
        hint = FONT_SMALL.render("Click to continue...", True, WHITE)
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80)))
    
    def handle_event(self, event):
        if self.back_button.handle_event(event):
            return "back"
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.board.game_over:
                return "back"
                
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if PADDING <= mouse_x <= PADDING + BOARD_WIDTH and 50 <= mouse_y <= 50 + BOARD_HEIGHT:
                col = (mouse_x - PADDING) // self.board.GRID_SIZE
                if 0 <= col < 7 and not self.board.animated_piece:
                    if self.board.drop_piece(col):
                        self.total_moves += 1
                        return True
        return False
    
    def ai_move(self):
        if self.board.game_over or self.board.animated_piece:
            return False
            
        current_ai = self.player1_ai if self.board.current_player == 1 else self.player2_ai
        if current_ai:
            col = get_ai_move(self.board.board, current_ai, self.board.current_player)
            if col is not None:
                if self.board.drop_piece(col):
                    self.total_moves += 1
                    return True
        return False

    def update(self):
        if self.board.update_animation():
            if not self.board.game_over:
                self.board.check_winner()
                if self.board.game_over:
                    self.final_time = time.time() - self.game_start_time
            return True
        return False
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Connect 4 AI")
    clock = pygame.time.Clock()
    
    current_screen = "menu"
    menu_screen = MenuScreen()
    algorithm_screen = AlgorithmSelectScreen()
    game_screen = None
    description_screen = None
    selected_algorithm = None
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_screen == "menu":
                choice = menu_screen.handle_event(event)
                if choice == 0:  # Human vs AI
                    current_screen = "algorithm"
                elif choice == 1:  # AI vs AI
                    game_screen = GameScreen(Algorithm.ALPHA_BETA, Algorithm.ITERATIVE_DEEPENING)
                    game_screen.color_selection_screen = False
                    game_screen.player_color = RED
                    game_screen.ai_color = YELLOW
                    current_screen = "game"
                elif choice == 2:  # Quit
                    running = False
            
            elif current_screen == "algorithm":
                action, algorithm_info = algorithm_screen.handle_event(event)
                if action == "back":
                    current_screen = "menu"
                elif action == "algorithm":
                    description_screen = AlgorithmDescriptionScreen(algorithm_info)
                    current_screen = "description"
                    selected_algorithm = algorithm_info["type"]
            
            elif current_screen == "description":
                result = description_screen.handle_event(event)
                if result == "continue":
                    game_screen = GameScreen(player2_ai=selected_algorithm)
                    current_screen = "game"
                elif result == "back":
                    current_screen = "algorithm"
            
            elif current_screen == "game":
                result = game_screen.handle_event(event)
                if result == "back":
                    current_screen = "menu"
                    game_screen = None
        
        # Game updates
        if current_screen == "game" and game_screen:
            game_screen.update()
            game_screen.ai_move()
        
        # Drawing
        screen.fill(WHITE)
        if current_screen == "menu":
            menu_screen.draw(screen)
        elif current_screen == "algorithm":
            algorithm_screen.draw(screen)
        elif current_screen == "description":
            algorithm_screen.draw(screen)
            description_screen.draw(screen)
        elif current_screen == "game" and game_screen:
            game_screen.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()