import pygame
import random

# Initialize Pygame
pygame.init()

# Set up display
window_size = (500, 500)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Random Shading')

# Define colors
base_color = (100, 200, 100)  # Base color of the square (greenish)

def draw_shaded_square(surface, top_left, size, base_color):
    for y in range(top_left[1], top_left[1] + size):
        for x in range(top_left[0], top_left[0] + size):
            # Randomly adjust the base color
            shade_variation = random.randint(-20, 20)  # Range of variation
            shaded_color = (
                max(0, min(255, base_color[0] + shade_variation)),
                max(0, min(255, base_color[1] + shade_variation)),
                max(0, min(255, base_color[2] + shade_variation))
            )
            surface.set_at((x, y), shaded_color)

# Example usage
top_left_position = (150, 150)
square_size = 100

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # Fill background with white
    draw_shaded_square(screen, top_left_position, square_size, base_color)
    
    pygame.display.flip()  # Update the display

pygame.quit()
