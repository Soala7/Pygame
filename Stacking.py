import pygame
import random
import sys
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stack 'Em Up - Container Balance Game")

# Colors
BACKGROUND = (135, 206, 235)  # Sky blue
GROUND_COLOR = (34, 139, 34)  # Forest green
CONTAINER_COLORS = [
    (255, 99, 71),    # Tomato
    (65, 105, 225),   # Royal Blue
    (255, 215, 0),    # Gold
    (218, 112, 214),  # Orchid
    (50, 205, 50),    # Lime Green
    (255, 165, 0),    # Orange
]

# Game variables
score = 0
level = 1
game_over = False
containers = []
container_width = 80
container_height = 40
current_container = None
container_speed = 3
base_platform = None
max_containers = 5  # Containers per level
containers_placed = 0
clock = pygame.time.Clock()
FPS = 60

# Physics simulation variables
gravity = 0.5
max_fall_speed = 10

# Sounds
try:
    place_sound = mixer.Sound("place.wav") if mixer.get_init() else None
    crash_sound = mixer.Sound("crash.wav") if mixer.get_init() else None
    level_up_sound = mixer.Sound("level_up.wav") if mixer.get_init() else None
except:
    place_sound = None
    crash_sound = None
    level_up_sound = None

# Fonts
font_large = pygame.font.SysFont("Arial", 50)
font_medium = pygame.font.SysFont("Arial", 30)
font_small = pygame.font.SysFont("Arial", 20)

class Container:
    def __init__(self, x, y, width, height, color, is_moving=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.is_moving = is_moving
        self.direction = 1 if random.random() > 0.5 else -1
        self.falling = False
        self.y_velocity = 0
        self.landed = False
        self.rotation = 0
        self.rotation_speed = 0
        
    def update(self):
        if self.is_moving and not self.falling:
            # Horizontal movement for the current container
            self.x += container_speed * self.direction
            
            # Change direction at screen edges
            if self.x < self.width//2:
                self.x = self.width//2
                self.direction = 1
            elif self.x > WIDTH - self.width//2:
                self.x = WIDTH - self.width//2
                self.direction = -1
        elif self.falling:
            # Apply gravity
            self.y_velocity = min(self.y_velocity + gravity, max_fall_speed)
            self.y += self.y_velocity
            
            # Apply rotation if falling
            if not self.landed:
                self.rotation += self.rotation_speed
                self.rotation_speed += 0.1 if self.direction > 0 else -0.1
    
    def draw(self, surface):
        # Create a surface for the container
        container_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(container_surface, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(container_surface, (0, 0, 0), (0, 0, self.width, self.height), 2)
        
        # Rotate if falling
        if self.falling and not self.landed:
            container_surface = pygame.transform.rotate(container_surface, self.rotation)
        
        # Get the rect and center it
        rect = container_surface.get_rect(center=(self.x, self.y))
        surface.blit(container_surface, rect.topleft)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
    
    def check_collision(self, other):
        if not self.falling or self.landed:
            return False
            
        self_rect = self.get_rect()
        other_rect = other.get_rect()
        
        # Simple AABB collision detection
        if (self_rect.right > other_rect.left and
            self_rect.left < other_rect.right and
            self_rect.bottom > other_rect.top and
            self_rect.top < other_rect.bottom):
            
            # Calculate overlap to position the container properly
            overlap = self_rect.bottom - other_rect.top
            self.y -= overlap
            return True
        
        return False

def create_base_platform():
    """Create the base platform"""
    width = 200
    height = 30
    x = WIDTH // 2
    y = HEIGHT - 100
    return Container(x, y, width, height, (139, 69, 19))  # Brown

def draw_ui():
    """Draw the game UI"""
    # Score
    score_text = font_medium.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))
    
    # Level
    level_text = font_medium.render(f"Level: {level}", True, (0, 0, 0))
    screen.blit(level_text, (20, 60))
    
    # Containers left
    containers_left = max_containers - containers_placed
    containers_text = font_medium.render(f"Containers Left: {containers_left}", True, (0, 0, 0))
    screen.blit(containers_text, (20, 100))

def draw_game_over():
    """Draw game over screen"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font_large.render("GAME OVER", True, (255, 255, 255))
    final_score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_text = font_small.render("Press R to Restart", True, (255, 255, 255))
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))

def reset_game():
    """Reset the game state"""
    global score, level, game_over, containers, containers_placed, current_container, container_speed, container_width, base_platform
    
    # Reset game variables
    score = 0
    level = 1
    game_over = False
    containers = []
    containers_placed = 0
    container_speed = 3
    container_width = 80
    
    # Create new base platform
    base_platform = create_base_platform()
    
    # Create first container
    current_container = Container(
        WIDTH // 2,
        100,
        container_width,
        container_height,
        random.choice(CONTAINER_COLORS),
        is_moving=True
    )
    
    return base_platform, current_container

# Create initial game objects
base_platform, current_container = reset_game()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                base_platform, current_container = reset_game()
            
            if event.key == pygame.K_SPACE and not game_over and current_container:
                # Convert current container to a falling container
                current_container.is_moving = False
                current_container.falling = True
                current_container.rotation_speed = random.uniform(-2, 2)
                containers.append(current_container)
                containers_placed += 1
                
                # Play sound if available
                if place_sound:
                    place_sound.play()
                
                # Score calculation based on placement accuracy
                distance_from_center = abs(current_container.x - WIDTH//2)
                placement_bonus = max(0, 100 - distance_from_center)
                score += 50 + placement_bonus
                
                # Check if level is complete
                if containers_placed >= max_containers:
                    level += 1
                    containers_placed = 0
                    max_containers += 2  # Increase difficulty
                    container_speed += 0.5  # Make it faster
                    container_width = max(40, container_width - 5)  # Make containers smaller
                    
                    if level_up_sound:
                        level_up_sound.play()
                
                # Create new moving container
                current_container = Container(
                    WIDTH // 2,
                    100,
                    container_width,
                    container_height,
                    random.choice(CONTAINER_COLORS),
                    is_moving=True
                )
    
    # Game logic
    if not game_over:
        # Update current container
        if current_container:
            current_container.update()
        
        # Update all placed containers
        for container in containers:
            if container.falling and not container.landed:
                container.update()
                
                # Check collision with base platform
                if container.check_collision(base_platform):
                    container.landed = True
                    container.rotation = 0
                
                # Check collision with other containers
                for other in containers:
                    if other != container and other.landed:
                        if container.check_collision(other):
                            container.landed = True
                            container.rotation = 0
                
                # Check if container fell off screen
                if container.y > HEIGHT + 100:
                    game_over = True
                    if crash_sound:
                        crash_sound.play()
    
    # Drawing
    screen.fill(BACKGROUND)
    
    # Draw ground
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - 50, WIDTH, 50))
    
    # Draw base platform
    base_platform.draw(screen)
    
    # Draw all placed containers (sorted by y-position for proper drawing order)
    for container in sorted(containers, key=lambda c: c.y):
        container.draw(screen)
    
    # Draw current moving container
    if current_container and not game_over:
        current_container.draw(screen)
    
    # Draw UI
    draw_ui()
    
    # Draw game over screen if needed
    if game_over:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()