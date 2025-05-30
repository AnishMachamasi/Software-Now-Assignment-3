# Game Configuration Constants

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)  # Maintain 16:10 aspect ratio
FPS = 60  # Frames per second for the game loop

# Physics
GRAVITY = 0.75  # Downward gravity for player and objects
SCROLL_THRESH = 200  # Threshold before screen starts scrolling

# Tile map dimensions
ROWS = 16
COLS = 150
TILE_TYPES = 21  # Number of unique tile types in the tile set
MAX_LEVELS = 3  # Total number of levels in the game
TILE_SIZE = SCREEN_HEIGHT // ROWS  # Height of each tile (square tiles)

# Color definitions (RGB tuples)
BG = (144, 201, 120)  # Background green
RED = (255, 0, 0)     # For player damage or alerts
WHITE = (255, 255, 255)  # General UI text
GREEN = (0, 255, 0)   # Health bar or indicators
BLACK = (0, 0, 0)     # UI outlines or text
PINK = (235, 65, 54)  # Fade effect or special alerts
