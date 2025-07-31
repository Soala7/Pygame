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

class MazeSolver:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Maze Solver - Python & Pygame")
        self.clock = pygame.time.Clock()
        
        # Maze properties
        self.maze_size = 25
        self.cell_size = MAZE_SIZE // self.maze_size
        self.maze = []
        self.solution_path = []
        self.explored_nodes = []
        
        # UI properties
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 36)
        
        # Algorithm selection
        self.algorithms = ["A*", "Dijkstra", "BFS", "DFS"]
        self.current_algorithm = 0
        
        # Statistics
        self.stats = {
            'path_length': 0,
            'nodes_explored': 0,
            'solve_time': 0.0
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
        
        # Clear previous solution
        self.solution_path = []
        self.explored_nodes = []
        self.stats = {'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0}
    
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
    
    def solve_maze(self):
        """Solve maze using selected algorithm"""
        if self.animating:
            return
            
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
        self.stats = {
            'path_length': len(path),
            'nodes_explored': len(explored),
            'solve_time': (end_time - start_time) * 1000  # Convert to milliseconds
        }
        
        # Start animation
        self.animate_solution()
    
    def animate_solution(self):
        """Animate the pathfinding process"""
        self.animating = True
        self.animation_step = 0
        self.show_exploration = True
    
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
        
        # Draw start and end points
        start_x, start_y = 1 * self.cell_size, 1 * self.cell_size
        end_x = (self.maze_size - 2) * self.cell_size
        end_y = (self.maze_size - 2) * self.cell_size
        
        pygame.draw.rect(self.screen, GREEN, (start_y, start_x, self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, RED, (end_y, end_x, self.cell_size, self.cell_size))
        
        # Draw grid lines
        for i in range(self.maze_size + 1):
            pygame.draw.line(self.screen, GRAY, (0, i * self.cell_size), (MAZE_SIZE, i * self.cell_size))
            pygame.draw.line(self.screen, GRAY, (i * self.cell_size, 0), (i * self.cell_size, MAZE_SIZE))
    
    def draw_controls(self):
        """Draw control panel"""
        # Clear control panel area
        pygame.draw.rect(self.screen, LIGHT_GRAY, (MAZE_SIZE, 0, CONTROL_PANEL_WIDTH, WINDOW_HEIGHT))
        
        y_offset = 20
        
        # Title
        title = self.title_font.render("Maze Solver", True, BLACK)
        self.screen.blit(title, (MAZE_SIZE + 10, y_offset))
        y_offset += 50
        
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
        
        # Algorithm selection
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
            ("Solve Maze", BLUE),
            ("Clear Solution", ORANGE)
        ]
        
        for i, (text, color) in enumerate(buttons):
            button_y = y_offset + i * 40
            pygame.draw.rect(self.screen, color, (MAZE_SIZE + 10, button_y, 150, 30))
            pygame.draw.rect(self.screen, BLACK, (MAZE_SIZE + 10, button_y, 150, 30), 2)
            button_text = self.font.render(text, True, BLACK)
            text_rect = button_text.get_rect(center=(MAZE_SIZE + 85, button_y + 15))
            self.screen.blit(button_text, text_rect)
        
        y_offset += 140
        
        # Statistics
        stats_title = self.font.render("Statistics:", True, BLACK)
        self.screen.blit(stats_title, (MAZE_SIZE + 10, y_offset))
        y_offset += 30
        
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
            if 850 <= y <= 875:
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
            
            # Algorithm selection
            elif 895 <= y <= 920:
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    self.current_algorithm = (self.current_algorithm + 1) % len(self.algorithms)
            
            # Control buttons
            elif 960 <= y <= 990:  # Generate Maze
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    self.generate_maze()
            elif 1000 <= y <= 1030:  # Solve Maze
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    self.solve_maze()
            elif 1040 <= y <= 1070:  # Clear Solution
                if MAZE_SIZE + 10 <= x <= MAZE_SIZE + 160:
                    self.solution_path = []
                    self.explored_nodes = []
                    self.stats = {'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0}
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
                    if event.key == pygame.K_SPACE:
                        self.solve_maze()
                    elif event.key == pygame.K_g:
                        self.generate_maze()
                    elif event.key == pygame.K_c:
                        self.solution_path = []
                        self.explored_nodes = []
                        self.stats = {'path_length': 0, 'nodes_explored': 0, 'solve_time': 0.0}
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