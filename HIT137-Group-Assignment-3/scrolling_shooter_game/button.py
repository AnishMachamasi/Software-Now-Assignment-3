import pygame


class Button:
    def __init__(self, x, y, image, scale):
        """
        Initialize the button with position, image, and scale.
        """
        # Check if the image is valid
        if not isinstance(image, pygame.Surface):
            raise TypeError("Image must be a pygame.Surface")

        # Check if scale is a valid positive number
        if not isinstance(scale, (int, float)) or scale <= 0:
            raise ValueError("Scale must be a positive number")

        # Resize the image based on the scale
        try:
            width = image.get_width()
            height = image.get_height()
            self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        except Exception as e:
            raise RuntimeError(f"Failed to scale image: {e}")

        # Set the button rectangle position
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Track if the button is clicked
        self.clicked = False

    def draw(self, surface):
        """
        Draw the button on the screen and return True if clicked.
        """
        # Ensure the surface is a valid pygame surface
        if not isinstance(surface, pygame.Surface):
            raise TypeError("Surface must be a pygame.Surface")

        action = False

        # Get current mouse position
        pos = pygame.mouse.get_pos()

        # Check if mouse is over the button and clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        # Reset clicked state when mouse button is released
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw the button image on the surface
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action