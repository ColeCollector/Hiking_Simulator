import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Font settings
font = pygame.font.SysFont(None, 74)

# Biomes
biomes = ["Rocky", "Forest", "Desert"]
current_biome_index = 0
biome = biomes[current_biome_index]

# Background colors for each biome
background_colors = {
    "Rocky": (100, 100, 100),
    "Forest": (34, 139, 34),
    "Desert": (237, 201, 175)
}

# Function to get a random color for the current biome
def get_random_color(base_color):
    return tuple(min(max(c + random.randint(-30, 30), 0), 255) for c in base_color)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Press SPACE to change biome
                current_biome_index = (current_biome_index + 1) % len(biomes)
                biome = biomes[current_biome_index]

    # Set random background color based on the current biome
    background_color = background_colors[biome]

    # Fill the screen with the background color
    screen.fill(background_color)

    # Render and display the current biome name
    biome_text = font.render(biome, True, (255, 255, 255))
    text_rect = biome_text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(biome_text, text_rect)

    # Update the display
    pygame.display.flip()
    clock.tick(30)
