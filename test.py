import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 960
display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
screen = pygame.Surface((WIDTH/2, HEIGHT/2))

# Colors
white = (255, 255, 255)

# Snowdrop properties
water = []
for _ in range(20):  # Number of snowdrops
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(0,15)

    water.append([x, y, size])

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill('light blue')  # Clear screen with a black background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update snowdrops
    for drop in water:

        if drop[2] > 40:
            drop[2] = 0
            drop[0] = random.randint(0, WIDTH)  # New random x position
            drop[1] = random.randint(0, HEIGHT)  # Start above the screen

        drop[2] += 1
        # Draw the snowdrop
        pygame.draw.circle(screen, 'white', (drop[0], drop[1]), drop[2], 1)

    # Update the display
    display.blit(pygame.transform.scale(screen, display.get_size()), (0, 0))
    pygame.display.flip()
    clock.tick(60)
    clicking = False

# Quit Pygame
pygame.quit()