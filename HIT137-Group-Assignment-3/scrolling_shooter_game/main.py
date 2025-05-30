import csv
import os
import random
import sys

import button
import pygame
from config import (BG, BLACK, COLS, FPS, GRAVITY, GREEN, MAX_LEVELS, PINK,
                    RED, ROWS, SCREEN_HEIGHT, SCREEN_WIDTH, SCROLL_THRESH,
                    TILE_SIZE, TILE_TYPES, WHITE)
from pygame import mixer

# Initialize pygame with error handling
try:
    if not pygame.get_init():
        pygame.init()
    if not mixer.get_init():
        mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shooter")
except (pygame.error, Exception) as e:
    print(f"Game initialization failed: {str(e)}")
    sys.exit(1)

# Set framerate with validation
try:
    clock = pygame.time.Clock()
    if not isinstance(FPS, (int, float)) or FPS <= 0:
        FPS = 60  # Default if invalid
except Exception as e:
    print(f"Clock initialization error: {str(e)}")
    FPS = 60
    clock = pygame.time.Clock()

# Game state variables with type checking
screen_scroll = 0 if isinstance(0, int) else 0
bg_scroll = 0 if isinstance(0, int) else 0
level = 1 if isinstance(1, int) and 1 <= MAX_LEVELS else 1
start_game = False if isinstance(False, bool) else False
start_intro = False if isinstance(False, bool) else False


# Player action variables with type checking
moving_left = False if isinstance(False, bool) else False
moving_right = False if isinstance(False, bool) else False
shoot = False if isinstance(False, bool) else False
grenade = False if isinstance(False, bool) else False
grenade_thrown = False if isinstance(False, bool) else False

def load_asset(path, asset_type="image", volume=0.05):
    """Load game assets with full validation and error handling"""
    if not isinstance(path, str) or not os.path.exists(path):
        print(f"Missing {asset_type} file: {path}")
        return None
    
    try:
        if asset_type == "sound":
            sound = pygame.mixer.Sound(path)
            if isinstance(volume, (int, float)) and 0 <= volume <= 1:
                sound.set_volume(volume)
            return sound
        elif asset_type == "image":
            img = pygame.image.load(path).convert_alpha()
            return img
    except (pygame.error, Exception) as e:
        print(f"Error loading {asset_type} {path}: {str(e)}")
    return None

# Load sounds
jump_fx = load_asset("./sounds/audio/jump.wav", "sound", 0.05) or pygame.mixer.Sound()
shot_fx = load_asset("./sounds/audio/shot.wav", "sound", 0.05) or pygame.mixer.Sound()
grenade_fx = load_asset("./sounds/audio/grenade.wav", "sound", 0.05) or pygame.mixer.Sound()


# Load images
start_img = load_asset("img/start_btn.png") or pygame.Surface((100, 50), pygame.SRCALPHA)
exit_img = load_asset("img/exit_btn.png") or pygame.Surface((100, 50), pygame.SRCALPHA)
restart_img = load_asset("img/restart_btn.png") or pygame.Surface((100, 50), pygame.SRCALPHA)
pine1_img = load_asset("img/Background/pine1.png") or pygame.Surface((100, 100), pygame.SRCALPHA)
pine2_img = load_asset("img/Background/pine2.png") or pygame.Surface((100, 100), pygame.SRCALPHA)
mountain_img = load_asset("img/Background/mountain.png") or pygame.Surface((100, 100), pygame.SRCALPHA)
sky_img = load_asset("img/Background/sky_cloud.png") or pygame.Surface((100, 100), pygame.SRCALPHA)

