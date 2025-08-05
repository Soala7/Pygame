import pygame
from PIL import Image
import random
import os

# === CONFIG ===
GRID_SIZE = 5  # Easy: 5x5 = 25 pieces
IMAGE_PATH = "assets/your_image.jpg"
TEMP_DIR = "temp_pieces"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# === INIT ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Puzzle Game - Easy Mode")
clock = pygame.time.Clock()

# === UTILS ===
def load_image_and_split(path, grid_size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    img = Image.open(path)
    img = img.resize((500, 500))  # Resize to fit screen
    pw = img.width // grid_size
    ph = img.height // grid_size

    pieces = []
    for y in range(grid_size):
        for x in range(grid_size):
            box = (x * pw, y * ph, (x + 1) * pw, (y + 1) * ph)
            piece_img = img.crop(box)
            piece_path = os.path.join(TEMP_DIR, f"piece_{x}_{y}.png")
            piece_img.save(piece_path)

            pieces.append({
                "image": pygame.image.load(piece_path),
                "correct_pos": (100 + x * pw, 50 + y * ph),
                "current_pos": [random.randint(600, 750), random.randint(50, 500)],
                "rect": pygame.Rect(0, 0, pw, ph),
                "placed": False
            })
    return pieces

def clean_temp():
    if os.path.exists(TEMP_DIR):
        for file in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, file))
        os.rmdir(TEMP_DIR)

# === GAME START ===
pieces = load_image_and_split(IMAGE_PATH, GRID_SIZE)
selected_piece = None

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Select a piece on click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for piece in reversed(pieces):  # top-first
                if piece["rect"].collidepoint(pos) and not piece["placed"]:
                    selected_piece = piece
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if selected_piece:
                # Snap to correct if close enough
                x, y = selected_piece["current_pos"]
                cx, cy = selected_piece["correct_pos"]
                if abs(x - cx) < 20 and abs(y - cy) < 20:
                    selected_piece["current_pos"] = [cx, cy]
                    selected_piece["placed"] = True
                selected_piece = None

    # Move piece with mouse
    if selected_piece:
        mx, my = pygame.mouse.get_pos()
        iw, ih = selected_piece["image"].get_size()
        selected_piece["current_pos"] = [mx - iw // 2, my - ih // 2]

    # Draw all pieces
    for piece in pieces:
        x, y = piece["current_pos"]
        screen.blit(piece["image"], (x, y))
        piece["rect"].topleft = (x, y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
clean_temp()
