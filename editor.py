import os
import pygame
from PIL import Image

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
GRID_COLOR = (200, 200, 200)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
ZOOM_FACTOR = 10

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Map Editor')

# Load map images
def load_maps():
    maps = {}
    for filename in os.listdir('maps'):
        if filename.endswith('-map.png'):
            parts = filename[:-8].split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                x, y = int(parts[0]), int(parts[1])
                maps[(x, y)] = pygame.image.load(os.path.join('maps', filename))
    return maps

# Save map image
def save_map(x, y, image):
    file_path = os.path.join('maps', f'{x}-{y}-map.png')
    pygame.image.save(image, file_path)

# Draw grid
def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

# Create a new map image with green background and grey frame
def create_new_map_image():
    image = pygame.Surface((TILE_SIZE, TILE_SIZE))
    image.fill(GREEN)
    pygame.draw.rect(image, GREY, image.get_rect(), 1)
    return image

# Open zoomed map window
def open_zoomed_map(image, x, y):
    zoomed_image = pygame.transform.scale(image, (image.get_width() * ZOOM_FACTOR, image.get_height() * ZOOM_FACTOR))
    zoomed_screen = pygame.display.set_mode((zoomed_image.get_width(), zoomed_image.get_height()))
    pygame.display.set_caption(f'Zoomed Map {x}-{y}')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                zx, zy = event.pos
                zx //= ZOOM_FACTOR
                zy //= ZOOM_FACTOR
                if event.button == 3:  # Right click to change color
                    current_color = zoomed_image.get_at((zx * ZOOM_FACTOR, zy * ZOOM_FACTOR))[:3]
                    next_color = GREEN if current_color == GREY else GREY
                    for i in range(ZOOM_FACTOR):
                        for j in range(ZOOM_FACTOR):
                            zoomed_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), next_color)
                    image.set_at((zx, zy), next_color)

        zoomed_screen.blit(zoomed_image, (0, 0))
        pygame.display.flip()

    save_map(x, y, image)
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Map Editor')

# Main loop
def main():
    maps = load_maps()
    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_grid()

        for (x, y), image in maps.items():
            screen.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x //= TILE_SIZE
                y //= TILE_SIZE
                if (x, y) not in maps:
                    maps[(x, y)] = create_new_map_image()
                    save_map(x, y, maps[(x, y)])
                open_zoomed_map(maps[(x, y)], x, y)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