# Load tiles
img_list = []
for x in range(TILE_TYPES if isinstance(TILE_TYPES, int) and TILE_TYPES > 0 else 0):
    img = load_asset(f"img/Tile/{x}.png") or pygame.Surface((TILE_SIZE, TILE_SIZE))
    if isinstance(TILE_SIZE, int) and TILE_SIZE > 0:
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Load items with validation
bullet_img = load_asset("img/icons/bullet.png") or pygame.Surface((10, 10), pygame.SRCALPHA)
grenade_img = load_asset("img/icons/grenade.png") or pygame.Surface((15, 15), pygame.SRCALPHA)
health_box_img = load_asset("img/icons/health_box.png") or pygame.Surface((30, 30), pygame.SRCALPHA)
ammo_box_img = load_asset("img/icons/ammo_box.png") or pygame.Surface((30, 30), pygame.SRCALPHA)
grenade_box_img = load_asset("img/icons/grenade_box.png") or pygame.Surface((30, 30), pygame.SRCALPHA)

item_boxes = {
    "Health": health_box_img if health_box_img else pygame.Surface((30, 30)),
    "Ammo": ammo_box_img if ammo_box_img else pygame.Surface((30, 30)),
    "Grenade": grenade_box_img if grenade_box_img else pygame.Surface((30, 30)),
}

# Initialize font with validation
try:
    font = pygame.font.SysFont("Futura", 30) if pygame.font else pygame.font.SysFont(None, 30)
except (pygame.error, Exception):
    font = pygame.font.SysFont(None, 30)


def draw_text(text, font, text_col, x, y):
    """Draw text on screen at (x,y) position"""
    try:
        if not text or not font:
            return  # Skip if invalid inputs
        
        img = font.render(str(text), True, text_col)
        screen.blit(img, (int(x), int(y)))
    except:
        print("Couldn't draw text")  # Fail silently for game continuity


def draw_bg():
    """Draw scrolling background"""
    try:
        screen.fill(BG)
        
        # Skip drawing if images aren't loaded
        if not all([sky_img, mountain_img, pine1_img, pine2_img]):
            return
            
        width = sky_img.get_width()
        for x in range(5):
            screen.blit(sky_img, ((x * width) - int(bg_scroll * 0.5), 0))
            screen.blit(mountain_img, (
                (x * width) - int(bg_scroll * 0.6),
                SCREEN_HEIGHT - mountain_img.get_height() - 300
            ))
            screen.blit(pine1_img, (
                (x * width) - int(bg_scroll * 0.7),
                SCREEN_HEIGHT - pine1_img.get_height() - 150
            ))
            screen.blit(pine2_img, (
                (x * width) - int(bg_scroll * 0.8), 
                SCREEN_HEIGHT - pine2_img.get_height()
            ))
    except:
        print("Background drawing error")

