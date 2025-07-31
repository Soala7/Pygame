import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 16
CELL_SIZE = 30
MINE_COUNT = 40
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 60  # Extra space for UI

# Colors
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GRAY = (211, 211, 211)

# Number colors
NUMBER_COLORS = {
    1: BLUE,
    2: GREEN,
    3: RED,
    4: PURPLE,
    5: BROWN,
    6: (0, 128, 128),  # Teal
    7: BLACK,
    8: DARK_GRAY
}

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Minesweeper:
    def __init__(self):
        self.grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.flags_remaining = MINE_COUNT
        
        # Pygame setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

    def place_mines(self, first_x, first_y):
        """Place mines randomly, avoiding the first clicked cell"""
        mines_placed = 0
        while mines_placed < MINE_COUNT:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            
            # Don't place mine on first click or if already has mine
            if (x == first_x and y == first_y) or self.grid[y][x].is_mine:
                continue
                
            self.grid[y][x].is_mine = True
            mines_placed += 1
        
        # Calculate adjacent mine counts
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if not self.grid[y][x].is_mine:
                    self.grid[y][x].adjacent_mines = self.count_adjacent_mines(x, y)

    def count_adjacent_mines(self, x, y):
        """Count mines in the 8 adjacent cells"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid[ny][nx].is_mine:
                        count += 1
        return count

    def reveal_cell(self, x, y):
        """Reveal a cell and cascade if it's empty"""
        if (x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE or 
            self.grid[y][x].is_revealed or self.grid[y][x].is_flagged):
            return

        self.grid[y][x].is_revealed = True

        if self.grid[y][x].is_mine:
            self.game_over = True
            # Reveal all mines
            for row in self.grid:
                for cell in row:
                    if cell.is_mine:
                        cell.is_revealed = True
            return

        # If cell has no adjacent mines, reveal all adjacent cells
        if self.grid[y][x].adjacent_mines == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal_cell(x + dx, y + dy)

    def toggle_flag(self, x, y):
        """Toggle flag on a cell"""
        if self.grid[y][x].is_revealed or self.game_over:
            return

        if self.grid[y][x].is_flagged:
            self.grid[y][x].is_flagged = False
            self.flags_remaining += 1
        else:
            if self.flags_remaining > 0:
                self.grid[y][x].is_flagged = True
                self.flags_remaining -= 1

    def check_win(self):
        """Check if player has won"""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.grid[y][x]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        self.game_won = True
        return True

    def reset_game(self):
        """Reset the game to initial state"""
        self.grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.flags_remaining = MINE_COUNT

    def handle_click(self, pos, button):
        """Handle mouse clicks"""
        if pos[1] < 30:  # Clicked in UI area
            return

        x = pos[0] // CELL_SIZE
        y = (pos[1] - 30) // CELL_SIZE

        if x >= GRID_SIZE or y >= GRID_SIZE:
            return

        if button == 1:  # Left click
            if self.first_click:
                self.place_mines(x, y)
                self.first_click = False
            
            if not self.game_over and not self.game_won:
                self.reveal_cell(x, y)
                if not self.game_over:
                    self.check_win()
        
        elif button == 3:  # Right click
            if not self.game_over and not self.game_won:
                self.toggle_flag(x, y)

    def draw_cell(self, x, y):
        """Draw a single cell"""
        cell = self.grid[y][x]
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + 30, CELL_SIZE, CELL_SIZE)
        
        if cell.is_revealed:
            if cell.is_mine:
                pygame.draw.rect(self.screen, RED, rect)
                # Draw mine
                pygame.draw.circle(self.screen, BLACK, 
                                 (x * CELL_SIZE + CELL_SIZE // 2, 
                                  y * CELL_SIZE + 30 + CELL_SIZE // 2), 8)
            else:
                pygame.draw.rect(self.screen, WHITE, rect)
                if cell.adjacent_mines > 0:
                    color = NUMBER_COLORS.get(cell.adjacent_mines, BLACK)
                    text = self.font.render(str(cell.adjacent_mines), True, color)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
        else:
            pygame.draw.rect(self.screen, GRAY, rect)
            if cell.is_flagged:
                # Draw flag
                flag_points = [
                    (x * CELL_SIZE + 8, y * CELL_SIZE + 35),
                    (x * CELL_SIZE + 8, y * CELL_SIZE + 50),
                    (x * CELL_SIZE + 22, y * CELL_SIZE + 42)
                ]
                pygame.draw.polygon(self.screen, RED, flag_points)
                pygame.draw.line(self.screen, BLACK, 
                               (x * CELL_SIZE + 8, y * CELL_SIZE + 35),
                               (x * CELL_SIZE + 8, y * CELL_SIZE + 55), 2)
        
        # Draw cell border
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_ui(self):
        """Draw the UI elements"""
        # Background for UI
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, WINDOW_WIDTH, 30))
        
        # Flags remaining counter
        flags_text = f"Flags: {self.flags_remaining}"
        text_surface = self.font.render(flags_text, True, BLACK)
        self.screen.blit(text_surface, (10, 5))
        
        # Game status
        if self.game_won:
            status_text = "YOU WIN! Press R to restart"
            color = GREEN
        elif self.game_over:
            status_text = "GAME OVER! Press R to restart"
            color = RED
        else:
            status_text = "Left click: reveal, Right click: flag"
            color = BLACK
            
        text_surface = self.font.render(status_text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 15))
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Draw the entire game"""
        self.screen.fill(WHITE)
        
        # Draw UI
        self.draw_ui()
        
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.draw_cell(x, y)

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()