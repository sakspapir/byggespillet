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
YELLOW = (255, 255, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Map Editor')

def load_maps():
    maps = {}
    monsters = {}
    for filename in os.listdir('maps'):
        if filename.endswith('-map.png'):
            parts = filename[:-8].split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                x, y = int(parts[0]), int(parts[1])
                maps[(x, y)] = pygame.image.load(os.path.join('maps', filename))
        elif filename.endswith('-monster.png'):
            parts = filename[:-12].split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                x, y = int(parts[0]), int(parts[1])
                monsters[(x, y)] = pygame.image.load(os.path.join('maps', filename))
    return maps, monsters

# Save map image
def save_map(x, y, image):
    file_path = os.path.join('maps', f'{x}-{y}-map.png')
    pygame.image.save(image, file_path)
    maps[(x, y)] = pygame.image.load(file_path)  # Reload the modified map

# Save monster image
def save_monster(x, y, image):
    # Create a new image with transparency
    transparent_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    transparent_image.fill((0, 0, 0, 0))  # Fill with transparent color

    # Copy only the red and yellow pixels from the original image
    for i in range(TILE_SIZE):
        for j in range(TILE_SIZE):
            color = image.get_at((i, j))[:3]
            if color == RED or color == YELLOW:
                transparent_image.set_at((i, j), color + (255,))  # Set pixel with full opacity

    file_path = os.path.join('maps', f'{x}-{y}-monster.png')
    pygame.image.save(transparent_image, file_path)
    monsters[(x, y)] = pygame.image.load(file_path)  # Reload the modified monster

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
def open_zoomed_map(image, x, y, monster_image=None):
    zoomed_image = pygame.transform.scale(image, (image.get_width() * ZOOM_FACTOR, image.get_height() * ZOOM_FACTOR))
    if monster_image:
        zoomed_monster_image = pygame.transform.scale(monster_image, (monster_image.get_width() * ZOOM_FACTOR, monster_image.get_height() * ZOOM_FACTOR))
    else:
        zoomed_monster_image = pygame.Surface(zoomed_image.get_size(), pygame.SRCALPHA)
        zoomed_monster_image.fill((0, 0, 0, 0))  # Fill with transparent color

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
                    if event.button == 3:  # Right click to change color or place/remove monster/bunny
                        if monster_mode:
                            current_color = zoomed_monster_image.get_at((zx * ZOOM_FACTOR, zy * ZOOM_FACTOR))[:3]
                            if current_color == RED:
                                # Change monster to bunny
                                for i in range(ZOOM_FACTOR):
                                    for j in range(ZOOM_FACTOR):
                                        zoomed_monster_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), YELLOW + (255,))  # Set yellow pixel with full opacity
                                scaled_down_image = pygame.transform.scale(zoomed_monster_image, (TILE_SIZE, TILE_SIZE))
                                save_monster(x, y, scaled_down_image)
                            elif current_color == YELLOW:
                                # Remove bunny
                                for i in range(ZOOM_FACTOR):
                                    for j in range(ZOOM_FACTOR):
                                        zoomed_monster_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), (0, 0, 0, 0))  # Set to transparent
                                scaled_down_image = pygame.transform.scale(zoomed_monster_image, (TILE_SIZE, TILE_SIZE))
                                save_monster(x, y, scaled_down_image)
                            else:
                                # Place monster
                                for i in range(ZOOM_FACTOR):
                                    for j in range(ZOOM_FACTOR):
                                        zoomed_monster_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), RED + (255,))  # Set red pixel with full opacity
                                scaled_down_image = pygame.transform.scale(zoomed_monster_image, (TILE_SIZE, TILE_SIZE))
                                save_monster(x, y, scaled_down_image)
                        else:
                            current_color = zoomed_image.get_at((zx * ZOOM_FACTOR, zy * ZOOM_FACTOR))[:3]
                            next_color = GREEN if current_color == GREY else GREY
                            for i in range(ZOOM_FACTOR):
                                for j in range(ZOOM_FACTOR):
                                    zoomed_image.set_at((zx * ZOOM_FACTOR + i, zy * ZOOM_FACTOR + j), next_color)
                            image.set_at((zx, zy), next_color)

        zoomed_screen.blit(zoomed_image, (0, 0))
        if monster_mode:
            zoomed_screen.blit(zoomed_monster_image, (0, 0))
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
    global maps, monsters
    maps, monsters = load_maps()
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
                open_zoomed_map(maps[(x, y)], x, y, monsters.get((x, y)))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