def reset_level():
    """Reset level by clearing all groups"""
    groups = [
        enemy_group, bullet_group, grenade_group,
        explosion_group, item_box_group, decoration_group,
        water_group, exit_group
    ]
    
    for group in groups:
        if hasattr(group, 'empty'):
            group.empty()
    
    # Return empty level data
    return [[-1 for _ in range(COLS)] for _ in range(ROWS)]

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        
        # Validate input parameters
        self.char_type = str(char_type) if char_type else "player"
        self.speed = max(0, float(speed)) if str(speed).replace('.', '').isdigit() else 5
        self.ammo = max(0, int(ammo)) if str(ammo).isdigit() else 0
        self.grenades = max(0, int(grenades)) if str(grenades).isdigit() else 0
        scale = float(scale) if str(scale).replace('.', '').isdigit() else 1.0
        x = int(x) if str(x).isdigit() else 0
        y = int(y) if str(y).isdigit() else 0
        
        # Initialize attributes
        self.alive = True
        self.start_ammo = self.ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        # AI specific
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load animations with validation
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            temp_list = []
            try:
                path = f"img/{self.char_type}/{animation}"
                if os.path.exists(path):  # Validate path exists
                    num_of_frames = len(os.listdir(path))
                    for i in range(num_of_frames):
                        img_path = f"{path}/{i}.png"
                        if os.path.exists(img_path):  # Validate image exists
                            img = pygame.image.load(img_path).convert_alpha()
                            img = pygame.transform.scale(
                                img, 
                                (max(1, int(img.get_width() * scale)), 
                                 max(1, int(img.get_height() * scale)))
                            )
                            temp_list.append(img)
            except Exception as e:
                print(f"Error loading {animation} animation: {e}")
            
            self.animation_list.append(temp_list if temp_list else [pygame.Surface((32, 32))])

        # Initialize sprite image and rect
        self.image = self.animation_list[self.action][self.frame_index] if self.animation_list else pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        if not hasattr(self, 'alive'):  # Ensure attribute exists
            self.alive = True
        self.update_animation()
        self.check_alive()
        if hasattr(self, 'shoot_cooldown') and self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(
                self.rect.x + dx, self.rect.y, self.width, self.height
            ):
                dx = 0
                # if the ai has hit a wall then make it turn around
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(
                self.rect.x, self.rect.y + dy, self.width, self.height
            ):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == "player":
            if (
                self.rect.right > SCREEN_WIDTH - SCROLL_THRESH
                and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH
            ) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(
                self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                self.rect.centery,
                self.direction,
            )
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (
                        self.rect.centerx + 75 * self.direction,
                        self.rect.centery,
                    )

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        if hasattr(self, 'image') and hasattr(self, 'rect') and hasattr(self, 'flip'):
            try:
                screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            except:
                pass


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        """Process level data with basic validation"""
        try:
            if not data or not isinstance(data, list):
                return None, None  # Return empty values if invalid data

            self.level_length = len(data[0]) if data and isinstance(data[0], list) else 0

            player = None
            health_bar = None

            for y, row in enumerate(data):
                if not isinstance(row, list):
                    continue  # Skip invalid rows

                for x, tile in enumerate(row):
                    try:
                        tile = int(tile) if str(tile).isdigit() else -1
                        if tile < 0:
                            continue

                        # Validate image exists in img_list before using
                        if not isinstance(img_list, list) or tile >= len(img_list) or not img_list[tile]:
                            continue

                        img = img_list[tile]
                        if not isinstance(img, pygame.Surface):
                            continue

                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)

                        # Obstacles (0-8)
                        if 0 <= tile <= 8:
                            self.obstacle_list.append(tile_data)

                        # Water (9-10)
                        elif 9 <= tile <= 10:
                            if hasattr(water_group, 'add'):
                                water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                                water_group.add(water)

                        # Decorations (11-14)
                        elif 11 <= tile <= 14:
                            if hasattr(decoration_group, 'add'):
                                decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                                decoration_group.add(decoration)

                        # Player (15)
                        elif tile == 15:
                            player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                            if hasattr(HealthBar, '__init__'):
                                health_bar = HealthBar(10, 10, player.health, player.health)

                        # Enemy (16)
                        elif tile == 16:
                            if hasattr(enemy_group, 'add'):
                                enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                                enemy_group.add(enemy)

                        # Items (17-19)
                        elif tile == 17:  # Ammo
                            if hasattr(item_box_group, 'add'):
                                item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                                item_box_group.add(item_box)
                        elif tile == 18:  # Grenade
                            if hasattr(item_box_group, 'add'):
                                item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                                item_box_group.add(item_box)
                        elif tile == 19:  # Health
                            if hasattr(item_box_group, 'add'):
                                item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                                item_box_group.add(item_box)

                        # Exit (20)
                        elif tile == 20:
                            if hasattr(exit_group, 'add'):
                                exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                                exit_group.add(exit)

                    except Exception as e:
                        print(f"Error processing tile at ({x},{y}): {e}")
                        continue

            return player, health_bar

        except Exception as e:
            print(f"Error processing level data: {e}")
            return None, None

    def draw(self):
        """Draw obstacles with scroll offset"""
        try:
            if not hasattr(self, 'obstacle_list'):
                return

            for tile in self.obstacle_list:
                if (len(tile) >= 2 and isinstance(tile[0], pygame.Surface) 
                    and isinstance(tile[1], pygame.Rect)):
                    try:
                        tile[1].x += screen_scroll
                        screen.blit(tile[0], tile[1])
                    except:
                        continue  # Skip if drawing fails
        except:
            pass  # Fail silently if drawing encounters errors

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Validate image
        if not isinstance(img, pygame.Surface):
            raise TypeError("img must be a pygame.Surface")

        # Validate x and y
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("x and y must be integers")

        # Validate TILE_SIZE before using in arithmetic
        if not isinstance(TILE_SIZE, int) or TILE_SIZE <= 0:
            raise ValueError("TILE_SIZE must be a positive integer")

        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()

        # Position the decoration sprite using TILE_SIZE and image height
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        # Validate screen_scroll before applying
        if not isinstance(screen_scroll, (int, float)):
            raise TypeError("screen_scroll must be a number")

        # Move the decoration with the screen
        self.rect.x += screen_scroll
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Basic sanity check for image
        if not hasattr(img, 'get_rect') or not hasattr(img, 'get_height'):
            raise ValueError("Invalid image: must be a valid pygame.Surface")

        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()

        # Use TILE_SIZE safely
        try:
            self.rect.midtop = (
                x + TILE_SIZE // 2,
                y + (TILE_SIZE - self.image.get_height()),
            )
        except Exception as e:
            raise ValueError(f"Invalid position or TILE_SIZE: {e}")

    def update(self):
        # Make sure screen_scroll exists and is numeric
        if not isinstance(screen_scroll, (int, float)):
            raise TypeError("screen_scroll must be a number")

        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        # Basic validation to ensure image has required attributes
        if not hasattr(img, 'get_rect') or not hasattr(img, 'get_height'):
            raise ValueError("Invalid image: must be a valid pygame.Surface")

        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()

        # Safe position calculation
        try:
            self.rect.midtop = (
                x + TILE_SIZE // 2,
                y + (TILE_SIZE - self.image.get_height()),
            )
        except Exception as e:
            raise ValueError(f"Invalid TILE_SIZE or coordinates: {e}")

    def update(self):
        # Validate scroll value
        if not isinstance(screen_scroll, (int, float)):
            raise TypeError("screen_scroll must be a number")

        self.rect.x += screen_scroll
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type

        try:
            self.image = item_boxes[self.item_type]
            self.rect = self.image.get_rect()
            self.rect.midtop = (
                x + TILE_SIZE // 2,
                y + (TILE_SIZE - self.image.get_height()),
            )
        except Exception as e:
            print(f"Error initializing ItemBox: {e}")

    def update(self):
        try:
            self.rect.x += screen_scroll

            if pygame.sprite.collide_rect(self, player):
                if self.item_type == "Health":
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                elif self.item_type == "Ammo":
                    player.ammo += 15
                elif self.item_type == "Grenade":
                    player.grenades += 3
                self.kill()
        except Exception as e:
            print(f"Error updating ItemBox: {e}")
