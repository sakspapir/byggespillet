import pygame
import math
import sys
import os
from PIL import Image

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32
PLAYER_SPEED = TILE_SIZE // 10  # Adjusted speed
BULLET_SPEED = 5
MONSTER_SPEED = TILE_SIZE // 20  # Adjusted speed for monsters

# Load images
player_image = pygame.image.load('player.png')
player2_image = pygame.image.load('player2.png')
grass_image = pygame.image.load('grass.png')
stone_image = pygame.image.load('stone.png')
bullet_image = pygame.image.load('bullet.png')
monster_image = pygame.image.load('monster.png')

class Map:
    def __init__(self, start_x, start_y):
        self.current_x = start_x
        self.current_y = start_y
        self.maps = {}
        self.overlays = {}
        self.load_all_maps()
        self.load_all_overlays()

    def load_all_maps(self):
        for filename in os.listdir('maps'):
            if filename.endswith('-map.png'):
                parts = filename[:-8].split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    x, y = int(parts[0]), int(parts[1])
                    self.maps[(x, y)] = self.load_map_from_png(os.path.join('maps', filename))

    def load_map_from_png(self, file_path):
        image = Image.open(file_path)
        pixels = image.load()
        width, height = image.size
        game_map = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = pixels[x, y][:3]
                if (r, g, b) == (128, 128, 128):  # Grey color for stone tiles
                    row.append('s')
                elif (r, g, b) == (0, 255, 0):  # Green color for grass tiles
                    row.append('g')
                else:
                    row.append('g')  # Default to grass if color is not recognized
            game_map.append(row)
        return game_map

    def load_all_overlays(self):
        for filename in os.listdir('maps'):
            if filename.endswith('-monster.png'):
                parts = filename[:-12].split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    x, y = int(parts[0]), int(parts[1])
                    if (x, y) not in self.overlays:
                        self.overlays[(x, y)] = []
                    self.overlays[(x, y)].append(self.load_overlay_from_png(os.path.join('maps', filename)))

    def load_overlay_from_png(self, file_path):
        image = Image.open(file_path)
        pixels = image.load()
        width, height = image.size
        overlay = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = pixels[x, y][:3]
                if (r, g, b) == (255, 0, 0):  # Red color for monsters
                    row.append('m')
                elif (r, g, b) == (0, 0, 255):  # Blue color for items
                    row.append('i')
                else:
                    row.append(None)  # No overlay
            overlay.append(row)
        return overlay

    def get_current_map(self):
        return self.maps.get((self.current_x, self.current_y))

    def get_current_overlays(self):
        return self.overlays.get((self.current_x, self.current_y), [])

    def move_to_adjacent_map(self, direction):
        # Clear current monsters
        monsters.empty()

        # Move to the new map
        if direction == 'left':
            self.current_x -= 1
        elif direction == 'right':
            self.current_x += 1
        elif direction == 'up':
            self.current_y -= 1
        elif direction == 'down':
            self.current_y += 1

        # Spawn monsters for the new map
        self.spawn_monsters(self.get_current_overlays())
        return self.get_current_map(), self.get_current_overlays()
    
    def get_current_overlays(self):
        overlays = self.overlays.get((self.current_x, self.current_y), [])
        return overlays

    def spawn_monsters(self, overlays):
        for overlay in overlays:
            for y, row in enumerate(overlay):
                for x, tile in enumerate(row):
                    if tile == 'm':  # 'm' for monster
                        monsters.add(Monster(x * TILE_SIZE, y * TILE_SIZE))

game_map = Map(6, 9)  # Initialize with starting map coordinates

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Top-Down Game')

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = direction
    
    def update(self):
        if self.direction == 'left':
            self.rect.x -= BULLET_SPEED
        elif self.direction == 'right':
            self.rect.x += BULLET_SPEED
        elif self.direction == 'up':
            self.rect.y -= BULLET_SPEED
        elif self.direction == 'down':
            self.rect.y += BULLET_SPEED
        
        # Check for collision with stone tiles
        if self.collides_with_stone():
            self.kill()
    
    def collides_with_stone(self):
        tile_x = self.rect.centerx // TILE_SIZE
        tile_y = self.rect.centery // TILE_SIZE
        if game_map.get_current_map()[tile_y][tile_x] == 's':
            return True
        return False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = 'down'
        self.controls = controls
    
    def update(self, keys):
        new_x, new_y = self.rect.topleft
        if keys[self.controls['left']]:
            new_x -= PLAYER_SPEED
            self.direction = 'left'
        if keys[self.controls['right']]:
            new_x += PLAYER_SPEED
            self.direction = 'right'
        if keys[self.controls['up']]:
            new_y -= PLAYER_SPEED
            self.direction = 'up'
        if keys[self.controls['down']]:
            new_y += PLAYER_SPEED
            self.direction = 'down'

        # Check for collision with stone tiles
        if not self.collides_with_stone(new_x, new_y):
            self.rect.topleft = (new_x, new_y)

        # Check if player exits the map and load the adjacent map
        if self.rect.right > SCREEN_WIDTH - 30:
            game_map.move_to_adjacent_map('right')
            self.rect.left = 32
            player1.rect.topleft = self.rect.topleft
            player2.rect.topleft = self.rect.topleft
        elif self.rect.left < 30:
            game_map.move_to_adjacent_map('left')
            self.rect.right = SCREEN_WIDTH - 32
            player1.rect.topleft = self.rect.topleft
            player2.rect.topleft = self.rect.topleft
        elif self.rect.bottom > SCREEN_HEIGHT - 30:
            game_map.move_to_adjacent_map('down')
            self.rect.top = 32
            player1.rect.topleft = self.rect.topleft
            player2.rect.topleft = self.rect.topleft
        elif self.rect.top < 30:
            game_map.move_to_adjacent_map('up')
            self.rect.bottom = SCREEN_HEIGHT - 32
            player1.rect.topleft = self.rect.topleft
            player2.rect.topleft = self.rect.topleft

    
    def collides_with_stone(self, x, y):
        corners = [
            (x, y),
            (x + self.rect.width - 1, y),
            (x, y + self.rect.height - 1),
            (x + self.rect.width - 1, y + self.rect.height - 1)
        ]
        for corner in corners:
            tile_x = corner[0] // TILE_SIZE
            tile_y = corner[1] // TILE_SIZE
            if game_map.get_current_map()[tile_y][tile_x] == 's':
                return True
        return False
    
    def shoot(self):
        if self.direction == 'left':
            bullet = Bullet(self.rect.left, self.rect.centery - 2, 'left')
        elif self.direction == 'right':
            bullet = Bullet(self.rect.right, self.rect.centery - 2, 'right')
        elif self.direction == 'up':
            bullet = Bullet(self.rect.centerx - 5, self.rect.top, 'up')
        elif self.direction == 'down':
            bullet = Bullet(self.rect.centerx - 5, self.rect.bottom, 'down')
        bullets.add(bullet)

# Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = monster_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def update(self):
        # Determine the closest player
        if player1.alive() and player2.alive():
            distance_to_player1 = math.sqrt((self.rect.x - player1.rect.x) ** 2 + (self.rect.y - player1.rect.y) ** 2)
            distance_to_player2 = math.sqrt((self.rect.x - player2.rect.x) ** 2 + (self.rect.y - player2.rect.y) ** 2)
            target_player = player1 if distance_to_player1 < distance_to_player2 else player2
        elif player1.alive():
            target_player = player1
        elif player2.alive():
            target_player = player2
        else:
            return  # No players alive, no need to move
        
        # Move towards the closest player
        if target_player.rect.x < self.rect.x:
            new_x = self.rect.x - MONSTER_SPEED
        elif target_player.rect.x > self.rect.x:
            new_x = self.rect.x + MONSTER_SPEED
        else:
            new_x = self.rect.x
        
        if target_player.rect.y < self.rect.y:
            new_y = self.rect.y - MONSTER_SPEED
        elif target_player.rect.y > self.rect.y:
            new_y = self.rect.y + MONSTER_SPEED
        else:
            new_y = self.rect.y
        
        # Check for collision with stone tiles
        if not self.collides_with_stone(new_x, new_y):
            self.rect.topleft = (new_x, new_y)
        
        # Check for collision with players
        if self.rect.colliderect(player1.rect):
            player1.kill()
        if self.rect.colliderect(player2.rect):
            player2.kill()
        
        # Check if both players are dead
        if not player1.alive() and not player2.alive():
            game_over()
    
    def collides_with_stone(self, x, y):
        # Check all four corners of the monster's bounding box
        corners = [
            (x, y),
            (x + self.rect.width - 1, y),
            (x, y + self.rect.height - 1),
            (x + self.rect.width - 1, y + self.rect.height - 1)
        ]
        for corner in corners:
            tile_x = corner[0] // TILE_SIZE
            tile_y = corner[1] // TILE_SIZE
            if game_map.get_current_map()[tile_y][tile_x] == 's':
                return True
        return False


def game_over():
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, (255, 0, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)
    main()


def main():
    global player1, player2, player_group, bullets, monsters

    # Create player instances
    player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RCTRL}, player_image)
    player2 = Player(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_g}, player2_image)
    player_group = pygame.sprite.Group(player1, player2)
    bullets = pygame.sprite.Group()
    
    # Create monsters
    monsters = pygame.sprite.Group()

    game_map.spawn_monsters(game_map.get_current_overlays())

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == player1.controls['shoot']:
                    player1.shoot()
                if event.key == player2.controls['shoot']:
                    player2.shoot()
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Update player positions
        player1.update(keys)
        player2.update(keys)
        
        # Update bullets
        bullets.update()
        
        # Update monsters
        monsters.update()
        
        # Check for bullet collisions with monsters
        for bullet in bullets:
            monster_hit = pygame.sprite.spritecollideany(bullet, monsters)
            if monster_hit:
                bullet.kill()
                monster_hit.kill()
        
        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw tiles from the map
        for y, row in enumerate(game_map.get_current_map()):
            for x, tile in enumerate(row):
                if tile == 'g':
                    screen.blit(grass_image, (x * TILE_SIZE, y * TILE_SIZE))
                elif tile == 's':
                    screen.blit(stone_image, (x * TILE_SIZE, y * TILE_SIZE))


        # Draw players, bullets, and monsters
        player_group.draw(screen)
        bullets.draw(screen)
        monsters.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    main()
