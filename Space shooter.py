import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Particle:
    def __init__(self, x, y, color, velocity, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x, self.vel_y = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1
        self.vel_x *= 0.98  # Friction
        self.vel_y *= 0.98
    
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        size = max(1, int(self.size * alpha))
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.health = 100
        self.max_health = 100
        self.radius = 20
        self.shoot_cooldown = 0
        self.power_level = 1
        self.shield = False
        self.shield_timer = 0
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.radius, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.radius, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(self.radius, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(SCREEN_HEIGHT - self.radius, self.y + self.speed)
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield = False
    
    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullets = []
            if self.power_level == 1:
                bullets.append(Bullet(self.x, self.y - self.radius, 0, -12, CYAN))
                self.shoot_cooldown = 10
            elif self.power_level == 2:
                bullets.append(Bullet(self.x - 10, self.y - self.radius, 0, -12, CYAN))
                bullets.append(Bullet(self.x + 10, self.y - self.radius, 0, -12, CYAN))
                self.shoot_cooldown = 8
            else:  # power_level >= 3
                bullets.append(Bullet(self.x, self.y - self.radius, 0, -12, CYAN))
                bullets.append(Bullet(self.x - 15, self.y - self.radius, -2, -12, CYAN))
                bullets.append(Bullet(self.x + 15, self.y - self.radius, 2, -12, CYAN))
                self.shoot_cooldown = 6
            return bullets
        return []
    
    def draw(self, screen):
        # Draw shield
        if self.shield:
            shield_alpha = min(255, self.shield_timer * 3)
            shield_color = (*BLUE, shield_alpha)
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius + 10, 3)
        
        # Draw player
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius - 5)
        
        # Draw health bar
        bar_width = 100
        bar_height = 10
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (10, 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (10, 10, bar_width * health_ratio, bar_height))

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        if enemy_type == "basic":
            self.health = 20
            self.speed = 2
            self.radius = 15
            self.color = RED
            self.shoot_cooldown = random.randint(60, 120)
        elif enemy_type == "fast":
            self.health = 10
            self.speed = 5
            self.radius = 10
            self.color = ORANGE
            self.shoot_cooldown = random.randint(40, 80)
        elif enemy_type == "tank":
            self.health = 60
            self.speed = 1
            self.radius = 25
            self.color = PURPLE
            self.shoot_cooldown = random.randint(80, 160)
        
        self.max_health = self.health
        
    def update(self, player):
        # Move towards player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        self.shoot_cooldown -= 1
    
    def shoot(self, player):
        if self.shoot_cooldown <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                speed = 6
                vel_x = (dx / distance) * speed
                vel_y = (dy / distance) * speed
                
                self.shoot_cooldown = random.randint(60, 120)
                return [Bullet(self.x, self.y, vel_x, vel_y, RED, is_enemy=True)]
        return []
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Health bar for enemies
        if self.health < self.max_health:
            bar_width = self.radius * 2
            bar_height = 4
            health_ratio = self.health / self.max_health
            bar_x = self.x - self.radius
            bar_y = self.y - self.radius - 10
            
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))

