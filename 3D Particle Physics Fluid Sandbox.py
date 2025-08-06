import pygame
import math
import random
import numpy as np
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.3
DAMPING = 0.99
SMOOTHING_RADIUS = 30
PRESSURE_MULTIPLIER = 0.5
VISCOSITY = 0.1
REST_DENSITY = 4
PARTICLE_MASS = 1
MAX_PARTICLES = 400

# Colors
BACKGROUND = (10, 15, 25)
WATER_BLUE = (64, 164, 223)
FIRE_RED = (255, 100, 50)
SAND_YELLOW = (255, 215, 0)
SMOKE_GRAY = (128, 128, 128)
UI_COLOR = (255, 255, 255)

class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector3D(self.x/mag, self.y/mag, self.z/mag)
        return Vector3D(0, 0, 0)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

class Particle:
    def __init__(self, x, y, z, particle_type="water"):
        self.position = Vector3D(x, y, z)
        self.velocity = Vector3D(0, 0, 0)
        self.force = Vector3D(0, 0, 0)
        self.density = 0
        self.pressure = 0
        self.type = particle_type
        self.life = 1.0
        self.age = 0
        self.size = random.uniform(2, 4)
        
        # Type-specific properties
        if particle_type == "fire":
            self.life = random.uniform(0.5, 1.5)
            self.velocity = Vector3D(random.uniform(-2, 2), random.uniform(-3, -1), random.uniform(-1, 1))
        elif particle_type == "smoke":
            self.life = random.uniform(2, 4)
            self.velocity = Vector3D(random.uniform(-1, 1), random.uniform(-2, -0.5), random.uniform(-0.5, 0.5))
        elif particle_type == "sand":
            self.size = random.uniform(1, 3)
    
    def update(self, dt):
        # Age and life decay
        self.age += dt
        if self.type in ["fire", "smoke"]:
            self.life -= dt * 0.5
        
        # Apply forces
        acceleration = self.force * (1.0 / PARTICLE_MASS)
        
        # Type-specific behaviors
        if self.type == "fire":
            # Fire rises and flickers
            acceleration.y -= GRAVITY * 2
            self.velocity.x += random.uniform(-0.5, 0.5)
            self.velocity.y += random.uniform(-0.2, 0.1)
        elif self.type == "smoke":
            # Smoke rises slowly and disperses
            acceleration.y -= GRAVITY * 0.3
            self.velocity.x += random.uniform(-0.3, 0.3)
            self.velocity = self.velocity * 0.98
        elif self.type == "sand":
            # Sand falls and settles
            acceleration.y += GRAVITY * 1.5
        else:  # water
            acceleration.y += GRAVITY
        
        # Update velocity and position
        self.velocity = self.velocity + acceleration * dt
        self.velocity = self.velocity * DAMPING
        self.position = self.position + self.velocity * dt
        
        # Boundary constraints with 3D consideration
        if self.position.x < self.size:
            self.position.x = self.size
            self.velocity.x *= -0.5
        elif self.position.x > SCREEN_WIDTH - self.size:
            self.position.x = SCREEN_WIDTH - self.size
            self.velocity.x *= -0.5
            
        if self.position.y < self.size:
            self.position.y = self.size
            self.velocity.y *= -0.3
        elif self.position.y > SCREEN_HEIGHT - self.size:
            self.position.y = SCREEN_HEIGHT - self.size
            self.velocity.y *= -0.3
            self.velocity.x *= 0.8  # Friction
        
        # Z-depth boundaries (for 3D effect)
        if self.position.z < -50:
            self.position.z = -50
            self.velocity.z *= -0.5
        elif self.position.z > 50:
            self.position.z = 50
            self.velocity.z *= -0.5
        
        # Reset forces
        self.force = Vector3D(0, 0, 0)
    
    def is_alive(self):
        return self.life > 0 and self.position.y < SCREEN_HEIGHT + 50

