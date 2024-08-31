import pygame
import sys
import json

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

# Load map from JSON file
with open('map.json') as f:
    game_map = json.load(f)['map']

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
        if game_map[tile_y][tile_x] == 's':
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
    
    def collides_with_stone(self, x, y):
        # Check all four corners of the player's bounding box
        corners = [
            (x, y),
            (x + self.rect.width - 1, y),
            (x, y + self.rect.height - 1),
            (x + self.rect.width - 1, y + self.rect.height - 1)
        ]
        for corner in corners:
            tile_x = corner[0] // TILE_SIZE
            tile_y = corner[1] // TILE_SIZE
            if game_map[tile_y][tile_x] == 's':
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
        # Move towards the player
        if player1.rect.x < self.rect.x:
            new_x = self.rect.x - MONSTER_SPEED
        elif player1.rect.x > self.rect.x:
            new_x = self.rect.x + MONSTER_SPEED
        else:
            new_x = self.rect.x
        
        if player1.rect.y < self.rect.y:
            new_y = self.rect.y - MONSTER_SPEED
        elif player1.rect.y > self.rect.y:
            new_y = self.rect.y + MONSTER_SPEED
        else:
            new_y = self.rect.y
        
        # Check for collision with stone tiles
        if not self.collides_with_stone(new_x, new_y):
            self.rect.topleft = (new_x, new_y)
        
        # Check for collision with players
        if self.rect.colliderect(player1.rect) or self.rect.colliderect(player2.rect):
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
            if game_map[tile_y][tile_x] == 's':
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
    monsters.add(Monster(100, 100))
    monsters.add(Monster(500, 300))
    
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
        for y, row in enumerate(game_map):
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