class Bullet:
    def __init__(self, x, y, vel_x, vel_y, color, is_enemy=False):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.radius = 3
        self.is_enemy = is_enemy
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = 15
        self.bob_offset = 0
        
        if power_type == "health":
            self.color = GREEN
        elif power_type == "power":
            self.color = YELLOW
        elif power_type == "shield":
            self.color = BLUE
    
    def update(self):
        self.bob_offset += 0.2
        self.y += math.sin(self.bob_offset) * 0.5
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cosmic Storm")
        self.clock = pygame.time.Clock()
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.powerups = []
        
        self.score = 0
        self.wave = 1
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Star field background
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]
    
    def spawn_enemy(self):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(-100, -50)
        
        # Increase variety as waves progress
        if self.wave < 3:
            enemy_type = "basic"
        elif self.wave < 6:
            enemy_type = random.choice(["basic", "fast"])
        else:
            enemy_type = random.choice(["basic", "fast", "tank"])
        
        self.enemies.append(Enemy(x, y, enemy_type))
    
    def spawn_powerup(self):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 200)
        power_type = random.choice(["health", "power", "shield"])
        self.powerups.append(PowerUp(x, y, power_type))
    
    def create_explosion(self, x, y, color, intensity=20):
        for _ in range(intensity):
            vel_x = random.uniform(-8, 8)
            vel_y = random.uniform(-8, 8)
            self.particles.append(Particle(x, y, color, (vel_x, vel_y), random.randint(30, 60)))
    
    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            if bullet.is_enemy:
                continue
                
            for enemy in self.enemies[:]:
                distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                if distance < bullet.radius + enemy.radius:
                    self.bullets.remove(bullet)
                    enemy.health -= 10
                    self.create_explosion(enemy.x, enemy.y, enemy.color, 5)
                    
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10
                        self.create_explosion(enemy.x, enemy.y, enemy.color, 15)
                    break
        
        # Enemy bullets vs player
        for bullet in self.bullets[:]:
            if not bullet.is_enemy:
                continue
                
            distance = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
            if distance < bullet.radius + self.player.radius:
                self.bullets.remove(bullet)
                if not self.player.shield:
                    self.player.health -= 10
                    self.create_explosion(self.player.x, self.player.y, RED, 10)
        
        # Enemies vs player
        for enemy in self.enemies[:]:
            distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if distance < enemy.radius + self.player.radius:
                if not self.player.shield:
                    self.player.health -= 20
                    self.create_explosion(self.player.x, self.player.y, RED, 15)
                self.enemies.remove(enemy)
                self.create_explosion(enemy.x, enemy.y, enemy.color, 15)
        
        # Player vs powerups
        for powerup in self.powerups[:]:
            distance = math.sqrt((powerup.x - self.player.x)**2 + (powerup.y - self.player.y)**2)
            if distance < powerup.radius + self.player.radius:
                self.powerups.remove(powerup)
                
                if powerup.type == "health":
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.type == "power":
                    self.player.power_level = min(3, self.player.power_level + 1)
                elif powerup.type == "shield":
                    self.player.shield = True
                    self.player.shield_timer = 300
                
                self.create_explosion(powerup.x, powerup.y, powerup.color, 10)
    
    def update_stars(self):
        for i, (x, y) in enumerate(self.stars):
            self.stars[i] = (x, y + 1)
            if y > SCREEN_HEIGHT:
                self.stars[i] = (random.randint(0, SCREEN_WIDTH), -5)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bullets.extend(self.player.shoot())
            
            # Update game objects
            self.player.update()
            
            for enemy in self.enemies:
                enemy.update(self.player)
                self.bullets.extend(enemy.shoot(self.player))
            
            for bullet in self.bullets[:]:
                bullet.update()
                if (bullet.x < 0 or bullet.x > SCREEN_WIDTH or 
                    bullet.y < 0 or bullet.y > SCREEN_HEIGHT):
                    self.bullets.remove(bullet)
            
            for particle in self.particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.particles.remove(particle)
            
            for powerup in self.powerups:
                powerup.update()
            
            # Spawn enemies
            self.enemy_spawn_timer += 1
            spawn_rate = max(30, 120 - self.wave * 10)
            if self.enemy_spawn_timer >= spawn_rate:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # Spawn powerups
            self.powerup_spawn_timer += 1
            if self.powerup_spawn_timer >= 600:  # Every 10 seconds
                self.spawn_powerup()
                self.powerup_spawn_timer = 0
            
            # Check for wave completion
            if len(self.enemies) == 0 and self.enemy_spawn_timer == 0:
                self.wave += 1
            
            self.check_collisions()
            self.update_stars()
            
            # Check game over
            if self.player.health <= 0:
                running = False
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw stars
            for x, y in self.stars:
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
            # Draw game objects
            for particle in self.particles:
                particle.draw(self.screen)
            
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            self.player.draw(self.screen)
            
            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
            power_text = self.small_font.render(f"Power Level: {self.player.power_level}", True, WHITE)
            
            self.screen.blit(score_text, (SCREEN_WIDTH - 200, 10))
            self.screen.blit(wave_text, (SCREEN_WIDTH - 200, 50))
            self.screen.blit(power_text, (10, 30))
            
            # Draw controls
            controls = [
                "WASD/Arrow Keys: Move",
                "Space: Shoot",
                "Green: Health",
                "Yellow: Power",
                "Blue: Shield"
            ]
            
            for i, control in enumerate(controls):
                text = self.small_font.render(control, True, WHITE)
                self.screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 20))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Game over screen
        game_over_text = self.font.render("GAME OVER", True, RED)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Close window to exit", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(final_score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        
        # Wait for window close
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()