class FluidSimulator:
    def __init__(self):
        self.particles = []
        self.spatial_grid = {}
        self.grid_size = SMOOTHING_RADIUS
    
    def add_particle(self, x, y, particle_type="water"):
        if len(self.particles) < MAX_PARTICLES:
            z = random.uniform(-20, 20)
            self.particles.append(Particle(x, y, z, particle_type))
    
    def update_spatial_grid(self):
        self.spatial_grid.clear()
        for i, particle in enumerate(self.particles):
            grid_x = int(particle.position.x / self.grid_size)
            grid_y = int(particle.position.y / self.grid_size)
            grid_z = int(particle.position.z / self.grid_size)
            
            key = (grid_x, grid_y, grid_z)
            if key not in self.spatial_grid:
                self.spatial_grid[key] = []
            self.spatial_grid[key].append(i)
    
    def get_nearby_particles(self, particle):
        grid_x = int(particle.position.x / self.grid_size)
        grid_y = int(particle.position.y / self.grid_size)
        grid_z = int(particle.position.z / self.grid_size)
        
        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    key = (grid_x + dx, grid_y + dy, grid_z + dz)
                    if key in self.spatial_grid:
                        nearby.extend(self.spatial_grid[key])
        return nearby
    
    def smoothing_kernel(self, distance, radius):
        if distance >= radius:
            return 0
        return (315 / (64 * math.pi * radius**9)) * (radius**2 - distance**2)**3
    
    def smoothing_kernel_gradient(self, distance_vector, distance, radius):
        if distance >= radius or distance == 0:
            return Vector3D(0, 0, 0)
        
        coefficient = -945 / (32 * math.pi * radius**9) * (radius**2 - distance**2)**2
        return distance_vector * coefficient
    
    def calculate_density_pressure(self):
        for particle in self.particles:
            if particle.type != "water":
                continue
                
            density = 0
            nearby_indices = self.get_nearby_particles(particle)
            
            for j in nearby_indices:
                neighbor = self.particles[j]
                if neighbor.type != "water":
                    continue
                    
                distance_vector = particle.position - neighbor.position
                distance = distance_vector.magnitude()
                
                if distance < SMOOTHING_RADIUS:
                    density += PARTICLE_MASS * self.smoothing_kernel(distance, SMOOTHING_RADIUS)
            
            particle.density = max(density, REST_DENSITY)
            particle.pressure = PRESSURE_MULTIPLIER * (particle.density - REST_DENSITY)
    
    def calculate_forces(self):
        for i, particle in enumerate(self.particles):
            if particle.type != "water":
                continue
                
            pressure_force = Vector3D(0, 0, 0)
            viscosity_force = Vector3D(0, 0, 0)
            
            nearby_indices = self.get_nearby_particles(particle)
            
            for j in nearby_indices:
                if i == j:
                    continue
                    
                neighbor = self.particles[j]
                if neighbor.type != "water":
                    continue
                
                distance_vector = particle.position - neighbor.position
                distance = distance_vector.magnitude()
                
                if distance < SMOOTHING_RADIUS and distance > 0:
                    # Pressure force
                    pressure_gradient = self.smoothing_kernel_gradient(
                        distance_vector, distance, SMOOTHING_RADIUS
                    )
                    shared_pressure = (particle.pressure + neighbor.pressure) / 2
                    pressure_force = pressure_force + pressure_gradient * (shared_pressure / neighbor.density)
                    
                    # Viscosity force
                    velocity_diff = neighbor.velocity - particle.velocity
                    viscosity_force = viscosity_force + velocity_diff * (
                        VISCOSITY * PARTICLE_MASS * self.smoothing_kernel(distance, SMOOTHING_RADIUS) / neighbor.density
                    )
            
            particle.force = particle.force + pressure_force * (-PARTICLE_MASS / particle.density) + viscosity_force
    
    def update(self, dt):
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Update spatial grid
        self.update_spatial_grid()
        
        # Calculate fluid dynamics for water particles
        self.calculate_density_pressure()
        self.calculate_forces()
        
        # Update all particles
        for particle in self.particles:
            particle.update(dt)

