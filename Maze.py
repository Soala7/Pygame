import pygame
import random
import heapq
from collections import deque
import time
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
MAZE_SIZE = 800
CONTROL_PANEL_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
PINK = (255, 192, 203)
LIME = (50, 205, 50)

class MazeSolver:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Interactive Maze Solver - Arrow Keys + Auto Solve")
        self.clock = pygame.time.Clock()
        
        # Maze properties
        self.maze_size = 25
        self.cell_size = MAZE_SIZE // self.maze_size
        self.maze = []
        self.solution_path = []
        self.explored_nodes = []
        
        # Manual navigation
        self.player_pos = (1, 1)  # Start position
        self.player_path = [(1, 1)]  # Track player's path
        self.manual_mode = True
        self.game_won = False
        
        # UI properties
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 48)
        
        # Algorithm selection
        self.algorithms = ["A*", "Dijkstra", "BFS", "DFS"]
        self.current_algorithm = 0
        
        # Statistics
        self.stats = {
            'path_length': 0,
            'nodes_explored': 0,
            'solve_time': 0.0,
            'player_steps': 1
        }
        
        # Animation
        self.animating = False
        self.animation_speed = 10  # milliseconds per step
        
        # Generate initial maze
        self.generate_maze()
    
    def generate_maze(self):
        """Generate maze using recursive backtracking algorithm"""
        # Initialize maze with walls (1 = wall, 0 = path)
        self.maze = [[1 for _ in range(self.maze_size)] for _ in range(self.maze_size)]
        
        # Recursive backtracking
        stack = []
        start = (1, 1)
        self.maze[start[0]][start[1]] = 0
        stack.append(start)
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            current = stack[-1]
            neighbors = []
            
            # Find unvisited neighbors
            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if (0 < nx < self.maze_size - 1 and 
                    0 < ny < self.maze_size - 1 and 
                    self.maze[nx][ny] == 1):
                    neighbors.append((nx, ny))
            
            if neighbors:
                # Choose random neighbor
                next_cell = random.choice(neighbors)
                
                # Remove wall between current and next
                wall_x = current[0] + (next_cell[0] - current[0]) // 2
                wall_y = current[1] + (next_cell[1] - current[1]) // 2
                self.maze[wall_x][wall_y] = 0
                self.maze[next_cell[0]][next_cell[1]] = 0
                
                stack.append(next_cell)
            else:
                stack.pop()
        
        # Ensure start and end are accessible
        self.maze[1][1] = 0  # Start
        self.maze[self.maze_size - 2][self.maze_size - 2] = 0  # End
        
        # Reset player and game state
        self.player_pos = (1, 1)
        self.player_path = [(1, 1)]
        self.manual_mode = True
        self.game_won = False
        
        # Clear previous solution
        self.solution_path = []
        self.explored_nodes = []
        self.stats = {'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0, 'player_steps': 1}
    
    def move_player(self, direction):
        """Move player in manual mode"""
        if not self.manual_mode or self.game_won or self.animating:
            return
        
        x, y = self.player_pos
        dx, dy = direction
        new_x, new_y = x + dx, y + dy
        
        # Check bounds and walls
        if (0 <= new_x < self.maze_size and 
            0 <= new_y < self.maze_size and 
            self.maze[new_x][new_y] == 0):
            
            self.player_pos = (new_x, new_y)
            
            # Add to path if not backtracking
            if (new_x, new_y) not in self.player_path:
                self.player_path.append((new_x, new_y))
                self.stats['player_steps'] = len(self.player_path)
            else:
                # Remove path from current position to end when backtracking
                try:
                    backtrack_index = self.player_path.index((new_x, new_y))
                    self.player_path = self.player_path[:backtrack_index + 1]
                    self.stats['player_steps'] = len(self.player_path)
                except ValueError:
                    pass
            
            # Check if reached the end
            if (new_x, new_y) == (self.maze_size - 2, self.maze_size - 2):
                self.game_won = True
    
    def get_neighbors(self, pos):
        """Get valid neighbors for pathfinding"""
        neighbors = []
        x, y = pos
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.maze_size and 
                0 <= ny < self.maze_size and 
                self.maze[nx][ny] == 0):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic for A*"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def solve_astar(self, start, end):
        """A* pathfinding algorithm"""
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        explored = []
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            explored.append(current)
            
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], explored
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return [], explored
    
    def solve_dijkstra(self, start, end):
        """Dijkstra's algorithm"""
        distances = {start: 0}
        previous = {}
        unvisited = [(0, start)]
        explored = []
        
        while unvisited:
            current_dist, current = heapq.heappop(unvisited)
            
            if current in explored:
                continue
                
            explored.append(current)
            
            if current == end:
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(start)
                return path[::-1], explored
            
            for neighbor in self.get_neighbors(current):
                distance = current_dist + 1
                
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(unvisited, (distance, neighbor))
        
        return [], explored
    
    def solve_bfs(self, start, end):
        """Breadth-First Search"""
        queue = deque([start])
        visited = {start}
        came_from = {}
        explored = []
        
        while queue:
            current = queue.popleft()
            explored.append(current)
            
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], explored
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        
        return [], explored
    
    def solve_dfs(self, start, end):
        """Depth-First Search"""
        stack = [start]
        visited = set()
        came_from = {}
        explored = []
        
        while stack:
            current = stack.pop()
            
            if current in visited:
                continue
                
            visited.add(current)
            explored.append(current)
            
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], explored
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    came_from[neighbor] = current
                    stack.append(neighbor)
        
        return [], explored
    
    def solve_maze_auto(self):
        """Automatically solve maze using selected algorithm"""
        if self.animating:
            return
            
        # Switch to auto mode
        self.manual_mode = False
        
        start = (1, 1)
        end = (self.maze_size - 2, self.maze_size - 2)
        algorithm = self.algorithms[self.current_algorithm]
        
        start_time = time.time()
        
        if algorithm == "A*":
            path, explored = self.solve_astar(start, end)
        elif algorithm == "Dijkstra":
            path, explored = self.solve_dijkstra(start, end)
        elif algorithm == "BFS":
            path, explored = self.solve_bfs(start, end)
        elif algorithm == "DFS":
            path, explored = self.solve_dfs(start, end)
        
        end_time = time.time()
        
        self.solution_path = path
        self.explored_nodes = explored
        self.stats.update({
            'path_length': len(path),
            'nodes_explored': len(explored),
            'solve_time': (end_time - start_time) * 1000  # Convert to milliseconds
        })
        
        # Start animation
        self.animate_solution()
    
    def animate_solution(self):
        """Animate the pathfinding process"""
        self.animating = True
        self.animation_step = 0
        self.show_exploration = True
    
    def toggle_mode(self):
        """Toggle between manual and auto mode"""
        if not self.animating:
            self.manual_mode = not self.manual_mode
            if self.manual_mode:
                # Reset to manual mode
                self.player_pos = (1, 1)
                self.player_path = [(1, 1)]
                self.game_won = False
                self.solution_path = []
                self.explored_nodes = []
                self.stats['player_steps'] = 1
    
    def draw_maze(self):
        """Draw the maze"""
        # Clear maze area
        pygame.draw.rect(self.screen, WHITE, (0, 0, MAZE_SIZE, MAZE_SIZE))
        
        # Draw maze cells
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                x = j * self.cell_size
                y = i * self.cell_size
                
                if self.maze[i][j] == 1:  # Wall
                    pygame.draw.rect(self.screen, BLACK, (x, y, self.cell_size, self.cell_size))
                else:  # Path
                    pygame.draw.rect(self.screen, WHITE, (x, y, self.cell_size, self.cell_size))
        
        # In auto mode, draw explored nodes and solution
        if not self.manual_mode:
            # Draw explored nodes (during animation)
            if self.animating and self.show_exploration:
                max_explored = min(self.animation_step, len(self.explored_nodes))
                for i in range(max_explored):
                    pos = self.explored_nodes[i]
                    x = pos[1] * self.cell_size
                    y = pos[0] * self.cell_size
                    pygame.draw.rect(self.screen, CYAN, (x, y, self.cell_size, self.cell_size))
            elif not self.animating:
                # Draw all explored nodes when not animating
                for pos in self.explored_nodes:
                    x = pos[1] * self.cell_size
                    y = pos[0] * self.cell_size
                    pygame.draw.rect(self.screen, CYAN, (x, y, self.cell_size, self.cell_size))
            
            # Draw solution path
            if self.animating and not self.show_exploration:
                max_path = min(self.animation_step - len(self.explored_nodes), len(self.solution_path))
                for i in range(max_path):
                    pos = self.solution_path[i]
                    x = pos[1] * self.cell_size
                    y = pos[0] * self.cell_size
                    pygame.draw.rect(self.screen, YELLOW, (x, y, self.cell_size, self.cell_size))
            elif not self.animating:
                # Draw complete solution path
                for pos in self.solution_path:
                    x = pos[1] * self.cell_size
                    y = pos[0] * self.cell_size
                    pygame.draw.rect(self.screen, YELLOW, (x, y, self.cell_size, self.cell_size))
        
        # In manual mode, draw player path
        if self.manual_mode:
            # Draw player's path (except current position)
            for pos in self.player_path[:-1]:
                x = pos[1] * self.cell_size
                y = pos[0] * self.cell_size
                pygame.draw.rect(self.screen, PINK, (x, y, self.cell_size, self.cell_size))
            
            # Draw player (current position)
            player_x = self.player_pos[1] * self.cell_size
            player_y = self.player_pos[0] * self.cell_size
            pygame.draw.rect(self.screen, BLUE, (player_x, player_y, self.cell_size, self.cell_size))
            
            # Draw arrow to show it's the player
            center_x = player_x + self.cell_size // 2
            center_y = player_y + self.cell_size // 2
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), self.cell_size // 4)
        
        # Always draw start and end points
        start_x, start_y = 1 * self.cell_size, 1 * self.cell_size
        end_x = (self.maze_size - 2) * self.cell_size
        end_y = (self.maze_size - 2) * self.cell_size
        
        # Draw start (green border)
        pygame.draw.rect(self.screen, GREEN, (start_y, start_x, self.cell_size, self.cell_size), 3)
        # Draw end (red border)
        pygame.draw.rect(self.screen, RED, (end_y, end_x, self.cell_size, self.cell_size), 3)
        
        # Draw win message
        if self.game_won:
            win_text = self.big_font.render("YOU WIN!", True, GREEN)
            text_rect = win_text.get_rect(center=(MAZE_SIZE // 2, 50))
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10))
            pygame.draw.rect(self.screen, GREEN, text_rect.inflate(20, 10), 3)
            self.screen.blit(win_text, text_rect)
        
        # Draw grid lines (subtle)
        for i in range(self.maze_size + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY, (0, i * self.cell_size), (MAZE_SIZE, i * self.cell_size))
            pygame.draw.line(self.screen, LIGHT_GRAY, (i * self.cell_size, 0), (i * self.cell_size, MAZE_SIZE))
    
    def draw_controls(self):
        """Draw control panel"""
        # Clear control panel area
        pygame.draw.rect(self.screen, LIGHT_GRAY, (MAZE_SIZE, 0, CONTROL_PANEL_WIDTH, WINDOW_HEIGHT))
        
        y_offset = 20
        
        # Title
        title = self.title_font.render("Maze Solver", True, BLACK)
        self.screen.blit(title, (MAZE_SIZE + 10, y_offset))
        y_offset += 50
        
        # Mode indicator
        mode_text = "MANUAL" if self.manual_mode else "AUTO"
        mode_color = BLUE if self.manual_mode else RED
        mode_display = self.font.render(f"Mode: {mode_text}", True, mode_color)
        self.screen.blit(mode_display, (MAZE_SIZE + 10, y_offset))
        y_offset += 30
        
        # Instructions based on mode
        if self.manual_mode:
            instructions = [
                "Use ARROW KEYS",
                "to navigate maze",
                "",
                "Press M to switch",
                "to Auto Mode"
            ]
        else:
            instructions = [
                "Watch algorithm",
                "solve the maze",
                "",
                "Press M to switch",
                "to Manual Mode"
            ]
        
        for instruction in instructions:
            if instruction:
                inst_text = self.small_font.render(instruction, True, BLACK)
                self.screen.blit(inst_text, (MAZE_SIZE + 10, y_offset))
            y_offset += 18
        
        y_offset += 10
        
        # Maze size control
        size_text = self.font.render(f"Size: {self.maze_size}x{self.maze_size}", True, BLACK)
        self.screen.blit(size_text, (MAZE_SIZE + 10, y_offset))
        y_offset += 30
        
        # Size buttons
        pygame.draw.rect(self.screen, DARK_GRAY, (MAZE_SIZE + 10, y_offset, 30, 25))
        minus_text = self.font.render("-", True, WHITE)
        self.screen.blit(minus_text, (MAZE_SIZE + 20, y_offset + 5))
        
        pygame.draw.rect(self.screen, DARK_GRAY, (MAZE_SIZE + 50, y_offset, 30, 25))
        plus_text = self.font.render("+", True, WHITE)
        self.screen.blit(plus_text, (MAZE_SIZE + 60, y_offset + 5))
        y_offset += 40
        
        # Algorithm selection (only show in auto mode)
        if not self.manual_mode:
            algo_text = self.font.render("Algorithm:", True, BLACK)
            self.screen.blit(algo_text, (MAZE_SIZE + 10, y_offset))
            y_offset += 25
            
            current_algo = self.algorithms[self.current_algorithm]
            algo_display = self.font.render(current_algo, True, BLACK)
            pygame.draw.rect(self.screen, WHITE, (MAZE_SIZE + 10, y_offset, 150, 25))
            pygame.draw.rect(self.screen, BLACK, (MAZE_SIZE + 10, y_offset, 150, 25), 2)
            self.screen.blit(algo_display, (MAZE_SIZE + 15, y_offset + 5))
            y_offset += 40
        
        # Control buttons
        buttons = [
            ("Generate Maze", GREEN),
            ("Toggle Mode", PURPLE),
        ]
        
        if not self.manual_mode:
            buttons.append(("Auto Solve", BLUE))
            buttons.append(("Clear Solution", ORANGE))
        else:
            buttons.append(("Reset Position", ORANGE))
        
        for i, (text, color) in enumerate(buttons):
            button_y = y_offset + i * 40
            pygame.draw.rect(self.screen, color, (MAZE_SIZE + 10, button_y, 150, 30))
            pygame.draw.rect(self.screen, BLACK, (MAZE_SIZE + 10, button_y, 150, 30), 2)
            button_text = self.small_font.render(text, True, BLACK)
            text_rect = button_text.get_rect(center=(MAZE_SIZE + 85, button_y + 15))
            self.screen.blit(button_text, text_rect)
        
        y_offset += len(buttons) * 40 + 20
        
        # Statistics
        stats_title = self.font.render("Statistics:", True, BLACK)
        self.screen.blit(stats_title, (MAZE_SIZE + 10, y_offset))
        y_offset += 30
        
        if self.manual_mode:
            stats_info = [
                f"Steps Taken: {self.stats['player_steps']}",
                f"Current Pos: {self.player_pos}",
                f"Won: {'Yes' if self.game_won else 'No'}"
            ]
        else:
            stats_info = [
                f"Path Length: {self.stats['path_length']}",
                f"Nodes Explored: {self.stats['nodes_explored']}",
                f"Time: {self.stats['solve_time']:.2f}ms"
            ]
        
        for stat in stats_info:
            stat_text = self.small_font.render(stat, True, BLACK)
            self.screen.blit(stat_text, (MAZE_SIZE + 10, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # Legend
        legend_title = self.font.render("Legend:", True, BLACK)
        self.screen.blit(legend_title, (MAZE_SIZE + 10, y_offset))
        y_offset += 30
        
        if self.manual_mode:
            legend_items = [
                ("Wall", BLACK),
                ("Path", WHITE),
                ("Start", GREEN),
                ("End", RED),
                ("Player", BLUE),
                ("Trail", PINK)
            ]
        else:
            legend_items = [
                ("Wall", BLACK),
                ("Path", WHITE),
                ("Start", GREEN),
                ("End", RED),
                ("Explored", CYAN),
                ("Solution", YELLOW)
            ]
        
        for text, color in legend_items:
            pygame.draw.rect(self.screen, color, (MAZE_SIZE + 10, y_offset, 15, 15))
            pygame.draw.rect(self.screen, BLACK, (MAZE_SIZE + 10, y_offset, 15, 15), 1)
            legend_text = self.small_font.render(text, True, BLACK)
            self.screen.blit(legend_text, (MAZE_SIZE + 30, y_offset))
            y_offset += 20
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        
        if x > MAZE_SIZE:  # Click in control panel
            # Size controls
            if 170 <= y <= 195:
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 40:  # Minus button
                    if self.maze_size > 10:
                        self.maze_size -= 5
                        self.cell_size = MAZE_SIZE // self.maze_size
                        self.generate_maze()
                elif MAZE_SIZE + 50 <= x <= MAZE_SIZE + 80:  # Plus button
                    if self.maze_size < 50:
                        self.maze_size += 5
                        self.cell_size = MAZE_SIZE // self.maze_size
                        self.generate_maze()
            
            # Algorithm selection (only in auto mode)
            elif not self.manual_mode and 235 <= y <= 260:
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    self.current_algorithm = (self.current_algorithm + 1) % len(self.algorithms)
            
            # Button clicks - find button position dynamically
            button_start_y = 275 if not self.manual_mode else 215
            button_height = 40
            
            for i in range(4):  # Maximum 4 buttons
                button_y_start = button_start_y + i * button_height
                button_y_end = button_y_start + 30
                
                if button_y_start <= y <= button_y_end and MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    if i == 0:  # Generate Maze
                        self.generate_maze()
                    elif i == 1:  # Toggle Mode
                        self.toggle_mode()
                    elif i == 2:
                        if not self.manual_mode:  # Auto Solve
                            self.solve_maze_auto()
                        else:  # Reset Position
                            self.player_pos = (1, 1)
                            self.player_path = [(1, 1)]
                            self.game_won = False
                            self.stats['player_steps'] = 1
                    elif i == 3 and not self.manual_mode:  # Clear Solution
                        self.solution_path = []
                        self.explored_nodes = []
                        self.stats.update({'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0})
                        self.animating = False
    
    def update_animation(self):
        """Update animation state"""
        if self.animating:
            self.animation_step += 1
            
            if self.show_exploration:
                if self.animation_step >= len(self.explored_nodes):
                    self.show_exploration = False
                    self.animation_step = 0
            else:
                if self.animation_step >= len(self.solution_path):
                    self.animating = False
    
    def run(self):
        """Main game loop"""
        running = True
        animation_timer = 0
        
        while running:
            dt = self.clock.tick(60)
            animation_timer += dt
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    # Arrow key movement (manual mode only)
                    if self.manual_mode:
                        if event.key == pygame.K_UP:
                            self.move_player((-1, 0))
                        elif event.key == pygame.K_DOWN:
                            self.move_player((1, 0))
                        elif event.key == pygame.K_LEFT:
                            self.move_player((0, -1))
                        elif event.key == pygame.K_RIGHT:
                            self.move_player((0, 1))
                    
                    # Other controls
                    if event.key == pygame.K_SPACE and not self.manual_mode:
                        self.solve_maze_auto()
                    elif event.key == pygame.K_g:
                        self.generate_maze()
                    elif event.key == pygame.K_m:
                        self.toggle_mode()
                    elif event.key == pygame.K_r and self.manual_mode:
                        self.player_pos = (1, 1)
                        self.player_path = [(1, 1)]
                        self.game_won = False
                        self.stats['player_steps'] = 1
                    elif event.key == pygame.K_c and not self.manual_mode:
                        self.solution_path = []
                        self.explored_nodes = []
                        self.stats.update({'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0})
                        self.animating = False
            
            # Update animation
            if animation_timer >= self.animation_speed:
                self.update_animation()
                animation_timer = 0
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_maze()
            self.draw_controls()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    maze_solver = MazeSolver()
    maze_solver.run()