class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        try:
            # update with new health
            self.health = health
            # calculate health ratio
            ratio = self.health / self.max_health

            pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
            pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
            pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
        except Exception as e:
            print(f"Error drawing HealthBar: {e}")
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        try:
            self.speed = 10
            self.image = bullet_img
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.direction = direction
        except Exception as e:
            print(f"Error initializing Bullet: {e}")

    def update(self):
        try:
            # move bullet
            self.rect.x += (self.direction * self.speed) + screen_scroll

            # check if bullet has gone off screen
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()

            # check for collision with level
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect):
                    self.kill()

            # check collision with player
            if pygame.sprite.spritecollide(player, bullet_group, False):
                if player.alive:
                    player.health -= 5
                    self.kill()

            # check collision with enemies
            for enemy in enemy_group:
                if pygame.sprite.spritecollide(enemy, bullet_group, False):
                    if enemy.alive:
                        enemy.health -= 25
                        self.kill()
        except Exception as e:
            print(f"Error updating Bullet: {e}")

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        try:
            self.timer = 100
            self.vel_y = -11
            self.speed = 7
            self.image = grenade_img
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.direction = direction
        except Exception as e:
            print(f"Error initializing Grenade: {e}")

    def update(self):
        try:
            self.vel_y += GRAVITY
            dx = self.direction * self.speed
            dy = self.vel_y

            # check for collision with level
            for tile in world.obstacle_list:
                # check collision with walls (x direction)
                if tile[1].colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    self.direction *= -1
                    dx = self.direction * self.speed
                # check for collision in the y direction
                if tile[1].colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    self.speed = 0
                    # thrown up
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                    # falling down
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        dy = tile[1].top - self.rect.bottom

            # update grenade position
            self.rect.x += dx + screen_scroll
            self.rect.y += dy

            # countdown timer
            self.timer -= 1
            if self.timer <= 0:
                self.kill()
                grenade_fx.play()
                explosion = Explosion(self.rect.x, self.rect.y, 0.5)
                explosion_group.add(explosion)
                # damage player if nearby
                if (
                    abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2
                    and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2
                ):
                    player.health -= 50
                # damage enemies if nearby
                for enemy in enemy_group:
                    if (
                        abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2
                        and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2
                    ):
                        enemy.health -= 50
        except Exception as e:
            print(f"Error updating Grenade: {e}")
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        try:
            for num in range(1, 6):
                img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale))
                )
                self.images.append(img)
        except Exception as e:
            print(f"Error loading explosion images: {e}")
        
        self.frame_index = 0
        if self.images:
            self.image = self.images[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
        else:
            self.image = None
            self.rect = pygame.Rect(x, y, 0, 0)  # fallback empty rect

        self.counter = 0

    def update(self):
        try:
            # scroll
            self.rect.x += screen_scroll

            EXPLOSION_SPEED = 4
            # update explosion animation
            self.counter += 1

            if self.counter >= EXPLOSION_SPEED:
                self.counter = 0
                self.frame_index += 1
                # if animation finished delete explosion
                if self.frame_index >= len(self.images):
                    self.kill()
                else:
                    self.image = self.images[self.frame_index]
        except Exception as e:
            print(f"Error updating Explosion: {e}")
class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        try:
            self.fade_counter += self.speed
            if self.direction == 1:  # whole screen fade
                pygame.draw.rect(
                    screen,
                    self.colour,
                    (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT),
                )
                pygame.draw.rect(
                    screen,
                    self.colour,
                    (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                )
                pygame.draw.rect(
                    screen,
                    self.colour,
                    (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2),
                )
                pygame.draw.rect(
                    screen,
                    self.colour,
                    (
                        0,
                        SCREEN_HEIGHT // 2 + self.fade_counter,
                        SCREEN_WIDTH,
                        SCREEN_HEIGHT,
                    ),
                )
            if self.direction == 2:  # vertical screen fade down
                pygame.draw.rect(
                    screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter)
                )
            if self.fade_counter >= SCREEN_WIDTH:
                fade_complete = True
        except Exception as e:
            print(f"Error during screen fade: {e}")

        return fade_complete
    
# create screen fades
try:
    intro_fade = ScreenFade(1, BLACK, 4)
    death_fade = ScreenFade(2, PINK, 4)
except Exception as e:
    print(f"Error creating screen fades: {e}")

# create buttons
try:
    start_button = button.Button(
        SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1
    )
    exit_button = button.Button(
        SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1
    )
    restart_button = button.Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2
    )
except Exception as e:
    print(f"Error creating buttons: {e}")

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list and load level data
world_data = []
try:
    for row in range(ROWS):
        world_data.append([-1] * COLS)
    with open(f"./level_data/level{level}_data.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
except Exception as e:
    print(f"Error loading level data: {e}")

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)

    if not start_game:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        health_bar.draw(player.health)
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade = Grenade(
                    player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                    player.rect.top,
                    player.direction,
                )
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)  # jump
            elif moving_left or moving_right:
                player.update_action(1)  # run
            else:
                player.update_action(0)  # idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                try:
                    with open(f"./level_data/level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                except Exception as e:
                    print(f"Error loading new level data: {e}")
                if level <= MAX_LEVELS:
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    try:
                        with open(f"./level_data/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                    except Exception as e:
                        print(f"Error loading level data after death: {e}")
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
