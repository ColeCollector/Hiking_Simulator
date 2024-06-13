import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Darken Screen Example')

# Set up a clock for managing the frame rate
clock = pygame.time.Clock()

# Create a semi-transparent surface
darken_surface = pygame.Surface((800, 600), pygame.SRCALPHA)  # Create a surface with the same size as the screen
darken_surface.fill((0, 0, 0, 128))                           # Fill the surface with black and set the alpha value (0-255)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen with a white background (or any other background)
    screen.fill((255, 255, 255))

    # (Here you would draw other elements to the screen)
    # Example: Drawing a red circle in the middle of the screen
    pygame.draw.circle(screen, (255, 0, 0), (400, 300), 50)

    # Blit the semi-transparent black surface onto the screen to darken it
    screen.blit(darken_surface, (0, 0))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 frames per second
    clock.tick(60)

pygame.quit()
sys.exit()
