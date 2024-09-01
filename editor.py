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
RED = (255, 0, 0)
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

# Save monster image
def save_monster(x, y, image):
    file_path = os.path.join('maps', f'{x}-{y}-monster.png')
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
    
    # Increase the window width to accommodate the button
    window_width = zoomed_image.get_width() + 150
    zoomed_screen = pygame.display.set_mode((window_width, zoomed_image.get_height()))
    pygame.display.set_caption(f'Zoomed Map {x}-{y}')

    # Place the button to the right of the map area
    mode_button_rect = pygame.Rect(zoomed_image.get_width() + 10, 10, 90, 30)
    mode_button_color = GREY
    mode_text_color = GREEN
    mode_text = 'Map mode'
    monster_mode = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                zx, zy = event.pos
                if mode_button_rect.collidepoint(zx, zy):
                    monster_mode = not monster_mode
                    mode_text = 'Monster mode' if monster_mode else 'Map mode'
                else:
                    zx //= ZOOM_FACTOR
                    zy //= ZOOM_FACTOR
                    if event.button == 3:  # Right click to change color or place/remove monster
                        if monster_mode:
                            current_color = zoomed_image.get_at((zx * ZOOM_FACTOR, zy * ZOOM_FACTOR))[:3]
                            if current_color == RED:
                                # Remove monster
                                for i in range(ZOOM_FACTOR):
                                    for j in range(ZOOM_FACTOR):
                                        zoomed_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), GREEN)
                                scaled_down_image = pygame.transform.scale(zoomed_image, (TILE_SIZE, TILE_SIZE))
                                save_monster(x, y, scaled_down_image)
                            else:
                                # Place monster
                                for i in range(ZOOM_FACTOR):
                                    for j in range(ZOOM_FACTOR):
                                        zoomed_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), RED)
                                scaled_down_image = pygame.transform.scale(zoomed_image, (TILE_SIZE, TILE_SIZE))
                                save_monster(x, y, scaled_down_image)
                        else:
                            current_color = zoomed_image.get_at((zx * ZOOM_FACTOR, zy * ZOOM_FACTOR))[:3]
                            next_color = GREEN if current_color == GREY else GREY
                            for i in range(ZOOM_FACTOR):
                                for j in range(ZOOM_FACTOR):
                                    zoomed_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), next_color)
                            image.set_at((zx, zy), next_color)

        zoomed_screen.blit(zoomed_image, (0, 0))
        pygame.draw.rect(zoomed_screen, mode_button_color, mode_button_rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(mode_text, True, mode_text_color)
        zoomed_screen.blit(text_surface, (mode_button_rect.x + 5, mode_button_rect.y + 5))
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