class ParticleRenderer:
    def __init__(self, screen):
        self.screen = screen
        
    def render_particle(self, particle):
        # 3D to 2D projection with perspective
        perspective_factor = 1 + particle.position.z / 200
        screen_x = int(particle.position.x)
        screen_y = int(particle.position.y)
        size = max(1, int(particle.size * perspective_factor))
        
        # Color and alpha based on particle type and life
        if particle.type == "water":
            alpha = min(255, int(200 * particle.life))
            color = (*WATER_BLUE, alpha)
        elif particle.type == "fire":
            life_factor = particle.life
            red = min(255, int(255 * life_factor))
            green = min(255, int(100 * life_factor))
            blue = min(50, int(50 * life_factor))
            alpha = min(255, int(255 * life_factor))
            color = (red, green, blue, alpha)
        elif particle.type == "smoke":
            alpha = min(200, int(150 * particle.life))
            color = (*SMOKE_GRAY, alpha)
        elif particle.type == "sand":
            alpha = 255
            color = (*SAND_YELLOW, alpha)
        else:
            color = (255, 255, 255, 255)
        
        # Create surface for particle with alpha
        if size > 0 and 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
            try:
                # Create a temporary surface for alpha blending
                temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                
                if particle.type == "fire":
                    # Fire effect with gradient
                    for r in range(size, 0, -1):
                        inner_alpha = int(color[3] * (r / size))
                        inner_color = (color[0], color[1], color[2], inner_alpha)
                        if inner_alpha > 0:
                            pygame.draw.circle(temp_surface, inner_color[:3], (size, size), r)
                else:
                    pygame.draw.circle(temp_surface, color[:3], (size, size), size)
                
                # Apply alpha to the entire surface
                temp_surface.set_alpha(color[3] if len(color) > 3 else 255)
                
                # Blit to main screen
                self.screen.blit(temp_surface, (screen_x - size, screen_y - size))
                
            except (pygame.error, OverflowError, ValueError):
                # Fallback to simple circle if advanced rendering fails
                pygame.draw.circle(self.screen, color[:3], (screen_x, screen_y), max(1, size // 2))

class ParticleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("3D Particle Physics Fluid Sandbox")
        self.clock = pygame.time.Clock()
        self.simulator = FluidSimulator()
        self.renderer = ParticleRenderer(self.screen)
        
        self.current_type = "water"
        self.mouse_pressed = False
        self.font = pygame.font.Font(None, 36)
        
        # Add some initial particles
        for _ in range(50):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, 300)
            self.simulator.add_particle(x, y, "water")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.current_type = "water"
                elif event.key == pygame.K_2:
                    self.current_type = "fire"
                elif event.key == pygame.K_3:
                    self.current_type = "smoke"
                elif event.key == pygame.K_4:
                    self.current_type = "sand"
                elif event.key == pygame.K_SPACE:
                    # Clear all particles
                    self.simulator.particles.clear()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_pressed = True
                elif event.button == 3:  # Right click - create explosion
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for _ in range(20):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(5, 15)
                        x = mouse_x + random.uniform(-20, 20)
                        y = mouse_y + random.uniform(-20, 20)
                        self.simulator.add_particle(x, y, self.current_type)
                        if len(self.simulator.particles) > 0:
                            particle = self.simulator.particles[-1]
                            particle.velocity.x = math.cos(angle) * speed
                            particle.velocity.y = math.sin(angle) * speed
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
        
        # Continuous particle creation when mouse held
        if self.mouse_pressed:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for _ in range(3):  # Create multiple particles per frame
                x = mouse_x + random.uniform(-10, 10)
                y = mouse_y + random.uniform(-10, 10)
                self.simulator.add_particle(x, y, self.current_type)
        
        return True
    
    def render_ui(self):
        # Instructions
        instructions = [
            "Left Click: Add particles | Right Click: Explosion",
            "1: Water | 2: Fire | 3: Smoke | 4: Sand",
            "SPACE: Clear | Current: " + self.current_type.title(),
            f"Particles: {len(self.simulator.particles)}/{MAX_PARTICLES}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, UI_COLOR)
            self.screen.blit(text, (10, 10 + i * 30))
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            running = self.handle_events()
            
            # Update simulation
            self.simulator.update(dt)
            
            # Render
            self.screen.fill(BACKGROUND)
            
            # Sort particles by z-depth for proper 3D rendering
            sorted_particles = sorted(self.simulator.particles, key=lambda p: p.position.z, reverse=True)
            
            # Render all particles
            for particle in sorted_particles:
                self.renderer.render_particle(particle)
            
            # Render UI
            self.render_ui()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = ParticleGame()
    game.run()